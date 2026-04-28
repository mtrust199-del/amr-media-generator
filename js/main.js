// Amr Cloud Control - Main JavaScript

// Navigation helper
function navigateTo(page) {
    window.location.href = page;
}

// Check if local backend is reachable
function checkLocalBackend() {
    fetch('http://127.0.0.1:5000/health', { mode: 'no-cors' })
        .then(() => {
            console.log('Local backend is reachable');
            document.body.classList.add('backend-online');
        })
        .catch(() => {
            console.log('Local backend is offline');
            document.body.classList.add('backend-offline');
        });
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
    console.log('Amr Cloud Control loaded');

    // Optional: check backend status
    // checkLocalBackend();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { navigateTo, checkLocalBackend };
}
