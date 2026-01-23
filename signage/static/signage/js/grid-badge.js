/**
 * Grid Badge Component JavaScript
 * Handles dropdown menu behavior and collapsed state
 * Part of The Grid Design System
 */

(function() {
    'use strict';

    const badges = document.querySelectorAll('.grid-badge');

    badges.forEach(badge => {
        let isOpen = false;

        // Toggle menu on click
        badge.addEventListener('click', (e) => {
            // Don't toggle if clicking a link inside the menu
            if (e.target.closest('.grid-badge__menu')) {
                return;
            }

            isOpen = !isOpen;
            badge.classList.toggle('grid-badge--open', isOpen);
            badge.setAttribute('aria-expanded', isOpen.toString());
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!badge.contains(e.target) && isOpen) {
                isOpen = false;
                badge.classList.remove('grid-badge--open');
                badge.setAttribute('aria-expanded', 'false');
            }
        });

        // Keyboard navigation
        badge.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                isOpen = !isOpen;
                badge.classList.toggle('grid-badge--open', isOpen);
                badge.setAttribute('aria-expanded', isOpen.toString());
            }

            if (e.key === 'Escape' && isOpen) {
                isOpen = false;
                badge.classList.remove('grid-badge--open');
                badge.setAttribute('aria-expanded', 'false');
                badge.focus();
            }
        });

        // Handle menu item clicks
        const menuItems = badge.querySelectorAll('.grid-badge__menu-item:not(.grid-badge__menu-item--disabled)');
        menuItems.forEach(item => {
            item.addEventListener('click', () => {
                isOpen = false;
                badge.classList.remove('grid-badge--open');
                badge.setAttribute('aria-expanded', 'false');
            });
        });
    });

    // Watch for nav collapse state changes and update badges
    const updateBadgeState = () => {
        const miniNav = localStorage.getItem('miniNav') === 'true';
        badges.forEach(badge => {
            badge.classList.toggle('grid-badge--collapsed', miniNav);
        });
    };

    // Initial state
    updateBadgeState();

    // Watch for changes
    window.addEventListener('storage', (e) => {
        if (e.key === 'miniNav') {
            updateBadgeState();
        }
    });

    // Poll for changes (backup for same-window updates)
    setInterval(updateBadgeState, 100);
})();
