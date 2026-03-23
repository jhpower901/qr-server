from __future__ import annotations

from typing import Any

from fastapi import Body, FastAPI, HTTPException, Query
from fastapi.responses import Response

from app.encoders import EncodeError, QRRequestData, encode_qr_payload
from app.renderers import (
    RenderError,
    build_qr_matrix,
    matrix_to_svg,
    rgb_to_css,
    svg_to_jpg_bytes,
    svg_to_png_bytes,
    validate_rgb,
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
    fg_r: int,
    fg_g: int,
    fg_b: int,
    bg_r: int,
    bg_g: int,
    bg_b: int,
    error_correction: str,
    version: int | None,
    optimize: int,
    jpg_quality: int,
) -> Response:
    fg_rgb = validate_rgb(fg_r, fg_g, fg_b, "foreground")
    bg_rgb = validate_rgb(bg_r, bg_g, bg_b, "background")

    foreground_css = rgb_to_css(*fg_rgb)
    background_css = rgb_to_css(*bg_rgb)

    payload = encode_qr_payload(req)

    matrix, _version = build_qr_matrix(
        data=payload,
        border=border,
        error_correction=error_correction,
        version=version,
        optimize=optimize,
    )

    fmt = fmt.lower()
    if fmt not in {"svg", "png", "jpg", "jpeg"}:
        raise ValueError("format must be one of svg, png, jpg, jpeg")

    svg_background = None if fmt == "png" else background_css

    svg = matrix_to_svg(
        matrix=matrix,
        style=style,
        scale=scale,
        color=foreground_css,
        background=svg_background,
        border=border,
    )

    if fmt == "svg":
        content = svg.encode("utf-8")
        media_type = "image/svg+xml"
        ext = "svg"
    elif fmt == "png":
        content = svg_to_png_bytes(svg)
        media_type = "image/png"
        ext = "png"
    else:
        content = svg_to_jpg_bytes(svg, background_rgb=bg_rgb, quality=jpg_quality)
        media_type = "image/jpeg"
        ext = "jpg"

    headers = {
        "Cache-Control": "public, max-age=3600",
    }

    if download:
        filename = build_filename(req.qr_type, ext)
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
    fmt: str = Query("svg", alias="format", description="svg | png | jpg"),
    download: bool = Query(False, description="파일 다운로드 여부"),
    scale: int = Query(20, ge=4, le=64, description="모듈 크기"),
    border: int = Query(4, ge=1, le=16, description="QR border size"),

    fg_r: int = Query(0, ge=0, le=255, description="foreground red"),
    fg_g: int = Query(0, ge=0, le=255, description="foreground green"),
    fg_b: int = Query(0, ge=0, le=255, description="foreground blue"),

    bg_r: int = Query(255, ge=0, le=255, description="background red"),
    bg_g: int = Query(255, ge=0, le=255, description="background green"),
    bg_b: int = Query(255, ge=0, le=255, description="background blue"),

    error_correction: str = Query("H", description="L | M | Q | H"),
    version: int | None = Query(None, ge=1, le=40, description="QR version (1~40)"),
    optimize: int = Query(20, ge=0, le=1000, description="data segmentation optimize value"),
    jpg_quality: int = Query(95, ge=1, le=100, description="JPEG quality"),

    data: str | None = Query(None, description="일반 문자열"),
    data_b64: str | None = Query(None, description="base64url encoded 문자열"),
    url: str | None = Query(None, description="URL"),

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
            fg_r=fg_r,
            fg_g=fg_g,
            fg_b=fg_b,
            bg_r=bg_r,
            bg_g=bg_g,
            bg_b=bg_b,
            error_correction=error_correction,
            version=version,
            optimize=optimize,
            jpg_quality=jpg_quality,
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
            fg_r=body.get("fg_r", 0),
            fg_g=body.get("fg_g", 0),
            fg_b=body.get("fg_b", 0),
            bg_r=body.get("bg_r", 255),
            bg_g=body.get("bg_g", 255),
            bg_b=body.get("bg_b", 255),
            error_correction=body.get("error_correction", "H"),
            version=body.get("version"),
            optimize=body.get("optimize", 20),
            jpg_quality=body.get("jpg_quality", 95),
        )
    except (EncodeError, RenderError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"failed to generate qr: {exc}") from exc