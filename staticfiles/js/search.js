document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchInput');
    const searchResults = document.getElementById('searchResults');
    const searchForm = document.getElementById('searchForm');
    
    // Add event listener for real-time search suggestions
    if (searchInput && searchResults) {
        let searchTimeout;
        
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            
            // Clear previous timeout
            clearTimeout(searchTimeout);
            
            // Don't search for empty strings or short queries
            if (query.length < 2) {
                searchResults.innerHTML = '';
                searchResults.style.display = 'none';
                return;
            }
            
            // Set a timeout to avoid making too many requests
            searchTimeout = setTimeout(() => {
                fetch(`/api/search?q=${encodeURIComponent(query)}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear previous results
                        searchResults.innerHTML = '';
                        
                        if (data.length === 0) {
                            searchResults.style.display = 'none';
                            return;
                        }
                        
                        // Display results
                        searchResults.style.display = 'block';
                        
                        // Take only first 5 results
                        const topResults = data.slice(0, 5);
                        
                        topResults.forEach(article => {
                            const resultItem = document.createElement('div');
                            resultItem.className = 'search-result-item';
                            resultItem.innerHTML = `
                                <a href="/article/${article.id}" class="d-block p-2 text-decoration-none">
                                    <div class="fw-bold">${article.title}</div>
                                    <div class="small text-muted">${article.summary}</div>
                                </a>
                            `;
                            searchResults.appendChild(resultItem);
                        });
                        
                        // Add "View all results" link if there are more results
                        if (data.length > 5) {
                            const viewAll = document.createElement('div');
                            viewAll.className = 'search-view-all p-2 text-center bg-light';
                            viewAll.innerHTML = `
                                <a href="/search?q=${encodeURIComponent(query)}" class="text-decoration-none">
                                    View all ${data.length} results
                                </a>
                            `;
                            searchResults.appendChild(viewAll);
                        }
                    })
                    .catch(error => {
                        console.error('Error performing search:', error);
                    });
            }, 300);
        });
        
        // Close search results when clicking outside
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
                searchResults.style.display = 'none';
            }
        });
    }
    
    // Handle search form submission
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const query = searchInput.value.trim();
            if (!query) {
                e.preventDefault();
                return;
            }
            
            // Let the form submit normally to /search?q=...
        });
    }
});
