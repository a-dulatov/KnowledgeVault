document.addEventListener('DOMContentLoaded', function() {
    // Handle tag filtering on article pages
    const tagButtons = document.querySelectorAll('.tag-button');
    
    if (tagButtons) {
        tagButtons.forEach(button => {
            button.addEventListener('click', function() {
                const tag = this.dataset.tag;
                window.location.href = `/search?q=${encodeURIComponent(tag)}`;
            });
        });
    }
    
    // Handle copy code button for code blocks
    const copyButtons = document.querySelectorAll('.copy-code-button');
    
    if (copyButtons) {
        copyButtons.forEach(button => {
            button.addEventListener('click', function() {
                const codeBlock = this.parentElement.querySelector('code');
                const code = codeBlock.textContent;
                
                // Copy to clipboard
                navigator.clipboard.writeText(code).then(() => {
                    // Change button text temporarily
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    
                    // Reset button text after 2 seconds
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Could not copy text: ', err);
                });
            });
        });
    }
    
    // Add copy buttons to all code blocks
    document.querySelectorAll('pre').forEach(block => {
        if (!block.querySelector('.copy-code-button')) {
            const button = document.createElement('button');
            button.className = 'copy-code-button btn btn-sm btn-outline-secondary';
            button.textContent = 'Copy';
            
            // Add the button to the code block
            block.style.position = 'relative';
            button.style.position = 'absolute';
            button.style.top = '5px';
            button.style.right = '5px';
            
            block.appendChild(button);
            
            // Add click event listener
            button.addEventListener('click', function() {
                const code = block.querySelector('code').textContent;
                
                navigator.clipboard.writeText(code).then(() => {
                    const originalText = this.textContent;
                    this.textContent = 'Copied!';
                    
                    setTimeout(() => {
                        this.textContent = originalText;
                    }, 2000);
                }).catch(err => {
                    console.error('Could not copy text: ', err);
                });
            });
        }
    });
    
    // Handle related articles section
    const relatedArticlesContainer = document.getElementById('relatedArticles');
    
    if (relatedArticlesContainer && relatedArticlesContainer.children.length === 0) {
        relatedArticlesContainer.parentElement.style.display = 'none';
    }
});
