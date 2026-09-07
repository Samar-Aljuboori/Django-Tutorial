document.addEventListener("DOMContentLoaded", function() {
    const toggleBtn = document.getElementById('darkModeToggle');
    const themeLabel = document.getElementById('themeLabel');
    const themeIcon = document.getElementById('themeIcon');
    const accentColorPicker = document.getElementById('accentColorPicker');

    const currentTheme = localStorage.getItem('theme');
    const savedAccentColor = localStorage.getItem('accentColor');

    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeLabel) themeLabel.textContent = 'Light';
        if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
    }

    if (savedAccentColor) {
        document.documentElement.style.setProperty('--primary-color', savedAccentColor);
        if (accentColorPicker) accentColorPicker.value = savedAccentColor;
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            let theme = 'light';
            if (document.documentElement.getAttribute('data-theme') === 'dark') {
                document.documentElement.removeAttribute('data-theme');
                theme = 'light';
                if (themeLabel) themeLabel.textContent = 'Dark';
                if (themeIcon) themeIcon.className = 'fa-solid fa-moon';
            } else {
                document.documentElement.setAttribute('data-theme', 'dark');
                theme = 'dark';
                if (themeLabel) themeLabel.textContent = 'Light';
                if (themeIcon) themeIcon.className = 'fa-solid fa-sun';
            }
            localStorage.setItem('theme', theme);
        });
    }

    if (accentColorPicker) {
        accentColorPicker.addEventListener('input', (event) => {
            const newColor = event.target.value;
            document.documentElement.style.setProperty('--primary-color', newColor);
            localStorage.setItem('accentColor', newColor);
        });
    }
});
/* ==========================================
   Splash Screen Dismissal Logic
   ========================================== */
window.addEventListener("load", function () {
    // Wait for the window to fully load, then trigger fade out after 1.5 seconds
    setTimeout(function () {
        const splashScreen = document.getElementById("splash-screen");
        if (splashScreen) {
            splashScreen.style.opacity = "0"; // Start fade-out effect
            
            // Remove the element completely from DOM after transition ends
            setTimeout(function () {
                splashScreen.style.display = "none";
            }, 500);
        }
    }, 1500);
});