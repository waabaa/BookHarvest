# Korean Language Tutor 프로젝트 통합 패키지

## 이전할 핵심 구성 요소

### 1. 데이터베이스 모델 (models.py)
```python
# Book 모델 - 스크래핑된 책 정보
# ScrapingJob 모델 - 스크래핑 작업 기록
# 추가 필드: author_photo_path, author_photo_rounded_path, lecture_plan
```

### 2. 스크래핑 시스템
- `scraper.py` - CommBooks 웹 스크래핑 엔진
- `image_processor.py` - 저자 사진 자동 추출
- `pdf_processor.py` - PDF 텍스트 추출

### 3. AI 강의안 생성
- `lecture_generator.py` - OpenAI GPT-4 기반
- `perplexity_generator.py` - Perplexity AI 기반 (PPT 최적화)
- `alternative_generators.py` - 다양한 AI 모델 지원

### 4. 웹 인터페이스
- 스크래핑 대시보드 (`templates/dashboard.html`)
- 책 상세 보기 (`templates/book_detail.html`)
- 강의안 생성 및 표시 기능
- AJAX 기반 실시간 진행률 표시

### 5. 유틸리티
- `export_manager.py` - 데이터 일괄 내보내기
- `ppt_generator.py` - PowerPoint 파일 생성
- `extract_authors.py` - 저자 정보 추출

### 6. 정적 파일
- `static/covers/` - 책 표지 이미지
- `static/authors/` - 저자 사진 (원본 + 원형)
- `static/pdfs/` - 업로드된 PDF 파일

## 데이터 마이그레이션 계획

### 1. 데이터베이스 백업
```bash
# 현재 데이터베이스 내용을 SQL 파일로 백업
pg_dump $DATABASE_URL > commbooks_backup.sql
```

### 2. 이미지 파일 압축
```bash
# 모든 이미지 파일을 압축하여 이전 준비
tar -czf images_backup.tar.gz static/covers/ static/authors/
```

### 3. 설정 파일
- `pyproject.toml` - 필요한 패키지 목록
- 환경 변수 설정 (API 키, 데이터베이스 URL)

## Korean Language Tutor 통합 가이드

### 1. 필요한 패키지 추가
```toml
[tool.poetry.dependencies]
beautifulsoup4 = "^4.12.2"
requests = "^2.31.0"
pillow = "^10.0.0"
openai = "^1.0.0"
anthropic = "^0.5.0"
google-genai = "^0.5.0"
trafilatura = "^1.6.0"
pypdf2 = "^3.0.0"
python-pptx = "^0.6.21"
```

### 2. 라우트 통합
```python
# 기존 Korean Language Tutor 라우트에 추가
@app.route('/commbooks')
def commbooks_dashboard():
    # 스크래핑 대시보드

@app.route('/commbooks/books')
def commbooks_books():
    # 책 목록

@app.route('/commbooks/generate-lecture/<int:book_id>')
def generate_lecture_plan(book_id):
    # 강의안 생성
```

### 3. 데이터베이스 모델 추가
```python
# Korean Language Tutor의 models.py에 추가
class Book(db.Model):
    # 스크래핑된 책 정보
    
class ScrapingJob(db.Model):
    # 스크래핑 작업 관리
```

### 4. 템플릿 통합
- 기존 템플릿 구조에 CommBooks 관련 페이지 추가
- 네비게이션 메뉴에 "도서 관리" 섹션 추가

## 통합 후 기능

### Korean Language Tutor + CommBooks 통합 시스템
1. **기존 한국어 교육 기능** (유지)
2. **AI 도서 스크래핑** (추가)
   - CommBooks.com에서 책 정보 자동 수집
   - 저자 사진 자동 추출 및 처리
3. **AI 강의안 생성** (통합)
   - 기존 한국어 교육 콘텐츠 + 스크래핑된 도서 기반
   - OpenAI, Perplexity AI 활용
4. **통합 대시보드**
   - 한국어 학습 진도 + 도서 관리 + 강의안 생성

## 이전 작업 순서

1. **Korean Language Tutor 프로젝트 접근 권한 확인**
2. **현재 데이터 백업 및 압축**
3. **의존성 패키지 설치**
4. **모델 및 라우트 추가**
5. **데이터 마이그레이션**
6. **템플릿 통합**
7. **테스트 및 최적화**

Korean Language Tutor 프로젝트에 접근할 수 있는 방법을 알려주시면 즉시 통합 작업을 시작하겠습니다.