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
* ✅ 확장 가능한 구조 (encoder / renderer 분리)

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

## 🎨 Style 옵션

| 값      | 설명         |
| ------ | ---------- |
| dot    | 점 스타일 (기본) |
| square | 정사각형       |

```text
?style=dot
```

---

## 🖼️ Format 옵션

| 값   | 설명      |
| --- | ------- |
| svg | 기본      |
| png | PNG 이미지 |

```text
?format=png
```

---

## 📥 다운로드

```text
?download=true
```

→ 브라우저에서 파일 다운로드됨

---

## 🎯 전체 파라미터

| 파라미터             | 설명                      |
| ---------------- | ----------------------- |
| type             | raw / text / url / wifi |
| data             | 문자열                     |
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

새로운 QR 타입 추가:

```python
class EmailEncoder:
    def encode(self, req):
        return f"mailto:{req.email}"
```

그리고 registry에 등록:

```python
ENCODER_REGISTRY["email"] = EmailEncoder()
```

---

## ⚠️ Notes

* PNG 변환은 `cairosvg` 사용
* Wi-Fi QR은 표준 형식 사용
* 스타일 과도 변경 시 인식률 저하 가능
* 긴 문자열은 QR 크기 증가

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
