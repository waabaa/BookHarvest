from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_cors import CORS
from app import app, db
from models import Book, ScrapingJob, PDFAttachment
from scraper import start_scraping_job
from lecture_generator import LectureGenerator
from ppt_generator import PPTGenerator
from pdf_processor import PDFProcessor

# Enable CORS for all API routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# PDF 프로세서 인스턴스 생성
pdf_processor = PDFProcessor()
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
        scraping_password = request.form.get('scraping_password', '')
        series_url = request.form.get('series_url', '').strip()
        
        # 스크래핑 비밀번호 확인
        if scraping_password != '0438':
            flash('스크래핑 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('dashboard'))
        
        if start_page < 1 or end_page < start_page or end_page > 100:
            flash('페이지 범위가 올바르지 않습니다. 1-100 범위로 입력해주세요.', 'error')
            return redirect(url_for('dashboard'))
        
        # Check if there's already a running job
        running_job = ScrapingJob.query.filter_by(status='running').first()
        if running_job:
            flash('이미 실행 중인 스크래핑 작업이 있습니다. 완료될 때까지 기다려주세요.', 'warning')
            return redirect(url_for('dashboard'))
        
        # Clear existing data if requested (with password check)
        if clear_existing:
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
                    return redirect(url_for('dashboard'))
        
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
        
        # Start new job
        job = start_scraping_job(start_page, end_page, series_url, series_name)
        if series_url:
            flash(f'{series_name} 시리즈 {start_page}-{end_page}페이지 스크래핑 작업이 시작되었습니다!', 'success')
        else:
            flash(f'{start_page}-{end_page}페이지 스크래핑 작업이 시작되었습니다!', 'success')
        
        return redirect(url_for('dashboard'))
        
    except Exception as e:
        logger.error(f"Error starting scraping job: {str(e)}")
        flash(f'스크래핑 작업 시작 중 오류 발생: {str(e)}', 'error')
        return redirect(url_for('dashboard'))

@app.route('/clear_all_data', methods=['POST'])
def clear_all_data():
    """Clear all scraped data and jobs with password protection"""
    try:
        # 비밀번호 확인
        password = request.form.get('password', '')
        if password != '0438':
            flash('비밀번호가 올바르지 않습니다. 데이터 삭제가 취소되었습니다.', 'error')
            return redirect(url_for('dashboard'))
        
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
        
        # Get PDF attachments for this book
        pdf_attachments = PDFAttachment.query.filter_by(book_id=book_id).all()
        pdf_content = ""
        if pdf_attachments:
            for pdf in pdf_attachments:
                if pdf.content_text:
                    pdf_content += f"\n\n[첨부 PDF: {pdf.filename}]\n{pdf.content_text[:2000]}..."  # 처음 2000자만
        
        # Prepare book data for lecture generation with PDF content
        book_data = {
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'contents': book.contents,
            'book_preview': book.book_preview,
            'review_200': book.review_200,
            'pdf_content': pdf_content
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

@app.route('/upload_pdf/<int:book_id>', methods=['POST'])
def upload_pdf(book_id):
    """PDF 파일 업로드"""
    try:
        book = Book.query.get_or_404(book_id)
        
        if 'pdf_file' not in request.files:
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        
        file = request.files['pdf_file']
        if file.filename == '':
            flash('파일이 선택되지 않았습니다.', 'error')
            return redirect(url_for('book_detail', book_id=book_id))
        
        # PDF 파일 저장 및 처리
        pdf_attachment, error = pdf_processor.save_pdf_file(file, book_id)
        
        if error:
            flash(error, 'error')
        elif pdf_attachment:
            flash(f'PDF 파일 "{pdf_attachment.filename}"이 성공적으로 업로드되었습니다.', 'success')
        else:
            flash('PDF 파일 업로드에 실패했습니다.', 'error')
        
    except Exception as e:
        logger.error(f"PDF 업로드 실패: {str(e)}")
        flash('PDF 업로드 중 오류가 발생했습니다.', 'error')
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/delete_pdf/<int:pdf_id>', methods=['POST'])
def delete_pdf(pdf_id):
    """PDF 파일 삭제"""
    try:
        pdf_attachment = PDFAttachment.query.get_or_404(pdf_id)
        book_id = pdf_attachment.book_id
        
        success, error = pdf_processor.delete_pdf(pdf_id)
        
        if error:
            flash(error, 'error')
        else:
            flash('PDF 파일이 성공적으로 삭제되었습니다.', 'success')
        
    except Exception as e:
        logger.error(f"PDF 삭제 실패: {str(e)}")
        flash('PDF 삭제 중 오류가 발생했습니다.', 'error')
        book_id = request.form.get('book_id', 1)  # fallback
    
    return redirect(url_for('book_detail', book_id=book_id))

@app.route('/pdfs')
def pdfs_list():
    """모든 PDF 첨부파일 목록"""
    pdfs = pdf_processor.get_all_pdfs()
    return render_template('pdfs_list.html', pdfs=pdfs)

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

@app.route('/api_docs')
def api_docs():
    """API documentation page"""
    return render_template('api_docs.html')

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

@app.route('/api/job_status/<int:job_id>')
def api_job_status(job_id):
    """Get specific job status"""
    job = ScrapingJob.query.get_or_404(job_id)
    
    return jsonify({
        'id': job.id,
        'status': job.status,
        'current_page': job.current_page,
        'total_books_found': job.total_books_found or 0,
        'books_scraped': job.books_scraped,
        'books_failed': job.books_failed,
        'start_page': job.start_page,
        'end_page': job.end_page,
        'series_name': job.series_name,
        'series_url': job.series_url,
        'error_message': job.error_message
    })

@app.route('/api/books')
def api_books():
    """Get all books with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    series = request.args.get('series', None)
    
    # Limit per_page to reasonable values
    per_page = min(per_page, 100)
    
    query = Book.query
    
    # Filter by series if specified
    if series:
        query = query.filter(Book.series_name.ilike(f'%{series}%'))
    
    # Paginate results
    books = query.order_by(Book.scraped_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    books_data = []
    for book in books.items:
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'review_200': book.review_200,
            'contents': book.contents,
            'book_preview': book.book_preview,
            'publish_date': book.publish_date,
            'series_name': book.series_name,
            'book_url': book.book_url,
            'scraped_at': book.scraped_at.isoformat() if book.scraped_at else None,
            'cover_image_url': f"{request.host_url}static/{book.cover_image_path}" if book.cover_image_path else None,
            'has_lecture_plan': bool(book.lecture_plan)
        }
        books_data.append(book_data)
    
    return jsonify({
        'books': books_data,
        'pagination': {
            'page': books.page,
            'pages': books.pages,
            'per_page': books.per_page,
            'total': books.total,
            'has_next': books.has_next,
            'has_prev': books.has_prev
        }
    })

@app.route('/api/books/<int:book_id>')
def api_book_detail(book_id):
    """Get detailed information about a specific book"""
    book = Book.query.get_or_404(book_id)
    
    # Get PDF attachments
    pdf_attachments = PDFAttachment.query.filter_by(book_id=book_id).all()
    pdfs_data = []
    for pdf in pdf_attachments:
        pdfs_data.append({
            'id': pdf.id,
            'filename': pdf.filename,
            'file_size': pdf.file_size,
            'uploaded_at': pdf.uploaded_at.isoformat() if pdf.uploaded_at else None,
            'has_content': bool(pdf.content_text)
        })
    
    book_data = {
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'description': book.description,
        'review_200': book.review_200,
        'contents': book.contents,
        'book_preview': book.book_preview,
        'publish_date': book.publish_date,
        'series_name': book.series_name,
        'book_url': book.book_url,
        'scraped_at': book.scraped_at.isoformat() if book.scraped_at else None,
        'cover_image_url': f"{request.host_url}static/{book.cover_image_path}" if book.cover_image_path else None,
        'lecture_plan': json.loads(book.lecture_plan) if book.lecture_plan else None,
        'pdf_attachments': pdfs_data
    }
    
    return jsonify(book_data)

@app.route('/api/series')
def api_series():
    """Get all available book series"""
    from sqlalchemy import func
    
    series_data = db.session.query(
        Book.series_name,
        func.count(Book.id).label('book_count')
    ).group_by(Book.series_name).all()
    
    series_list = []
    for series_name, book_count in series_data:
        if series_name:  # Skip null series names
            series_list.append({
                'name': series_name,
                'book_count': book_count
            })
    
    return jsonify({
        'series': series_list,
        'total_series': len(series_list)
    })

@app.route('/api/search')
def api_search():
    """Search books by title, author, or content"""
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    if not query:
        return jsonify({'error': 'Search query is required'}), 400
    
    # Limit per_page to reasonable values
    per_page = min(per_page, 100)
    
    # Search in title, author, description, and contents
    search_filter = db.or_(
        Book.title.ilike(f'%{query}%'),
        Book.author.ilike(f'%{query}%'),
        Book.description.ilike(f'%{query}%'),
        Book.contents.ilike(f'%{query}%')
    )
    
    books = Book.query.filter(search_filter).order_by(
        Book.scraped_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    books_data = []
    for book in books.items:
        book_data = {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'series_name': book.series_name,
            'cover_image_url': f"{request.host_url}static/{book.cover_image_path}" if book.cover_image_path else None,
            'scraped_at': book.scraped_at.isoformat() if book.scraped_at else None
        }
        books_data.append(book_data)
    
    return jsonify({
        'query': query,
        'books': books_data,
        'pagination': {
            'page': books.page,
            'pages': books.pages,
            'per_page': books.per_page,
            'total': books.total,
            'has_next': books.has_next,
            'has_prev': books.has_prev
        }
    })

@app.route('/api/lecture_plans')
def api_lecture_plans():
    """Get all books that have lecture plans"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    series = request.args.get('series', None)
    
    # Limit per_page to reasonable values
    per_page = min(per_page, 100)
    
    query = Book.query.filter(Book.lecture_plan.isnot(None))
    
    # Filter by series if specified
    if series:
        query = query.filter(Book.series_name.ilike(f'%{series}%'))
    
    # Paginate results
    books = query.order_by(Book.scraped_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    lecture_plans_data = []
    for book in books.items:
        try:
            lecture_plan = json.loads(book.lecture_plan) if book.lecture_plan else None
        except:
            lecture_plan = None
            
        lecture_data = {
            'book_id': book.id,
            'book_title': book.title,
            'book_author': book.author,
            'series_name': book.series_name,
            'cover_image_url': f"{request.host_url}static/{book.cover_image_path}" if book.cover_image_path else None,
            'lecture_plan': lecture_plan,
            'ppt_download_url': f"{request.host_url}api/download_ppt/{book.id}" if lecture_plan else None,
            'created_at': book.scraped_at.isoformat() if book.scraped_at else None
        }
        lecture_plans_data.append(lecture_data)
    
    return jsonify({
        'lecture_plans': lecture_plans_data,
        'pagination': {
            'page': books.page,
            'pages': books.pages,
            'per_page': books.per_page,
            'total': books.total,
            'has_next': books.has_next,
            'has_prev': books.has_prev
        }
    })

@app.route('/api/lecture_plan/<int:book_id>')
def api_lecture_plan_detail(book_id):
    """Get detailed lecture plan for a specific book"""
    book = Book.query.get_or_404(book_id)
    
    if not book.lecture_plan:
        return jsonify({'error': 'No lecture plan found for this book'}), 404
    
    try:
        lecture_plan = json.loads(book.lecture_plan)
    except:
        return jsonify({'error': 'Invalid lecture plan data'}), 500
    
    # Get PDF attachments
    pdf_attachments = PDFAttachment.query.filter_by(book_id=book_id).all()
    pdfs_data = []
    for pdf in pdf_attachments:
        pdfs_data.append({
            'id': pdf.id,
            'filename': pdf.filename,
            'file_size': pdf.file_size,
            'uploaded_at': pdf.uploaded_at.isoformat() if pdf.uploaded_at else None
        })
    
    response_data = {
        'book_info': {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'description': book.description,
            'series_name': book.series_name,
            'cover_image_url': f"{request.host_url}static/{book.cover_image_path}" if book.cover_image_path else None,
            'pdf_attachments': pdfs_data
        },
        'lecture_plan': lecture_plan,
        'ppt_download_url': f"{request.host_url}api/download_ppt/{book_id}",
        'generated_at': lecture_plan.get('generated_at') if lecture_plan else None
    }
    
    return jsonify(response_data)

@app.route('/api/download_ppt/<int:book_id>')
def api_download_ppt(book_id):
    """Download PPT file for a specific book's lecture plan"""
    try:
        book = Book.query.get_or_404(book_id)
        
        if not book.lecture_plan:
            return jsonify({'error': 'No lecture plan found for this book'}), 404
        
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
            return jsonify({'error': 'Failed to generate PPT'}), 500
        
        # Save PPT file
        filename = f"{book.title.replace(' ', '_')}_강의안.pptx"
        file_path = os.path.join('static', 'downloads', filename)
        
        # Ensure downloads directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if not ppt_generator.save_ppt(file_path):
            return jsonify({'error': 'Failed to save PPT'}), 500
        
        logger.info(f"Generated PPT via API for book: {book.title}")
        
        # Send file for download
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
        )
        
    except Exception as e:
        logger.error(f"Error generating PPT via API for book {book_id}: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/generate_lecture_plan/<int:book_id>', methods=['POST'])
def api_generate_lecture_plan(book_id):
    """Generate lecture plan via API"""
    try:
        book = Book.query.get_or_404(book_id)
        
        # Check if lecture plan already exists
        if book.lecture_plan:
            try:
                existing_plan = json.loads(book.lecture_plan)
                return jsonify({
                    'message': 'Lecture plan already exists',
                    'lecture_plan': existing_plan,
                    'book_info': {
                        'id': book.id,
                        'title': book.title,
                        'author': book.author
                    }
                })
            except:
                pass  # Continue to regenerate if existing plan is invalid
        
        # Get PDF content if available
        pdf_content = ""
        pdf_attachments = PDFAttachment.query.filter_by(book_id=book_id).all()
        for pdf in pdf_attachments:
            if pdf.content_text:
                pdf_content += f"\n\n=== {pdf.filename} ===\n{pdf.content_text}"
        
        # Prepare book content
        book_content = {
            'title': book.title,
            'author': book.author,
            'description': book.description or "",
            'contents': book.contents or "",
            'book_preview': book.book_preview or "",
            'review_200': book.review_200 or "",
            'pdf_content': pdf_content
        }
        
        # Generate lecture plan
        generator = LectureGenerator()
        lecture_plan = generator.generate_lecture_plan(book_content)
        
        if not lecture_plan:
            return jsonify({'error': 'Failed to generate lecture plan'}), 500
        
        # Add generation timestamp
        current_time = datetime.now().isoformat()
        lecture_plan['generated_at'] = current_time
        
        # Save to database
        book.lecture_plan = json.dumps(lecture_plan, ensure_ascii=False, indent=2)
        db.session.commit()
        
        logger.info(f"Generated lecture plan via API for book: {book.title}")
        
        return jsonify({
            'message': 'Lecture plan generated successfully',
            'lecture_plan': lecture_plan,
            'book_info': {
                'id': book.id,
                'title': book.title,
                'author': book.author,
                'series_name': book.series_name
            },
            'ppt_download_url': f"{request.host_url}api/download_ppt/{book_id}"
        })
        
    except Exception as e:
        logger.error(f"Error generating lecture plan via API for book {book_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500
