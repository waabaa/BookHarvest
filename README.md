# CommBooks-AI오투오 - AI 교제/교안 작성 시스템

CommBooks.com에서 책 정보를 자동 수집하여 PostgreSQL에 저장하고, OpenAI API로 사용자 맞춤형 강의안을 생성하는 웹 시스템입니다.

## 🚀 주요 기능

### 📚 스크래핑 시스템
- **시리즈별 스크래핑**: URL 패턴 기반으로 다양한 도서 시리즈 자동 수집
- **실시간 진행 상황**: 스크래핑 작업의 실시간 모니터링
- **보안 인증**: 비밀번호(0438) 보호로 안전한 데이터 관리

### 🤖 AI 강의안 생성
- **OpenAI GPT-4 기반**: 고품질 강의안 자동 생성
- **PDF 연동**: 책별 PDF 첨부로 더 정확한 강의안 생성
- **PPT 다운로드**: 생성된 강의안을 전문적인 PPT 형태로 제공

### 🌐 REST API
- **외부 연동**: 다른 웹사이트에서 책 데이터 활용 가능
- **CORS 지원**: 브라우저에서 직접 API 호출 가능
- **완전한 API**: 책 목록, 상세정보, 검색, 강의안, PPT 다운로드

## 📋 API 엔드포인트

### 도서 관련
- `GET /api/books` - 전체 도서 목록 (페이지네이션)
- `GET /api/books/{id}` - 특정 도서 상세 정보
- `GET /api/search?q={keyword}` - 도서 검색
- `GET /api/series` - 시리즈 목록

### 강의안 관련
- `GET /api/lecture_plans` - 강의안이 있는 도서 목록
- `GET /api/lecture_plan/{id}` - 특정 강의안 상세 정보
- `POST /api/generate_lecture_plan/{id}` - AI 강의안 생성
- `GET /api/download_ppt/{id}` - PPT 파일 다운로드

## 🛠 기술 스택

### Backend
- **Flask** - 웹 프레임워크
- **SQLAlchemy** - ORM 및 데이터베이스 관리
- **PostgreSQL** - 데이터베이스
- **Gunicorn** - WSGI 서버

### AI & 데이터 처리
- **OpenAI GPT-4** - 강의안 생성
- **BeautifulSoup4** - 웹 스크래핑
- **Pillow** - 이미지 처리
- **python-pptx** - PPT 생성

### Frontend & API
- **Bootstrap 5** - UI 프레임워크 (다크 테마)
- **Chart.js** - 진행 상황 시각화
- **Flask-CORS** - API 외부 접근 지원

## 🚀 서버 배포

### 1. 저장소 클론
```bash
git clone https://github.com/JungChulLee1/commbooks-ai.git
cd commbooks-ai
```

### 2. 자동 배포 스크립트 실행
```bash
chmod +x deploy_to_server.sh
./deploy_to_server.sh
```

### 3. API 키 설정
```bash
nano /var/www/commbooks-ai/.env
# OPENAI_API_KEY를 실제 키로 변경
systemctl restart commbooks-ai
```

## 📊 시스템 관리

### 관리 명령어
```bash
# 서비스 상태 확인
commbooks-manage status

# 실시간 로그 확인
commbooks-manage logs

# 서비스 재시작
commbooks-manage restart

# 데이터베이스 백업
commbooks-manage backup
```

### 서비스 URL
- **메인 웹사이트**: https://aio2o.ktenterprise.net
- **API 엔드포인트**: https://aio2o.ktenterprise.net/api/
- **API 문서**: https://aio2o.ktenterprise.net/api_docs

## 🔧 개발 환경 설정

### 로컬 개발
```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 패키지 설치
pip install -e .

# 환경 변수 설정
cp .env.example .env
nano .env

# 개발 서버 실행
python main.py
```

## 📝 사용법

### 1. 스크래핑 시작
1. 메인 대시보드에서 시작/종료 페이지 입력
2. 시리즈 URL 입력 (선택사항)
3. 비밀번호(0438) 입력
4. 스크래핑 시작 버튼 클릭

### 2. 강의안 생성
1. Books 메뉴에서 원하는 책 선택
2. PDF 첨부 (선택사항)
3. "AI 강의안 생성" 버튼 클릭
4. 생성된 강의안 확인 및 PPT 다운로드

### 3. API 사용
```javascript
// 책 목록 가져오기
fetch('https://aio2o.ktenterprise.net/api/books')
  .then(response => response.json())
  .then(data => console.log(data));

// 강의안 생성
fetch('https://aio2o.ktenterprise.net/api/generate_lecture_plan/1', {
  method: 'POST'
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📋 시스템 요구사항

- **OS**: Ubuntu 20.04+ (권장: 24.04 LTS)
- **Python**: 3.8+
- **PostgreSQL**: 12+
- **Nginx**: 1.18+
- **메모리**: 2GB+ 권장
- **디스크**: 10GB+ 여유 공간

## 🔒 보안 기능

- **비밀번호 보호**: 모든 스크래핑 작업에 인증 필요
- **SSL 인증서**: Let's Encrypt 자동 설치
- **방화벽 설정**: UFW로 포트 관리
- **환경 변수**: 민감한 정보 .env 파일 관리

## 📈 모니터링

- **실시간 대시보드**: 스크래핑 진행 상황 추적
- **로그 시스템**: 상세한 작업 로그 기록
- **시스템 상태**: 서비스 상태 및 리소스 모니터링

## 🤝 기여하기

1. 이 저장소를 Fork
2. 새 브랜치 생성 (`git checkout -b feature/새기능`)
3. 변경사항 커밋 (`git commit -am '새 기능 추가'`)
4. 브랜치에 Push (`git push origin feature/새기능`)
5. Pull Request 생성

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 📞 문의

- **도메인**: aio2o.ktenterprise.net
- **개발자**: JungChulLee1
- **목적**: AI 교제/교안 작성 시스템

---

**AI오투오 | AI 강의 파트너와 더 효과적인 수업 준비**