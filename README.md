# QR Server (qr.example.kr)

FastAPI 기반의 **QR 코드 생성 API 서버 + Web UI**입니다.
URL, 텍스트, Wi-Fi QR을 생성하고 SVG / PNG / JPG로 반환합니다.

---

## 🚀 Features

### Core

* ✅ URL QR
* ✅ Text QR
* ✅ Wi-Fi QR (SSID / Password / Encryption)
* ✅ SVG / PNG / JPG 출력

### Rendering

* ✅ PNG → **투명 배경**
* ✅ JPG → **배경색 적용**
* ✅ RGB 색상 커스터마이징 (foreground / background)
* ✅ dot / square 스타일

### Advanced

* ✅ QR version 제어
* ✅ error correction (L/M/Q/H)
* ✅ optimize (데이터 분할)
* ✅ 다운로드 (`Content-Disposition`)
* ✅ 특수문자 안전 처리 (`data_b64`, POST 지원)

### UI

* ✅ `/ui` 웹 인터페이스
* ✅ 실시간 미리보기
* ✅ 색상 프리셋
* ✅ PNG/JPG 차이 안내

---

## 📌 What is this?

이 프로젝트는 **웹앱 + API 서버**입니다.

### 1) API 모드

```text
https://qr.example.kr/?type=text&data=hello
```

👉 QR 이미지가 바로 반환됨

### 2) UI 모드

```text
https://qr.example.kr/ui
```

👉 브라우저에서 직접 생성

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

| 경로        | 설명              |
| --------- | --------------- |
| `/`       | QR 이미지 생성 (GET) |
| `/render` | QR 생성 (POST)    |
| `/ui`     | 웹 UI            |
| `/health` | 헬스체크            |

---

# 🧪 Basic Usage

## Text

```text
https://qr.example.kr/?type=text&data=안녕하세요
```

---

## URL

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

👉 `https://` 자동 보정

---

## Wi-Fi

```text
https://qr.example.kr/?type=wifi&ssid=MyWifi&password=12345678
```

---

# 🖼️ Format

| format | 설명     |
| ------ | ------ |
| svg    | 기본     |
| png    | 투명 배경  |
| jpg    | 배경색 적용 |

---

## PNG (투명)

```text
?format=png
```

---

## JPG (배경 포함)

```text
?format=jpg
```

---

# 🎨 RGB 색상

## 전경색

```text
fg_r=255&fg_g=0&fg_b=0
```

## 배경색

```text
bg_r=255&bg_g=255&bg_b=0
```

---

## 예시

```text
https://qr.example.kr/?type=text&data=hello&format=jpg&fg_r=255&fg_g=255&fg_b=255&bg_r=0&bg_g=0&bg_b=0
```

---

# ⚙️ Advanced Parameters

| 파라미터             | 설명                      |
| ---------------- | ----------------------- |
| type             | raw / text / url / wifi |
| style            | dot / square            |
| format           | svg / png / jpg         |
| scale            | 크기                      |
| border           | 여백                      |
| error_correction | L / M / Q / H           |
| version          | QR version (1~40)       |
| optimize         | segmentation            |
| download         | 파일 다운로드                 |
| fg_r,g,b         | 전경 RGB                  |
| bg_r,g,b         | 배경 RGB                  |
| jpg_quality      | JPG 품질                  |
| data_b64         | base64url 데이터           |

---

# 🔥 특수문자 처리

다음이 포함되면:

```text
&, ?, #
```

👉 `data=` 사용 시 깨질 수 있음

---

## 해결 1: data_b64

```text
?data_b64=BASE64URL
```

---

## 해결 2: POST (권장)

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

* 실시간 미리보기
* 타입 선택 (text/url/wifi)
* 색상 프리셋
* PNG/JPG 차이 안내
* 다운로드

---

# ⚠️ Notes

* PNG → 배경 투명
* JPG → 배경색 필요
* QR 스타일 과도 변경 시 인식률 저하 가능
* 긴 데이터 → QR 복잡도 증가
* 특수문자 → POST 또는 data_b64 사용

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

* [ ] Email QR
* [ ] Phone QR
* [ ] SMS QR
* [ ] vCard
* [ ] Logo 삽입
* [ ] Redis 캐싱
* [ ] Rate limiting

---

# 🧾 License

MIT
