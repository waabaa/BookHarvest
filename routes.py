from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app, db
from models import Book, ScrapingJob
from scraper import start_scraping_job
import logging
import os

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
    return render_template('book_detail.html', book=book)

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
