# AI전문 교육 플랫폼

## Overview

한국어 전문 교육 플랫폼이 메인 사이트로 전환된 통합 교육 시스템입니다. Korean Language Tutor의 교육 구조와 내용을 메인 사이트로 구축하고, 기존 CommBooks 스크래핑 및 AI 강의안 생성 기능은 서브 메뉴(/commbooks)로 제공하는 종합 교육 플랫폼입니다. AI 전문가 과정, 창의적 사고 개발, 리더십 과정 등 다양한 교육 프로그램과 함께 AI 기반 자동 교안 생성 시스템을 통합 제공합니다.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (2025-07-31)

✓ 프로젝트 구조 완전 변경 - Korean Language Tutor 통합 (2025-07-31):
- Korean Language Tutor 교육 구조를 메인 사이트로 전환 완료
- CommBooks 기능을 /commbooks 서브메뉴로 이동
- 통합된 네비게이션 구조로 교육 과정과 AI 시스템 연결
- 새로운 홈페이지: AI전문 교육 플랫폼 컨셉으로 변경
- 강사진, 교육과정, AI 교안 시스템의 유기적 통합

✓ 새로운 메인 사이트 구조 구축:
- 홈페이지: AI 시대 교육 플랫폼 소개
- 강사진: AI, 데이터사이언스, 비즈니스, UX 전문가
- 교육과정: AI 전문가/창의적 사고/리더십 개발 과정
- AI 교안 시스템: CommBooks 스크래핑 및 강의안 생성

✓ URL 구조 재편성:
- / : 메인 홈페이지 (Korean Language Tutor 기반)
- /authors : 강사진 소개
- /curriculums : 교육 과정 소개
- /commbooks : CommBooks 스크래핑 대시보드
- /commbooks/books : 수집된 책 목록
- /commbooks/book/<id> : 책 상세 정보

✓ 기존 CommBooks 기능 유지:
- 모든 스크래핑 기능 그대로 유지
- AI 강의안 생성 기능 그대로 유지
- 경로만 /commbooks/* 로 변경

## Previous Changes (2025-07-30)

✓ Perplexity AI 혁신적 개선 - PPT 준비 강의안 (2025-07-30):
- PPT 슬라이드별 구성: 제목, 핵심 포인트, 상세 내용, 발표자 노트 포함
- 실제 기업 사례 요구: 회사명, 캠페인명, 구체적 성과 수치 필수 포함
- 최신 데이터 인용: 2023-2024년 통계, 연구 결과, 출처 명시
- 시각적 자료 제안: 차트, 그래프, 이미지 활용 가이드
- PPT 제작 최적화: 발표에 바로 사용할 수 있는 실무적 구성
- 검색 기반 콘텐츠: 온라인 검색을 통한 최신 정보 수집 강화

✓ 강의안 표시 시스템 완전 수정:
- format_lecture_plan 함수 전면 개선으로 빈 콘텐츠 문제 해결
- Perplexity AI 데이터 구조에 최적화된 HTML 렌더링
- 강의 세션별 상세 내용, 학습목표, 실무 적용방안 표시
- 참고자료 및 생성일시 정보 포함

✓ 책 이미지 표시 개선 (2025-07-31):
- object-fit: cover → contain으로 변경하여 책 전체가 보이도록 수정
- 첫 페이지와 상세 페이지 모두 세로폭에 맞춰 전체 표시
- 배경색 추가로 빈 공간 자연스럽게 처리

✓ 저자 사진 자동 추출 기능 구현 (2025-07-31):
- ImageProcessor 클래스로 책 표지에서 저자 사진 영역 자동 감지 및 추출
- 원형 저자 사진 생성 기능 (프로필용)
- 데이터베이스에 저자 사진 경로 저장 (author_photo_path, author_photo_rounded_path)
- 책 상세 페이지에서 자동 추출 및 표시
- 저자명 옆에 작은 원형 프로필 사진, 책 표지 아래에 큰 저자 사진 카드 표시

✓ Korean Language Tutor 통합 패키지 준비 완료 (2025-07-31):
- 모든 스크래핑 데이터 및 이미지 백업 완료
- 통합용 Python 모듈, 템플릿, 라우트 코드 패키징
- 상세한 통합 가이드 및 단계별 매뉴얼 작성
- korean_tutor_integration_package.tar.gz 통합 패키지 생성
- 데이터베이스 백업 및 이미지 파일 압축 완료

✓ 전체 시스템 기능 완성 (2025-07-31):
- 스크래핑 데이터 처리 옵션: skip/update 선택 기능 구현
- AI 정보 숨김 처리: 강의안에서 AI 관련 정보 자동 필터링
- 강의안 생성 UI 개선: "Perplexity AI 활용" 마케팅 텍스트 제거
- 저자 사진 개선: 원본 비율 유지하며 얼굴 중심 원형 크롭 처리
- 강의안 히스토리 관리: 이전 버전 자동 보관 및 표시 시스템
- 전체 데이터 내보내기: ZIP 형태로 책 정보, 이미지, PDF, 강의안 통합 다운로드
- 강의안 개별 다운로드: 텍스트(.txt), PPT(.pptx) 형태로 개별 다운로드
- 웹사이트 이전 가이드: 상세한 시스템 이전 매뉴얼 작성
- 다운로드 버튼 UI 개선: 대시보드와 책 상세 페이지에 직관적인 다운로드 메뉴 추가

✓ UI/UX 전면 개편:
- 첨부된 디자인 파일 기반 밝은 배경 테마로 완전 변경
- 핑크/자홍색 계열 primary 컬러 적용 (#e91e63)
- 책 표지 표시 크기 확대 및 중앙 정렬로 개선
- 카드 기반 깔끔한 레이아웃 적용
- 현대적이고 깔끔한 디자인 시스템 구축

✓ 브랜딩 및 UI 완전 적용:
- 헤더: "AI오투오" → "컴북스-AI오투오"로 변경
- 메인 타이틀: "AI 교제/교안 작성"으로 정리
- 푸터: "AI오투오 | AI 강의 파트너와 더 효과적인 수업 준비"로 변경

✓ 보안 강화:
- 스크래핑 시작 시 비밀번호(0438) 인증 기능 추가
- 기존 데이터 삭제 시에도 동일한 비밀번호 보호

✓ 시리즈별 스크래핑 기능 구현:
- URL 입력을 통한 새로운 시리즈 스크래핑 지원
- URL 패턴: /도서-태그/[시리즈명]/page/[페이지번호]/
- 시리즈명 자동 추출 및 데이터베이스 저장
- 기존 AI총서 외에 커뮤니케이션이해총서 등 다양한 시리즈 지원

✓ 데이터베이스 스키마 확장:
- Book 모델에 series_name 컬럼 추가
- ScrapingJob 모델에 series_name, series_url 컬럼 추가
- 시리즈별 책 분류 및 관리 기능

✓ PDF 첨부 및 강의안 연동:
- 책별 PDF 파일 업로드 및 텍스트 추출
- 강의안 생성 시 PDF 내용 자동 포함
- PDF 관리 (업로드, 삭제) 기능
- 사용자 안내 메시지 개선

## System Architecture

### Backend Architecture
- **Framework**: Flask web framework with SQLAlchemy ORM
- **Database**: PostgreSQL with SQLAlchemy models
- **Web Scraping**: BeautifulSoup4 and requests for HTML parsing and HTTP requests
- **Image Processing**: PIL (Pillow) for cover image handling
- **Threading**: Background job processing for scraping tasks
- **Session Management**: Flask sessions with configurable secret keys

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **Main Site Design**: 밝은 테마의 현대적 교육 플랫폼 디자인
- **UI Framework**: Bootstrap 5 with 핑크/자홍색 primary 컬러 (#e91e63)
- **Navigation**: 통합 네비게이션 (교육과정, 강사진, AI 교안 시스템)
- **Icons**: Font Awesome for UI icons
- **Charts**: Chart.js for CommBooks 진행률 시각화
- **Responsive**: 모바일 최적화된 반응형 디자인

### Database Schema
The application uses two main database models:

1. **Book Model**: Stores scraped book information
   - Basic info: title, author, description
   - Extended content: 200-character reviews, table of contents, book previews
   - Metadata: publish date, cover image path, source URL, scraping timestamp
   - AI features: lecture_plan field (JSON format) for AI-generated course content

2. **ScrapingJob Model**: Tracks scraping job progress
   - Job parameters: start/end page ranges
   - Progress tracking: current page, books found/scraped/failed
   - Status management: pending, running, completed, failed states
   - Timing: start/completion timestamps, error messages

## Key Components

### Web Scraper (scraper.py)
- **CommBooksScraper Class**: Main scraping engine with improved text formatting
- **Session Management**: Persistent HTTP sessions with proper headers
- **Rate Limiting**: Built-in delays to respect server resources
- **Image Handling**: Enhanced book cover image detection and downloads
- **Error Handling**: Robust error handling with logging and retry mechanisms
- **Threading Support**: Background job execution to prevent UI blocking
- **Data Validation**: Automatic text cleanup and length constraints
- **Footer Filtering**: Removes website footer content from scraped data

### AI Lecture Generator (lecture_generator.py)
- **LectureGenerator Class**: OpenAI GPT-4 powered lecture plan creation
- **Content Analysis**: Analyzes book content to determine appropriate difficulty level
- **Structured Output**: Generates 3-4 session course outlines in JSON format
- **Fallback System**: Provides basic structure when AI generation fails
- **Customization**: Adapts lecture content based on book topic and complexity

### Web Interface (routes.py)
- **Main Site Routes**: Korean Language Tutor 기반 교육 플랫폼 홈페이지
  - / : 메인 홈페이지 (교육 과정, 강사진, AI 시스템 소개)
  - /authors : 전문 강사진 소개 페이지
  - /curriculums : 교육 과정 상세 안내
- **CommBooks Routes**: AI 교안 생성 시스템 (/commbooks/* 경로)
  - /commbooks : 스크래핑 대시보드 및 통계
  - /commbooks/books : 수집된 책 목록 및 검색
  - /commbooks/book/<id> : 책 상세 정보 및 강의안 생성
  - /commbooks/start_scraping : 새 스크래핑 작업 시작
- **API Endpoints**: CommBooks 관련 RESTful API (/api/commbooks/*)
- **Progress Monitoring**: 실시간 스크래핑 진행률 추적

### Models (models.py)
- **Database Models**: SQLAlchemy models with proper relationships
- **Data Validation**: Built-in constraints and validation
- **Timestamps**: Automatic timestamp management for tracking
- **AI Integration**: Lecture plan storage in JSON format

## Data Flow

1. **Job Initiation**: User submits scraping parameters through web interface
2. **Validation**: System validates page ranges and checks for existing running jobs
3. **Job Creation**: New ScrapingJob record created in database
4. **Background Processing**: Scraper runs in separate thread to avoid blocking
5. **Page Processing**: Each page is scraped for book links
6. **Book Extraction**: Individual book details are extracted and saved
7. **Image Processing**: Cover images are downloaded and stored locally
8. **Progress Updates**: Job status and progress updated in real-time
9. **Completion**: Final statistics and status recorded

## External Dependencies

### Core Dependencies
- **Flask**: Web framework and routing
- **SQLAlchemy**: Database ORM and migrations
- **PostgreSQL**: Primary data storage
- **BeautifulSoup4**: HTML parsing for web scraping
- **Requests**: HTTP client for web requests
- **Pillow**: Image processing for cover images
- **OpenAI**: GPT-4 API for AI lecture plan generation

### Frontend Dependencies
- **Bootstrap 5**: UI framework with dark theme
- **Font Awesome**: Icon library
- **Chart.js**: Progress visualization charts

### Target Website
- **CommBooks.com**: Source website for book data
- **AI Book Collection**: Specific category being scraped (/도서-태그/인공지능총서/)

## Deployment Strategy

### Environment Configuration
- **Database URL**: Configurable via DATABASE_URL environment variable
- **Session Secret**: Configurable via SESSION_SECRET environment variable
- **Default Values**: Fallback to development defaults for local testing

### Database Management
- **Auto-creation**: Tables automatically created on startup
- **Connection Pooling**: Configured with pool recycling and pre-ping
- **Migration Support**: SQLAlchemy-based schema management

### Static Files
- **Image Storage**: Local file system storage for book covers
- **CSS/JS**: Static assets served directly by Flask
- **CDN Resources**: External CDN for Bootstrap and other libraries

### Production Considerations
- **Proxy Support**: ProxyFix middleware for reverse proxy deployments
- **Logging**: Comprehensive logging throughout the application
- **Error Handling**: Graceful error handling with user feedback
- **Rate Limiting**: Built-in delays to prevent overwhelming target website

통합 교육 플랫폼은 Korean Language Tutor의 교육 구조와 CommBooks의 AI 기술을 결합하여, 포괄적인 AI 시대 교육 솔루션을 제공합니다. Replit, Heroku 등의 PaaS 플랫폼에 최소 설정으로 배포 가능하도록 설계되었습니다.