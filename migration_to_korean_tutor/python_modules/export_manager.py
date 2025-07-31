#!/usr/bin/env python3
"""
데이터 내보내기 관리자 - 스크래핑 데이터 및 강의안 다운로드 기능
"""

import os
import json
import zipfile
import shutil
from datetime import datetime
from io import BytesIO
from PIL import Image
import tempfile

class ExportManager:
    """데이터 내보내기 관리 클래스"""
    
    def __init__(self):
        self.temp_dir = tempfile.mkdtemp()
        
    def export_all_data(self, books, include_images=True, include_pdfs=True, include_lectures=True):
        """
        모든 스크래핑 데이터를 ZIP 파일로 내보내기
        
        Args:
            books: 책 리스트
            include_images: 이미지 포함 여부
            include_pdfs: PDF 포함 여부  
            include_lectures: 강의안 포함 여부
            
        Returns:
            str: ZIP 파일 경로
        """
        try:
            # 임시 디렉토리 생성
            export_dir = os.path.join(self.temp_dir, 'commbooks_export')
            os.makedirs(export_dir, exist_ok=True)
            
            # 메타데이터 준비
            metadata = {
                'export_date': datetime.now().isoformat(),
                'total_books': len(books),
                'export_options': {
                    'images': include_images,
                    'pdfs': include_pdfs,
                    'lectures': include_lectures
                }
            }
            
            books_data = []
            
            for book in books:
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
                    'scraped_at': book.scraped_at.isoformat() if book.scraped_at else None,
                    'book_url': book.book_url
                }
                
                # 이미지 처리
                if include_images:
                    book_dir = os.path.join(export_dir, f'book_{book.id}')
                    os.makedirs(book_dir, exist_ok=True)
                    
                    # 책 표지 복사
                    if book.cover_image_path:
                        cover_src = os.path.join('static', book.cover_image_path)
                        if os.path.exists(cover_src):
                            cover_dst = os.path.join(book_dir, 'cover.png')
                            shutil.copy2(cover_src, cover_dst)
                            book_data['cover_image'] = 'cover.png'
                    
                    # 저자 사진 복사
                    if book.author_photo_path:
                        author_src = os.path.join('static', book.author_photo_path)
                        if os.path.exists(author_src):
                            author_dst = os.path.join(book_dir, 'author.png')
                            shutil.copy2(author_src, author_dst)
                            book_data['author_photo'] = 'author.png'
                    
                    # 원형 저자 사진 복사
                    if book.author_photo_rounded_path:
                        rounded_src = os.path.join('static', book.author_photo_rounded_path)
                        if os.path.exists(rounded_src):
                            rounded_dst = os.path.join(book_dir, 'author_rounded.png')
                            shutil.copy2(rounded_src, rounded_dst)
                            book_data['author_photo_rounded'] = 'author_rounded.png'
                
                # PDF 첨부파일 처리
                if include_pdfs and hasattr(book, 'pdf_attachments'):
                    if not 'book_dir' in locals():
                        book_dir = os.path.join(export_dir, f'book_{book.id}')
                        os.makedirs(book_dir, exist_ok=True)
                    
                    pdfs_data = []
                    for pdf in book.pdf_attachments:
                        if os.path.exists(pdf.file_path):
                            pdf_dst = os.path.join(book_dir, pdf.filename)
                            shutil.copy2(pdf.file_path, pdf_dst)
                            pdfs_data.append({
                                'filename': pdf.filename,
                                'file_size': pdf.file_size,
                                'content_text': pdf.content_text,
                                'uploaded_at': pdf.uploaded_at.isoformat() if pdf.uploaded_at else None
                            })
                    book_data['pdf_attachments'] = pdfs_data
                
                # 강의안 처리
                if include_lectures:
                    if book.lecture_plan:
                        book_data['lecture_plan'] = json.loads(book.lecture_plan) if isinstance(book.lecture_plan, str) else book.lecture_plan
                    
                    if book.lecture_plan_history:
                        book_data['lecture_plan_history'] = json.loads(book.lecture_plan_history) if isinstance(book.lecture_plan_history, str) else book.lecture_plan_history
                
                books_data.append(book_data)
            
            # 메타데이터와 책 데이터를 JSON으로 저장
            metadata['books'] = books_data
            
            metadata_file = os.path.join(export_dir, 'metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # ZIP 파일 생성
            zip_path = os.path.join(self.temp_dir, f'commbooks_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(export_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, export_dir)
                        zipf.write(file_path, arc_path)
            
            return zip_path
            
        except Exception as e:
            print(f"데이터 내보내기 오류: {e}")
            return None
    
    def export_lectures_only(self, books):
        """
        강의안만 따로 내보내기 (책 제목과 저자 포함)
        
        Args:
            books: 책 리스트
            
        Returns:
            str: ZIP 파일 경로
        """
        try:
            export_dir = os.path.join(self.temp_dir, 'lectures_export')
            os.makedirs(export_dir, exist_ok=True)
            
            lectures_data = {
                'export_date': datetime.now().isoformat(),
                'export_type': 'lectures_only',
                'lectures': []
            }
            
            for book in books:
                if book.lecture_plan:
                    lecture_data = {
                        'book_id': book.id,
                        'book_title': book.title,
                        'book_author': book.author,
                        'series_name': book.series_name,
                        'lecture_plan': json.loads(book.lecture_plan) if isinstance(book.lecture_plan, str) else book.lecture_plan
                    }
                    
                    # 강의안 히스토리도 포함
                    if book.lecture_plan_history:
                        lecture_data['lecture_plan_history'] = json.loads(book.lecture_plan_history) if isinstance(book.lecture_plan_history, str) else book.lecture_plan_history
                    
                    lectures_data['lectures'].append(lecture_data)
                    
                    # 개별 강의안 파일도 생성
                    lecture_filename = f"{book.id}_{book.title[:20].replace('/', '_')}_강의안.json"
                    lecture_file_path = os.path.join(export_dir, lecture_filename)
                    
                    with open(lecture_file_path, 'w', encoding='utf-8') as f:
                        json.dump(lecture_data, f, ensure_ascii=False, indent=2)
            
            # 전체 강의안 파일 생성
            all_lectures_file = os.path.join(export_dir, 'all_lectures.json')
            with open(all_lectures_file, 'w', encoding='utf-8') as f:
                json.dump(lectures_data, f, ensure_ascii=False, indent=2)
            
            # ZIP 파일 생성
            zip_path = os.path.join(self.temp_dir, f'lectures_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.zip')
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(export_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arc_path = os.path.relpath(file_path, export_dir)
                        zipf.write(file_path, arc_path)
            
            return zip_path
            
        except Exception as e:
            print(f"강의안 내보내기 오류: {e}")
            return None
    
    def cleanup(self):
        """임시 파일 정리"""
        try:
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"임시 파일 정리 오류: {e}")

if __name__ == "__main__":
    # 테스트용
    from app import app, db
    from models import Book
    
    with app.app_context():
        export_manager = ExportManager()
        books = Book.query.limit(2).all()
        
        if books:
            print("전체 데이터 내보내기 테스트...")
            zip_path = export_manager.export_all_data(books)
            if zip_path:
                print(f"✅ 전체 데이터 내보내기 성공: {zip_path}")
            
            print("강의안만 내보내기 테스트...")
            lectures_zip = export_manager.export_lectures_only(books)
            if lectures_zip:
                print(f"✅ 강의안 내보내기 성공: {lectures_zip}")
        
        export_manager.cleanup()