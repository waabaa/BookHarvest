#!/usr/bin/env python3
"""
CommBooks -> Korean Language Tutor 마이그레이션 스크립트
이 스크립트는 현재 프로젝트의 모든 구성 요소를 Korean Language Tutor에 통합하기 위한 파일들을 생성합니다.
"""

import os
import shutil
import json
from datetime import datetime

def create_migration_package():
    """마이그레이션에 필요한 모든 파일을 준비합니다."""
    
    # 마이그레이션 폴더 생성
    migration_dir = "migration_to_korean_tutor"
    if os.path.exists(migration_dir):
        shutil.rmtree(migration_dir)
    os.makedirs(migration_dir)
    
    # 1. 핵심 Python 파일들 복사
    core_files = [
        'models.py',
        'scraper.py', 
        'image_processor.py',
        'lecture_generator.py',
        'perplexity_generator.py',
        'alternative_generators.py',
        'pdf_processor.py',
        'ppt_generator.py',
        'export_manager.py',
        'extract_authors.py'
    ]
    
    python_dir = os.path.join(migration_dir, "python_modules")
    os.makedirs(python_dir)
    
    for file in core_files:
        if os.path.exists(file):
            shutil.copy2(file, python_dir)
            print(f"복사됨: {file}")
    
    # 2. 라우트 파일에서 CommBooks 관련 라우트만 추출
    routes_content = """
# CommBooks 통합을 위한 라우트들
# Korean Language Tutor의 routes.py에 추가할 코드

from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from models import Book, ScrapingJob  # CommBooks 모델들 import 추가
from scraper import CommBooksScraper
from lecture_generator import LectureGenerator
from perplexity_generator import PerplexityLectureGenerator
from image_processor import ImageProcessor
import threading

# CommBooks 대시보드
@app.route('/commbooks')
def commbooks_dashboard():
    \"\"\"CommBooks 스크래핑 대시보드\"\"\"
    latest_job = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).first()
    current_job = ScrapingJob.query.filter_by(status='running').first()
    
    total_books = Book.query.count()
    recent_books = Book.query.order_by(Book.scraped_at.desc()).limit(10).all()
    lecture_plans_count = Book.query.filter(Book.lecture_plan.isnot(None)).count()
    
    total_jobs = ScrapingJob.query.count()
    completed_jobs = ScrapingJob.query.filter_by(status='completed').count()
    running_jobs = ScrapingJob.query.filter_by(status='running').count()
    recent_jobs = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).limit(5).all()
    
    return render_template('commbooks/dashboard.html',
                         latest_job=latest_job,
                         current_job=current_job,
                         total_books=total_books,
                         recent_books=recent_books,
                         lecture_plans_count=lecture_plans_count,
                         total_jobs=total_jobs,
                         completed_jobs=completed_jobs,
                         running_jobs=running_jobs,
                         recent_jobs=recent_jobs)

@app.route('/commbooks/books')
def commbooks_books():
    \"\"\"책 목록 페이지\"\"\"
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    series = request.args.get('series', '')
    
    query = Book.query
    
    if search:
        query = query.filter(
            db.or_(
                Book.title.contains(search),
                Book.author.contains(search),
                Book.description.contains(search)
            )
        )
    
    if series:
        query = query.filter(Book.series_name == series)
    
    books = query.order_by(Book.scraped_at.desc()).paginate(
        page=page, per_page=12, error_out=False
    )
    
    series_list = db.session.query(Book.series_name).distinct().filter(
        Book.series_name.isnot(None)
    ).all()
    series_list = [s[0] for s in series_list]
    
    return render_template('commbooks/books_list.html', 
                         books=books, 
                         search=search, 
                         series=series,
                         series_list=series_list)

@app.route('/commbooks/book/<int:book_id>')
def commbooks_book_detail(book_id):
    \"\"\"책 상세 페이지\"\"\"
    book = Book.query.get_or_404(book_id)
    
    # 강의안 히스토리 조회
    lecture_history = []
    if book.lecture_plan:
        try:
            if isinstance(book.lecture_plan, str):
                lecture_data = json.loads(book.lecture_plan)
            else:
                lecture_data = book.lecture_plan
                
            if isinstance(lecture_data, list):
                lecture_history = lecture_data
            else:
                lecture_history = [lecture_data]
        except:
            lecture_history = []
    
    return render_template('commbooks/book_detail.html', 
                         book=book, 
                         lecture_history=lecture_history)

@app.route('/commbooks/generate-lecture/<int:book_id>', methods=['POST'])
def generate_commbooks_lecture(book_id):
    \"\"\"강의안 생성\"\"\"
    book = Book.query.get_or_404(book_id)
    generator_type = request.form.get('generator_type', 'perplexity')
    
    try:
        if generator_type == 'perplexity':
            generator = PerplexityLectureGenerator()
        else:
            generator = LectureGenerator()
            
        lecture_plan = generator.generate_lecture_plan(
            title=book.title,
            author=book.author,
            description=book.description,
            table_of_contents=book.table_of_contents,
            book_preview=book.book_preview,
            pdf_content=book.pdf_content
        )
        
        # 강의안 히스토리 관리
        existing_plans = []
        if book.lecture_plan:
            try:
                if isinstance(book.lecture_plan, str):
                    existing_data = json.loads(book.lecture_plan)
                else:
                    existing_data = book.lecture_plan
                    
                if isinstance(existing_data, list):
                    existing_plans = existing_data
                else:
                    existing_plans = [existing_data]
            except:
                existing_plans = []
        
        # 새 강의안 추가
        new_plan = {
            'content': lecture_plan,
            'generated_at': datetime.now().isoformat(),
            'generator': generator_type
        }
        existing_plans.insert(0, new_plan)
        
        # 최대 5개까지만 유지
        if len(existing_plans) > 5:
            existing_plans = existing_plans[:5]
        
        book.lecture_plan = json.dumps(existing_plans, ensure_ascii=False)
        db.session.commit()
        
        flash('강의안이 성공적으로 생성되었습니다!', 'success')
        
    except Exception as e:
        flash(f'강의안 생성 중 오류가 발생했습니다: {str(e)}', 'error')
    
    return redirect(url_for('commbooks_book_detail', book_id=book_id))

@app.route('/api/commbooks/job_status')
def api_commbooks_job_status():
    \"\"\"스크래핑 작업 상태 API\"\"\"
    current_job = ScrapingJob.query.filter_by(status='running').first()
    
    if current_job:
        return jsonify({
            'current_job': {
                'id': current_job.id,
                'status': current_job.status,
                'current_page': current_job.current_page,
                'start_page': current_job.start_page,
                'end_page': current_job.end_page,
                'total_books_found': current_job.total_books_found,
                'books_scraped': current_job.books_scraped,
                'books_failed': current_job.books_failed,
                'series_name': current_job.series_name
            }
        })
    else:
        return jsonify({'current_job': None})
"""
    
    with open(os.path.join(migration_dir, "routes_to_add.py"), 'w', encoding='utf-8') as f:
        f.write(routes_content)
    
    # 3. 템플릿 파일들 복사
    templates_dir = os.path.join(migration_dir, "templates")
    if os.path.exists("templates"):
        shutil.copytree("templates", templates_dir)
        print("템플릿 파일들이 복사되었습니다.")
    
    # 4. 설정 파일들 생성
    config_content = """
# Korean Language Tutor에 추가할 패키지들
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
psycopg2-binary = "^2.9.0"

# 환경 변수에 추가할 항목들
OPENAI_API_KEY=your_openai_api_key
PERPLEXITY_API_KEY=your_perplexity_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  # 선택사항
GEMINI_API_KEY=your_gemini_api_key  # 선택사항
"""
    
    with open(os.path.join(migration_dir, "config_additions.txt"), 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    # 5. 마이그레이션 가이드 생성
    guide_content = """
# Korean Language Tutor 통합 가이드

## 1. 파일 배치
1. `python_modules/` 폴더의 모든 파일을 Korean Language Tutor 프로젝트 루트에 복사
2. `templates/` 폴더를 Korean Language Tutor의 templates 폴더에 병합
3. `routes_to_add.py`의 내용을 Korean Language Tutor의 routes.py에 추가

## 2. 패키지 설치
`config_additions.txt`에 있는 패키지들을 pyproject.toml에 추가하고 설치

## 3. 환경 변수 설정
Replit Secrets에 API 키들 추가

## 4. 데이터베이스 마이그레이션
1. `commbooks_data_backup.sql` 파일을 Korean Language Tutor 프로젝트에 업로드
2. PostgreSQL에 데이터 복원:
   ```bash
   psql $DATABASE_URL < commbooks_data_backup.sql
   ```

## 5. 이미지 파일 복원
1. `commbooks_images.tar.gz` 파일을 Korean Language Tutor 프로젝트에 업로드
2. 압축 해제:
   ```bash
   tar -xzf commbooks_images.tar.gz
   ```

## 6. 네비게이션 메뉴 추가
base.html 또는 main layout에 CommBooks 메뉴 추가:
```html
<li><a href="/commbooks">도서 관리</a></li>
<li><a href="/commbooks/books">책 목록</a></li>
```

## 7. 테스트
- /commbooks 경로로 접속하여 대시보드 확인
- 스크래핑 기능 테스트
- 강의안 생성 기능 테스트
"""
    
    with open(os.path.join(migration_dir, "INTEGRATION_GUIDE.md"), 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print(f"\\n마이그레이션 패키지가 '{migration_dir}' 폴더에 생성되었습니다!")
    print("\\n포함된 항목:")
    print("- python_modules/ : 핵심 Python 파일들")
    print("- templates/ : HTML 템플릿들")
    print("- routes_to_add.py : 추가할 라우트 코드")
    print("- config_additions.txt : 패키지 및 환경 변수 설정")
    print("- INTEGRATION_GUIDE.md : 상세한 통합 가이드")
    print("\\n추가로 필요한 파일:")
    print("- commbooks_data_backup.sql : 데이터베이스 백업")
    print("- commbooks_images.tar.gz : 이미지 파일들")

if __name__ == "__main__":
    create_migration_package()