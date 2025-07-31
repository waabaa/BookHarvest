#!/usr/bin/env python3
"""
기존 책들에서 저자 사진 추출하는 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import app, db
from models import Book
from image_processor import ImageProcessor

def extract_all_author_photos():
    """모든 기존 책에서 저자 사진 추출"""
    with app.app_context():
        processor = ImageProcessor()
        
        # 표지 이미지가 있는 책들 가져오기
        books = Book.query.filter(Book.cover_image_path.isnot(None)).all()
        
        print(f"총 {len(books)}권의 책에서 저자 사진 추출을 시도합니다...")
        
        success_count = 0
        total_count = len(books)
        
        for i, book in enumerate(books, 1):
            print(f"\n[{i}/{total_count}] 처리 중: {book.title}")
            
            if book.author_photo_path:
                print("  → 이미 저자 사진이 있습니다. 건너뜀.")
                continue
            
            if not book.cover_image_path:
                print("  → 표지 이미지가 없습니다. 건너뜀.")
                continue
            
            cover_path = os.path.join('static', book.cover_image_path)
            
            if not os.path.exists(cover_path):
                print(f"  → 표지 파일을 찾을 수 없음: {cover_path}")
                continue
            
            try:
                result = processor.process_book_cover(cover_path, book.id)
                
                if result['author_photo']:
                    book.author_photo_path = result['author_photo']
                    book.author_photo_rounded_path = result['author_photo_rounded']
                    db.session.commit()
                    
                    success_count += 1
                    print(f"  ✅ 저자 사진 추출 성공: {result['author_photo']}")
                    if result['author_photo_rounded']:
                        print(f"      원형 사진: {result['author_photo_rounded']}")
                else:
                    print("  ❌ 저자 사진 추출 실패")
                    
            except Exception as e:
                print(f"  ❌ 오류 발생: {e}")
        
        print(f"\n{'='*50}")
        print(f"작업 완료!")
        print(f"성공: {success_count}권")
        print(f"전체: {total_count}권")
        print(f"성공률: {(success_count/total_count*100):.1f}%")

if __name__ == "__main__":
    extract_all_author_photos()