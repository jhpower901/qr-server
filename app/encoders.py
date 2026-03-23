from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Protocol
from urllib.parse import quote, urlparse


class EncodeError(ValueError):
    pass


@dataclass
class QRRequestData:
    qr_type: str

    # 공용/텍스트
    text: str | None = None
    text_b64: str | None = None

    # URL
    url: str | None = None
    url_b64: str | None = None

    # Wi-Fi
    wifi_ssid: str | None = None
    wifi_password: str | None = None
    wifi_encryption: str | None = None
    wifi_hidden: bool = False

    # Email
    email_address: str | None = None
    email_subject: str | None = None
    email_body: str | None = None

    # Phone
    phone_number: str | None = None

    # SMS
    sms_number: str | None = None
    sms_message: str | None = None

    # vCard
    vcard_name: str | None = None
    vcard_phone: str | None = None
    vcard_email: str | None = None


class QREncoder(Protocol):
    def encode(self, req: QRRequestData) -> str:
        ...


def decode_base64url(value: str) -> str:
    try:
        padded = value + "=" * (-len(value) % 4)
        decoded = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return decoded.decode("utf-8")
    except Exception as exc:
        raise EncodeError("invalid base64url value") from exc


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


def escape_wifi_value(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace(";", r"\;")
        .replace(",", r"\,")
        .replace(":", r"\:")
        .replace('"', r"\"")
    )


def get_text_input(req: QRRequestData) -> str:
    if req.text_b64:
        decoded = decode_base64url(req.text_b64)
        if not decoded.strip():
            raise EncodeError("decoded text_b64 is empty")
        return decoded.strip()

    if req.text and req.text.strip():
        return req.text.strip()

    raise EncodeError("text is empty")


class TextEncoder:
    def encode(self, req: QRRequestData) -> str:
        return get_text_input(req)


class UrlEncoder:
    def encode(self, req: QRRequestData) -> str:
        if req.url_b64:
            decoded = decode_base64url(req.url_b64)
            return normalize_url(decoded)

        if req.url:
            return normalize_url(req.url)

        raise EncodeError("url is required for type=url")


class WifiEncoder:
    ALLOWED = {"WPA", "WEP", "nopass"}

    def encode(self, req: QRRequestData) -> str:
        if not req.wifi_ssid or not req.wifi_ssid.strip():
            raise EncodeError("wifi_ssid is required for type=wifi")

        ssid = escape_wifi_value(req.wifi_ssid.strip())

        encryption = (req.wifi_encryption or "WPA").strip()
        if encryption not in self.ALLOWED:
            raise EncodeError("wifi_encryption must be one of WPA, WEP, nopass")

        password = req.wifi_password or ""
        if encryption != "nopass" and not password:
            raise EncodeError("wifi_password is required unless wifi_encryption=nopass")

        password = escape_wifi_value(password)
        hidden = "true" if req.wifi_hidden else "false"

        return f"WIFI:T:{encryption};S:{ssid};P:{password};H:{hidden};;"


class EmailEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.email_address or not req.email_address.strip():
            raise EncodeError("email_address is required for type=email")

        address = req.email_address.strip()
        subject = req.email_subject.strip() if req.email_subject else ""
        body = req.email_body.strip() if req.email_body else ""

        query_parts: list[str] = []

        if subject:
            query_parts.append(f"subject={quote(subject)}")
        if body:
            query_parts.append(f"body={quote(body)}")

        if query_parts:
            return f"mailto:{address}?{'&'.join(query_parts)}"
        return f"mailto:{address}"


class PhoneEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.phone_number or not req.phone_number.strip():
            raise EncodeError("phone_number is required for type=phone")

        return f"tel:{req.phone_number.strip()}"


class SMSEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.sms_number or not req.sms_number.strip():
            raise EncodeError("sms_number is required for type=sms")

        number = req.sms_number.strip()
        message = req.sms_message.strip() if req.sms_message else ""

        return f"SMSTO:{number}:{message}"


class VCardEncoder:
    def encode(self, req: QRRequestData) -> str:
        if not req.vcard_name or not req.vcard_name.strip():
            raise EncodeError("vcard_name is required for type=vcard")

        name = req.vcard_name.strip()
        phone = req.vcard_phone.strip() if req.vcard_phone else ""
        email = req.vcard_email.strip() if req.vcard_email else ""

        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{name}",
            f"FN:{name}",
        ]

        if phone:
            lines.append(f"TEL:{phone}")

        if email:
            lines.append(f"EMAIL:{email}")

        lines.append("END:VCARD")

        return "\n".join(lines)


ENCODER_REGISTRY: dict[str, QREncoder] = {
    "raw": TextEncoder(),
    "text": TextEncoder(),
    "url": UrlEncoder(),
    "wifi": WifiEncoder(),
    "email": EmailEncoder(),
    "phone": PhoneEncoder(),
    "sms": SMSEncoder(),
    "vcard": VCardEncoder(),
}


def encode_qr_payload(req: QRRequestData) -> str:
    qr_type = (req.qr_type or "text").strip().lower()

    encoder = ENCODER_REGISTRY.get(qr_type)
    if encoder is None:
        raise EncodeError(
            f"unsupported type: {qr_type}. "
            f"available: {', '.join(sorted(ENCODER_REGISTRY.keys()))}"
        )

    return encoder.encode(req)
