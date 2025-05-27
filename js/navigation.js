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
        const navDropdown = document.querySelector('.nav__dropdown');
        const dropdownToggle = document.querySelector('.nav__dropdown-toggle');

        // Mobile menu toggle - ouvrir/fermer avec le même bouton
        if (navToggle) {
            navToggle.addEventListener('click', (e) => {
                e.stopPropagation();
                navMenu.classList.toggle('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            });
        }

        // Dropdown Menu functionality
        if (dropdownToggle) {
            // Click event
            dropdownToggle.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                navDropdown.classList.toggle('active');
            });

            // Touch events for better mobile support
            dropdownToggle.addEventListener('touchend', (e) => {
                e.preventDefault();
                e.stopPropagation();
                navDropdown.classList.toggle('active');
            });

            // Prevent double firing on devices that support both touch and click
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

        // Gestion des liens dropdown - AMÉLIORATION CRITIQUE
        const dropdownLinks = document.querySelectorAll('.nav__dropdown-link');
        dropdownLinks.forEach(link => {
            // Pour la navigation normale (click)
            link.addEventListener('click', (e) => {
                // Ne pas empêcher la navigation par défaut
                navDropdown.classList.remove('active');
                navMenu.classList.remove('show-menu');
                
                // Permettre la navigation normale
                window.location.href = link.href;
            });
            
            // Pour les appareils tactiles - SUPPRESSION des événements touchend qui bloquent
            // On garde seulement le click qui fonctionne sur tous les appareils
        });

        // Close menu when clicking outside (amélioré)
        document.addEventListener('click', (e) => {
            // Vérifier si le clic est à l'extérieur du menu ET du bouton toggle
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            }
            // Fermer le dropdown si on clique à l'extérieur (même dans le menu)
            else if (navDropdown && !navDropdown.contains(e.target)) {
                navDropdown.classList.remove('active');
            }
        });

        // Touch events pour mobile - SIMPLIFICATION
        document.addEventListener('touchstart', (e) => {
            if (!navMenu.contains(e.target) && !navToggle.contains(e.target)) {
                navMenu.classList.remove('show-menu');
                if (navDropdown) {
                    navDropdown.classList.remove('active');
                }
            }
            else if (navDropdown && !navDropdown.contains(e.target)) {
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
