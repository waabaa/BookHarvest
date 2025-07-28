// Dashboard JavaScript for CommBooks Scraper

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    const tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-refresh statistics
    function updateStats() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                // Update statistics cards if they exist
                const statsCards = document.querySelectorAll('.card-title');
                if (statsCards.length >= 4) {
                    statsCards[0].textContent = data.total_books;
                    statsCards[1].textContent = data.completed_jobs;
                    statsCards[2].textContent = data.running_jobs;
                    statsCards[3].textContent = data.failed_jobs;
                }
            })
            .catch(error => {
                console.error('Error updating stats:', error);
            });
    }

    // Form validation
    const scrapingForm = document.querySelector('form[action*="start_scraping"]');
    if (scrapingForm) {
        scrapingForm.addEventListener('submit', function(e) {
            const startPage = parseInt(document.getElementById('start_page').value);
            const endPage = parseInt(document.getElementById('end_page').value);
            
            if (startPage < 1 || endPage < startPage || endPage > 100) {
                e.preventDefault();
                alert('Please enter a valid page range (1-100).');
                return false;
            }
            
            if (endPage - startPage > 50) {
                if (!confirm('You are about to scrape more than 50 pages. This may take a very long time. Continue?')) {
                    e.preventDefault();
                    return false;
                }
            }
            
            // Show loading spinner
            showLoadingSpinner();
        });
    }

    // Show loading spinner
    function showLoadingSpinner() {
        const spinner = document.createElement('div');
        spinner.className = 'spinner-overlay';
        spinner.innerHTML = `
            <div class="text-center">
                <div class="spinner-border spinner-border-custom" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-3 text-light">Starting scraping job...</p>
            </div>
        `;
        document.body.appendChild(spinner);
        
        // Remove spinner after 3 seconds
        setTimeout(() => {
            spinner.remove();
        }, 3000);
    }

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Live search for books (if on books page)
    const searchInput = document.getElementById('book-search');
    if (searchInput) {
        let searchTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                filterBooks(this.value);
            }, 300);
        });
    }

    function filterBooks(searchTerm) {
        const bookCards = document.querySelectorAll('.book-card');
        const searchLower = searchTerm.toLowerCase();
        
        bookCards.forEach(card => {
            const title = card.querySelector('.card-title').textContent.toLowerCase();
            const author = card.querySelector('.text-muted')?.textContent.toLowerCase() || '';
            const description = card.querySelector('.card-text')?.textContent.toLowerCase() || '';
            
            if (title.includes(searchLower) || author.includes(searchLower) || description.includes(searchLower)) {
                card.closest('.col-md-6, .col-lg-4').style.display = 'block';
            } else {
                card.closest('.col-md-6, .col-lg-4').style.display = 'none';
            }
        });
    }

    // Image lazy loading
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                imageObserver.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));

    // Progress animation
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 100);
    });

    // Update stats every 30 seconds
    setInterval(updateStats, 30000);
});

// Utility functions
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatDuration(startDate, endDate) {
    const start = new Date(startDate);
    const end = new Date(endDate);
    const duration = end - start;
    
    const hours = Math.floor(duration / (1000 * 60 * 60));
    const minutes = Math.floor((duration % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((duration % (1000 * 60)) / 1000);
    
    if (hours > 0) {
        return `${hours}h ${minutes}m ${seconds}s`;
    } else if (minutes > 0) {
        return `${minutes}m ${seconds}s`;
    } else {
        return `${seconds}s`;
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Handle network errors
window.addEventListener('offline', function() {
    const toast = document.createElement('div');
    toast.className = 'toast-container position-fixed top-0 end-0 p-3';
    toast.innerHTML = `
        <div class="toast show" role="alert">
            <div class="toast-header">
                <strong class="me-auto">Connection Error</strong>
                <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
            </div>
            <div class="toast-body">
                You are currently offline. Some features may not work properly.
            </div>
        </div>
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
});
