// Favorites functionality
document.addEventListener('DOMContentLoaded', function() {
    // Get CSRF token
    function getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Handle favorite toggle
    function handleFavoriteToggle(button) {
        const articleId = button.dataset.articleId;
        const isFavorited = button.dataset.favorited === 'true';
        
        // Disable button during request
        button.disabled = true;
        
        fetch(`/article/${articleId}/toggle-favorite/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateFavoriteButton(button, data.is_favorited);
                
                // Special handling for favorites page - remove unfavorited articles
                if (!data.is_favorited && window.location.pathname === '/my-favorites/') {
                    const articleCard = button.closest('.article-card');
                    if (articleCard) {
                        articleCard.style.opacity = '0.5';
                        setTimeout(() => {
                            articleCard.remove();
                            checkEmptyFavorites();
                        }, 300);
                    }
                }
            } else {
                console.error('Error toggling favorite:', data.error);
                // Show user-friendly error message
                showNotification('Error updating favorite status. Please try again.', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error updating favorite status. Please try again.', 'error');
        })
        .finally(() => {
            button.disabled = false;
        });
    }

    // Update favorite button appearance
    function updateFavoriteButton(button, isFavorited) {
        const icon = button.querySelector('i');
        
        if (isFavorited) {
            icon.className = 'fas fa-heart text-danger';
            button.title = 'Remove from favorites';
            button.dataset.favorited = 'true';
        } else {
            icon.className = 'far fa-heart text-muted';
            button.title = 'Add to favorites';
            button.dataset.favorited = 'false';
        }
    }

    // Check if favorites page is empty and show message
    function checkEmptyFavorites() {
        const articlesContainer = document.getElementById('articles-container');
        if (articlesContainer && document.querySelectorAll('.article-card').length === 0) {
            articlesContainer.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-heart fa-3x text-muted mb-3"></i>
                    <h3 class="text-muted">No Favorites Yet</h3>
                    <p class="text-muted">Start adding articles to your favorites by clicking the heart icon on any article.</p>
                    <a href="/" class="btn btn-primary">Browse Articles</a>
                </div>
            `;
        }
    }

    // Show notification to user
    function showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'error' ? 'danger' : 'success'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; max-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }

    // Add event listeners to all favorite buttons
    function initializeFavoriteButtons() {
        const favoriteButtons = document.querySelectorAll('.favorite-btn');
        
        favoriteButtons.forEach(button => {
            // Remove any existing listeners
            button.removeEventListener('click', handleFavoriteToggle);
            
            // Add new listener
            button.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                handleFavoriteToggle(this);
            });
        });
    }

    // Initialize on page load
    initializeFavoriteButtons();
    
    // Re-initialize when new content is loaded dynamically
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(function(node) {
                    if (node.nodeType === 1) { // Element node
                        const newFavoriteButtons = node.querySelectorAll ? node.querySelectorAll('.favorite-btn') : [];
                        if (newFavoriteButtons.length > 0) {
                            initializeFavoriteButtons();
                        }
                    }
                });
            }
        });
    });
    
    observer.observe(document.body, {
        childList: true,
        subtree: true
    });
});