// Fonctions utilitaires pour l'application

/**
 * Affiche une notification stylisée
 * @param {string} message - Le message à afficher
 * @param {string} type - Le type de notification (success, info, warning, danger)
 * @param {number} duration - Durée d'affichage en ms
 */
function showNotification(message, type = 'info', duration = 5000) {
    // Créer l'élément de notification
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    notification.role = 'alert';
    
    // Ajouter une icône en fonction du type
    let icon = 'info-circle';
    if (type === 'success') icon = 'check-circle';
    if (type === 'warning') icon = 'exclamation-triangle';
    if (type === 'danger') icon = 'exclamation-circle';
    
    notification.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi bi-${icon} me-2" style="font-size: 1.2rem;"></i>
            <div>${message}</div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Fermer"></button>
    `;
    
    // Créer un conteneur pour les notifications s'il n'existe pas déjà
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        notificationContainer.style.position = 'fixed';
        notificationContainer.style.top = '20px';
        notificationContainer.style.right = '20px';
        notificationContainer.style.zIndex = '1050';
        notificationContainer.style.maxWidth = '350px';
        document.body.appendChild(notificationContainer);
    }
    
    // Ajouter la notification au conteneur
    notificationContainer.appendChild(notification);
    
    // Appliquer des styles
    notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    notification.style.borderRadius = '8px';
    notification.style.marginBottom = '10px';
    notification.style.opacity = '0.95';
    
    // Ajouter un effet de survol
    notification.addEventListener('mouseenter', () => {
        notification.style.opacity = '1';
        notification.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
    });
    
    notification.addEventListener('mouseleave', () => {
        notification.style.opacity = '0.95';
        notification.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
    });
    
    // Supprimer la notification après la durée spécifiée
    setTimeout(() => {
        notification.remove();
        // Supprimer le conteneur s'il est vide
        if (notificationContainer.children.length === 0) {
            notificationContainer.remove();
        }
    }, duration);
}

// Fonction pour copier du texte dans le presse-papier
function copyToClipboard(text) {
    // Créer un élément textarea temporaire
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Sélectionner et copier le texte
    textarea.select();
    document.execCommand('copy');
    
    // Supprimer l'élément textarea
    document.body.removeChild(textarea);
    
    // Afficher une notification
    showNotification('Texte copié dans le presse-papier !', 'success');
}

// Fonction pour télécharger du texte sous forme de fichier
function downloadAsFile(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    
    URL.revokeObjectURL(url);
    
    // Afficher une notification
    showNotification(`Fichier "${filename}" téléchargé !`, 'success');
}

/**
 * Fonction pour basculer l'éditeur de code en mode plein écran
 */
function toggleFullscreen(element) {
    if (!document.fullscreenElement) {
        element.requestFullscreen().catch(err => {
            showNotification(`Erreur lors du passage en plein écran: ${err.message}`, 'warning');
        });
    } else {
        document.exitFullscreen();
    }
}

/**
 * Fonction pour ajouter des raccourcis clavier
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl+Enter pour exécuter le code
        if (e.ctrlKey && e.key === 'Enter') {
            const runButton = document.getElementById('run-code-btn');
            if (runButton && !runButton.disabled) {
                runButton.click();
                e.preventDefault();
            }
        }
        
        // Ctrl+Shift+Enter pour évaluer le code
        if (e.ctrlKey && e.shiftKey && e.key === 'Enter') {
            const evaluateButton = document.getElementById('evaluate-code-btn');
            if (evaluateButton && !evaluateButton.disabled) {
                evaluateButton.click();
                e.preventDefault();
            }
        }
        
        // Ctrl+S pour télécharger le code
        if (e.ctrlKey && e.key === 's') {
            const editor = document.querySelector('.CodeMirror')?.CodeMirror;
            if (editor) {
                const code = editor.getValue();
                downloadAsFile(code, 'exercice_python.py');
                e.preventDefault();
            }
        }
        
        // Échap pour quitter le mode plein écran
        if (e.key === 'Escape' && document.fullscreenElement) {
            document.exitFullscreen();
        }
    });
}

/**
 * Gestion du sélecteur de rôle
 */
function setupRoleSelector() {
    // Récupérer le rôle stocké dans localStorage ou utiliser 'admin' par défaut
    const currentRole = localStorage.getItem('userRole') || 'admin';
    
    // Appliquer le rôle au chargement de la page
    document.body.className = document.body.className.replace(/role-\w+/g, '');
    document.body.classList.add('role-' + currentRole);
    
    // Sélectionner les bons boutons radio (desktop et mobile)
    const roleRadio = document.getElementById('role-' + currentRole);
    const roleMobileRadio = document.getElementById('role-' + currentRole + '-mobile');
    
    if (roleRadio) {
        roleRadio.checked = true;
    }
    
    if (roleMobileRadio) {
        roleMobileRadio.checked = true;
    }
    
    // Fonction pour changer le rôle
    const changeRole = function(value) {
        // Mettre à jour la classe du body
        document.body.className = document.body.className.replace(/role-\w+/g, '');
        document.body.classList.add('role-' + value);
        
        // Sauvegarder le rôle dans localStorage
        localStorage.setItem('userRole', value);
        
        // Mettre à jour les deux sélecteurs
        const desktopRadio = document.getElementById('role-' + value);
        const mobileRadio = document.getElementById('role-' + value + '-mobile');
        
        if (desktopRadio) {
            desktopRadio.checked = true;
        }
        
        if (mobileRadio) {
            mobileRadio.checked = true;
        }
        
        // Afficher une notification
        const roleNames = {
            'admin': 'Administrateur',
            'teacher': 'Professeur',
            'student': 'Étudiant'
        };
        showNotification(`Vue changée : ${roleNames[value]}`, 'info');
    };
    
    // Ajouter des écouteurs d'événements pour les boutons radio desktop
    const roleRadios = document.querySelectorAll('input[name="role"]');
    roleRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            changeRole(this.value);
        });
    });
    
    // Ajouter des écouteurs d'événements pour les boutons radio mobile
    const roleMobileRadios = document.querySelectorAll('input[name="role-mobile"]');
    roleMobileRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            changeRole(this.value);
        });
    });
}

/**
 * Gestion du thème clair/sombre
 */
function setupThemeToggle() {
    const themeToggle = document.getElementById('theme-toggle');
    const themeToggleMobile = document.getElementById('theme-toggle-mobile');
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    
    // Vérifier la préférence stockée ou utiliser la préférence système
    const currentTheme = localStorage.getItem('theme') || 
                         (prefersDarkScheme.matches ? 'dark' : 'light');
    
    // Appliquer le thème initial
    if (currentTheme === 'dark') {
        document.documentElement.setAttribute('data-theme', 'dark');
        if (themeToggle) themeToggle.checked = true;
        if (themeToggleMobile) themeToggleMobile.checked = true;
    }
    
    // Gérer le changement de thème (version desktop)
    if (themeToggle) {
        themeToggle.addEventListener('change', function() {
            toggleTheme(this.checked);
        });
    }
    
    // Gérer le changement de thème (version mobile)
    if (themeToggleMobile) {
        themeToggleMobile.addEventListener('change', function() {
            toggleTheme(this.checked);
            // Synchroniser avec le toggle desktop
            if (themeToggle) themeToggle.checked = this.checked;
        });
    }
    
    // Écouter les changements de préférence système
    prefersDarkScheme.addEventListener('change', (e) => {
        if (!localStorage.getItem('theme')) {
            const isDark = e.matches;
            document.documentElement.setAttribute('data-theme', isDark ? 'dark' : 'light');
            if (themeToggle) themeToggle.checked = isDark;
            if (themeToggleMobile) themeToggleMobile.checked = isDark;
        }
    });
}

function toggleTheme(isDark) {
    if (isDark) {
        document.documentElement.setAttribute('data-theme', 'dark');
        localStorage.setItem('theme', 'dark');
        showNotification('Thème sombre activé', 'info');
    } else {
        document.documentElement.removeAttribute('data-theme');
        localStorage.setItem('theme', 'light');
        showNotification('Thème clair activé', 'info');
    }
}

/**
 * Animation de code qui tombe (Matrix-like) - version temporaire
 */
function setupCodeRain() {
    const codeRainContainer = document.getElementById('code-rain');
    if (!codeRainContainer) return;
    
    const pythonSymbols = [
        'def', 'class', 'import', 'from', 'if', 'else', 'elif', 'for', 'while', 
        'return', 'yield', 'try', 'except', 'finally', 'with', 'as', 'lambda',
        'print', 'input', 'range', 'len', 'str', 'int', 'float', 'list', 'dict',
        'set', 'tuple', 'True', 'False', 'None', '0', '1', ':', '=', '+', '-',
        '*', '/', '%', '**', '//', '==', '!=', '>', '<', '>=', '<=', 'and', 'or',
        'not', 'in', 'is', '()', '[]', '{}', '#', 'self', '__init__', '__main__'
    ];
    
    // Nombre de gouttes de code basé sur la largeur de l'écran
    const dropCount = Math.floor(window.innerWidth / 30);
    
    // Créer les gouttes de code
    for (let i = 0; i < dropCount; i++) {
        createCodeDrop(codeRainContainer, pythonSymbols);
    }
    
    // Arrêter l'animation après 8 secondes
    setTimeout(() => {
        // Supprimer toutes les gouttes existantes
        while (codeRainContainer.firstChild) {
            codeRainContainer.removeChild(codeRainContainer.firstChild);
        }
        
        // Ajouter une classe pour masquer le conteneur
        codeRainContainer.classList.add('hidden');
    }, 8000);
}

function createCodeDrop(container, symbols) {
    const drop = document.createElement('div');
    drop.className = 'code-drop';
    
    // Position aléatoire horizontale
    const left = Math.random() * 100;
    drop.style.left = `${left}%`;
    
    // Vitesse et délai aléatoires (plus courts)
    const speed = 2 + Math.random() * 4; // entre 2 et 6 secondes
    const delay = Math.random() * 3; // délai jusqu'à 3 secondes
    
    drop.style.animationDuration = `${speed}s`;
    drop.style.animationDelay = `${delay}s`;
    
    // Contenu aléatoire
    const symbol = symbols[Math.floor(Math.random() * symbols.length)];
    drop.textContent = symbol;
    
    // Taille et opacité aléatoires
    const size = 12 + Math.floor(Math.random() * 8); // entre 12 et 20px
    const opacity = 0.3 + Math.random() * 0.4; // entre 0.3 et 0.7
    
    drop.style.fontSize = `${size}px`;
    drop.style.opacity = opacity;
    
    container.appendChild(drop);
    
    // Ne pas recréer la goutte après son animation
    drop.addEventListener('animationend', () => {
        if (container.contains(drop)) {
            container.removeChild(drop);
        }
    });
}

// Ajouter des boutons d'action aux éléments de code et initialiser les fonctionnalités
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser le sélecteur de rôle
    setupRoleSelector();
    
    // Initialiser le sélecteur de thème
    setupThemeToggle();
    
    // Initialiser l'animation de code rain si on est sur la page d'accueil
    if (document.getElementById('code-rain')) {
        setupCodeRain();
    }
    
    // Ajouter des boutons pour copier le code
    document.querySelectorAll('pre code').forEach(codeBlock => {
        // Créer le conteneur de boutons
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'code-buttons';
        buttonContainer.style.position = 'absolute';
        buttonContainer.style.top = '5px';
        buttonContainer.style.right = '5px';
        buttonContainer.style.opacity = '0';
        buttonContainer.style.transition = 'opacity 0.3s ease';
        
        // Bouton de copie
        const copyButton = document.createElement('button');
        copyButton.className = 'btn btn-sm btn-light';
        copyButton.innerHTML = '<i class="bi bi-clipboard"></i> Copier';
        copyButton.addEventListener('click', () => {
            copyToClipboard(codeBlock.textContent);
        });
        
        // Ajouter les boutons au conteneur
        buttonContainer.appendChild(copyButton);
        
        // Ajouter le conteneur au bloc de code
        const preElement = codeBlock.parentElement;
        preElement.style.position = 'relative';
        preElement.appendChild(buttonContainer);
        
        // Afficher les boutons au survol
        preElement.addEventListener('mouseenter', () => {
            buttonContainer.style.opacity = '1';
        });
        
        preElement.addEventListener('mouseleave', () => {
            buttonContainer.style.opacity = '0';
        });
    });
    
    // Ajouter des boutons pour l'éditeur de code
    const codeEditorCard = document.getElementById('code-editor-card');
    if (codeEditorCard) {
        const buttonContainer = document.createElement('div');
        buttonContainer.className = 'editor-buttons';
        buttonContainer.style.position = 'absolute';
        buttonContainer.style.top = '10px';
        buttonContainer.style.right = '10px';
        
        // Bouton pour télécharger le code
        const downloadButton = document.createElement('button');
        downloadButton.className = 'btn btn-sm btn-outline-secondary me-2';
        downloadButton.innerHTML = '<i class="bi bi-download"></i> Télécharger';
        downloadButton.title = 'Télécharger le code (Ctrl+S)';
        downloadButton.addEventListener('click', () => {
            const editor = document.querySelector('.CodeMirror').CodeMirror;
            if (editor) {
                const code = editor.getValue();
                downloadAsFile(code, 'exercice_python.py');
            } else {
                showNotification("Impossible d'accéder à l'éditeur de code", "warning");
            }
        });
        
        // Bouton pour le mode plein écran
        const fullscreenButton = document.createElement('button');
        fullscreenButton.className = 'btn btn-sm btn-outline-primary me-2';
        fullscreenButton.innerHTML = '<i class="bi bi-arrows-fullscreen"></i>';
        fullscreenButton.title = 'Mode plein écran (F11)';
        fullscreenButton.addEventListener('click', () => {
            const editorElement = codeEditorCard.querySelector('.CodeMirror');
            if (editorElement) {
                toggleFullscreen(editorElement);
            }
        });
        
        // Bouton pour effacer le code
        const clearButton = document.createElement('button');
        clearButton.className = 'btn btn-sm btn-outline-danger';
        clearButton.innerHTML = '<i class="bi bi-trash"></i> Effacer';
        clearButton.title = 'Effacer le code';
        clearButton.addEventListener('click', () => {
            const editor = document.querySelector('.CodeMirror').CodeMirror;
            if (editor && confirm('Êtes-vous sûr de vouloir effacer tout le code ?')) {
                editor.setValue('# Écrivez votre code ici\n\n');
                showNotification("Code effacé", "info");
            }
        });
        
        // Ajouter les boutons au conteneur
        buttonContainer.appendChild(downloadButton);
        buttonContainer.appendChild(fullscreenButton);
        buttonContainer.appendChild(clearButton);
        
        // Ajouter le conteneur à la carte de l'éditeur
        const cardHeader = codeEditorCard.querySelector('.card-header');
        cardHeader.style.position = 'relative';
        cardHeader.appendChild(buttonContainer);
        
        // Ajouter des info-bulles pour les raccourcis clavier
        const shortcutsInfo = document.createElement('div');
        shortcutsInfo.className = 'shortcuts-info small text-muted mt-2';
        shortcutsInfo.innerHTML = `
            <div class="d-flex justify-content-end">
                <span class="me-3"><kbd>Ctrl</kbd> + <kbd>Enter</kbd> : Exécuter</span>
                <span><kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>Enter</kbd> : Évaluer</span>
            </div>
        `;
        codeEditorCard.querySelector('.card-body').appendChild(shortcutsInfo);
    }
    
    // Configurer les raccourcis clavier
    setupKeyboardShortcuts();
});
