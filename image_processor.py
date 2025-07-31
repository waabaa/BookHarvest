#!/usr/bin/env python3
"""
이미지 처리 모듈 - 책 표지에서 저자 사진을 원형으로 추출
"""

import os
from PIL import Image, ImageDraw
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
        책 표지에서 저자 사진 부분을 추출하여 원형으로 만들기
        
        Args:
            cover_image_path (str): 책 표지 이미지 경로
            book_id (int): 책 ID
            
        Returns:
            dict: 추출된 저자 사진 파일 경로 (실패시 None)
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
                author_left = int(width * 0.05)    # 좌측 5%
                author_top = int(height * 0.65)    # 상단 65%
                author_right = int(width * 0.55)   # 우측 55%
                author_bottom = int(height * 0.95) # 하단 95%
                
                # 저자 사진 영역 추출
                author_box = (author_left, author_top, author_right, author_bottom)
                author_img = img.crop(author_box)
                
                # 얼굴 중심으로 정사각형 크롭하여 원형으로 만들기
                author_img = self.create_circular_author_photo(author_img)
                
                # 저자 사진 파일명 생성
                author_filename = f"author_{book_id}.png"
                author_path = os.path.join(self.authors_dir, author_filename)
                
                # PNG로 저장하여 투명도 유지
                author_img.save(author_path, 'PNG', optimize=True)
                
                print(f"원형 저자 사진 생성 완료: {author_path}")
                
                return {
                    'author_photo_path': f"authors/{author_filename}",
                    'author_photo_rounded_path': f"authors/{author_filename}"
                }
                
        except Exception as e:
            print(f"저자 사진 추출 중 오류 발생: {e}")
            return None
    
    def create_circular_author_photo(self, img):
        """
        얼굴 중심으로 정사각형 크롭하여 원형 저자 사진 생성 (원본 비율 유지)
        """
        try:
            # 원본 크기
            width, height = img.size
            
            # 정사각형으로 만들기 위해 중심부 크롭
            if width > height:
                # 가로가 더 길면 세로 중심으로 크롭
                left = (width - height) // 2
                top = 0
                right = left + height
                bottom = height
            else:
                # 세로가 더 길면 가로 중심으로 크롭 (얼굴은 보통 상단에 위치)
                left = 0
                top = 0  # 얼굴이 상단에 있을 가능성이 높으므로 상단부터
                right = width
                bottom = width
            
            # 정사각형 크롭
            square_img = img.crop((left, top, right, bottom))
            
            # 200x200 크기로 리사이즈 (원본 비율 유지됨)
            size = 200
            square_img = square_img.resize((size, size), Image.Resampling.LANCZOS)
            
            # 원형 마스크 생성
            mask = Image.new('L', (size, size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, size, size), fill=255)
            
            # RGBA 모드로 변환
            if square_img.mode != 'RGBA':
                square_img = square_img.convert('RGBA')
            
            # 원형 마스크 적용
            output = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            output.paste(square_img, (0, 0))
            output.putalpha(mask)
            
            return output
            
        except Exception as e:
            print(f"원형 저자 사진 생성 중 오류: {e}")
            return img
    
    def create_rounded_image(self, input_path, output_path, size=(200, 200)):
        """
        기존 이미지를 원형으로 만들기 (호환성을 위해 유지)
        """
        try:
            with Image.open(input_path) as img:
                # 정사각형으로 크롭
                circular_img = self.create_circular_author_photo(img)
                
                # 저장
                circular_img.save(output_path, 'PNG', optimize=True)
                print(f"원형 이미지 생성 완료: {output_path}")
                
        except Exception as e:
            print(f"원형 이미지 생성 오류: {e}")