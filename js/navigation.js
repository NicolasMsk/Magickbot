document.addEventListener('DOMContentLoaded', function() {
    // Configuration du menu
    const menuConfig = {
        logo: {
            src: 'logo_magickbot.png',
            alt: 'Magickbot Logo',
            title: 'Magickbot'
        },
        menuItems: [
            { text: 'Accueil', href: 'index.html#accueil' },
            { text: 'Services', href: 'index.html#services' },
            {
                text: 'Catégories',
                isDropdown: true,
                items: [
                    { text: 'E-commerce', href: 'e-commerce.html' },
                    { text: 'Immobilier', href: 'immobilier.html' },
                    { text: 'Bien-être & Esthétique', href: 'bien-etre-esthetique.html' },
                    { text: 'Joaillerie & Bijouterie', href: 'joaillerie-bijouterie.html' }
                ]
            },
            { text: 'À Propos', href: 'index.html#about' },
            { text: 'FAQ', href: 'index.html#faq' },
            { text: 'Contact', href: 'index.html#contact' }
        ]
    };

    // Créer la structure HTML du menu
    function createNavigation() {
        // Vérifier si la navigation existe déjà
        if (document.querySelector('.nav')) {
            return;
        }

        const body = document.body;
        
        const nav = document.createElement('nav');
        nav.className = 'nav';
        
        const container = document.createElement('div');
        container.className = 'nav__container container';

        // Brand section
        const brand = document.createElement('a');
        brand.className = 'nav__brand';
        brand.href = '#';
        brand.innerHTML = `
            <img src="${menuConfig.logo.src}" alt="${menuConfig.logo.alt}" class="nav__logo">
            <span class="nav__title">${menuConfig.logo.title}</span>
        `;

        // Menu section
        const menu = document.createElement('div');
        menu.className = 'nav__menu';
        menu.id = 'nav-menu';

        const menuList = document.createElement('ul');
        menuList.className = 'nav__list';

        // Créer les items du menu
        menuConfig.menuItems.forEach(item => {
            const listItem = document.createElement('li');
            listItem.className = 'nav__item';

            if (item.isDropdown) {
                // Créer dropdown
                listItem.className += ' nav__dropdown';
                listItem.innerHTML = `
                    <div class="nav__dropdown-toggle nav__link" role="button" tabindex="0">
                        ${item.text}
                        <i class="fas fa-chevron-down"></i>
                    </div>
                    <ul class="nav__dropdown-menu">
                        ${item.items.map(subItem => `
                            <li>
                                <a href="${subItem.href}" class="nav__dropdown-link">
                                    ${subItem.text}
                                </a>
                            </li>
                        `).join('')}
                    </ul>
                `;
            } else {
                // Créer lien normal
                listItem.innerHTML = `
                    <a href="${item.href}" class="nav__link">
                        ${item.text}
                    </a>
                `;
            }

            menuList.appendChild(listItem);
        });

        menu.appendChild(menuList);

        // Toggle button pour mobile
        const toggle = document.createElement('button');
        toggle.className = 'nav__toggle';
        toggle.id = 'nav-toggle';
        toggle.setAttribute('aria-label', 'Toggle menu');
        toggle.innerHTML = `
            <span class="nav__toggle-line"></span>
            <span class="nav__toggle-line"></span>
            <span class="nav__toggle-line"></span>
        `;

        // Créer l'overlay pour mobile
        const overlay = document.createElement('div');
        overlay.className = 'nav__overlay';
        overlay.id = 'nav-overlay';

        // Assembler la navigation
        container.appendChild(brand);
        container.appendChild(menu);
        container.appendChild(toggle);
        nav.appendChild(container);
        nav.appendChild(overlay);

        // Insérer au début du body
        body.insertBefore(nav, body.firstChild);
    }

    // Initialiser la navigation
    createNavigation();

    // Fonctionnalités interactives
    function initializeNavigation() {
        const navToggle = document.getElementById('nav-toggle');
        const navMenu = document.getElementById('nav-menu');
        const navOverlay = document.getElementById('nav-overlay');
        const navLinks = document.querySelectorAll('.nav__link:not(.nav__dropdown-toggle)');
        const dropdowns = document.querySelectorAll('.nav__dropdown');

        console.log('Navigation initialized:', { navToggle, navMenu, navOverlay, dropdowns });

        // Fonction pour fermer le menu
        function closeMenu() {
            navMenu?.classList.remove('show-menu');
            navToggle?.classList.remove('active');
            navOverlay?.classList.remove('show');
            document.body.style.overflow = '';
            document.body.style.height = '';
            document.documentElement.style.overflow = '';
        }

        // Fonction pour ouvrir le menu
        function openMenu() {
            navMenu?.classList.add('show-menu');
            navToggle?.classList.add('active');
            navOverlay?.classList.add('show');
            document.body.style.overflow = 'hidden';
            document.body.style.height = '100vh';
            document.documentElement.style.overflow = 'hidden';
        }

        // Toggle menu mobile
        if (navToggle && navMenu) {
            navToggle.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                console.log('Toggle clicked, current menu state:', navMenu.classList.contains('show-menu'));
                
                if (navMenu.classList.contains('show-menu')) {
                    closeMenu();
                } else {
                    openMenu();
                }
            });
        }

        // Fermer le menu en cliquant sur l'overlay
        if (navOverlay) {
            navOverlay.addEventListener('click', closeMenu);
        }

        // Gestion des dropdowns
        dropdowns.forEach(dropdown => {
            const toggle = dropdown.querySelector('.nav__dropdown-toggle');
            
            if (toggle) {
                // Événement de clic (fonctionne sur mobile et desktop)
                toggle.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log('Dropdown clicked:', dropdown);
                    
                    // Fermer les autres dropdowns
                    dropdowns.forEach(otherDropdown => {
                        if (otherDropdown !== dropdown) {
                            otherDropdown.classList.remove('active');
                        }
                    });
                    
                    // Toggle le dropdown actuel
                    dropdown.classList.toggle('active');
                });

                // Événement de survol pour desktop uniquement
                function handleDesktopHover() {
                    if (window.innerWidth > 768) {
                        dropdown.addEventListener('mouseenter', () => {
                            dropdown.classList.add('active');
                        });

                        dropdown.addEventListener('mouseleave', () => {
                            dropdown.classList.remove('active');
                        });
                    }
                }

                // Appliquer les événements de survol au chargement
                handleDesktopHover();

                // Événement tactile pour mobile
                toggle.addEventListener('touchstart', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    console.log('Dropdown touched on mobile:', dropdown);
                    
                    // Fermer les autres dropdowns
                    dropdowns.forEach(otherDropdown => {
                        if (otherDropdown !== dropdown) {
                            otherDropdown.classList.remove('active');
                        }
                    });
                    
                    // Toggle le dropdown actuel
                    dropdown.classList.toggle('active');
                }, { passive: false });
            }
        });

        // Fermer les dropdowns en cliquant ailleurs
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.nav__dropdown')) {
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });

        // Fermer le menu mobile lors du clic sur un lien
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (navMenu && navMenu.classList.contains('show-menu')) {
                    closeMenu();
                }
            });
        });

        // Gestion du scroll header
        window.addEventListener('scroll', () => {
            const nav = document.querySelector('.nav');
            if (nav) {
                if (window.scrollY >= 50) {
                    nav.classList.add('scrolled');
                } else {
                    nav.classList.remove('scrolled');
                }
            }
        });

        // Gestion responsive
        function handleResize() {
            if (window.innerWidth > 768) {
                closeMenu();
                // Fermer tous les dropdowns en mode desktop
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
                
                // Réactiver les événements de survol pour desktop
                dropdowns.forEach(dropdown => {
                    const toggle = dropdown.querySelector('.nav__dropdown-toggle');
                    if (toggle) {
                        // Nettoyer les anciens événements
                        dropdown.replaceWith(dropdown.cloneNode(true));
                        
                        // Récupérer la nouvelle référence
                        const newDropdown = document.querySelector(`[data-dropdown="${dropdown.dataset.dropdown || dropdown.className}"]`) || dropdown;
                        const newToggle = newDropdown.querySelector('.nav__dropdown-toggle');
                        
                        if (newToggle) {
                            // Rétablir les événements de clic
                            newToggle.addEventListener('click', function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                
                                dropdowns.forEach(otherDropdown => {
                                    if (otherDropdown !== newDropdown) {
                                        otherDropdown.classList.remove('active');
                                    }
                                });
                                
                                newDropdown.classList.toggle('active');
                            });

                            // Ajouter les événements de survol pour desktop
                            newDropdown.addEventListener('mouseenter', () => {
                                newDropdown.classList.add('active');
                            });

                            newDropdown.addEventListener('mouseleave', () => {
                                newDropdown.classList.remove('active');
                            });
                        }
                    }
                });
            } else {
                // Mode mobile - s'assurer que seuls les clics fonctionnent
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        }

        window.addEventListener('resize', handleResize);

        // Prévenir le scroll du body quand le menu est ouvert
        document.addEventListener('touchmove', (e) => {
            if (navMenu && navMenu.classList.contains('show-menu')) {
                // Permettre le scroll seulement dans le menu
                if (!e.target.closest('.nav__menu')) {
                    e.preventDefault();
                }
            }
        }, { passive: false });

        // Gestion de la touche Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                if (navMenu && navMenu.classList.contains('show-menu')) {
                    closeMenu();
                }
                // Fermer tous les dropdowns
                dropdowns.forEach(dropdown => {
                    dropdown.classList.remove('active');
                });
            }
        });
    }

    // Initialiser après un court délai pour s'assurer que le DOM est prêt
    setTimeout(initializeNavigation, 100);
});
