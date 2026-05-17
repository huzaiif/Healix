/* Healix — Global JS utilities */

// Theme Toggle Logic
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtns = document.querySelectorAll('.theme-toggle-btn');
    const root = document.documentElement;
    
    // Set initial icon based on current theme
    const currentTheme = root.getAttribute('data-theme') || 'light';
    updateToggleIcons(currentTheme);

    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            let theme = root.getAttribute('data-theme');
            let newTheme = theme === 'dark' ? 'light' : 'dark';
            
            if (newTheme === 'dark') {
                root.setAttribute('data-theme', 'dark');
            } else {
                root.removeAttribute('data-theme');
            }
            localStorage.setItem('theme', newTheme);
            updateToggleIcons(newTheme);
        });
    });

    function updateToggleIcons(theme) {
        toggleBtns.forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) {
                if (theme === 'dark') {
                    icon.className = 'fas fa-sun';
                } else {
                    icon.className = 'fas fa-moon';
                }
            }
        });
    }
});

// Auto-dismiss flash alerts after 5s
document.addEventListener('DOMContentLoaded', () => {
    const alerts = document.querySelectorAll('.flash-messages .alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            alert.style.transform = 'translateX(20px)';
            alert.style.transition = 'all 0.4s ease';
            setTimeout(() => alert.remove(), 400);
        }, 5000);
    });
});
