document.addEventListener('DOMContentLoaded', function() {
    const labelFilters = document.querySelectorAll('.label-filter');
    const spaceItems = document.querySelectorAll('.space-item');
    const labelCounts = document.querySelectorAll('.label-count');
    
    // Initialize label counts
    function updateLabelCounts() {
        labelCounts.forEach(countElement => {
            const labelId = countElement.getAttribute('data-label-id');
            const count = document.querySelectorAll(`.space-item[data-label-id="${labelId}"]`).length;
            countElement.textContent = count;
        });
        
        // Update count for spaces without labels
        const noLabelCount = document.querySelectorAll('.space-item[data-label-id="none"]').length;
        const allCount = spaceItems.length;
        
        // Update "All Spaces" count
        const allButton = document.querySelector('.label-filter[data-label="all"]');
        if (allButton) {
            allButton.textContent = `All Spaces (${allCount})`;
        }
    }
    
    // Filter spaces by label
    function filterSpacesByLabel(selectedLabelId) {
        spaceItems.forEach(spaceItem => {
            const spaceLabelId = spaceItem.getAttribute('data-label-id');
            
            if (selectedLabelId === 'all') {
                spaceItem.style.display = 'block';
            } else if (selectedLabelId === 'none' && spaceLabelId === 'none') {
                spaceItem.style.display = 'block';
            } else if (spaceLabelId === selectedLabelId) {
                spaceItem.style.display = 'block';
            } else {
                spaceItem.style.display = 'none';
            }
        });
        
        // Update active button state
        labelFilters.forEach(button => {
            button.classList.remove('btn-primary');
            button.classList.add('btn-outline-secondary');
        });
        
        const activeButton = document.querySelector(`.label-filter[data-label="${selectedLabelId}"]`);
        if (activeButton) {
            activeButton.classList.remove('btn-outline-secondary');
            activeButton.classList.add('btn-primary');
        }
    }
    
    // Add click event listeners to filter buttons
    labelFilters.forEach(button => {
        button.addEventListener('click', function() {
            const labelId = this.getAttribute('data-label');
            filterSpacesByLabel(labelId);
        });
    });
    
    // Initialize counts and set "All Spaces" as active by default
    updateLabelCounts();
    filterSpacesByLabel('all');
});