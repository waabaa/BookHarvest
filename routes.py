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
                                html_content.append(f"<div class='mt-3'><strong>강의 내용:</strong> {content}</div>")
                        elif outline:
                            html_content.append("<div class='mt-3'><strong>강의 구성:</strong></div>")
                            if isinstance(outline, list):
                                for section in outline:
                                    if isinstance(section, dict):
                                        section_title = section.get('section', '섹션')
                                        section_content = section.get('content', '')
                                        section_time = section.get('time', '')
                                        html_content.append(f"<div class='ms-3 mb-2'>")
                                        html_content.append(f"<strong>{section_title}</strong>")
                                        if section_time:
                                            html_content.append(f" <small class='text-muted'>({section_time})</small>")
                                        if section_content:
                                            html_content.append(f"<br>{section_content}")
                                        html_content.append(f"</div>")
                                    else:
                                        html_content.append(f"<div class='ms-3 mb-2'>{section}</div>")
                        
                        # PPT 슬라이드 구성 처리 (새로운 상세 형식)
                        detailed_outline = lecture.get('detailed_outline', [])
                        if detailed_outline:
                            html_content.append("<div class='mt-3'><strong>📊 PPT 슬라이드 구성:</strong></div>")
                            for section in detailed_outline:
                                if isinstance(section, dict):
                                    section_title = section.get('section_title', '섹션')
                                    duration = section.get('duration', '')
                                    html_content.append(f"<div class='card mt-2 mb-3'>")
                                    html_content.append(f"<div class='card-header bg-primary text-white'>")
                                    html_content.append(f"<h6 class='mb-0'>{section_title}")
                                    if duration:
                                        html_content.append(f" <small>({duration})</small>")
                                    html_content.append(f"</h6></div>")
                                    html_content.append(f"<div class='card-body'>")
                                    
                                    # PPT 슬라이드들
                                    ppt_slides = section.get('ppt_slides', [])
                                    if ppt_slides:
                                        for slide in ppt_slides:
                                            slide_title = slide.get('slide_title', '')
                                            key_points = slide.get('key_points', [])
                                            detailed_content = slide.get('detailed_content', '')
                                            speaker_notes = slide.get('speaker_notes', '')
                                            
                                            html_content.append(f"<div class='border-start border-3 border-info ps-3 mb-3'>")
                                            html_content.append(f"<h6 class='text-primary'>🎯 {slide_title}</h6>")
                                            
                                            if key_points:
                                                html_content.append("<strong>핵심 포인트:</strong>")
                                                html_content.append("<ul class='mb-2'>")
                                                for point in key_points:
                                                    html_content.append(f"<li>{point}</li>")
                                                html_content.append("</ul>")
                                            
                                            if detailed_content:
                                                html_content.append(f"<div class='mb-2'><strong>상세 내용:</strong> {detailed_content}</div>")
                                            
                                            if speaker_notes:
                                                html_content.append(f"<div class='text-muted small'><strong>발표자 노트:</strong> {speaker_notes}</div>")
                                            
                                            html_content.append("</div>")
                                    
                                    # 실제 사례와 최신 데이터
                                    real_examples = section.get('real_examples', '')
                                    latest_data = section.get('latest_data', '')
                                    practical_tips = section.get('practical_tips', [])
                                    
                                    if real_examples:
                                        html_content.append(f"<div class='alert alert-success'><strong>🏢 실제 사례:</strong> {real_examples}</div>")
                                    
                                    if latest_data:
                                        html_content.append(f"<div class='alert alert-info'><strong>📈 최신 데이터:</strong> {latest_data}</div>")
                                    
                                    if practical_tips:
                                        html_content.append("<div class='alert alert-warning'><strong>💡 실무 팁:</strong>")
                                        html_content.append("<ul class='mb-0'>")
                                        for tip in practical_tips:
                                            html_content.append(f"<li>{tip}</li>")
                                        html_content.append("</ul></div>")
                                    
                                    html_content.append("</div></div>")
                        
                        # 실무 적용, 사례 연구 등 추가 정보
                        if 'practical_applications' in lecture:
                            html_content.append(f"<div class='mt-3'><strong>실무 적용:</strong> {lecture['practical_applications']}</div>")
                        
                        if 'case_studies' in lecture:
                            html_content.append(f"<div class='mt-3'><strong>사례 연구:</strong> {lecture['case_studies']}</div>")
                        
                        if 'key_concepts' in lecture:
                            concepts = lecture['key_concepts']
                            if concepts:
                                html_content.append("<div class='mt-3'><strong>핵심 개념:</strong></div>")
                                html_content.append("<ul class='list-inline'>")
                                for concept in concepts:
                                    html_content.append(f"<li class='list-inline-item'><span class='badge bg-secondary'>{concept}</span></li>")
                                html_content.append("</ul>")
                        
                        html_content.append("</div>")
        
        # 기존 content 형식도 지원
        elif 'content' in lecture_plan_data:
            content = lecture_plan_data['content']
            content = content.replace('\n## ', '</p><h3>').replace('\n### ', '</p><h4>')
            content = content.replace('\n- ', '</p><li>').replace('\n* ', '</p><li>')
            content = content.replace('\n**', '</p><strong>').replace('**', '</strong>')
            content = content.replace('\n\n', '</p><p>')
            content = f"<div>{content}</div>"
            html_content.append(content)
        
        # 인용 출처
        if 'citations' in lecture_plan_data and lecture_plan_data['citations']:
            html_content.append('<h4 class="mt-4">참고 자료</h4>')
            html_content.append('<ul>')
            for citation in lecture_plan_data['citations']:
                html_content.append(f'<li><a href="{citation}" target="_blank" class="text-primary">{citation}</a></li>')
            html_content.append('</ul>')
        
        # 생성 정보
        if 'generated_at' in lecture_plan_data:
            html_content.append(f'<p class="text-muted small mt-4"><i class="fas fa-clock me-1"></i>생성일시: {lecture_plan_data["generated_at"]}</p>')
        
        result = '\n'.join(html_content)
        return result if result.strip() else "<p>강의안 내용을 표시할 수 없습니다.</p>"
        
    except Exception as e:
        logger.error(f"Error formatting lecture plan: {str(e)}")
        return f"<p class='text-danger'>강의안 포맷팅 중 오류가 발생했습니다: {str(e)}</p>"

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
    
    pagination = Book.query.order_by(Book.scraped_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('books_list.html', books=pagination.items, pagination=pagination)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """Display detailed information about a specific book"""
    book = Book.query.get_or_404(book_id)
    
    # Get PDF attachments for this book
    pdf_attachments = PDFAttachment.query.filter_by(book_id=book_id).all()
    
    # Parse lecture plan if it exists
    lecture_plan_data = None
    lecture_plan_content = ""
    if book.lecture_plan:
        try:
            lecture_plan_data = json.loads(book.lecture_plan)
            lecture_plan_content = format_lecture_plan(lecture_plan_data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in lecture_plan for book {book_id}")
            lecture_plan_content = "<p>강의안 데이터를 읽을 수 없습니다.</p>"
    
    return render_template('book_detail.html', 
                         book=book, 
                         lecture_plan=lecture_plan_data,
                         lecture_plan_content=lecture_plan_content,
                         pdf_attachments=pdf_attachments)

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
            'lecture_style': request.form.get('lecture_style', 'comprehensive'),
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
        
        # 1차 시도: Perplexity AI 생성기 (최신 정보 포함)
        try:
            from perplexity_generator import get_perplexity_generator
            perplexity_gen = get_perplexity_generator()
            
            if perplexity_gen:
                print("🔄 Perplexity AI 생성기 시도 중...")
                lecture_plan = perplexity_gen.generate_lecture_plan(book_data, lecture_preferences)
                
                if lecture_plan and not lecture_plan.get('error'):
                    print("✅ Perplexity AI 생성기 성공")
                    flash('최신 정보가 포함된 강의안을 생성했습니다!', 'success')
                else:
                    error_messages.append("Perplexity AI 생성기 실패")
                    lecture_plan = None
            else:
                error_messages.append("Perplexity AI 초기화 실패")
                
        except Exception as perplexity_error:
            error_messages.append(f"Perplexity AI 오류: {str(perplexity_error)}")
            lecture_plan = None
        
        # 2차 시도: 기본 생성기 (OpenAI)
        if not lecture_plan:
            try:
                from lecture_generator import LectureGenerator
                lecture_generator = LectureGenerator()
                print("🔄 OpenAI 기본 생성기 시도 중...")
                lecture_plan = lecture_generator.generate_lecture_plan(book_data, lecture_preferences)
                
                if lecture_plan and not lecture_plan.get('error'):
                    print("✅ OpenAI 기본 생성기 성공")
                    flash('기본 모드로 강의안을 생성했습니다!', 'success')
                else:
                    error_messages.append("OpenAI 기본 생성기 실패")
                    lecture_plan = None
                    
            except Exception as openai_error:
                error_messages.append(f"OpenAI 기본 생성기 오류: {str(openai_error)}")
                lecture_plan = None
        
        # 3차 시도: 대안 생성기들
        if not lecture_plan:
            try:
                from alternative_generators import AlternativeLectureGenerator
                alt_gen = AlternativeLectureGenerator()
                
                print("🔄 대안 생성기 시도 중...")
                lecture_plan = alt_gen.generate_with_openai_simple(book_data, lecture_preferences)
                
                if lecture_plan:
                    print("✅ 대안 생성기 성공")
                    flash('간단 모드로 강의안을 생성했습니다!', 'success')
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
        else:
            filename = pdf_attachment.filename if pdf_attachment else "파일"
            flash(f'PDF 파일 "{filename}"이 성공적으로 업로드되었습니다.', 'success')
        
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
