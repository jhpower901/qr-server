# QR Server (qr.example.kr)

FastAPI 기반의 **QR 코드 생성 API 서버**입니다.
URL, 텍스트, Wi-Fi QR을 지원하며 SVG / PNG로 반환합니다.

---

## 🚀 Features

* ✅ URL QR
* ✅ Text QR (임의 문자열)
* ✅ Wi-Fi QR (SSID / Password / Encryption)
* ✅ SVG / PNG 출력 지원
* ✅ 다운로드 (`Content-Disposition`)
* ✅ dot / square 스타일
* ✅ **특수문자 안전 처리 (`data_b64`, POST 지원)**
* ✅ 확장 가능한 구조 (encoder / renderer 분리)

---

## 📌 What is this?

이 프로젝트는 **웹 UI 서비스가 아니라 API 서버**입니다.

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

👉 HTML 페이지가 아니라 **QR 이미지 자체가 응답됩니다**

### 적합한 사용

* 백엔드에서 QR 이미지 생성
* 자동화 / 봇 / 내부 서비스
* self-hosted QR API

### 포함되지 않은 것

* 입력 폼 UI
* 버튼 기반 생성 페이지
* QR 관리 기능

---

## 📦 Project Structure

```
qr-server/
├── app
│   ├── __init__.py
│   ├── encoders.py        # QR payload 생성 로직
│   ├── renderers.py       # QR → SVG/PNG 렌더링
│   └── main.py            # FastAPI 엔드포인트
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## ⚙️ Run

### Docker Compose

```bash
docker compose up -d --build
```

---

## 🌐 API Usage

기본 엔드포인트:

```
https://qr.example.kr/
```

---

## 🔹 1. Text QR

```text
https://qr.example.kr/?type=text&data=안녕하세요
```

---

## 🔹 2. URL QR

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

자동으로 `https://` 붙습니다.

---

## 🔹 3. Wi-Fi QR

### 기본 (WPA)

```text
https://qr.example.kr/?type=wifi&ssid=MyWifi&password=12345678&encryption=WPA
```

### 비밀번호 없음

```text
https://qr.example.kr/?type=wifi&ssid=GuestWifi&encryption=nopass
```

### 숨김 SSID

```text
https://qr.example.kr/?type=wifi&ssid=HiddenNet&password=12345678&hidden=true
```

---

## 🔥 특수문자 포함 데이터 처리 (중요)

QR 데이터에 아래 문자가 포함되면 문제가 발생할 수 있습니다:

```text
&, ?, #
```

### ❌ 문제

```text
data=vless://...?x=1&y=2#tag
```

* `&` → 파라미터 분리됨
* `#` → 서버로 전달되지 않음

---

## ✅ 해결 방법 1: data_b64 사용 (추천)

```text
https://qr.example.kr/?type=text&data_b64=BASE64URL&format=png
```

### Python 예시

```python
import base64

raw = "vless://example?x=1&y=2#tag"
encoded = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
print(encoded)
```

---

## ✅ 해결 방법 2: POST /render (가장 안전)

```bash
curl -X POST "https://qr.example.kr/render" \
  -H "Content-Type: application/json" \
  -o qr.png \
  -d '{
    "type": "text",
    "data": "vless://example?x=1&y=2#tag",
    "format": "png"
  }'
```

👉 긴 문자열 / 설정 문자열은 이 방법 권장

---

## 🎨 Style 옵션

| 값      | 설명         |
| ------ | ---------- |
| dot    | 점 스타일 (기본) |
| square | 정사각형       |

---

## 🖼️ Format 옵션

| 값   | 설명      |
| --- | ------- |
| svg | 기본      |
| png | PNG 이미지 |

---

## 📥 다운로드

```text
?download=true
```

---

## 🎯 전체 파라미터

| 파라미터             | 설명                      |
| ---------------- | ----------------------- |
| type             | raw / text / url / wifi |
| data             | 문자열                     |
| data_b64         | base64url 인코딩 문자열       |
| url              | URL                     |
| ssid             | Wi-Fi 이름                |
| password         | Wi-Fi 비밀번호              |
| encryption       | WPA / WEP / nopass      |
| hidden           | true / false            |
| style            | dot / square            |
| format           | svg / png               |
| download         | true / false            |
| scale            | QR 크기                   |
| border           | 여백                      |
| color            | 전경색                     |
| background       | 배경색                     |
| error_correction | L / M / Q / H           |

---

## 🧪 Examples

### PNG 다운로드

```text
https://qr.example.kr/?type=url&url=www.naver.com&format=png&download=true
```

---

### Wi-Fi QR PNG

```text
https://qr.example.kr/?type=wifi&ssid=MyWifi&password=12345678&format=png
```

---

## 🧠 Architecture

```
[Request]
   ↓
[encoders.py]  → QR payload 생성
   ↓
[renderers.py] → SVG 생성 / PNG 변환
   ↓
[Response]
```

---

## 🔌 Extending (확장 방법)

```python
class EmailEncoder:
    def encode(self, req):
        return f"mailto:{req.email}"
```

```python
ENCODER_REGISTRY["email"] = EmailEncoder()
```

---

## ⚠️ Notes

* PNG 변환은 `cairosvg` 사용
* Wi-Fi QR은 표준 형식 사용
* 스타일 과도 변경 시 인식률 저하 가능
* 긴 문자열은 QR 밀도 증가
* `data` 대신 `data_b64` 또는 `POST` 사용 권장

---

## 📌 TODO (확장 예정)

* [ ] Email QR (`mailto:`)
* [ ] Phone QR (`tel:`)
* [ ] SMS QR
* [ ] vCard (연락처)
* [ ] Logo 삽입
* [ ] Redis 캐싱
* [ ] Rate limiting

---

## 🧾 License

MIT
