from __future__ import annotations

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response

from app.encoders import EncodeError, QRRequestData, encode_qr_payload
from app.renderers import RenderError, build_qr_matrix, matrix_to_svg, svg_to_png_bytes

app = FastAPI(title="Anzam QR Server")


def build_filename(qr_type: str, fmt: str) -> str:
    safe_type = (qr_type or "qr").replace("/", "_").replace(" ", "_")
    return f"{safe_type}-qr.{fmt}"


@app.get("/")
def generate_qr(
    # 공통
    qr_type: str = Query("raw", alias="type", description="raw | text | url | wifi"),
    style: str = Query("dot", description="dot | square"),
    fmt: str = Query("svg", alias="format", description="svg | png"),
    download: bool = Query(False, description="true면 attachment로 다운로드"),
    scale: int = Query(16, ge=4, le=64, description="모듈 크기"),
    border: int = Query(4, ge=1, le=16, description="QR border size"),
    color: str = Query("#000000", description="foreground color"),
    background: str = Query("#ffffff", description="background color"),
    error_correction: str = Query("M", description="L | M | Q | H"),

    # raw/text
    data: str | None = Query(None, description="범용 문자열"),

    # url
    url: str | None = Query(None, description="URL"),

    # wifi
    ssid: str | None = Query(None, description="Wi-Fi SSID"),
    password: str | None = Query(None, description="Wi-Fi password"),
    encryption: str | None = Query("WPA", description="WPA | WEP | nopass"),
    hidden: bool = Query(False, description="숨김 SSID 여부"),
):
    try:
        req = QRRequestData(
            qr_type=qr_type,
            data=data,
            url=url,
            ssid=ssid,
            password=password,
            encryption=encryption,
            hidden=hidden,
        )

        payload = encode_qr_payload(req)

        matrix = build_qr_matrix(
            data=payload,
            border=border,
            error_correction=error_correction,
        )

        svg = matrix_to_svg(
            matrix=matrix,
            style=style,
            scale=scale,
            color=color,
            background=background,
            border=border,
        )

        fmt = fmt.lower()
        if fmt not in {"svg", "png"}:
            raise ValueError("format must be one of svg, png")

        if fmt == "svg":
            content = svg.encode("utf-8")
            media_type = "image/svg+xml"
        else:
            content = svg_to_png_bytes(svg)
            media_type = "image/png"

        headers = {
            "Cache-Control": "public, max-age=3600",
        }

        if download:
            filename = build_filename(qr_type, fmt)
            headers["Content-Disposition"] = f'attachment; filename="{filename}"'

        return Response(
            content=content,
            media_type=media_type,
            headers=headers,
        )

    except (EncodeError, RenderError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to generate qr: {exc}") from exc