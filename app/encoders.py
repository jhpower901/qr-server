from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from urllib.parse import urlparse


class EncodeError(ValueError):
    pass


@dataclass
class QRRequestData:
    qr_type: str
    data: str | None = None
    url: str | None = None

    # wifi
    ssid: str | None = None
    password: str | None = None
    encryption: str | None = None   # WPA | WEP | nopass
    hidden: bool = False


class QREncoder(Protocol):
    def encode(self, req: QRRequestData) -> str:
        ...


def escape_wifi_value(value: str) -> str:
    """
    WIFI QR 포맷에서 특수문자를 escape 합니다.
    """
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace(":", r"\:")
        .replace('"', r"\"")
    )


def normalize_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        raise EncodeError("url is empty")

    parsed = urlparse(raw_url)
    if not parsed.scheme:
        raw_url = f"https://{raw_url}"
        parsed = urlparse(raw_url)

    if not parsed.netloc:
        raise EncodeError("invalid url")

    return raw_url


class RawEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.data or not req.data.strip():
            raise EncodeError("data is empty")
        return req.data.strip()


class UrlEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.url:
            raise EncodeError("url is required for type=url")
        return normalize_url(req.url)


class WifiEncoder:
    """
    표준적인 Wi-Fi QR 문자열:
    WIFI:T:WPA;S:MySSID;P:mypassword;H:false;;
    """
    ALLOWED = {"WPA", "WEP", "nopass"}

    def encode(self, req: QRRequestData) -> str:
        if not req.ssid or not req.ssid.strip():
            raise EncodeError("ssid is required for type=wifi")

        ssid = escape_wifi_value(req.ssid.strip())

        encryption = (req.encryption or "WPA").strip()
        if encryption not in self.ALLOWED:
            raise EncodeError("encryption must be one of WPA, WEP, nopass")

        password = req.password or ""
        if encryption != "nopass" and not password:
            raise EncodeError("password is required unless encryption=nopass")

        password = escape_wifi_value(password)
        hidden = "true" if req.hidden else "false"

        return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{hidden};;"


ENCODER_REGISTRY: dict[str, QREncoder] = {
    "raw": RawEncoder(),
    "text": RawEncoder(),
    "url": UrlEncoder(),
    "wifi": WifiEncoder(),
}


def encode_qr_payload(req: QRRequestData) -> str:
    qr_type = (req.qr_type or "raw").strip().lower()

    encoder = ENCODER_REGISTRY.get(qr_type)
    if encoder is None:
        raise EncodeError(
            f"unsupported type: {qr_type}. "
            f"available: {', '.join(sorted(ENCODER_REGISTRY.keys()))}"
        )

    return encoder.encode(req)

