import requests
from bs4 import BeautifulSoup
import time
import os
import logging
import re
from urllib.parse import urljoin, urlparse
from PIL import Image
import io
from app import db
from models import Book, ScrapingJob
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class CommBooksScraper:
    def __init__(self):
        self.base_url = "https://commbooks.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.images_dir = "static/images/covers"
        os.makedirs(self.images_dir, exist_ok=True)
    
    def get_page_book_links(self, page_num):
        """Extract all book links from a specific page"""
        url = f"{self.base_url}/도서-태그/인공지능총서/page/{page_num}/"
        logger.info(f"Scraping page {page_num}: {url}")
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all book links - adjust selector based on actual site structure
            book_links = []
            
            # Look for links that contain book information
            # This selector may need adjustment based on the actual HTML structure
            book_elements = soup.find_all('a', href=True)
            
            for element in book_elements:
                href = element.get('href')
                if href and isinstance(href, str):
                    # Filter for book detail pages
                    if '/도서/' in href and href not in book_links:
                        full_url = urljoin(self.base_url, href)
                        book_links.append(full_url)
            
            logger.info(f"Found {len(book_links)} book links on page {page_num}")
            return book_links
            
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {str(e)}")
            return []
    
    def clean_text(self, text):
        """Clean extracted text by removing unwanted patterns"""
        if not text:
            return ""
        
        # Remove common unwanted patterns specific to CommBooks
        unwanted_patterns = [
            r'읽기구매선택하세요.*?책소개',
            r'정보발행일.*?원',
            r'ISBN\(.*?\).*?원',
            r'분류컴북스.*?총서\??',
            r'열람서비스.*?중지',
            r'구매.*?선택하세요',
            r'\d+원\s*$',
            r'^\d+\s*',  # Leading numbers
            r'쪽수\s*\d+\s*쪽',
            r'판형\s*\d+\*\d+mm',
            r'ISBN\([^)]+\)\s*\d+\s*\d+원',
            r'지은이.*?책소개',
            r'발행일.*?쪽수',
            r'구매.*?원',
            r'컴북스.*?총서',
            r'\d{13}\s*\d+\s*\d+원',  # ISBN patterns
            r'05500\s*\d+원',
            r'04500\s*\d+원',
            r'045009800원',
            r'210\*297mm',
            r'128\*188mm',
            # Footer and legal information patterns
            r'이용약관.*?권장합니다\.',
            r'개인정보취급방침.*?All Rights Reserved',
            r'페이스북컴북스.*?파이어폭스를 권장합니다',
            r'서울시.*?commbooks@commbooks\.com',
            r'대표이사.*?통신판매업신고',
            r'Copyright.*?All Rights Reserved',
            r'커뮤니케이션북스.*?권장합니다',
            r'사업자등록번호.*?\d+-\d+-\d+',
            r'02\.7474\.001.*?02\.736\.5047',
            r'성북구.*?성북동1가',
        ]
        
        cleaned_text = text
        for pattern in unwanted_patterns:
            cleaned_text = re.sub(pattern, '', cleaned_text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove extra whitespace and normalize
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        
        # Check if the cleaned text is mostly footer/legal info
        footer_indicators = [
            '이용약관', '개인정보취급방침', 'commbooks@commbooks.com',
            '대표이사', '사업자등록번호', 'Copyright', '커뮤니케이션북스',
            '성북구', '페이스북컴북스'
        ]
        
        footer_count = sum(1 for indicator in footer_indicators if indicator in cleaned_text)
        if footer_count >= 3:  # If 3 or more footer indicators, likely footer content
            return ""
        
        return cleaned_text
    
    def extract_section_content(self, soup, section_title):
        """Extract content from a specific section by title - improved for CommBooks"""
        try:
            # Find all text nodes containing the section title
            section_headers = soup.find_all(string=lambda text: text and section_title in str(text))
            
            for header in section_headers:
                # Find the parent element containing the header
                parent = header.parent
                if not parent:
                    continue
                
                # Start with the parent and look for content in various ways
                content_candidates = []
                
                # Method 1: Look for next sibling elements
                current = parent
                while current:
                    next_sibling = current.find_next_sibling()
                    if next_sibling:
                        content_text = next_sibling.get_text(separator=' ', strip=True)
                        if content_text and len(content_text) > 20:
                            content_candidates.append(content_text)
                            break
                    current = current.parent
                
                # Method 2: Look for content in the same container
                container = parent
                for i in range(3):  # Go up max 3 levels
                    container = container.parent if container.parent else container
                    if container:
                        # Find all text after our header
                        all_text = container.get_text(separator=' ', strip=True)
                        header_pos = all_text.find(section_title)
                        if header_pos >= 0:
                            after_header = all_text[header_pos + len(section_title):]
                            # Stop at next section header
                            next_sections = ['지은이', '책소개', '200자평', '차례', '책속으로', '발행일', '정보']
                            for next_section in next_sections:
                                if next_section != section_title and next_section in after_header:
                                    section_end = after_header.find(next_section)
                                    after_header = after_header[:section_end]
                                    break
                            if after_header and len(after_header) > 20:
                                content_candidates.append(after_header)
                
                # Method 3: Look for content in nearby div/p elements
                nearby_elements = parent.find_next_siblings(['div', 'p', 'span'])[:3]
                for element in nearby_elements:
                    element_text = element.get_text(separator=' ', strip=True)
                    if element_text and len(element_text) > 20:
                        content_candidates.append(element_text)
                
                # Choose the best candidate
                for candidate in content_candidates:
                    cleaned_text = self.clean_text(candidate)
                    # Ensure content doesn't contain our section title and is substantial
                    if (len(cleaned_text) > 10 and 
                        section_title not in cleaned_text and
                        not cleaned_text.startswith(section_title)):
                        return cleaned_text
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting {section_title}: {str(e)}")
            return ""

    def scrape_book_details(self, book_url):
        """Scrape detailed information from a single book page"""
        logger.info(f"Scraping book details: {book_url}")
        
        try:
            response = self.session.get(book_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            book_data = {
                'book_url': book_url,
                'title': '',
                'author': '',
                'description': '',
                'review_200': '',
                'contents': '',
                'book_preview': '',
                'publish_date': '',
                'cover_image_path': ''
            }
            
            # Extract title - look for h1 or page title
            title_candidates = [
                soup.find('h1', class_=lambda x: x and 'title' in x.lower()),
                soup.find('h1'),
                soup.find('title')
            ]
            
            for title_element in title_candidates:
                if title_element:
                    title_text = title_element.get_text(strip=True)
                    # Remove site name and other noise
                    title_text = re.sub(r'\s*-\s*CommBooks.*$', '', title_text)
                    title_text = re.sub(r'\s*\|\s*CommBooks.*$', '', title_text)
                    book_data['title'] = title_text.strip()
                    if book_data['title']:
                        break
            
            # Extract author
            author_text = self.extract_section_content(soup, "지은이")
            if author_text:
                # Remove "지은이" label and clean
                author_text = re.sub(r'^지은이[:\s]*', '', author_text)
                book_data['author'] = author_text.strip()
            
            # Extract description/introduction
            desc_text = self.extract_section_content(soup, "책소개")
            if not desc_text:
                desc_text = self.extract_section_content(soup, "소개")
            if desc_text:
                book_data['description'] = desc_text
            
            # Extract 200자평
            review_text = self.extract_section_content(soup, "200자평")
            if review_text:
                book_data['review_200'] = review_text
            
            # Extract contents (차례) with improved formatting
            contents_text = self.extract_section_content(soup, "차례")
            if contents_text:
                # Clean up and format contents properly
                contents_text = self.format_contents_text(contents_text)
                book_data['contents'] = contents_text
            
            # Extract book preview (책속으로)
            preview_text = self.extract_section_content(soup, "책속으로")
            if not preview_text:
                preview_text = self.extract_section_content(soup, "책 브리핑")
            if preview_text:
                book_data['book_preview'] = preview_text
            
            # Extract publish date
            date_text = self.extract_section_content(soup, "발행일")
            if date_text:
                # Extract just the date, remove extra text
                date_match = re.search(r'(\d{4}년?\s*\d{1,2}월?\s*\d{1,2}일?)', date_text)
                if date_match:
                    book_data['publish_date'] = date_match.group(1)
                else:
                    book_data['publish_date'] = re.sub(r'발행일[:\s]*', '', date_text).strip()
            
            # Extract and download cover image - improved for CommBooks structure
            img_selectors = [
                'img[src*="/wp-content/uploads/"]',  # CommBooks specific upload path
                'img[alt*="표지"]',
                'img[alt*="cover"]',
                '.entry-content img',
                '.post-content img', 
                'article img',
                '.book-cover img',
                '.cover img',
                'img[src*="cover"]',
                '.product-image img',
                '.main-image img',
                '.content img'
            ]
            
            cover_found = False
            for selector in img_selectors:
                if cover_found:
                    break
                    
                img_elements = soup.select(selector)
                logger.debug(f"Found {len(img_elements)} images with selector: {selector}")
                
                for img_element in img_elements:
                    if img_element:
                        src = img_element.get('src')
                        data_src = img_element.get('data-src')  # lazy loading
                        
                        # Try both src and data-src
                        img_src = src or data_src
                        
                        if img_src and isinstance(img_src, str):
                            # Skip obvious non-cover images
                            skip_patterns = ['icon', 'logo', 'nav', 'menu', 'btn', 'arrow', 'social', 'footer']
                            if any(skip in img_src.lower() for skip in skip_patterns):
                                continue
                            
                            # Skip very small images by file path patterns
                            if any(size in img_src.lower() for size in ['-50x', '-30x', '-20x', 'thumb']):
                                continue
                            
                            # Check alt text for book cover indicators
                            alt_text = img_element.get('alt', '').lower()
                            if any(indicator in alt_text for indicator in ['표지', 'cover', book_data['title'].lower()[:10]]):
                                logger.info(f"Found potential cover image by alt text: {alt_text}")
                            
                            img_url = urljoin(book_url, img_src)
                            logger.debug(f"Attempting to download image: {img_url}")
                            
                            image_path = self.download_image(img_url, book_data['title'])
                            if image_path:
                                book_data['cover_image_path'] = image_path
                                logger.info(f"Successfully downloaded cover image: {image_path}")
                                cover_found = True
                                break
            
            if not cover_found:
                logger.warning(f"No cover image found for book: {book_data['title']}")
            
            # Validate and truncate data to fit database constraints
            book_data = self.validate_book_data(book_data)
            
            logger.info(f"Scraped book: {book_data['title']}")
            return book_data
            
        except Exception as e:
            logger.error(f"Error scraping book {book_url}: {str(e)}")
            return None
    
    def validate_book_data(self, book_data):
        """Validate and clean book data before saving to database"""
        # Truncate fields that have database length limits
        if book_data['title']:
            book_data['title'] = book_data['title'][:500]
        
        if book_data['author']:
            book_data['author'] = book_data['author'][:300]
        
        if book_data['publish_date']:
            book_data['publish_date'] = book_data['publish_date'][:200]
        
        if book_data['cover_image_path']:
            book_data['cover_image_path'] = book_data['cover_image_path'][:500]
        
        if book_data['book_url']:
            book_data['book_url'] = book_data['book_url'][:500]
        
        # Ensure we have a title at minimum
        if not book_data['title'] or book_data['title'].strip() == '':
            book_data['title'] = 'Unknown Title'
        
        # Check if any field contains mostly footer content and clear it
        fields_to_check = ['author', 'description', 'review_200', 'contents', 'book_preview', 'publish_date']
        for field in fields_to_check:
            if book_data[field] and self.is_footer_content(book_data[field]):
                book_data[field] = ''
                logger.warning(f"Cleared {field} field as it contained footer content")
        
        return book_data
    
    def is_footer_content(self, text):
        """Check if text is mostly footer/legal content"""
        if not text or len(text) < 20:
            return False
        
        footer_indicators = [
            '이용약관', '개인정보취급방침', 'commbooks@commbooks.com',
            '대표이사', '사업자등록번호', 'Copyright', '커뮤니케이션북스',
            '성북구', '페이스북컴북스', 'All Rights Reserved'
        ]
        
        footer_count = sum(1 for indicator in footer_indicators if indicator in text)
        return footer_count >= 2
    
    def format_contents_text(self, contents_text):
        """차례 텍스트의 포맷팅을 개선합니다."""
        if not contents_text:
            return ""
        
        lines = contents_text.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Remove page numbers at the end
            line = re.sub(r'\s*\d+\s*$', '', line)
            # Remove page numbers at the beginning  
            line = re.sub(r'^\s*\d+\s*', '', line)
            
            # Handle chapter/section numbering
            if re.match(r'^[0-9]+\s*장', line) or re.match(r'^제\s*[0-9]+\s*장', line):
                # Main chapters - add extra spacing
                if formatted_lines:
                    formatted_lines.append('')
                formatted_lines.append(line)
            elif re.match(r'^[0-9]+\.[0-9]+', line):
                # Sub-sections with numbering
                formatted_lines.append('  ' + line)
            elif line.startswith('-') or line.startswith('•'):
                # Bullet points
                formatted_lines.append('  ' + line)
            else:
                # Regular content
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    def download_image(self, img_url, book_title):
        """Download and save book cover image"""
        try:
            # Check if it's a valid image URL
            if not img_url or 'data:' in img_url or len(img_url) < 10:
                return None
            
            response = self.session.get(img_url, timeout=15)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if not any(img_type in content_type.lower() for img_type in ['image', 'jpeg', 'jpg', 'png', 'webp']):
                logger.warning(f"Not an image: {img_url} (content-type: {content_type})")
                return None
            
            # Check image size (avoid downloading tiny images)
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) < 1000:  # Less than 1KB
                logger.warning(f"Image too small: {img_url}")
                return None
            
            # Create safe filename from book title
            safe_title = re.sub(r'[^\w\s-]', '', book_title).strip()
            safe_title = re.sub(r'[-\s]+', '-', safe_title)
            safe_title = safe_title[:50]  # Limit length
            
            # Determine file extension
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                # Try to determine from URL
                url_ext = os.path.splitext(img_url)[1].lower()
                if url_ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    ext = url_ext
                else:
                    ext = '.jpg'  # Default
            
            timestamp = int(time.time())
            filename = f"{safe_title}_{timestamp}{ext}"
            filepath = os.path.join(self.images_dir, filename)
            
            # Save image and verify it's valid
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Verify the image can be opened (basic validation)
            try:
                with Image.open(filepath) as img:
                    # Check minimum dimensions
                    if img.width < 50 or img.height < 50:
                        os.remove(filepath)
                        logger.warning(f"Image too small after download: {img.width}x{img.height}")
                        return None
                    
                    logger.info(f"Downloaded image: {filepath} ({img.width}x{img.height})")
                    return f"images/covers/{filename}"  # Return relative path for templates
            except Exception as e:
                # Remove invalid image file
                if os.path.exists(filepath):
                    os.remove(filepath)
                logger.error(f"Invalid image downloaded from {img_url}: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"Error downloading image {img_url}: {str(e)}")
            return None
    
    def save_book_to_db(self, book_data):
        """Save book data to database"""
        try:
            # Check if book already exists
            existing_book = Book.query.filter_by(book_url=book_data['book_url']).first()
            if existing_book:
                logger.info(f"Book already exists: {book_data['title']}")
                return existing_book
            
            # Create new book record
            book = Book()
            book.title = book_data['title']
            book.author = book_data['author']
            book.description = book_data['description']
            book.review_200 = book_data['review_200']
            book.contents = book_data['contents']
            book.book_preview = book_data['book_preview']
            book.publish_date = book_data['publish_date']
            book.cover_image_path = book_data['cover_image_path']
            book.book_url = book_data['book_url']
            
            db.session.add(book)
            db.session.commit()
            
            logger.info(f"Saved book to database: {book_data['title']}")
            return book
            
        except Exception as e:
            logger.error(f"Error saving book to database: {str(e)}")
            db.session.rollback()
            return None
    
    def run_scraping_job(self, job_id):
        """Run a scraping job in background"""
        from app import app
        
        with app.app_context():
            job = ScrapingJob.query.get(job_id)
            if not job:
                return
            
            try:
                job.status = 'running'
                job.started_at = datetime.utcnow()
                db.session.commit()
                
                # Collect all book links first
                all_book_links = []
                for page_num in range(job.start_page, job.end_page + 1):
                    job.current_page = page_num
                    db.session.commit()
                    
                    book_links = self.get_page_book_links(page_num)
                    all_book_links.extend(book_links)
                    
                    # Rate limiting
                    time.sleep(1)
                
                job.total_books_found = len(all_book_links)
                db.session.commit()
                
                # Scrape each book
                for book_url in all_book_links:
                    try:
                        book_data = self.scrape_book_details(book_url)
                        if book_data:
                            saved_book = self.save_book_to_db(book_data)
                            if saved_book:
                                job.books_scraped += 1
                            else:
                                job.books_failed += 1
                        else:
                            job.books_failed += 1
                        
                        db.session.commit()
                        
                        # Rate limiting
                        time.sleep(2)
                        
                    except Exception as e:
                        logger.error(f"Error processing book {book_url}: {str(e)}")
                        job.books_failed += 1
                        db.session.commit()
                
                job.status = 'completed'
                job.completed_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Scraping job {job_id} completed successfully")
                
            except Exception as e:
                logger.error(f"Scraping job {job_id} failed: {str(e)}")
                job.status = 'failed'
                job.error_message = str(e)
                job.completed_at = datetime.utcnow()
                db.session.commit()

def start_scraping_job(start_page, end_page):
    """Start a new scraping job"""
    job = ScrapingJob()
    job.start_page = start_page
    job.end_page = end_page
    
    db.session.add(job)
    db.session.commit()
    
    # Start scraping in background thread
    scraper = CommBooksScraper()
    thread = threading.Thread(target=scraper.run_scraping_job, args=(job.id,))
    thread.daemon = True
    thread.start()
    
    return job
