/**
 * Custom JavaScript for SEO Audit Tool
 */

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('SEO Audit Tool loaded successfully');

    // Initialize tooltips
    initTooltips();

    // Initialize form validation
    initFormValidation();

    // Initialize animations
    initAnimations();

    // Initialize progress bars
    initProgressBars();
});

/**
 * Initialize Bootstrap tooltips
 */
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');

    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            } else {
                // Show loading state
                showLoadingState(form);
            }
            form.classList.add('was-validated');
        }, false);
    });
}

/**
 * Show loading state for form submission
 */
function showLoadingState(form) {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        const originalText = submitBtn.innerHTML;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Анализ...';
        submitBtn.disabled = true;

        // Re-enable button after 30 seconds (timeout)
        setTimeout(() => {
            submitBtn.innerHTML = originalText;
            submitBtn.disabled = false;
        }, 30000);
    }
}

/**
 * Initialize animations
 */
function initAnimations() {
    // Animate cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe all cards
    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
}

/**
 * Initialize progress bars with animation
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');

    progressBars.forEach(bar => {
        const targetWidth = bar.style.width;
        bar.style.width = '0%';

        setTimeout(() => {
            bar.style.width = targetWidth;
            bar.classList.add('progress-animated');
        }, 500);
    });
}

/**
 * Show notification/alert
 */
function showNotification(message, type = 'info') {
    const alertClass = `alert-${type}`;
    const alertHtml = `
        <div class="alert ${alertClass} alert-dismissible alert-fade fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    // Find or create alerts container
    let alertsContainer = document.querySelector('.alerts-container');
    if (!alertsContainer) {
        alertsContainer = document.createElement('div');
        alertsContainer.className = 'alerts-container position-fixed top-0 end-0 p-3';
        alertsContainer.style.zIndex = '9999';
        document.body.appendChild(alertsContainer);
    }

    alertsContainer.insertAdjacentHTML('beforeend', alertHtml);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const alert = alertsContainer.lastElementChild;
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showNotification('Скопировано в буфер обмена!', 'success');
        }).catch(err => {
            console.error('Failed to copy: ', err);
            fallbackCopyTextToClipboard(text);
        });
    } else {
        fallbackCopyTextToClipboard(text);
    }
}

/**
 * Fallback copy function for older browsers
 */
function fallbackCopyTextToClipboard(text) {
    const textArea = document.createElement("textarea");
    textArea.value = text;
    textArea.style.position = "fixed";
    textArea.style.left = "-999999px";
    textArea.style.top = "-999999px";
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showNotification('Скопировано в буфер обмена!', 'success');
        } else {
            showNotification('Не удалось скопировать', 'error');
        }
    } catch (err) {
        showNotification('Не удалось скопировать', 'error');
    }

    document.body.removeChild(textArea);
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Get URL parameters
 */
function getUrlParameter(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    const regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    const results = regex.exec(location.search);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
}

/**
 * Update URL without page reload
 */
function updateUrlParameter(key, value) {
    const url = new URL(window.location);
    url.searchParams.set(key, value);
    window.history.pushState({}, '', url);
}

/**
 * Check if element is in viewport
 */
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Smooth scroll to element
 */
function smoothScrollTo(elementId) {
    const element = document.getElementById(elementId);
    if (element) {
        element.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

/**
 * Generate random ID
 */
function generateId() {
    return 'id_' + Math.random().toString(36).substr(2, 9);
}

/**
 * Validate URL
 */
function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

// Export functions to global scope if needed
window.SEOAuditTool = {
    showNotification,
    copyToClipboard,
    formatNumber,
    smoothScrollTo,
    isValidUrl
};
