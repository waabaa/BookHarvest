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
    series_name = db.Column(String(300))  # 시리즈명 (예: 인공지능총서, 커뮤니케이션이해총서)
    author_photo_path = db.Column(String(500))  # 저자 사진 경로 (책 표지에서 추출)
    author_photo_rounded_path = db.Column(String(500))  # 원형 저자 사진 경로
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
    series_name = db.Column(String(300))  # 시리즈명
    series_url = db.Column(String(500))   # 시리즈 URL
    started_at = db.Column(DateTime, default=datetime.utcnow)
    completed_at = db.Column(DateTime)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<ScrapingJob {self.id}: Pages {self.start_page}-{self.end_page}>'

class PDFAttachment(db.Model):
    __tablename__ = 'pdf_attachments'
    
    id = db.Column(Integer, primary_key=True)
    filename = db.Column(String(500), nullable=False)
    file_path = db.Column(String(500), nullable=False)
    file_size = db.Column(Integer)  # 파일 크기 (bytes)
    content_text = db.Column(Text)  # PDF에서 추출한 텍스트
    uploaded_at = db.Column(DateTime, default=datetime.utcnow)
    
    # Book과의 관계 설정
    book_id = db.Column(Integer, db.ForeignKey('books.id'), nullable=True)
    book = db.relationship('Book', backref='pdf_attachments')
    
    def __repr__(self):
        return f'<PDFAttachment {self.filename}>'
