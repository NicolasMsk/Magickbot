// Navigation commune pour toutes les pages
class NavigationManager {
    constructor() {
        this.currentPage = this.getCurrentPage();
        this.init();
    }

    getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.split('/').pop() || 'index.html';
        return filename.replace('.html', '');
    }

    getMenuStructure() {
        const isIndex = this.currentPage === 'index' || this.currentPage === '';
        
        return {
            brand: {
                logo: 'logo_magickbot.png',
                title: 'Magickbot'
            },
            items: [
                { 
                    text: 'Accueil', 
                    href: isIndex ? '#accueil' : 'index.html#accueil',
                    active: isIndex
                },
                { 
                    text: 'Services', 
                    href: isIndex ? '#services' : 'index.html#services'
                },
                { 
                    text: 'À propos', 
                    href: isIndex ? '#about' : 'index.html#about'
                },
                { 
                    text: 'Témoignages', 
                    href: isIndex ? '#testimonials' : 'index.html#testimonials'
                },
                { 
                    text: 'Contact', 
                    href: isIndex ? '#contact' : 'index.html#contact'
                }
            ],
            dropdown: {
                text: 'Catégories',
                items: [
                    {
                        text: 'E-commerce',
                        href: 'e-commerce.html',
                        active: this.currentPage === 'e-commerce'
                    },
                    {
                        text: 'Immobilier',
                        href: 'immobilier.html',
                        active: this.currentPage === 'immobilier'
                    },
                    {
                        text: 'Joaillerie & Bijouterie',
                        href: 'joaillerie-bijouterie.html',
                        active: this.currentPage === 'joaillerie-bijouterie'
                    },
                    {
                        text: 'Bien-être & Esthétique',
                        href: 'bien-etre-esthetique.html',
                        active: this.currentPage === 'bien-etre-esthetique'
                    }
                ]
            }
        };
    }

    generateNavHTML() {
        const menu = this.getMenuStructure();
        
        return `
            <nav class="nav container">
                <div class="nav__brand">
                    <img src="${menu.brand.logo}" alt="${menu.brand.title} Logo" class="nav__logo">
                    <span class="nav__title">${menu.brand.title}</span>
                </div>
                <div class="nav__menu" id="nav-menu">
                    <ul class="nav__list">
                        ${menu.items.map(item => `
                            <li class="nav__item">
                                <a href="${item.href}" class="nav__link ${item.active ? 'active' : ''}">${item.text}</a>
                            </li>
                        `).join('')}
                        <li class="nav__item nav__dropdown">
                            <a href="#" class="nav__link nav__dropdown-toggle">
                                ${menu.dropdown.text} <i class="fas fa-chevron-down"></i>
                            </a>
                            <ul class="nav__dropdown-menu">
                                ${menu.dropdown.items.map(item => `
                                    <li><a href="${item.href}" class="nav__dropdown-link ${item.active ? 'active' : ''}">${item.text}</a></li>
                                `).join('')}
                            </ul>
                        </li>
                    </ul>
                    <div class="nav__close" id="nav-close">
                        <i class="fas fa-times"></i>
                    </div>
                </div>
                <div class="nav__toggle" id="nav-toggle">
                    <i class="fas fa-bars"></i>
                </div>
            </nav>
        `;
    }

    init() {
        // Injecter le HTML de navigation
        const header = document.querySelector('.header');
        if (header) {
            header.innerHTML = this.generateNavHTML();
        }

        // Initialiser les événements après injection du HTML
        setTimeout(() => {
            this.initEvents();
        }, 100);
    }

    initEvents() {
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        const navClose = document.getElementById('nav-close');
        const navDropdown = document.querySelector('.nav__dropdown');
        const dropdownToggle = document.querySelector('.nav__dropdown-toggle');

        // Mobile menu toggle
        if (navToggle) {
            navToggle.addEventListener('click', () => {
                navMenu.classList.add('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            });
        }

        if (navClose) {
            navClose.addEventListener('click', () => {
                navMenu.classList.remove('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            });
        }

        // Dropdown Menu functionality
        if (dropdownToggle) {
            dropdownToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                navDropdown.classList.toggle('active');
            });

            dropdownToggle.addEventListener('touchstart', (e) => {
                e.stopPropagation();
            });
        }

        // Close menu when clicking on nav links (EXCEPT dropdown toggle)
        const navLinks = document.querySelectorAll('.nav__link:not(.nav__dropdown-toggle)');
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                navMenu.classList.remove('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            });
        });

        // Close dropdown when clicking on a dropdown link
        const dropdownLinks = document.querySelectorAll('.nav__dropdown-link');
        dropdownLinks.forEach(link => {
            link.addEventListener('click', () => {
                navDropdown.classList.remove('active');
                navMenu.classList.remove('show-menu');
            });
            
            link.addEventListener('touchend', () => {
                navDropdown.classList.remove('active');
                navMenu.classList.remove('show-menu');
            });
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (navDropdown && !navDropdown.contains(e.target)) {
                navDropdown.classList.remove('active');
            }
        });

        document.addEventListener('touchstart', (e) => {
            if (navDropdown && !navDropdown.contains(e.target)) {
                navDropdown.classList.remove('active');
            }
        });

        // Header scroll effect
        window.addEventListener('scroll', () => {
            const header = document.querySelector('.header');
            if (window.scrollY >= 100) {
                header.classList.add('scroll-header');
            } else {
                header.classList.remove('scroll-header');
            }
        });

        // Smooth scroll for anchor links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// Initialiser la navigation quand le DOM est chargé
document.addEventListener('DOMContentLoaded', () => {
    new NavigationManager();
});
