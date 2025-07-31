import PyPDF2
import os
import logging
from werkzeug.utils import secure_filename
from models import PDFAttachment
from app import db

logger = logging.getLogger(__name__)

class PDFProcessor:
    """PDF 파일을 처리하고 텍스트를 추출하는 클래스"""
    
    ALLOWED_EXTENSIONS = {'pdf'}
    UPLOAD_FOLDER = 'static/uploads/pdfs'
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    def __init__(self):
        # 업로드 폴더 생성
        os.makedirs(self.UPLOAD_FOLDER, exist_ok=True)
    
    def allowed_file(self, filename):
        """허용된 파일 확장자인지 확인"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in self.ALLOWED_EXTENSIONS
    
    def extract_text_from_pdf(self, file_path):
        """PDF 파일에서 텍스트 추출"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ''
                
                # 모든 페이지의 텍스트 추출
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + '\n'
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"PDF 텍스트 추출 실패: {str(e)}")
            return None
    
    def save_pdf_file(self, file, book_id=None):
        """PDF 파일을 저장하고 텍스트를 추출하여 데이터베이스에 저장"""
        try:
            if not file or not self.allowed_file(file.filename):
                return None, "허용되지 않는 파일 형식입니다. PDF 파일만 업로드 가능합니다."
            
            # 파일 크기 확인
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > self.MAX_FILE_SIZE:
                return None, f"파일 크기가 너무 큽니다. 최대 {self.MAX_FILE_SIZE // (1024*1024)}MB까지 업로드 가능합니다."
            
            # 안전한 파일명 생성
            filename = secure_filename(file.filename)
            
            # 중복 파일명 처리
            base_name, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(os.path.join(self.UPLOAD_FOLDER, filename)):
                filename = f"{base_name}_{counter}{ext}"
                counter += 1
            
            # 파일 저장
            file_path = os.path.join(self.UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # PDF에서 텍스트 추출
            extracted_text = self.extract_text_from_pdf(file_path)
            
            if extracted_text is None:
                # 파일 삭제
                os.remove(file_path)
                return None, "PDF 파일에서 텍스트를 추출할 수 없습니다."
            
            # 데이터베이스에 저장
            pdf_attachment = PDFAttachment(
                filename=filename,
                file_path=file_path,
                file_size=file_size,
                content_text=extracted_text,
                book_id=book_id
            )
            
            db.session.add(pdf_attachment)
            db.session.commit()
            
            logger.info(f"PDF 파일 저장 완료: {filename}")
            return pdf_attachment, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"PDF 파일 저장 실패: {str(e)}")
            return None, f"파일 저장 중 오류가 발생했습니다: {str(e)}"
    
    def get_all_pdfs(self):
        """모든 PDF 첨부파일 목록 반환"""
        return PDFAttachment.query.order_by(PDFAttachment.uploaded_at.desc()).all()
    
    def get_pdf_by_id(self, pdf_id):
        """ID로 PDF 첨부파일 조회"""
        return PDFAttachment.query.get(pdf_id)
    
    def delete_pdf(self, pdf_id):
        """PDF 첨부파일 삭제 (파일과 DB 레코드 모두)"""
        try:
            pdf_attachment = PDFAttachment.query.get(pdf_id)
            if not pdf_attachment:
                return False, "파일을 찾을 수 없습니다."
            
            # 실제 파일 삭제
            if os.path.exists(pdf_attachment.file_path):
                os.remove(pdf_attachment.file_path)
            
            # DB 레코드 삭제
            db.session.delete(pdf_attachment)
            db.session.commit()
            
            logger.info(f"PDF 파일 삭제 완료: {pdf_attachment.filename}")
            return True, None
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"PDF 파일 삭제 실패: {str(e)}")
            return False, f"파일 삭제 중 오류가 발생했습니다: {str(e)}"