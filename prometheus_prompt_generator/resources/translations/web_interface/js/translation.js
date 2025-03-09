/**
 * Prometheus AI Prompt Generator - Translation Portal
 * JavaScript functionality for the translation web interface
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize translation interface
    initTranslationInterface();
    
    // Set up event listeners
    setupEventListeners();
});

/**
 * Initialize the translation interface
 */
function initTranslationInterface() {
    // Hide translation interface initially (until language is selected)
    const translationInterface = document.querySelector('.row:has(.card-header:contains("Translating to"))');
    if (translationInterface) {
        translationInterface.style.display = 'none';
    }
    
    // Load translation statistics
    loadTranslationStats();
}

/**
 * Load translation statistics from the server
 */
function loadTranslationStats() {
    // In a real implementation, this would be an API call
    // For this mockup, we'll use static data
    
    const stats = {
        total_strings: 1245,
        languages: [
            { 
                code: 'de', 
                name: 'German', 
                translated: 808, 
                needs_review: 54,
                progress: 65
            },
            { 
                code: 'es', 
                name: 'Spanish', 
                translated: 996, 
                needs_review: 32,
                progress: 80
            },
            { 
                code: 'fr', 
                name: 'French', 
                translated: 934, 
                needs_review: 45,
                progress: 75
            }
        ]
    };
    
    // Update the UI with statistics
    updateStatistics(stats);
}

/**
 * Update the UI with translation statistics
 */
function updateStatistics(stats) {
    // Update total strings count
    const totalStringsEl = document.querySelector('p:contains("Total strings:")');
    if (totalStringsEl) {
        totalStringsEl.innerHTML = `<strong>Total strings:</strong> ${stats.total_strings}`;
    }
    
    // Update progress bars
    stats.languages.forEach(lang => {
        const progressBar = document.querySelector(`.progress-bar:contains("${lang.name}")`);
        if (progressBar) {
            progressBar.style.width = `${lang.progress}%`;
            progressBar.textContent = `${lang.name} (${lang.progress}%)`;
        }
        
        // Update language cards
        const cardText = document.querySelector(`.card-title:contains("${lang.name}")`).closest('.card').querySelector('.card-text');
        if (cardText) {
            cardText.textContent = `${lang.translated}/${stats.total_strings} strings translated`;
        }
    });
}

/**
 * Set up event listeners for the UI
 */
function setupEventListeners() {
    // Language selection
    const languageCards = document.querySelectorAll('.language-card');
    languageCards.forEach(card => {
        card.addEventListener('click', function() {
            const languageName = this.querySelector('.card-title').textContent;
            selectLanguage(languageName);
        });
    });
    
    // Continue translation buttons
    const continueButtons = document.querySelectorAll('.language-card .btn-primary');
    continueButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.stopPropagation(); // Prevent card click
            const languageName = this.closest('.card').querySelector('.card-title').textContent;
            selectLanguage(languageName);
        });
    });
    
    // Filter buttons
    const filterButtons = document.querySelectorAll('.btn-group[role="group"] .btn');
    filterButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Apply filter
            const filter = this.textContent.trim().toLowerCase();
            applyFilter(filter);
        });
    });
    
    // Save buttons
    const saveButtons = document.querySelectorAll('.btn-primary:contains("Save")');
    saveButtons.forEach(button => {
        button.addEventListener('click', function() {
            saveTranslation(this.closest('.translation-item'));
        });
    });
    
    // Save & Next buttons
    const saveNextButtons = document.querySelectorAll('.btn-success:contains("Save & Next")');
    saveNextButtons.forEach(button => {
        button.addEventListener('click', function() {
            const item = this.closest('.translation-item');
            saveTranslation(item);
            goToNextItem(item);
        });
    });
    
    // Search functionality
    const searchButton = document.querySelector('.input-group .btn');
    if (searchButton) {
        searchButton.addEventListener('click', function() {
            const searchInput = this.previousElementSibling;
            searchStrings(searchInput.value);
        });
        
        // Also trigger search on Enter key
        const searchInput = searchButton.previousElementSibling;
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchStrings(this.value);
            }
        });
    }
    
    // Suggest translation buttons
    const suggestButtons = document.querySelectorAll('.btn-outline-secondary:contains("Suggest Translation")');
    suggestButtons.forEach(button => {
        button.addEventListener('click', function() {
            suggestTranslation(this.closest('.translation-item'));
        });
    });
    
    // Discuss buttons
    const discussButtons = document.querySelectorAll('.btn-outline-secondary:contains("Discuss")');
    discussButtons.forEach(button => {
        button.addEventListener('click', function() {
            openDiscussion(this.closest('.translation-item'));
        });
    });
    
    // Create Pull Request button
    const prButton = document.querySelector('.btn-primary:contains("Create Pull Request")');
    if (prButton) {
        prButton.addEventListener('click', createPullRequest);
    }
    
    // Download TS File button
    const downloadButton = document.querySelector('.btn-outline-primary:contains("Download TS File")');
    if (downloadButton) {
        downloadButton.addEventListener('click', downloadTsFile);
    }
}

/**
 * Select a language for translation
 */
function selectLanguage(languageName) {
    // Extract language code
    const langCode = languageName.match(/\(([^)]+)\)/)?.[1] || 'en';
    
    // Update header
    const header = document.querySelector('.card-header h5');
    if (header) {
        header.textContent = `Translating to ${languageName}`;
    }
    
    // Show translation interface
    const translationInterface = document.querySelector('.row:has(.card-header:contains("Translating to"))');
    if (translationInterface) {
        translationInterface.style.display = 'flex';
    }
    
    // Scroll to translation interface
    translationInterface.scrollIntoView({ behavior: 'smooth' });
    
    // Load strings for selected language
    loadStrings(langCode);
}

/**
 * Load translation strings for a language
 */
function loadStrings(langCode) {
    // In a real implementation, this would be an API call
    // For this mockup, we'll use the existing UI
    console.log(`Loading strings for ${langCode}...`);
    
    // You would replace this with actual data loading code
    // For now, we just show a loading indicator
    const listGroup = document.querySelector('.list-group');
    if (listGroup) {
        listGroup.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"></div><p class="mt-2">Loading translation strings...</p></div>';
        
        // Simulate loading delay
        setTimeout(() => {
            // Restore the original content (in a real app, you'd populate with actual data)
            listGroup.innerHTML = document.querySelector('.list-group').innerHTML;
            
            // Re-attach event listeners (since we replaced the content)
            setupEventListeners();
        }, 1000);
    }
}

/**
 * Apply filter to translation items
 */
function applyFilter(filter) {
    const items = document.querySelectorAll('.translation-item');
    
    items.forEach(item => {
        if (filter === 'all') {
            item.style.display = 'block';
        } else if (filter === 'untranslated' && item.classList.contains('untranslated')) {
            item.style.display = 'block';
        } else if (filter === 'needs review' && item.classList.contains('needs-review')) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Search translation strings
 */
function searchStrings(query) {
    if (!query) {
        // Show all items if query is empty
        applyFilter('all');
        return;
    }
    
    query = query.toLowerCase();
    const items = document.querySelectorAll('.translation-item');
    
    items.forEach(item => {
        const sourceText = item.querySelector('.bg-light').textContent.toLowerCase();
        const contextText = item.querySelector('.badge').textContent.toLowerCase();
        const idText = item.querySelector('.text-muted').textContent.toLowerCase();
        
        if (sourceText.includes(query) || contextText.includes(query) || idText.includes(query)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

/**
 * Save a translation
 */
function saveTranslation(item) {
    const sourceText = item.querySelector('.bg-light').textContent;
    const translationText = item.querySelector('textarea').value;
    const context = item.querySelector('.badge').textContent;
    const id = item.querySelector('.text-muted').textContent.split(': ')[1];
    
    console.log('Saving translation:', {
        id,
        context,
        source: sourceText,
        translation: translationText
    });
    
    // In a real implementation, this would be an API call
    // For this mockup, we'll just update the UI
    
    // Mark as translated
    item.classList.remove('untranslated', 'needs-review');
    item.classList.add('translated');
    
    // Show success message
    showNotification('Translation saved successfully', 'success');
}

/**
 * Go to the next translation item
 */
function goToNextItem(currentItem) {
    const nextItem = currentItem.nextElementSibling;
    if (nextItem && nextItem.classList.contains('translation-item')) {
        // Scroll to next item
        nextItem.scrollIntoView({ behavior: 'smooth' });
        
        // Focus the textarea
        const textarea = nextItem.querySelector('textarea');
        if (textarea) {
            textarea.focus();
        }
    } else {
        // No next item, go to next page
        const nextPageLink = document.querySelector('.page-item.active + .page-item .page-link');
        if (nextPageLink) {
            nextPageLink.click();
        }
    }
}

/**
 * Suggest a translation using machine translation
 */
function suggestTranslation(item) {
    const sourceText = item.querySelector('.bg-light').textContent;
    const textarea = item.querySelector('textarea');
    
    // In a real implementation, this would call a machine translation API
    // For this mockup, we'll use a simple placeholder
    
    // Show loading indicator
    textarea.disabled = true;
    textarea.value = 'Generating suggestion...';
    
    // Simulate API call delay
    setTimeout(() => {
        // Provide suggested translation
        if (sourceText === 'Prometheus AI Prompt Generator') {
            textarea.value = 'Prometheus KI Prompt-Generator';
        } else if (sourceText === '&Save') {
            textarea.value = '&Speichern';
        } else {
            // Generate a placeholder translation
            textarea.value = sourceText + ' (translated)';
        }
        
        textarea.disabled = false;
        textarea.focus();
        
        // Show success message
        showNotification('Translation suggested', 'info');
    }, 1000);
}

/**
 * Open discussion for a translation
 */
function openDiscussion(item) {
    const sourceText = item.querySelector('.bg-light').textContent;
    const id = item.querySelector('.text-muted').textContent.split(': ')[1];
    
    // In a real implementation, this would open a discussion panel or modal
    // For this mockup, we'll just show an alert
    alert(`Discussion for "${sourceText}" (${id}) would open here.`);
}

/**
 * Create a pull request with translation changes
 */
function createPullRequest() {
    // In a real implementation, this would prepare and submit a pull request
    // For this mockup, we'll just show a confirmation dialog
    
    if (confirm('Create a pull request with your translation changes?')) {
        // Show loading indicator
        const prButton = document.querySelector('.btn-primary:contains("Create Pull Request")');
        const originalText = prButton.innerHTML;
        prButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Creating...';
        prButton.disabled = true;
        
        // Simulate API call delay
        setTimeout(() => {
            // Show success message
            showNotification('Pull request created successfully: #1234', 'success');
            
            // Restore button
            prButton.innerHTML = originalText;
            prButton.disabled = false;
        }, 2000);
    }
}

/**
 * Download the TS file for a language
 */
function downloadTsFile() {
    // In a real implementation, this would download the actual TS file
    // For this mockup, we'll just show a notification
    
    showNotification('Downloading TS file...', 'info');
    
    // Simulate download delay
    setTimeout(() => {
        // Show success message
        showNotification('TS file downloaded successfully', 'success');
    }, 1000);
}

/**
 * Show a notification message
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} notification`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '1000';
    notification.style.opacity = '0';
    notification.style.transition = 'opacity 0.3s ease-in-out';
    
    // Add to document
    document.body.appendChild(notification);
    
    // Fade in
    setTimeout(() => {
        notification.style.opacity = '1';
    }, 10);
    
    // Fade out and remove after delay
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
} 