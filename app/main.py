from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import Response

from app.encoders import EncodeError, QRRequestData, encode_qr_payload
from app.renderers import (
    RenderError,
    build_qr_matrix,
    matrix_to_svg,
    svg_to_png_bytes,
)

app = FastAPI(title="QR Server")


def build_filename(qr_type: str, fmt: str) -> str:
    safe_type = (qr_type or "qr").replace("/", "_").replace(" ", "_")
    return f"{safe_type}-qr.{fmt}"


def render_response(
    req: QRRequestData,
    style: str,
    fmt: str,
    download: bool,
    scale: int,
    border: int,
    color: str,
    background: str,
    error_correction: str,
) -> Response:
    payload = encode_qr_payload(req)

    matrix, _version = build_qr_matrix(
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
        filename = build_filename(req.qr_type, fmt)
        headers["Content-Disposition"] = f'attachment; filename="{filename}"'

    return Response(
        content=content,
        media_type=media_type,
        headers=headers,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def generate_qr_get(
    qr_type: str = Query("raw", alias="type", description="raw | text | url | wifi"),
    style: str = Query("dot", description="dot | square"),
    fmt: str = Query("svg", alias="format", description="svg | png"),
    download: bool = Query(False, description="파일 다운로드 여부"),
    scale: int = Query(20, ge=4, le=64, description="모듈 크기"),
    border: int = Query(4, ge=1, le=16, description="QR border size"),
    color: str = Query("#000000", description="foreground color"),
    background: str = Query("#ffffff", description="background color"),
    error_correction: str = Query("H", description="L | M | Q | H"),

    # raw/text/url
    data: str | None = Query(None, description="일반 문자열"),
    data_b64: str | None = Query(None, description="base64url encoded 문자열"),
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
            data_b64=data_b64,
            url=url,
            ssid=ssid,
            password=password,
            encryption=encryption,
            hidden=hidden,
        )

        return render_response(
            req=req,
            style=style,
            fmt=fmt,
            download=download,
            scale=scale,
            border=border,
            color=color,
            background=background,
            error_correction=error_correction,
        )
    except (EncodeError, RenderError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to generate qr: {exc}") from exc


@app.post("/render")
def generate_qr_post(
    body: dict[str, Any] = Body(...),
):
    try:
        req = QRRequestData(
            qr_type=body.get("type", "raw"),
            data=body.get("data"),
            data_b64=body.get("data_b64"),
            url=body.get("url"),
            ssid=body.get("ssid"),
            password=body.get("password"),
            encryption=body.get("encryption", "WPA"),
            hidden=body.get("hidden", False),
        )

        return render_response(
            req=req,
            style=body.get("style", "dot"),
            fmt=body.get("format", "svg"),
            download=body.get("download", False),
            scale=body.get("scale", 20),
            border=body.get("border", 4),
            color=body.get("color", "#000000"),
            background=body.get("background", "#ffffff"),
            error_correction=body.get("error_correction", "H"),
        )
    except (EncodeError, RenderError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to generate qr: {exc}") from exc