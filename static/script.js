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
    notification.className = `alert alert-${type} alert-dismissible fade show notification-toast animate__animated animate__fadeInRight`;
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
        notification.classList.remove('animate__fadeInRight');
        notification.classList.add('animate__fadeOutRight');
        setTimeout(() => {
            notification.remove();
            // Supprimer le conteneur s'il est vide
            if (notificationContainer.children.length === 0) {
                notificationContainer.remove();
            }
        }, 500);
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
 * Fonction pour animer les transitions entre les sections
 * @param {HTMLElement} element - L'élément à animer
 * @param {string} animation - Nom de l'animation (fadeIn, fadeOut, slideIn, etc.)
 * @param {Function} callback - Fonction à exécuter après l'animation
 */
function animateElement(element, animation, callback = null) {
    // Ajouter la classe d'animation
    element.classList.add('animate__animated', `animate__${animation}`);
    
    // Écouter la fin de l'animation
    const handleAnimationEnd = () => {
        element.classList.remove('animate__animated', `animate__${animation}`);
        element.removeEventListener('animationend', handleAnimationEnd);
        
        if (callback && typeof callback === 'function') {
            callback();
        }
    };
    
    element.addEventListener('animationend', handleAnimationEnd);
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
 * Fonction pour créer un effet de confetti lors d'un succès
 */
function showConfetti() {
    const confettiCount = 200;
    const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'];
    
    const confettiContainer = document.createElement('div');
    confettiContainer.style.position = 'fixed';
    confettiContainer.style.top = '0';
    confettiContainer.style.left = '0';
    confettiContainer.style.width = '100%';
    confettiContainer.style.height = '100%';
    confettiContainer.style.pointerEvents = 'none';
    confettiContainer.style.zIndex = '9999';
    document.body.appendChild(confettiContainer);
    
    for (let i = 0; i < confettiCount; i++) {
        const confetti = document.createElement('div');
        confetti.style.position = 'absolute';
        confetti.style.width = `${Math.random() * 10 + 5}px`;
        confetti.style.height = `${Math.random() * 5 + 3}px`;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.borderRadius = '50%';
        confetti.style.top = '-10px';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.transform = `rotate(${Math.random() * 360}deg)`;
        confetti.style.opacity = Math.random();
        
        const animationDuration = Math.random() * 3 + 2;
        confetti.style.animation = `fall ${animationDuration}s linear forwards`;
        
        confettiContainer.appendChild(confetti);
        
        // Supprimer le confetti après l'animation
        setTimeout(() => {
            confetti.remove();
        }, animationDuration * 1000);
    }
    
    // Supprimer le conteneur après que tous les confettis sont tombés
    setTimeout(() => {
        confettiContainer.remove();
    }, 5000);
    
    // Ajouter l'animation CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fall {
            0% {
                transform: translateY(0) rotate(0deg);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh) rotate(720deg);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
}

// Ajouter des boutons d'action aux éléments de code et initialiser les fonctionnalités
document.addEventListener('DOMContentLoaded', function() {
    // Ajouter la bibliothèque Animate.css pour les animations
    const animateCss = document.createElement('link');
    animateCss.rel = 'stylesheet';
    animateCss.href = 'https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css';
    document.head.appendChild(animateCss);
    
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
            // Accéder à l'éditeur CodeMirror via la variable globale
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
            // Accéder à l'éditeur CodeMirror via la variable globale
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
    
    // Ajouter des animations aux boutons d'exécution et d'évaluation
    const runCodeBtn = document.getElementById('run-code-btn');
    const evaluateCodeBtn = document.getElementById('evaluate-code-btn');
    
    if (runCodeBtn) {
        runCodeBtn.addEventListener('click', function() {
            animateElement(this, 'pulse');
        });
    }
    
    if (evaluateCodeBtn) {
        evaluateCodeBtn.addEventListener('click', function() {
            animateElement(this, 'pulse');
        });
    }
    
    // Configurer les raccourcis clavier
    setupKeyboardShortcuts();
    
    // Ajouter des animations aux cartes
    document.querySelectorAll('.card').forEach((card, index) => {
        // Retarder l'animation pour chaque carte
        setTimeout(() => {
            animateElement(card, 'fadeInUp');
        }, index * 100);
    });
    
    // Ajouter un effet de confetti lorsque l'évaluation est positive
    const evaluationContent = document.getElementById('evaluation-content');
    if (evaluationContent) {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Vérifier si l'évaluation contient des messages de succès
                    if (evaluationContent.innerHTML.includes('text-success') && 
                        evaluationContent.innerHTML.includes('✅') && 
                        !evaluationContent.innerHTML.includes('❌')) {
                        showConfetti();
                    }
                }
            });
        });
        
        observer.observe(evaluationContent, { childList: true });
    }
});
