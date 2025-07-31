#!/usr/bin/env python3
"""
이미지 처리 모듈 - 책 표지에서 저자 사진 추출
"""

import os
from PIL import Image, ImageDraw, ImageFilter
import requests
from io import BytesIO

class ImageProcessor:
    """책 표지 이미지에서 저자 사진을 추출하는 클래스"""
    
    def __init__(self):
        self.static_dir = 'static'
        self.covers_dir = os.path.join(self.static_dir, 'covers')
        self.authors_dir = os.path.join(self.static_dir, 'authors')
        
        # 디렉토리 생성
        os.makedirs(self.authors_dir, exist_ok=True)
    
    def extract_author_photo(self, cover_image_path, book_id):
        """
        책 표지에서 저자 사진 부분을 추출
        
        Args:
            cover_image_path (str): 책 표지 이미지 경로
            book_id (int): 책 ID
            
        Returns:
            str: 추출된 저자 사진 파일 경로 (실패시 None)
        """
        try:
            # 전체 경로 구성
            full_cover_path = os.path.join(cover_image_path)
            
            if not os.path.exists(full_cover_path):
                print(f"책 표지 파일을 찾을 수 없습니다: {full_cover_path}")
                return None
            
            # 이미지 열기
            with Image.open(full_cover_path) as img:
                # 이미지 크기 확인
                width, height = img.size
                print(f"원본 이미지 크기: {width} x {height}")
                
                # 저자 사진 영역 추정 (일반적으로 우하단에 위치)
                # 첨부된 이미지 기준으로 저자 사진 위치 계산
                author_left = int(width * 0.05)    # 좌측 5%
                author_top = int(height * 0.65)    # 상단 65%
                author_right = int(width * 0.55)   # 우측 55%
                author_bottom = int(height * 0.95) # 하단 95%
                
                # 저자 사진 영역 추출
                author_box = (author_left, author_top, author_right, author_bottom)
                author_img = img.crop(author_box)
                
                # 저자 사진 파일명 생성
                author_filename = f"author_{book_id}.png"
                author_path = os.path.join(self.authors_dir, author_filename)
                
                # 저자 사진 크기 조정 (적절한 크기로)
                author_img = author_img.resize((200, 280), Image.Resampling.LANCZOS)
                
                # 저자 사진 저장
                author_img.save(author_path, 'PNG', quality=95, optimize=True)
                
                # 상대 경로 반환
                relative_path = os.path.join('authors', author_filename)
                print(f"저자 사진 추출 완료: {relative_path}")
                return relative_path
                
        except Exception as e:
            print(f"저자 사진 추출 중 오류 발생: {e}")
            return None
    
    def create_rounded_author_photo(self, author_image_path):
        """
        저자 사진을 원형으로 만들기
        
        Args:
            author_image_path (str): 저자 사진 경로
            
        Returns:
            str: 원형 저자 사진 경로
        """
        try:
            full_path = os.path.join('static', author_image_path)
            
            if not os.path.exists(full_path):
                return None
            
            with Image.open(full_path) as img:
                # 정사각형으로 크롭
                size = min(img.size)
                left = (img.width - size) // 2
                top = (img.height - size) // 2
                right = left + size
                bottom = top + size
                
                img = img.crop((left, top, right, bottom))
                
                # 원형 마스크 생성
                mask = Image.new('L', (size, size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, size, size), fill=255)
                
                # 원형 이미지 생성
                output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
                output.paste(img, (0, 0))
                output.putalpha(mask)
                
                # 원형 파일명 생성
                base_name = os.path.basename(author_image_path)
                name, ext = os.path.splitext(base_name)
                rounded_filename = f"{name}_rounded{ext}"
                rounded_path = os.path.join(self.authors_dir, rounded_filename)
                
                output.save(rounded_path, 'PNG')
                
                return os.path.join('authors', rounded_filename)
                
        except Exception as e:
            print(f"원형 저자 사진 생성 중 오류: {e}")
            return None
    
    def process_book_cover(self, cover_image_path, book_id):
        """
        책 표지를 처리하여 저자 사진을 추출하고 원형으로 만들기
        
        Args:
            cover_image_path (str): 책 표지 이미지 경로
            book_id (int): 책 ID
            
        Returns:
            dict: 처리 결과 {'author_photo': path, 'author_photo_rounded': path}
        """
        result = {
            'author_photo': None,
            'author_photo_rounded': None
        }
        
        # 저자 사진 추출
        author_photo = self.extract_author_photo(cover_image_path, book_id)
        if author_photo:
            result['author_photo'] = author_photo
            
            # 원형 저자 사진 생성
            rounded_photo = self.create_rounded_author_photo(author_photo)
            if rounded_photo:
                result['author_photo_rounded'] = rounded_photo
        
        return result

def process_existing_covers():
    """기존 책 표지들을 처리하여 저자 사진 추출"""
    from app import app, db
    from models import Book
    
    processor = ImageProcessor()
    
    with app.app_context():
        books = Book.query.filter(Book.cover_image_path.isnot(None)).all()
        
        for book in books:
            print(f"\n책 처리 중: {book.title}")
            
            if book.cover_image_path:
                full_cover_path = os.path.join('static', book.cover_image_path)
                
                if os.path.exists(full_cover_path):
                    result = processor.process_book_cover(full_cover_path, book.id)
                    
                    if result['author_photo']:
                        print(f"저자 사진 추출 성공: {result['author_photo']}")
                        # 데이터베이스에 저자 사진 경로 저장 (필요시)
                        # book.author_photo_path = result['author_photo']
                        # book.author_photo_rounded_path = result['author_photo_rounded']
                        # db.session.commit()
                    else:
                        print("저자 사진 추출 실패")
                else:
                    print(f"표지 파일을 찾을 수 없음: {full_cover_path}")

if __name__ == "__main__":
    # 테스트용 첨부 파일 처리
    processor = ImageProcessor()
    
    # 첨부된 이미지 처리
    attached_image = "attached_assets/image_1753926234908.png"
    if os.path.exists(attached_image):
        print("첨부된 이미지로 테스트 시작...")
        result = processor.process_book_cover(attached_image, 999)  # 테스트용 ID
        print(f"처리 결과: {result}")
    else:
        print("첨부된 이미지를 찾을 수 없습니다.")