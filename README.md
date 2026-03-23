# QR Server (qr.example.kr)

FastAPI 기반의 **QR 코드 생성 API 서버**입니다.
URL, 텍스트, Wi-Fi QR을 지원하며 SVG / PNG / JPG로 반환합니다.

---

## 🚀 Features

* ✅ URL QR
* ✅ Text QR (임의 문자열)
* ✅ Wi-Fi QR (SSID / Password / Encryption)
* ✅ SVG / PNG / JPG 출력
* ✅ PNG 투명 배경 지원
* ✅ JPG 배경색 적용
* ✅ RGB 색상 커스터마이징
* ✅ 다운로드 (`Content-Disposition`)
* ✅ dot / square 스타일
* ✅ 특수문자 안전 처리 (`data_b64`, POST 지원)
* ✅ QR version / optimize 파라미터 지원
* ✅ 확장 가능한 구조 (encoder / renderer 분리)

---

## 📌 What is this?

이 프로젝트는 **웹 UI 서비스가 아니라 API 서버**입니다.

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

👉 요청하면 **HTML이 아니라 QR 이미지 자체를 반환합니다**

### 사용 용도

* 백엔드에서 QR 이미지 생성
* 자동화 / 봇 / 내부 서비스
* self-hosted QR API

### 포함되지 않는 기능

* 웹 입력 폼 UI
* QR 관리 페이지
* 사용자 인터페이스

---

## 📦 Project Structure

```
qr-server/
├── app
│   ├── __init__.py
│   ├── encoders.py        # QR payload 생성
│   ├── renderers.py       # SVG / PNG / JPG 렌더링
│   └── main.py            # FastAPI API
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

## 🌐 API Endpoint

```
https://qr.example.kr/
```

---

# 🧪 Basic Usage

## Text QR

```text
https://qr.example.kr/?type=text&data=안녕하세요
```

---

## URL QR

```text
https://qr.example.kr/?type=url&url=www.naver.com
```

👉 자동으로 `https://` 보정됨

---

## Wi-Fi QR

```text
https://qr.example.kr/?type=wifi&ssid=MyWifi&password=12345678&encryption=WPA
```

---

# 🖼️ Format

| format | 설명     |
| ------ | ------ |
| svg    | 기본     |
| png    | 배경 투명  |
| jpg    | 배경색 적용 |

---

## PNG (투명 배경)

```text
https://qr.example.kr/?type=text&data=hello&format=png
```

---

## JPG (배경 포함)

```text
https://qr.example.kr/?type=text&data=hello&format=jpg
```

---

# 🎨 색상 설정 (RGB)

## 전경색 (QR 색)

```text
fg_r=255&fg_g=0&fg_b=0
```

## 배경색

```text
bg_r=255&bg_g=255&bg_b=0
```

---

## 예시

### 빨간 QR (PNG)

```text
https://qr.example.kr/?type=text&data=hello&format=png&fg_r=255&fg_g=0&fg_b=0
```

---

### 검정 배경 + 흰 QR (JPG)

```text
https://qr.example.kr/?type=text&data=hello&format=jpg&fg_r=255&fg_g=255&fg_b=255&bg_r=0&bg_g=0&bg_b=0
```

---

# 📥 다운로드

```text
?download=true
```

---

# 🔥 특수문자 데이터 처리 (중요)

다음 문자가 포함된 경우:

```
&, ?, #
```

👉 일반 `data=`는 깨질 수 있음

---

## 방법 1: data_b64 (추천)

```text
https://qr.example.kr/?type=text&data_b64=BASE64URL
```

### Python

```python
import base64

raw = "vless://example?x=1&y=2#tag"
encoded = base64.urlsafe_b64encode(raw.encode()).decode().rstrip("=")
```

---

## 방법 2: POST /render (가장 안전)

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

# ⚙️ Advanced Parameters

| 파라미터             | 설명                      |
| ---------------- | ----------------------- |
| type             | raw / text / url / wifi |
| style            | dot / square            |
| format           | svg / png / jpg         |
| scale            | QR 크기                   |
| border           | 여백                      |
| error_correction | L / M / Q / H           |
| version          | QR version (1~40)       |
| optimize         | 데이터 최적화                 |
| download         | 파일 다운로드                 |
| fg_r,g,b         | 전경 RGB                  |
| bg_r,g,b         | 배경 RGB                  |
| data_b64         | base64url 데이터           |

---

# 🧠 Architecture

```
[Request]
   ↓
[encoders.py] → QR payload 생성
   ↓
[renderers.py] → SVG 생성 → PNG/JPG 변환
   ↓
[Response]
```

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

# ⚠️ Notes

* PNG는 배경 투명
* JPG는 배경색 필요
* 긴 데이터 → QR 복잡도 증가
* 스타일 과도 변경 시 인식률 저하 가능
* 특수문자 포함 데이터는 `data_b64` 또는 POST 사용

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
