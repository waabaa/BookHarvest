
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
    """CommBooks 스크래핑 대시보드"""
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
    """책 목록 페이지"""
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
    """책 상세 페이지"""
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
    """강의안 생성"""
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
    """스크래핑 작업 상태 API"""
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
