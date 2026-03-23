from __future__ import annotations

import html
from io import BytesIO, StringIO
from typing import List, Tuple

import cairosvg
import qrcode
from PIL import Image


class RenderError(ValueError):
    pass


def validate_rgb(r: int, g: int, b: int, name: str) -> tuple[int, int, int]:
    for v in (r, g, b):
        if not (0 <= v <= 255):
            raise RenderError(f"{name} RGB values must be between 0 and 255")
    return r, g, b


def rgb_to_css(r: int, g: int, b: int) -> str:
    return f"rgb({r}, {g}, {b})"


def build_qr_matrix(
    data: str,
    border: int = 4,
    error_correction: str = "H",
    version: int | None = None,
    optimize: int = 20,
) -> tuple[list[list[bool]], int]:
    ec_map = {
        "L": qrcode.constants.ERROR_CORRECT_L,
        "M": qrcode.constants.ERROR_CORRECT_M,
        "Q": qrcode.constants.ERROR_CORRECT_Q,
        "H": qrcode.constants.ERROR_CORRECT_H,
    }

    ec = error_correction.upper()
    if ec not in ec_map:
        raise RenderError("error_correction must be one of L, M, Q, H")

    if version is not None and not (1 <= version <= 40):
        raise RenderError("version must be between 1 and 40")

    qr = qrcode.QRCode(
        version=version,
        error_correction=ec_map[ec],
        box_size=10,
        border=border,
    )
    qr.add_data(data, optimize=optimize)
    qr.make(fit=(version is None))

    return qr.get_matrix(), qr.version


def is_in_finder_zone(row: int, col: int, n: int, border: int) -> bool:
    top = border
    left = border
    size = 7

    zones = [
        (top - 1, left - 1),
        (top - 1, n - border - size),
        (n - border - size, left - 1),
    ]

    for zr, zc in zones:
        if zr <= row <= zr + size + 1 and zc <= col <= zc + size + 1:
            return True
    return False


def svg_header(total_px: int, background: str | None) -> str:
    if background is None:
        bg_rect = ""
    else:
        bg_rect = f'<rect width="{total_px}" height="{total_px}" fill="{html.escape(background)}"/>'

    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_px}" height="{total_px}" '
        f'viewBox="0 0 {total_px} {total_px}" fill="none">'
        f"{bg_rect}"
    )


def svg_footer() -> str:
    return "</svg>"


def draw_dot_modules(
    out: StringIO,
    matrix: List[List[bool]],
    scale: int,
    color: str,
    border: int,
) -> None:
    fill = html.escape(color)
    n = len(matrix)

    radius = scale * 0.5

    for r in range(n):
        for c in range(n):
            if not matrix[r][c]:
                continue
            if is_in_finder_zone(r, c, n, border):
                continue

            cx = c * scale + scale / 2
            cy = r * scale + scale / 2

            out.write(
                f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" fill="{fill}"/>'
            )


def draw_square_modules(
    out: StringIO,
    matrix: List[List[bool]],
    scale: int,
    color: str,
) -> None:
    fill = html.escape(color)
    n = len(matrix)

    for r in range(n):
        for c in range(n):
            if not matrix[r][c]:
                continue

            x = c * scale
            y = r * scale

            out.write(
                f'<rect x="{x}" y="{y}" width="{scale}" height="{scale}" fill="{fill}"/>'
            )


def draw_finder(
    out: StringIO,
    x: int,
    y: int,
    scale: int,
    color: str,
) -> None:
    """
    배경색과 무관하게 동작하는 finder.
    가운데 영역을 실제로 비워서(구멍) PNG에서는 투명, JPG/SVG에서는 배경이 보이게 만듭니다.
    """
    fill = html.escape(color)

    outer = 7 * scale
    middle = 5 * scale
    inner = 3 * scale

    outer_rx = scale * 1.55
    middle_rx = scale * 1.10
    inner_rx = scale * 0.72

    x1, y1 = x, y
    x2, y2 = x + scale, y + scale
    x3, y3 = x + 2 * scale, y + 2 * scale

    # evenodd fill 규칙을 이용해서:
    # 1) 바깥 rounded rect를 채우고
    # 2) 가운데 rounded rect를 "구멍"으로 뚫습니다.
    # 그러면 배경색이 무엇이든 자연스럽게 보입니다.
    path = f"""
    <path fill="{fill}" fill-rule="evenodd" d="
        M {x1 + outer_rx:.2f} {y1:.2f}
        H {x1 + outer - outer_rx:.2f}
        A {outer_rx:.2f} {outer_rx:.2f} 0 0 1 {x1 + outer:.2f} {y1 + outer_rx:.2f}
        V {y1 + outer - outer_rx:.2f}
        A {outer_rx:.2f} {outer_rx:.2f} 0 0 1 {x1 + outer - outer_rx:.2f} {y1 + outer:.2f}
        H {x1 + outer_rx:.2f}
        A {outer_rx:.2f} {outer_rx:.2f} 0 0 1 {x1:.2f} {y1 + outer - outer_rx:.2f}
        V {y1 + outer_rx:.2f}
        A {outer_rx:.2f} {outer_rx:.2f} 0 0 1 {x1 + outer_rx:.2f} {y1:.2f}
        Z

        M {x2 + middle_rx:.2f} {y2:.2f}
        H {x2 + middle - middle_rx:.2f}
        A {middle_rx:.2f} {middle_rx:.2f} 0 0 1 {x2 + middle:.2f} {y2 + middle_rx:.2f}
        V {y2 + middle - middle_rx:.2f}
        A {middle_rx:.2f} {middle_rx:.2f} 0 0 1 {x2 + middle - middle_rx:.2f} {y2 + middle:.2f}
        H {x2 + middle_rx:.2f}
        A {middle_rx:.2f} {middle_rx:.2f} 0 0 1 {x2:.2f} {y2 + middle - middle_rx:.2f}
        V {y2 + middle_rx:.2f}
        A {middle_rx:.2f} {middle_rx:.2f} 0 0 1 {x2 + middle_rx:.2f} {y2:.2f}
        Z
    "/>
    """
    out.write(path)

    # 가운데 안쪽 진한 마커
    out.write(
        f'<rect x="{x3}" y="{y3}" width="{inner}" height="{inner}" '
        f'rx="{inner_rx:.2f}" fill="{fill}"/>'
    )


def draw_all_finders(
    out: StringIO,
    matrix: List[List[bool]],
    scale: int,
    color: str,
    border: int,
) -> None:
    n = len(matrix)

    positions: List[Tuple[int, int]] = [
        (border * scale, border * scale),
        ((n - border - 7) * scale, border * scale),
        (border * scale, (n - border - 7) * scale),
    ]

    for x, y in positions:
        draw_finder(out, x, y, scale, color)


def matrix_to_svg(
    matrix: List[List[bool]],
    style: str = "dot",
    scale: int = 10,
    color: str = "rgb(0, 0, 0)",
    background: str | None = "rgb(255, 255, 255)",
    border: int = 4,
) -> str:
    style = style.lower()
    if style not in {"dot", "square"}:
        raise RenderError("unsupported style. allowed: dot, square")

    n = len(matrix)
    total_px = n * scale

    out = StringIO()
    out.write(svg_header(total_px, background))

    if style == "dot":
        draw_dot_modules(out, matrix, scale, color, border)
        draw_all_finders(out, matrix, scale, color, border)
    else:
        draw_square_modules(out, matrix, scale, color)
        if background is not None:
            pass

    out.write(svg_footer())
    return out.getvalue()


def svg_to_png_bytes(svg: str) -> bytes:
    buffer = BytesIO()
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=buffer)
    return buffer.getvalue()


def svg_to_jpg_bytes(svg: str, background_rgb: tuple[int, int, int], quality: int = 95) -> bytes:
    png_bytes = svg_to_png_bytes(svg)

    with Image.open(BytesIO(png_bytes)).convert("RGBA") as rgba:
        bg = Image.new("RGB", rgba.size, background_rgb)
        bg.paste(rgba, mask=rgba.getchannel("A"))

        out = BytesIO()
        bg.save(out, format="JPEG", quality=quality, optimize=True)
        return out.getvalue()
    