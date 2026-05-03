/**
 * BTP Algeria - Core Frontend Logic
 */

// Formatage montants DZD
function formatDZD(amount) {
    return new Intl.NumberFormat('fr-DZ', {
        style: 'currency',
        currency: 'DZD',
        minimumFractionDigits: 2
    }).format(amount);
}

// Toast Notifications
const showToast = (message, type = 'success') => {
    // Implementation normally uses Bootstrap Toast or a library like Toastr
    console.log(`[${type.toUpperCase()}] ${message}`);
};

// Confirmation Modals
function confirmAction(title, message, callback) {
    // Trigger a custom modal or standard confirm
    if (confirm(`${title}\n\n${message}`)) {
        callback();
    }
}

// Auto-refresh Dashboard (5 minutes)
if (window.location.pathname.includes('/dashboard/')) {
    setInterval(() => {
        console.log("Auto-refreshing dashboard data...");
        window.location.reload();
    }, 300000); // 300,000 ms = 5 min
}

// Session Timeout Warning (2 minutes before expiration)
// This is a simplified version; real implementation would check session cookie/expiry
let sessionTimeout;
function resetSessionTimer() {
    clearTimeout(sessionTimeout);
    sessionTimeout = setTimeout(() => {
        alert("Attention : Votre session va expirer dans 2 minutes. Veuillez sauvegarder votre travail.");
    }, (settings.SESSION_COOKIE_AGE - 120) * 1000); 
}

// Initialize tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });
});
