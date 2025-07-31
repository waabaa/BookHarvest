# Replit 프로젝트 통합 가이드

## 통합 방법들

### 1. 코드 복사 및 병합 (가장 간단)
```bash
# 다른 프로젝트의 파일들을 현재 프로젝트로 복사
# 파일 탐색기에서 드래그&드롭 또는 복사/붙여넣기
```

### 2. Git을 통한 통합
```bash
# 현재 프로젝트를 Git 리포지토리로 초기화
git init
git add .
git commit -m "Initial commit"

# 다른 프로젝트를 서브모듈로 추가
git submodule add <다른-replit-git-url> external_project

# 또는 다른 프로젝트의 특정 폴더만 가져오기
git remote add other-project <다른-replit-git-url>
git fetch other-project
git checkout other-project/main -- specific_folder/
```

### 3. API 기반 통합
```python
# 다른 Replit 프로젝트를 API 서버로 활용
import requests

def call_other_project_api(data):
    response = requests.post('https://other-project.username.repl.co/api/endpoint', json=data)
    return response.json()
```

### 4. 공유 데이터베이스 통합
```python
# 동일한 PostgreSQL 데이터베이스를 공유
# DATABASE_URL을 동일하게 설정하여 데이터 공유
```

## 현재 프로젝트 통합 가능한 요소들

### 스크래핑 시스템
- `scraper.py` - 웹 스크래핑 엔진
- `models.py` - 데이터베이스 모델
- `image_processor.py` - 이미지 처리

### AI 강의안 생성
- `lecture_generator.py` - OpenAI 기반 강의안 생성
- `perplexity_generator.py` - Perplexity AI 강의안 생성
- `alternative_generators.py` - 다양한 AI 모델 지원

### 웹 인터페이스
- `routes.py` - Flask 라우트
- `templates/` - HTML 템플릿
- `static/` - CSS, JS, 이미지

### 유틸리티
- `pdf_processor.py` - PDF 텍스트 추출
- `ppt_generator.py` - PowerPoint 생성
- `export_manager.py` - 데이터 내보내기

## 통합 시 고려사항

### 1. 의존성 충돌 해결
```bash
# pyproject.toml 병합 시 버전 충돌 확인
# 공통 라이브러리는 최신 버전으로 통일
```

### 2. 환경 변수 통합
```bash
# .env 파일이나 Replit Secrets 통합
DATABASE_URL=<통합된-데이터베이스-URL>
OPENAI_API_KEY=<공유-API-키>
```

### 3. 포트 및 라우팅
```python
# Flask 앱 병합 시 라우트 충돌 방지
from flask import Blueprint

# 다른 프로젝트 기능을 Blueprint로 분리
other_bp = Blueprint('other', __name__, url_prefix='/other')
app.register_blueprint(other_bp)
```

## 통합 단계별 진행

### 1단계: 프로젝트 분석
- 통합하려는 프로젝트의 구조 파악
- 공통 기능과 고유 기능 식별
- 데이터 모델 호환성 확인

### 2단계: 아키텍처 설계
- 통합된 시스템 구조 설계
- 모듈 간 인터페이스 정의
- 데이터 흐름 계획

### 3단계: 점진적 통합
- 핵심 기능부터 단계적 통합
- 각 단계별 테스트
- 충돌 해결 및 최적화

### 4단계: 테스트 및 최적화
- 통합 테스트 수행
- 성능 최적화
- 문서 업데이트

## 구체적인 통합 요청

어떤 프로젝트와 통합하시겠습니까?
1. 프로젝트 URL 또는 리포지토리 링크
2. 통합하려는 기능 설명
3. 원하는 통합 방식

이 정보를 제공해주시면 구체적인 통합 계획을 세워드리겠습니다.