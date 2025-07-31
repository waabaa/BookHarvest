from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Book, ScrapingJob, PDFAttachment
from scraper import start_scraping_job
from lecture_generator import LectureGenerator
from ppt_generator import PPTGenerator
from pdf_processor import PDFProcessor

# PDF 프로세서 인스턴스 생성
pdf_processor = PDFProcessor()
import logging
import os
import json
from datetime import datetime
from flask import send_file

logger = logging.getLogger(__name__)

def format_lecture_plan(lecture_plan_data):
    """강의안 데이터를 HTML로 포맷팅"""
    if not lecture_plan_data:
        return "<p>강의안 데이터가 없습니다.</p>"
    
    try:
        html_content = []
        
        # Perplexity AI 형식 처리
        if 'lecture_overview' in lecture_plan_data:
            overview = lecture_plan_data['lecture_overview']
            if 'title' in overview:
                html_content.append(f"<h2 class='mb-3'>{overview['title']}</h2>")
            if 'description' in overview:
                html_content.append(f"<p class='lead'>{overview['description']}</p>")
            if 'target_audience' in overview:
                html_content.append(f"<p><strong>대상:</strong> {overview['target_audience']}</p>")
            if 'duration' in overview:
                html_content.append(f"<p><strong>시간:</strong> {overview['duration']}</p>")
        
        # 강의 세션 내용
        if 'lectures' in lecture_plan_data:
            lectures = lecture_plan_data['lectures']
            if isinstance(lectures, list):
                html_content.append("<h3 class='mt-4 mb-3'>강의 세션</h3>")
                for i, lecture in enumerate(lectures, 1):
                    if isinstance(lecture, dict):
                        html_content.append(f"<div class='mb-4 p-3 bg-light rounded'>")
                        
                        # 제목 처리 (여러 형식 지원)
                        title = lecture.get('session_title') or lecture.get('title', f"{i}강")
                        html_content.append(f"<h4>{i}강: {title}</h4>")
                        
                        # 시간 처리
                        if 'duration' in lecture:
                            html_content.append(f"<p><small class='text-muted'>시간: {lecture['duration']}</small></p>")
                        
                        # 학습목표 처리 (여러 형식 지원)
                        objectives = lecture.get('learning_objectives') or lecture.get('objectives', [])
                        if objectives:
                            html_content.append("<strong>학습목표:</strong>")
                            html_content.append("<ul>")
                            for obj in objectives:
                                html_content.append(f"<li>{obj}</li>")
                            html_content.append("</ul>")
                        
                        # PPT 슬라이드 구성 처리
                        detailed_outline = lecture.get('detailed_outline', [])
                        
                        # 내용 처리 (여러 형식 지원)
                        content = lecture.get('content')
                        outline = lecture.get('outline')
                        
                        if content:
                            if isinstance(content, list):
                                html_content.append("<div class='mt-3'><strong>강의 내용:</strong></div>")
                                html_content.append("<ul>")
                                for item in content:
                                    html_content.append(f"<li>{item}</li>")
                                html_content.append("</ul>")
                            else:
                                html_content.append(f"<div class='mt-3'><strong>강의 내용:</strong></div>")
                                html_content.append(f"<p>{content}</p>")
                        
                        if outline:
                            if isinstance(outline, list):
                                html_content.append("<div class='mt-3'><strong>강의 개요:</strong></div>")
                                html_content.append("<ul>")
                                for item in outline:
                                    html_content.append(f"<li>{item}</li>")
                                html_content.append("</ul>")
                            else:
                                html_content.append(f"<div class='mt-3'><strong>강의 개요:</strong></div>")
                                html_content.append(f"<p>{outline}</p>")
                        
                        html_content.append("</div>")
        
        # 참고자료 처리
        if 'references' in lecture_plan_data:
            references = lecture_plan_data['references']
            if references:
                html_content.append("<h3 class='mt-4 mb-3'>참고자료</h3>")
                html_content.append("<ul>")
                for ref in references:
                    html_content.append(f"<li>{ref}</li>")
                html_content.append("</ul>")
        
        return ''.join(html_content) if html_content else "<p>강의안 내용을 표시할 수 없습니다.</p>"
        
    except Exception as e:
        logger.error(f"Error formatting lecture plan: {str(e)}")
        return f"<p class='text-danger'>강의안 포맷팅 중 오류가 발생했습니다: {str(e)}</p>"

# =================================
# 메인 Korean Language Tutor 라우트
# =================================

@app.route('/')
def home():
    """Korean Language Tutor 메인 홈페이지"""
    return render_template('index.html')

@app.route('/authors')
def authors():
    """강사진 소개 페이지"""
    # 실제 강사진 데이터는 추후 데이터베이스에서 가져올 수 있습니다
    return render_template('authors.html')

@app.route('/curriculums')
def curriculums():
    """교육 과정 소개 페이지"""
    return render_template('curriculums.html')

# =================================
# CommBooks 서브 메뉴 라우트
# =================================

@app.route('/commbooks')
def commbooks_dashboard():
    """CommBooks 스크래핑 대시보드"""
    # Get latest scraping job
    latest_job = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).first()
    
    # Get currently running job
    current_job = ScrapingJob.query.filter_by(status='running').first()
    
    # Get book statistics
    total_books = Book.query.count()
    recent_books = Book.query.order_by(Book.scraped_at.desc()).limit(10).all()
    lecture_plans_count = Book.query.filter(Book.lecture_plan.isnot(None)).count()
    
    # Get job statistics
    total_jobs = ScrapingJob.query.count()
    completed_jobs = ScrapingJob.query.filter_by(status='completed').count()
    running_jobs = ScrapingJob.query.filter_by(status='running').count()
    failed_jobs = ScrapingJob.query.filter_by(status='failed').count()
    
    # Get recent jobs for display
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
                         failed_jobs=failed_jobs,
                         recent_jobs=recent_jobs)

@app.route('/commbooks/start_scraping', methods=['POST'])
def commbooks_start_scraping():
    """Start a new scraping job"""
    try:
        start_page = int(request.form.get('start_page', 1))
        end_page = int(request.form.get('end_page', 26))
        data_handling = request.form.get('data_handling', 'skip')
        password = request.form.get('password', '')
        series_url = request.form.get('series_url', '').strip()
        
        # 스크래핑 비밀번호 확인
        if password != '0438':
            flash('스크래핑 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('commbooks_dashboard'))
        
        if start_page < 1 or end_page < start_page or end_page > 100:
            flash('페이지 범위가 올바르지 않습니다. 1-100 범위로 입력해주세요.', 'error')
            return redirect(url_for('commbooks_dashboard'))
        
        # Check if there's already a running job
        running_job = ScrapingJob.query.filter_by(status='running').first()
        if running_job:
            flash('이미 실행 중인 스크래핑 작업이 있습니다. 완료될 때까지 기다려주세요.', 'warning')
            return redirect(url_for('commbooks_dashboard'))
        
        # Handle existing data based on user choice
        if data_handling == 'clear':
            # 비밀번호 확인
            clear_password = request.form.get('clear_password', '')
            if clear_password != '0438':
                flash('기존 데이터 삭제 비밀번호가 올바르지 않습니다. 스크래핑을 계속 진행합니다.', 'warning')
            else:
                try:
                    # Delete all books and their images
                    books = Book.query.all()
                    deleted_count = 0
                    for book in books:
                        if book.cover_image_path:
                            # Remove image file
                            image_path = os.path.join('static', book.cover_image_path)
                            if os.path.exists(image_path):
                                os.remove(image_path)
                        db.session.delete(book)
                        deleted_count += 1
                    
                    # Delete all scraping jobs
                    ScrapingJob.query.delete()
                
                    db.session.commit()
                    flash(f'기존 데이터 {deleted_count}권의 책과 모든 작업 기록이 삭제되었습니다.', 'info')
                    logger.info(f"Cleared {deleted_count} books and all jobs")
                    
                except Exception as e:
                    db.session.rollback()
                    logger.error(f"Error clearing existing data: {str(e)}")
                    flash('기존 데이터 삭제 중 오류가 발생했습니다.', 'error')
                    return redirect(url_for('commbooks_dashboard'))
        
        # 시리즈명 추출
        series_name = "인공지능총서"  # 기본값
        if series_url:
            try:
                import urllib.parse
                parsed_url = urllib.parse.unquote(series_url)
                if '/도서-태그/' in parsed_url:
                    series_part = parsed_url.split('/도서-태그/')[1]
                    series_name = series_part.split('/')[0]
            except Exception:
                series_name = "인공지능총서"
        
        # Start new job with data handling option
        job = start_scraping_job(start_page, end_page, series_url, series_name, data_handling)
        if series_url:
            flash(f'{series_name} 시리즈 {start_page}-{end_page}페이지 스크래핑 작업이 시작되었습니다!', 'success')
        else:
            flash(f'{start_page}-{end_page}페이지 스크래핑 작업이 시작되었습니다!', 'success')
        
        return redirect(url_for('commbooks_dashboard'))
        
    except Exception as e:
        logger.error(f"Error starting scraping job: {str(e)}")
        flash(f'스크래핑 작업 시작 중 오류 발생: {str(e)}', 'error')
        return redirect(url_for('commbooks_dashboard'))

@app.route('/commbooks/books')
def commbooks_books_list():
    """Display list of all books"""
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
    
    # Get list of all series for filter
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
    """Display detailed information about a specific book"""
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
def commbooks_generate_lecture(book_id):
    """Generate lecture plan for a book"""
    book = Book.query.get_or_404(book_id)
    generator_type = request.form.get('generator_type', 'perplexity')
    
    try:
        if generator_type == 'perplexity':
            from perplexity_generator import PerplexityLectureGenerator
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

# API 엔드포인트들
@app.route('/api/commbooks/job_status')
def api_commbooks_job_status():
    """Get current scraping job status"""
    current_job = ScrapingJob.query.filter_by(status='running').first()
    
    if current_job:
        progress = 0
        if current_job.end_page > current_job.start_page:
            progress = ((current_job.current_page - current_job.start_page) / 
                       (current_job.end_page - current_job.start_page)) * 100
        
        return jsonify({
            'current_job': {
                'id': current_job.id,
                'status': current_job.status,
                'current_page': current_job.current_page,
                'start_page': current_job.start_page,
                'end_page': current_job.end_page,
                'progress': round(progress, 1),
                'total_books_found': current_job.total_books_found,
                'books_scraped': current_job.books_scraped,
                'books_failed': current_job.books_failed,
                'series_name': current_job.series_name
            }
        })
    else:
        return jsonify({'current_job': None})

# 기타 필요한 라우트들을 계속 추가...