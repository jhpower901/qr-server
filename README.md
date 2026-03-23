# QR Server (qr.example.kr)

FastAPI 기반의 **QR 코드 생성 API 서버 + Web UI**입니다.  
Text, URL, Wi-Fi, Email 등 다양한 QR을 생성하고 SVG / PNG / JPG로 반환합니다.

---

## 🚀 Features

### Core

- ✅ Text / URL / Wi-Fi QR
- ✅ Email / Phone / SMS / vCard
- ✅ SVG / PNG / JPG 출력

### Rendering

- ✅ PNG → **투명 배경**
- ✅ JPG → **배경색 적용**
- ✅ RGB 색상 커스터마이징
- ✅ `dot` / `square` 스타일

### Advanced

- ✅ QR version 제어
- ✅ error correction (`L/M/Q/H`)
- ✅ optimize (데이터 분할)
- ✅ 다운로드 지원 (`Content-Disposition`)
- ✅ Base64URL 입력 지원
- ✅ POST 지원 (특수문자 / 긴 데이터 안전)

### UI

- ✅ `/ui` 웹 인터페이스
- ✅ 실시간 미리보기
- ✅ 색상 프리셋
- ✅ 공유 링크 생성

---

## 📌 What is this?

이 프로젝트는 **웹앱 + API 서버**입니다.

### 1) API 모드

```text
https://qr.example.kr/?type=text&text=hello
```

👉 QR 이미지가 바로 반환됩니다.

### 2) UI 모드

```text
https://qr.example.kr/ui
```

👉 브라우저에서 직접 생성하고 다운로드할 수 있습니다.

---

## 📦 Project Structure

```text
qr-server/
├── app
│   ├── __init__.py
│   ├── encoders.py
│   ├── renderers.py
│   ├── main.py
│   ├── static/
│   │   └── app.js
│   └── templates/
│       └── index.html
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Run

```bash
docker compose up -d --build
```

---

## 🌐 Endpoints

| 경로 | 설명 |
|------|------|
| `/` | QR 이미지 생성 (GET) |
| `/render` | QR 생성 (POST) |
| `/ui` | 웹 UI |
| `/health` | 헬스체크 |

---

# 🧪 Usage

## 📡 GET 방식

### Text

```text
https://qr.example.kr/?type=text&text=안녕하세요
```

### Text Base64URL

```text
https://qr.example.kr/?type=text&text_b64=7JWI64WV7ZWY7IS47JqU
```

`text_b64`가 있으면 `text`보다 우선합니다.

### URL

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

👉 `https://` 자동 보정

### URL Base64URL

```text
https://qr.example.kr/?type=url&url_b64=aHR0cHM6Ly93d3cubmF2ZXIuY29t
```

### Wi-Fi

```text
https://qr.example.kr/?type=wifi&wifi_ssid=MyWifi&wifi_password=12345678&wifi_encryption=WPA
```

### Email

```text
https://qr.example.kr/?type=email&email_address=test@example.com&email_subject=Hello&email_body=Hi
```

### Phone

```text
https://qr.example.kr/?type=phone&phone_number=01012345678
```

### SMS

```text
https://qr.example.kr/?type=sms&sms_number=01012345678&sms_message=Hello
```

### vCard

```text
https://qr.example.kr/?type=vcard&vcard_name=홍길동&vcard_phone=01012345678&vcard_email=test@example.com
```

---

## 📮 POST 방식

특수문자, 긴 데이터, API 연동에는 POST를 권장합니다.

### Text

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -o qr.png \
  -d '{
    "type": "text",
    "text": "hello",
    "format": "png"
  }'
```

### URL

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "url",
    "url": "https://naver.com"
  }'
```

### Wi-Fi

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "wifi",
    "wifi_ssid": "MyWifi",
    "wifi_password": "12345678",
    "wifi_encryption": "WPA"
  }'
```

### Email

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "email",
    "email_address": "test@example.com",
    "email_subject": "Hello",
    "email_body": "Hi"
  }'
```

### SMS

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "sms",
    "sms_number": "01012345678",
    "sms_message": "Hello"
  }'
```

### vCard

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "vcard",
    "vcard_name": "홍길동",
    "vcard_phone": "01012345678",
    "vcard_email": "test@example.com"
  }'
```

---

# 🖼️ Format

| format | 설명 |
|--------|------|
| svg | 기본 |
| png | 투명 배경 |
| jpg | 배경색 적용 |

### PNG 예시

```text
?type=text&text=hello&format=png
```

### JPG 예시

```text
?type=text&text=hello&format=jpg
```

---

# 🎨 색상 / 스타일 예시

## 전경색 RGB

```text
?type=text&text=hello&fg_r=255&fg_g=0&fg_b=0
```

## 배경색 RGB

```text
?type=text&text=hello&bg_r=255&bg_g=255&bg_b=0
```

## 흰 QR + 검은 배경 JPG

```text
https://qr.example.kr/?type=text&text=hello&format=jpg&fg_r=255&fg_g=255&fg_b=255&bg_r=0&bg_g=0&bg_b=0
```

## dot 스타일

```text
?type=text&text=hello&style=dot
```

## square 스타일

```text
?type=text&text=hello&style=square
```

---

# ⚙️ 파라미터 설명 + 예시

## 공통 파라미터

| 파라미터 | 설명 | 예시 |
|----------|------|------|
| `type` | QR 타입 | `type=text` |
| `style` | 모듈 스타일 | `style=dot` |
| `format` | 출력 포맷 | `format=png` |
| `scale` | 이미지 크기 배율 | `scale=12` |
| `border` | QR 바깥 여백 | `border=2` |
| `error_correction` | ECC 레벨 | `error_correction=H` |
| `version` | QR 버전(1~40) | `version=5` |
| `optimize` | segmentation 정도 | `optimize=20` |
| `download` | 다운로드 응답 | `download=1` |
| `fg_r`,`fg_g`,`fg_b` | 전경색 RGB | `fg_r=255&fg_g=0&fg_b=0` |
| `bg_r`,`bg_g`,`bg_b` | 배경색 RGB | `bg_r=255&bg_g=255&bg_b=255` |
| `jpg_quality` | JPG 품질 | `jpg_quality=95` |

### 공통 파라미터 사용 예시

```text
https://qr.example.kr/?type=text&text=hello&style=dot&format=jpg&scale=12&border=2&error_correction=H&version=5&optimize=20&fg_r=255&fg_g=255&fg_b=255&bg_r=0&bg_g=0&bg_b=0&jpg_quality=95&download=1
```

## 타입별 데이터 파라미터

| 타입 | 파라미터 | 예시 |
|------|----------|------|
| `text` | `text`, `text_b64` | `?type=text&text=hello` |
| `url` | `url`, `url_b64` | `?type=url&url=www.naver.com` |
| `wifi` | `wifi_ssid`, `wifi_password`, `wifi_encryption`, `wifi_hidden` | `?type=wifi&wifi_ssid=MyWifi&wifi_password=12345678&wifi_encryption=WPA` |
| `email` | `email_address`, `email_subject`, `email_body` | `?type=email&email_address=test@example.com` |
| `phone` | `phone_number` | `?type=phone&phone_number=01012345678` |
| `sms` | `sms_number`, `sms_message` | `?type=sms&sms_number=01012345678&sms_message=Hello` |
| `vcard` | `vcard_name`, `vcard_phone`, `vcard_email` | `?type=vcard&vcard_name=홍길동&vcard_phone=01012345678&vcard_email=test@example.com` |

---

# 🔥 특수문자 처리

다음이 포함되면 GET에서 다루기 불편할 수 있습니다.

```text
&, ?, #
```

이 경우에는 `text_b64`, `url_b64` 또는 POST를 사용하는 것을 권장합니다.

## 예시 1: Text Base64URL

```text
?type=text&text_b64=dmxlc3M6Ly9leGFtcGxlP3g9MSZ5PTIjdGFn
```

## 예시 2: URL Base64URL

```text
?type=url&url_b64=aHR0cHM6Ly9leGFtcGxlLmNvbS94PzEmeT0yI3RhZw
```

## 예시 3: POST

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -o qr.png \
  -d '{
    "type": "text",
    "text": "vless://example?x=1&y=2#tag",
    "format": "png"
  }'
```

---

# 🧠 Rendering Logic

```text
[Request]
   ↓
[encoders.py] → payload 생성
   ↓
[renderers.py] → SVG 생성
   ↓
PNG / JPG 변환
   ↓
[Response]
```

---

# 🖥️ Web UI

```text
https://qr.example.kr/ui
```

### 기능

- 실시간 미리보기
- 타입 선택 (`text`, `url`, `wifi`, `email`, `phone`, `sms`, `vcard`)
- 색상 프리셋
- PNG / JPG 차이 안내
- 다운로드
- 공유 링크 생성

---

# ⚠️ Notes

- PNG → 배경 투명
- JPG → 배경색 적용
- `text_b64`가 입력되면 `text`는 무시됩니다.
- `url_b64`가 입력되면 `url`은 무시됩니다.
- 스타일을 과하게 변경하면 인식률이 떨어질 수 있습니다.
- 긴 데이터일수록 QR가 복잡해집니다.
- 특수문자는 POST 또는 Base64URL 사용을 권장합니다.

---

# 🔌 Extending

```python
class EmailEncoder:
    def encode(self, req):
        return f"mailto:{req.email}"
```

```python
ENCODER_REGISTRY["email"] = EmailEncoder()
```

---

# 📌 TODO

- [ ] Logo 삽입
- [ ] Redis 캐싱
- [ ] Rate limiting

---

# 🧾 License

MIT
