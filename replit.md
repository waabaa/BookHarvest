# CommBooks Scraper

## Overview

This is a Flask-based web scraper application designed to extract book information from the CommBooks website (commbooks.com). The application provides a dashboard interface for managing scraping jobs, viewing scraped books, and monitoring job progress. It scrapes book details including titles, authors, descriptions, reviews, and cover images from the AI book collection pages. The system now includes AI-powered lecture plan generation using OpenAI's GPT-4 to create 3-4 session course outlines based on book content.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (2025-07-29)

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
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome for UI icons
- **Charts**: Chart.js for progress visualization
- **Styling**: Custom CSS with responsive design

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
- **Dashboard Route**: Main interface showing statistics and recent activity
- **Job Management**: Start new scraping jobs with validation
- **Book Details**: Enhanced book view with AI lecture plan integration
- **Lecture Generation**: On-demand AI course creation from book content
- **API Endpoints**: RESTful endpoints for status updates and data retrieval
- **Progress Monitoring**: Real-time job progress tracking

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

The application is designed to be easily deployable to platforms like Replit, Heroku, or similar PaaS providers with minimal configuration changes.