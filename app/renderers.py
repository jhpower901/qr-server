from __future__ import annotations

import html
from io import BytesIO, StringIO
from typing import List, Tuple

import cairosvg
import qrcode


class RenderError(ValueError):
    pass


def build_qr_matrix(
    data: str,
    border: int = 4,
    error_correction: str = "M",
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

    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_map[ec],
        box_size=10,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    return qr.get_matrix(), qr.version


def is_in_finder_zone(row: int, col: int, n: int, border: int) -> bool:
    """
    Finder pattern(좌상, 우상, 좌하) 영역과 그 주변 1칸까지 제외합니다.
    dot 렌더링 시 finder를 따로 예쁘게 그리기 위해 사용합니다.
    """
    top = border
    left = border
    size = 7

    zones = [
        (top - 1, left - 1),           # top-left
        (top - 1, n - border - size), # top-right
        (n - border - size, left - 1) # bottom-left
    ]

    for zr, zc in zones:
        if zr <= row <= zr + size + 1 and zc <= col <= zc + size + 1:
            return True
    return False


def svg_header(total_px: int, background: str) -> str:
    bg = html.escape(background)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total_px}" height="{total_px}" '
        f'viewBox="0 0 {total_px} {total_px}" fill="none">'
        f'<rect width="{total_px}" height="{total_px}" fill="{bg}"/>'
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
    """
    원형 dot 스타일 렌더링.
    연결 바 없이 각 모듈을 독립적인 circle로 그립니다.
    """
    fill = html.escape(color)
    n = len(matrix)

    # 원 크기를 조금 키워서 더 촘촘하고 qr.io 느낌에 가깝게
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
    background: str,
) -> None:
    """
    qr.io 느낌의 둥근 finder pattern
    """
    fill = html.escape(color)
    bg = html.escape(background)

    outer = 7 * scale
    middle = 5 * scale
    inner = 3 * scale

    out.write(
        f'<rect x="{x}" y="{y}" width="{outer}" height="{outer}" '
        f'rx="{scale * 1.55:.2f}" fill="{fill}"/>'
    )
    out.write(
        f'<rect x="{x + scale}" y="{y + scale}" width="{middle}" height="{middle}" '
        f'rx="{scale * 1.10:.2f}" fill="{bg}"/>'
    )
    out.write(
        f'<rect x="{x + 2 * scale}" y="{y + 2 * scale}" width="{inner}" height="{inner}" '
        f'rx="{scale * 0.72:.2f}" fill="{fill}"/>'
    )


def draw_all_finders(
    out: StringIO,
    matrix: List[List[bool]],
    scale: int,
    color: str,
    background: str,
    border: int,
) -> None:
    n = len(matrix)

    positions: List[Tuple[int, int]] = [
        (border * scale, border * scale),
        ((n - border - 7) * scale, border * scale),
        (border * scale, (n - border - 7) * scale),
    ]

    for x, y in positions:
        draw_finder(out, x, y, scale, color, background)


def matrix_to_svg(
    matrix: List[List[bool]],
    style: str = "dot",
    scale: int = 10,
    color: str = "#000000",
    background: str = "#ffffff",
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
        draw_all_finders(out, matrix, scale, color, background, border)
    else:
        draw_square_modules(out, matrix, scale, color)

    out.write(svg_footer())
    return out.getvalue()


def svg_to_png_bytes(svg: str) -> bytes:
    buffer = BytesIO()
    cairosvg.svg2png(bytestring=svg.encode("utf-8"), write_to=buffer)
    return buffer.getvalue()