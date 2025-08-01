# BookHarvest - AI 교재/강의안 자동 생성 시스템

BookHarvest는 CommBooks.com의 책 데이터를 자동으로 수집하고, OpenAI API를 통해 사용자 맞춤형 강의안을 생성하는 AI 기반 웹 플랫폼입니다.

## 🚀 주요 기능

### 📚 스크래핑 시스템
- **시리즈별 수집**: URL 패턴으로 다양한 도서 시리즈 자동 수집
- **진행 상태 시각화**: 스크래핑 실시간 모니터링
- **비밀번호 보호**: 인증 코드(0438)로 작업 보호

### 🤖 AI 강의안 생성
- **GPT-4 기반 생성**: 책 기반 맞춤형 강의안 자동 생성
- **PDF 연동**: 정확도 향상을 위한 도서 PDF 연동
- **PPT 출력**: 전문적인 프레젠테이션 다운로드 제공

### 🌐 REST API
- **외부 시스템 연동 가능**
- **CORS 지원**
- **책/강의안/PPT에 대한 전체 API 제공**

## 📋 API 엔드포인트

### 도서 관련
- `GET /api/books` – 도서 목록 조회
- `GET /api/books/{id}` – 도서 상세
- `GET /api/search?q=검색어` – 검색
- `GET /api/series` – 시리즈 목록

### 강의안 관련
- `GET /api/lecture_plans`
- `GET /api/lecture_plan/{id}`
- `POST /api/generate_lecture_plan/{id}`
- `GET /api/download_ppt/{id}`

## 🛠 기술 스택

### Backend
- Flask + SQLAlchemy + PostgreSQL
- Gunicorn for production WSGI

### AI & 스크래핑
- OpenAI GPT-4
- BeautifulSoup4
- python-pptx
- Pillow

### Frontend & API
- Bootstrap 5 (Dark Theme)
- Chart.js
- Flask-CORS

## 🚀 서버 배포 절차

### 1. 저장소 클론
```bash
git clone https://github.com/waabaa/BookHarvest.git /var/www/bookharvest
cd /var/www/bookharvest
```

### 2. 자동 배포 스크립트 실행
```bash
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

### 3. API 키 설정
```bash
nano /var/www/bookharvest/.env
# OPENAI_API_KEY, ANTHROPIC_API_KEY, GEMINI_API_KEY 등 입력
systemctl restart bookharvest
```

## 📊 시스템 관리 명령어

```bash
# 상태 확인
bookharvest-manage status

# 로그 확인
bookharvest-manage logs

# 재시작
bookharvest-manage restart

# 백업
bookharvest-manage backup
```

### 서비스 주소

- **웹사이트**: https://aio2o.ktenterprise.net
- **API**: https://aio2o.ktenterprise.net/api/
- **API 문서**: https://aio2o.ktenterprise.net/api_docs

## 🔧 로컬 개발 환경

```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -e .

# 환경 변수 설정
cp .env.example .env
nano .env

# 개발 서버 실행
python main.py
```

## 📝 사용 방법

### 1. 스크래핑 시작
- 메인 대시보드에서 페이지 범위 입력
- 시리즈 URL 입력 (선택)
- 인증 코드 0438 입력
- "스크래핑 시작" 클릭

### 2. 강의안 생성
- 도서 선택
- PDF 업로드 (선택)
- "AI 강의안 생성" 클릭
- PPT 다운로드 가능

### 3. API 사용 예시
```javascript
// 도서 목록 가져오기
fetch('https://aio2o.ktenterprise.net/api/books')
  .then(res => res.json())
  .then(data => console.log(data));

// 강의안 생성
fetch('https://aio2o.ktenterprise.net/api/generate_lecture_plan/1', {
  method: 'POST'
})
.then(res => res.json())
.then(data => console.log(data));
```

## 🖥 시스템 요구사항

- Ubuntu 20.04+ (권장: 24.04 LTS)
- Python 3.8+
- PostgreSQL 12+
- Nginx 1.18+
- RAM 2GB 이상
- 여유 디스크 공간 10GB 이상

## 🔐 보안 기능

- 비밀번호 기반 보호
- Let's Encrypt SSL 인증서
- UFW 방화벽 적용
- 환경변수(.env) 기반 민감정보 관리

## 📈 모니터링 기능

- 실시간 대시보드
- 작업 로그 수집
- 상태 점검 및 리소스 감시

## 🤝 기여 가이드

1. Fork 하기
2. 새 브랜치 생성 (`feature/새기능`)
3. 커밋 (`git commit -am '기능 추가'`)
4. Push 및 Pull Request 제출

## 📄 라이선스

MIT License

## 📞 문의

- 도메인: [aio2o.ktenterprise.net](https://aio2o.ktenterprise.net)
- GitHub: [waabaa](https://github.com/waabaa)
- 개발자: leejungchul@gmail.com

---

**BookHarvest | AI 강의 파트너와 함께 더 스마트한 수업 준비**
