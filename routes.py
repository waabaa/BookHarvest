from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Book, ScrapingJob
from scraper import start_scraping_job
from lecture_generator import LectureGenerator
from ppt_generator import PPTGenerator
import logging
import os
import json
from datetime import datetime
from flask import send_file

logger = logging.getLogger(__name__)

@app.route('/')
def dashboard():
    """Main dashboard showing scraping status and results"""
    # Get latest scraping job
    latest_job = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).first()
    
    # Get book statistics
    total_books = Book.query.count()
    recent_books = Book.query.order_by(Book.scraped_at.desc()).limit(10).all()
    
    # Get job statistics
    total_jobs = ScrapingJob.query.count()
    completed_jobs = ScrapingJob.query.filter_by(status='completed').count()
    running_jobs = ScrapingJob.query.filter_by(status='running').count()
    failed_jobs = ScrapingJob.query.filter_by(status='failed').count()
    
    return render_template('dashboard.html',
                         latest_job=latest_job,
                         total_books=total_books,
                         recent_books=recent_books,
                         total_jobs=total_jobs,
                         completed_jobs=completed_jobs,
                         running_jobs=running_jobs,
                         failed_jobs=failed_jobs)

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    """Start a new scraping job"""
    try:
        start_page = int(request.form.get('start_page', 1))
        end_page = int(request.form.get('end_page', 26))
        clear_existing = request.form.get('clear_existing') == 'on'
        
        if start_page < 1 or end_page < start_page or end_page > 100:
            flash('페이지 범위가 올바르지 않습니다. 1-100 범위로 입력해주세요.', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if there's already a running job
        running_job = ScrapingJob.query.filter_by(status='running').first()
        if running_job:
            flash('이미 실행 중인 스크래핑 작업이 있습니다. 완료될 때까지 기다려주세요.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Clear existing data if requested
        if clear_existing:
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
                return redirect(url_for('dashboard'))
        
        # Start new job
        job = start_scraping_job(start_page, end_page)
        flash(f'{start_page}-{end_page}페이지 스크래핑 작업이 시작되었습니다!', 'success')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error starting scraping job: {str(e)}")
        flash(f'스크래핑 작업 시작 중 오류 발생: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/clear_all_data', methods=['POST'])
def clear_all_data():
    """Clear all scraped data and jobs"""
    try:
        # Check if there's a running job
        running_job = ScrapingJob.query.filter_by(status='running').first()
        if running_job:
            flash('실행 중인 스크래핑 작업이 있어 데이터를 삭제할 수 없습니다.', 'error')
            return redirect(url_for('dashboard'))
        
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
        flash(f'모든 데이터가 삭제되었습니다. ({deleted_count}권의 책과 모든 작업 기록)', 'success')
        logger.info(f"Cleared all data: {deleted_count} books and all jobs")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error clearing all data: {str(e)}")
        flash('데이터 삭제 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/api/job_status/<int:job_id>')
def job_status(job_id):
    """Get status of a specific scraping job"""
    job = ScrapingJob.query.get_or_404(job_id)
    
    return jsonify({
        'id': job.id,
        'status': job.status,
        'start_page': job.start_page,
        'end_page': job.end_page,
        'current_page': job.current_page,
        'total_books_found': job.total_books_found,
        'books_scraped': job.books_scraped,
        'books_failed': job.books_failed,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'error_message': job.error_message
    })

@app.route('/api/latest_job_status')
def latest_job_status():
    """Get status of the latest scraping job"""
    job = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).first()
    
    if not job:
        return jsonify({'status': 'no_jobs'})
    
    return jsonify({
        'id': job.id,
        'status': job.status,
        'start_page': job.start_page,
        'end_page': job.end_page,
        'current_page': job.current_page,
        'total_books_found': job.total_books_found,
        'books_scraped': job.books_scraped,
        'books_failed': job.books_failed,
        'started_at': job.started_at.isoformat() if job.started_at else None,
        'completed_at': job.completed_at.isoformat() if job.completed_at else None,
        'error_message': job.error_message
    })

@app.route('/books')
def books_list():
    """Display list of all scraped books"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    books = Book.query.order_by(Book.scraped_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('books_list.html', books=books)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """Display detailed information about a specific book"""
    book = Book.query.get_or_404(book_id)
    
    # Parse lecture plan if it exists
    lecture_plan_data = None
    if book.lecture_plan:
        try:
            lecture_plan_data = json.loads(book.lecture_plan)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in lecture_plan for book {book_id}")
    
    return render_template('book_detail.html', book=book, lecture_plan=lecture_plan_data)

@app.route('/generate_lecture/<int:book_id>', methods=['POST'])
def generate_lecture(book_id):
    """Generate AI lecture plan for a specific book"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Prepare book data for lecture generation
        book_data = {
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'contents': book.contents,
            'book_preview': book.book_preview,
            'review_200': book.review_200
        }
        
        # Get user preferences from form
        lecture_preferences = {
            'lecture_style': request.form.get('lecture_style'),
            'target_level': request.form.get('target_level'),
            'session_count': request.form.get('session_count'),
            'session_duration': request.form.get('session_duration'),
            'special_focus': request.form.get('special_focus', '').strip()
        }
        
        # Remove empty values
        lecture_preferences = {k: v for k, v in lecture_preferences.items() if v}
        
        # Generate lecture plan using AI with multiple fallback options
        session_count = int(lecture_preferences.get('session_count', 3))
        
        lecture_plan = None
        error_messages = []
        
        # 1차 시도: 개선된 기본 생성기 (빠른 GPT-3.5)
        try:
            from lecture_generator import LectureGenerator
            lecture_generator = LectureGenerator()
            lecture_plan = lecture_generator.generate_lecture_plan(book_data, lecture_preferences)
            
            if lecture_plan and not lecture_plan.get('error'):
                print("✅ 기본 생성기 성공")
            else:
                error_messages.append("기본 생성기 실패")
                lecture_plan = None
                
        except Exception as api_error:
            error_messages.append(f"기본 생성기 오류: {str(api_error)}")
            lecture_plan = None
        
        # 2차 시도: 대안 생성기들
        if not lecture_plan:
            try:
                from alternative_generators import AlternativeLectureGenerator
                alt_gen = AlternativeLectureGenerator()
                
                # OpenAI 간단 모드 시도
                print("🔄 대안 생성기 시도 중...")
                lecture_plan = alt_gen.generate_with_openai_simple(book_data, lecture_preferences)
                
                if lecture_plan:
                    print("✅ 대안 생성기 성공")
                    flash('빠른 모드로 강의안을 생성했습니다!', 'success')
                else:
                    error_messages.append("대안 생성기도 실패")
                    
            except Exception as alt_error:
                error_messages.append(f"대안 생성기 오류: {str(alt_error)}")
        
        # 모든 시도 실패시 에러 처리
        if not lecture_plan:
            logger.error(f"All lecture generators failed: {'; '.join(error_messages)}")
            flash('현재 AI 서비스가 불안정합니다. 잠시 후 다시 시도해주세요.', 'warning')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Check if lecture plan generation was successful
        if not lecture_plan or lecture_plan.get('error'):
            # Show specific error message based on the error type
            error_type = lecture_plan.get('error_type', 'unknown')
            
            if error_type == 'timeout':
                flash('강의안 생성 시간이 초과되었습니다. 강의 세션 수를 줄이거나 잠시 후 다시 시도해주세요.', 'warning')
            elif error_type == 'api_key':
                flash('AI 서비스 인증에 문제가 있습니다. 관리자에게 문의해주세요.', 'warning')
            elif error_type == 'rate_limit':
                flash('현재 많은 사용자가 동시에 이용 중입니다. 잠시 후 다시 시도해주세요.', 'warning')
            elif error_type == 'connection' or error_type == 'ssl':
                flash('네트워크 연결에 일시적인 문제가 있습니다. 잠시 후 다시 시도해주세요.', 'warning')
            else:
                flash('AI 서비스에 일시적인 문제가 발생했습니다. 잠시 후 다시 시도해주세요.', 'warning')
            
            # 대체 강의안이 있으면 그것을 사용
            if lecture_plan and lecture_plan.get('fallback_plan'):
                fallback_plan = lecture_plan['fallback_plan']
                fallback_plan['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                fallback_plan['is_fallback'] = True
                
                book.lecture_plan = json.dumps(fallback_plan, ensure_ascii=False, indent=2)
                db.session.commit()
                
                flash('기본 강의안을 제공합니다. AI 서비스 복구 후 다시 생성해보세요.', 'info')
            
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Save the lecture plan to database (keep history by timestamping)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # If there's already a lecture plan, archive it
        if book.lecture_plan:
            try:
                existing_plan = json.loads(book.lecture_plan)
                if not existing_plan.get('history'):
                    existing_plan['history'] = []
                
                # Add current plan to history
                existing_plan['history'].append({
                    'generated_at': existing_plan.get('generated_at', 'Unknown'),
                    'plan': existing_plan.copy()
                })
                
                # Remove history from the copy we're archiving
                if 'history' in existing_plan['history'][-1]['plan']:
                    del existing_plan['history'][-1]['plan']['history']
                
                lecture_plan['history'] = existing_plan['history']
            except:
                logger.warning("Could not parse existing lecture plan for history")
        
        # Add generation timestamp
        lecture_plan['generated_at'] = current_time
        
        book.lecture_plan = json.dumps(lecture_plan, ensure_ascii=False, indent=2)
        db.session.commit()
        
        flash('AI 강의안이 성공적으로 생성되었습니다! 아래에서 확인해보세요.', 'success')
        logger.info(f"Generated lecture plan for book: {book.title}")
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error generating lecture plan for book {book_id}: {error_msg}")
        
        # Provide user-friendly error messages
        if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
            flash('네트워크 연결 시간이 초과되었습니다. 잠시 후 다시 시도해주세요.', 'warning')
        elif 'api_key' in error_msg.lower() or 'unauthorized' in error_msg.lower():
            flash('AI 서비스 인증에 문제가 있습니다. 관리자에게 문의해주세요.', 'warning')
        elif 'connection' in error_msg.lower():
            flash('인터넷 연결에 문제가 있습니다. 연결 상태를 확인 후 다시 시도해주세요.', 'warning')
        else:
            flash('강의안 생성 중 예상치 못한 오류가 발생했습니다. 잠시 후 다시 시도해주세요.', 'error')
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/download_lecture_ppt/<int:book_id>')
def download_lecture_ppt(book_id):
    """강의안을 PPT 형태로 다운로드"""
    try:
        book = Book.query.get_or_404(book_id)
        
        if not book.lecture_plan:
            flash('강의안이 아직 생성되지 않았습니다. 먼저 강의안을 생성해주세요.', 'warning')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Prepare book data
        book_data = {
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'contents': book.contents,
            'book_preview': book.book_preview,
            'review_200': book.review_200
        }
        
        # Generate PPT
        ppt_generator = PPTGenerator()
        success = ppt_generator.generate_lecture_ppt(book_data, book.lecture_plan)
        
        if not success:
            flash('PPT 생성 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # Save PPT file
        filename = f"{book.title.replace(' ', '_')}_강의안.pptx"
        file_path = os.path.join('static', 'downloads', filename)
        
        # Ensure downloads directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not ppt_generator.save_ppt(file_path):
            flash('PPT 저장 중 오류가 발생했습니다.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        
        logger.info(f"Generated PPT for book: {book.title}")
        
        # Send file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        logger.error(f"Error generating PPT for book {book_id}: {str(e)}")
        flash('PPT 다운로드 중 오류가 발생했습니다.', 'error')
        return redirect(url_for('book_detail', book_id=book_id))

@app.route('/jobs')
def jobs_list():
    """Display list of all scraping jobs"""
    jobs = ScrapingJob.query.order_by(ScrapingJob.started_at.desc()).all()
    return render_template('jobs_list.html', jobs=jobs)

@app.route('/api/stats')
def api_stats():
    """Get overall statistics"""
    total_books = Book.query.count()
    total_jobs = ScrapingJob.query.count()
    completed_jobs = ScrapingJob.query.filter_by(status='completed').count()
    running_jobs = ScrapingJob.query.filter_by(status='running').count()
    failed_jobs = ScrapingJob.query.filter_by(status='failed').count()
    
    return jsonify({
        'total_books': total_books,
        'total_jobs': total_jobs,
        'completed_jobs': completed_jobs,
        'running_jobs': running_jobs,
        'failed_jobs': failed_jobs
    })
