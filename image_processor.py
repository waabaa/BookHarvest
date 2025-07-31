#!/usr/bin/env python3
"""
이미지 처리 모듈 - 책 표지에서 저자 사진 추출
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageChops
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
        책 표지에서 저자 사진 부분을 추출 (배경 제거 포함)
        
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
                
                # 배경 제거 시도
                author_img = self.remove_background(author_img)
                
                # 저자 사진 파일명 생성
                author_filename = f"author_{book_id}.png"
                author_path = os.path.join(self.authors_dir, author_filename)
                
                # 가로폭에 맞춰 비율 유지하면서 크기 조정 (찌그러지지 않게)
                original_width, original_height = author_img.size
                target_width = 200
                
                # 원본 비율 유지
                aspect_ratio = original_height / original_width
                target_height = int(target_width * aspect_ratio)
                
                # 최소/최대 높이 제한 (너무 길거나 짧지 않게)
                min_height = 150
                max_height = 400
                
                if target_height < min_height:
                    target_height = min_height
                    target_width = int(target_height / aspect_ratio)
                elif target_height > max_height:
                    target_height = max_height
                    target_width = int(target_height / aspect_ratio)
                
                author_img = author_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
                print(f"크기 조정: {original_width}x{original_height} → {target_width}x{target_height}")
                
                # 저자 사진 저장 (PNG로 투명도 유지)
                author_img.save(author_path, 'PNG', quality=95, optimize=True)
                
                # 상대 경로 반환
                relative_path = os.path.join('authors', author_filename)
                print(f"저자 사진 추출 완료: {relative_path}")
                return relative_path
                
        except Exception as e:
            print(f"저자 사진 추출 중 오류 발생: {e}")
            return None
    
    def remove_background(self, image):
        """
        이미지에서 배경 제거 (사람 부분만 남기기)
        
        Args:
            image (PIL.Image): 원본 이미지
            
        Returns:
            PIL.Image: 배경이 제거된 이미지
        """
        try:
            print("PIL 기반 배경 제거 적용 중...")
            return self.remove_background_by_color_pil(image)
                
        except Exception as e:
            print(f"배경 제거 중 오류: {e}")
            # 실패시 원본 반환
            return image
    
    def remove_background_by_color_pil(self, image):
        """
        PIL만 사용한 색상 기반 배경 제거 (파란색 배경 제거)
        
        Args:
            image (PIL.Image): 원본 이미지
            
        Returns:
            PIL.Image: 배경이 제거된 이미지
        """
        try:
            # RGBA로 변환
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # 픽셀 데이터 가져오기
            data = image.getdata()
            new_data = []
            
            for item in data:
                r, g, b, a = item
                
                # 파란색 계열 배경 감지 (첨부된 이미지의 파란색 줄무늬)
                is_background = False
                
                # 색상 분석을 위한 변수
                total_brightness = r + g + b
                blue_dominance = b - max(r, g)
                
                # 1. 파란색 줄무늬 패턴 감지 (더 엄격한 기준)
                if (b > 100 and blue_dominance > 30) or (b > 150 and r < 100 and g < 120):
                    is_background = True
                
                # 2. 흰색 또는 매우 밝은 픽셀 (텍스트 영역)
                elif total_brightness > 700 and abs(r-g) < 20 and abs(g-b) < 20:  
                    is_background = True
                
                # 3. 파란색 계열의 줄무늬 (시안/터키석 색상 포함)
                elif b > 80 and (b > r + 20) and (b > g + 10):  
                    is_background = True
                
                # 4. 매우 어두운 배경 (그림자 등)
                elif total_brightness < 120 and b >= max(r, g):
                    is_background = True
                
                # 5. 연한 파란색/하늘색 계열
                elif b > 120 and g > 100 and r < 100:
                    is_background = True
                
                if is_background:
                    new_data.append((r, g, b, 0))  # 투명하게
                else:
                    new_data.append(item)  # 원본 유지
            
            # 새로운 이미지 생성
            image.putdata(new_data)
            
            # 가장자리 정리 (앨리어싱 제거)
            image = self.clean_edges(image)
            
            return image
            
        except Exception as e:
            print(f"PIL 배경 제거 오류: {e}")
            # 실패시 RGBA로 변환해서 반환
            if image.mode != 'RGBA':
                return image.convert('RGBA')
            return image
    
    def clean_edges(self, image):
        """
        이미지 가장자리 정리 (앨리어싱 제거)
        
        Args:
            image (PIL.Image): RGBA 이미지
            
        Returns:
            PIL.Image: 가장자리가 정리된 이미지
        """
        try:
            # 알파 채널 추출
            alpha = image.split()[-1]
            
            # 약간의 블러 적용으로 부드럽게
            alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.8))
            
            # 이미지에 다시 적용
            image.putalpha(alpha)
            
            # 추가 후처리: 고립된 픽셀 제거
            image = self.remove_isolated_pixels(image)
            
            return image
            
        except Exception as e:
            print(f"가장자리 정리 오류: {e}")
            return image
    
    def remove_isolated_pixels(self, image):
        """
        고립된 픽셀들 제거 (노이즈 제거)
        
        Args:
            image (PIL.Image): RGBA 이미지
            
        Returns:
            PIL.Image: 노이즈가 제거된 이미지
        """
        try:
            width, height = image.size
            pixels = list(image.getdata())
            new_pixels = []
            
            for y in range(height):
                for x in range(width):
                    index = y * width + x
                    pixel = pixels[index]
                    
                    # 투명한 픽셀은 그대로 유지
                    if pixel[3] == 0:
                        new_pixels.append(pixel)
                        continue
                    
                    # 주변 8개 픽셀 중 투명하지 않은 픽셀 개수 계산
                    opaque_neighbors = 0
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                neighbor_index = ny * width + nx
                                if pixels[neighbor_index][3] > 0:
                                    opaque_neighbors += 1
                    
                    # 주변에 불투명한 픽셀이 2개 이하면 제거 (고립된 픽셀)
                    if opaque_neighbors <= 2:
                        new_pixels.append((pixel[0], pixel[1], pixel[2], 0))
                    else:
                        new_pixels.append(pixel)
            
            image.putdata(new_pixels)
            return image
            
        except Exception as e:
            print(f"고립된 픽셀 제거 오류: {e}")
            return image
    
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