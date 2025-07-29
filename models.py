from app import db
from datetime import datetime
from sqlalchemy import Text, String, DateTime, Integer, Boolean

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(Integer, primary_key=True)
    title = db.Column(String(500), nullable=False)
    author = db.Column(String(300))
    description = db.Column(Text)
    review_200 = db.Column(Text)  # 200자평
    contents = db.Column(Text)    # 차례
    book_preview = db.Column(Text)  # 책속으로 (책 브리핑)
    publish_date = db.Column(String(200))
    cover_image_path = db.Column(String(500))
    book_url = db.Column(String(500), unique=True, nullable=False)
    lecture_plan = db.Column(Text)  # AI 생성 강의안 (JSON 형태)
    scraped_at = db.Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Book {self.title}>'

class ScrapingJob(db.Model):
    __tablename__ = 'scraping_jobs'
    
    id = db.Column(Integer, primary_key=True)
    start_page = db.Column(Integer, nullable=False)
    end_page = db.Column(Integer, nullable=False)
    current_page = db.Column(Integer, default=0)
    total_books_found = db.Column(Integer, default=0)
    books_scraped = db.Column(Integer, default=0)
    books_failed = db.Column(Integer, default=0)
    status = db.Column(String(50), default='pending')  # pending, running, completed, failed
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<ScrapingJob {self.id}: Pages {self.start_page}-{self.end_page}>'
