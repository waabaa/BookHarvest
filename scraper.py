import requests
from bs4 import BeautifulSoup
import time
import os
import logging
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
            
            # Extract title
            title_element = soup.find('h1') or soup.find('title')
            if title_element:
                book_data['title'] = title_element.get_text(strip=True)
            
            # Extract author - look for common patterns
            author_selectors = [
                'span:contains("지은이")',
                '.author',
                '[class*="author"]',
                'p:contains("지은이")'
            ]
            
            for selector in author_selectors:
                try:
                    if ':contains(' in selector:
                        # Handle contains pseudo-selector manually
                        elements = soup.find_all(string=lambda text: text and "지은이" in str(text))
                        if elements:
                            parent = elements[0].parent
                            if parent:
                                book_data['author'] = parent.get_text(strip=True).replace('지은이', '').strip()
                                break
                    else:
                        author_element = soup.select_one(selector)
                        if author_element:
                            book_data['author'] = author_element.get_text(strip=True)
                            break
                except:
                    continue
            
            # Extract description/introduction
            desc_selectors = [
                '.book-intro',
                '.description',
                '[class*="intro"]',
                '[class*="description"]'
            ]
            
            for selector in desc_selectors:
                desc_element = soup.select_one(selector)
                if desc_element:
                    book_data['description'] = desc_element.get_text(strip=True)
                    break
            
            # Extract 200자평
            review_selectors = [
                'div:contains("200자평")',
                '.review-200',
                '[class*="review"]'
            ]
            
            for selector in review_selectors:
                try:
                    if ':contains(' in selector:
                        elements = soup.find_all(string=lambda text: text and "200자평" in str(text))
                        if elements:
                            parent = elements[0].parent
                            if parent:
                                book_data['review_200'] = parent.get_text(strip=True)
                                break
                    else:
                        review_element = soup.select_one(selector)
                        if review_element:
                            book_data['review_200'] = review_element.get_text(strip=True)
                            break
                except:
                    continue
            
            # Extract contents (차례)
            contents_selectors = [
                'div:contains("차례")',
                '.contents',
                '.table-of-contents'
            ]
            
            for selector in contents_selectors:
                try:
                    if ':contains(' in selector:
                        elements = soup.find_all(string=lambda text: text and "차례" in str(text))
                        if elements:
                            parent = elements[0].parent
                            if parent:
                                book_data['contents'] = parent.get_text(strip=True)
                                break
                    else:
                        contents_element = soup.select_one(selector)
                        if contents_element:
                            book_data['contents'] = contents_element.get_text(strip=True)
                            break
                except:
                    continue
            
            # Extract book preview (책속으로)
            preview_selectors = [
                'div:contains("책속으로")',
                '.book-preview',
                '[class*="preview"]'
            ]
            
            for selector in preview_selectors:
                try:
                    if ':contains(' in selector:
                        elements = soup.find_all(string=lambda text: text and "책속으로" in str(text))
                        if elements:
                            parent = elements[0].parent
                            if parent:
                                book_data['book_preview'] = parent.get_text(strip=True)
                                break
                    else:
                        preview_element = soup.select_one(selector)
                        if preview_element:
                            book_data['book_preview'] = preview_element.get_text(strip=True)
                            break
                except:
                    continue
            
            # Extract publish date
            date_selectors = [
                'span:contains("발행일")',
                '.publish-date',
                '[class*="date"]'
            ]
            
            for selector in date_selectors:
                try:
                    if ':contains(' in selector:
                        elements = soup.find_all(string=lambda text: text and "발행일" in str(text))
                        if elements:
                            parent = elements[0].parent
                            if parent:
                                book_data['publish_date'] = parent.get_text(strip=True).replace('발행일', '').strip()
                                break
                    else:
                        date_element = soup.select_one(selector)
                        if date_element:
                            book_data['publish_date'] = date_element.get_text(strip=True)
                            break
                except:
                    continue
            
            # Extract and download cover image
            img_selectors = [
                '.book-cover img',
                '.cover img',
                'img[alt*="표지"]',
                'img[src*="cover"]',
                'img'
            ]
            
            for selector in img_selectors:
                img_element = soup.select_one(selector)
                if img_element:
                    src = img_element.get('src')
                    if src and isinstance(src, str):
                        img_url = urljoin(book_url, src)
                        image_path = self.download_image(img_url, book_data['title'])
                        if image_path:
                            book_data['cover_image_path'] = image_path
                            break
            
            return book_data
            
        except Exception as e:
            logger.error(f"Error scraping book {book_url}: {str(e)}")
            return None
    
    def download_image(self, img_url, book_title):
        """Download and save book cover image"""
        try:
            response = self.session.get(img_url, timeout=10)
            response.raise_for_status()
            
            # Create filename from book title
            safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            safe_title = safe_title[:50]  # Limit length
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # Default
            
            filename = f"{safe_title}_{int(time.time())}{ext}"
            filepath = os.path.join(self.images_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Downloaded image: {filepath}")
            return filepath
            
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
