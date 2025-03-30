"""
Module pour l'exécution sécurisée de code Python.

Ce module contient les classes et fonctions nécessaires pour exécuter du code Python
de manière sécurisée, en protégeant contre les boucles infinies, les attaques par
déni de service et autres codes malveillants.
"""

import sys
import time
import signal
import threading
import traceback
import ast
import builtins
import inspect
import re
from io import StringIO
from typing import Dict, Any, List, Set, Optional, Tuple

# Essayer d'importer le module resource (disponible uniquement sur Unix)
try:
    import resource
    RESOURCE_MODULE_AVAILABLE = True
except ImportError:
    RESOURCE_MODULE_AVAILABLE = False

# Liste des modules autorisés pour l'importation
ALLOWED_MODULES = {
    # Modules scientifiques
    'numpy', 'pandas', 'scipy', 'sympy', 'matplotlib', 'matplotlib.pyplot',
    # Modules de traitement de texte
    're', 'string', 'nltk', 'textblob',
    # Modules standards
    'math', 'random', 'statistics', 'datetime', 'collections', 'itertools',
    'functools', 'operator', 'decimal', 'fractions', 'json', 'csv'
}

# Liste des attributs dangereux à bloquer dans les builtins
UNSAFE_BUILTINS = {
    'open', 'eval', 'exec', 'compile', '__import__', 'globals', 'locals',
    'vars', 'getattr', 'setattr', 'delattr', 'hasattr', 'dir',
    'memoryview', 'classmethod', 'staticmethod', 'property',
    'breakpoint', 'help', 'print', 'super'
    # 'input' retiré de la liste pour permettre son utilisation
}

# Créer une version sécurisée des builtins
safe_builtins = {
    name: getattr(builtins, name)
    for name in dir(builtins)
    if name not in UNSAFE_BUILTINS and not name.startswith('__')
}

# Ajouter des versions sécurisées de certaines fonctions
safe_builtins['print'] = print  # On autorise print car on redirige stdout
safe_builtins['input'] = input  # On autorise input pour permettre les entrées utilisateur

# Ajouter une version sécurisée de __import__ pour les modules autorisés
def safe_import(name, *args, **kwargs):
    if name not in ALLOWED_MODULES:
        raise ImportError(f"Import non autorisé: {name}")
    return __import__(name, *args, **kwargs)

safe_builtins['__import__'] = safe_import

class TimeoutException(Exception):
    """Exception levée lorsque l'exécution du code dépasse le temps imparti."""
    pass

class MemoryLimitException(Exception):
    """Exception levée lorsque l'exécution du code dépasse la limite de mémoire."""
    pass

class CodeAnalysisException(Exception):
    """Exception levée lorsque l'analyse statique du code détecte un problème."""
    pass

class InstructionCountExceededException(Exception):
    """Exception levée lorsque le nombre d'instructions exécutées dépasse la limite."""
    pass

def timeout_handler(signum, frame):
    """Gestionnaire de signal pour le timeout."""
    raise TimeoutException("L'exécution du code a dépassé le temps imparti (60 secondes).")

class InstructionCounter:
    """Classe pour compter les instructions exécutées."""
    
    def __init__(self, max_instructions=1000000):
        self.count = 0
        self.max_instructions = max_instructions
        self.original_trace = None
    
    def trace_callback(self, frame, event, arg):
        """Fonction de callback pour le traceur d'instructions."""
        if event == 'line':
            self.count += 1
            if self.count > self.max_instructions:
                raise InstructionCountExceededException(
                    f"Le code a exécuté plus de {self.max_instructions} instructions. "
                    "Il s'agit probablement d'une boucle infinie ou d'un code très inefficace."
                )
        return self.trace_callback
    
    def __enter__(self):
        """Activer le compteur d'instructions."""
        self.original_trace = sys.gettrace()
        sys.settrace(self.trace_callback)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Désactiver le compteur d'instructions."""
        sys.settrace(self.original_trace)

class CodeAnalyzer:
    """Classe pour analyser statiquement le code Python avant exécution."""
    
    def __init__(self, max_loop_iterations=10000):
        self.max_loop_iterations = max_loop_iterations
    
    def analyze(self, code: str) -> List[str]:
        """
        Analyse le code Python pour détecter des problèmes potentiels.
        
        Args:
            code: Le code Python à analyser
            
        Returns:
            Liste des problèmes détectés (vide si aucun problème)
        """
        issues = []
        
        try:
            # Parser le code en AST
            tree = ast.parse(code)
            
            # Vérifier les imports
            issues.extend(self._check_imports(tree))
            
            # Vérifier les boucles potentiellement infinies
            issues.extend(self._check_infinite_loops(tree))
            
            # Vérifier les appels dangereux
            issues.extend(self._check_dangerous_calls(tree))
            
        except SyntaxError as e:
            issues.append(f"Erreur de syntaxe: {str(e)}")
        
        return issues
    
    def _check_imports(self, tree: ast.AST) -> List[str]:
        """Vérifie les imports pour détecter des modules non autorisés."""
        issues = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    if name.name not in ALLOWED_MODULES:
                        issues.append(f"Import non autorisé: {name.name}")
            
            elif isinstance(node, ast.ImportFrom):
                if node.module not in ALLOWED_MODULES:
                    issues.append(f"Import non autorisé: {node.module}")
        
        return issues
    
    def _check_infinite_loops(self, tree: ast.AST) -> List[str]:
        """Vérifie les boucles pour détecter des boucles potentiellement infinies."""
        issues = []
        
        for node in ast.walk(tree):
            # Vérifier les boucles while True sans break
            if isinstance(node, ast.While) and isinstance(node.test, ast.Constant) and node.test.value is True:
                # Vérifier s'il y a un break dans le corps de la boucle
                has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
                if not has_break:
                    issues.append("Boucle 'while True' sans instruction 'break' détectée.")
            
            # Vérifier les boucles for avec range(très grand nombre)
            if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
                if isinstance(node.iter.func, ast.Name) and node.iter.func.id == 'range':
                    # Vérifier si le range a un argument très grand
                    if len(node.iter.args) >= 1 and isinstance(node.iter.args[0], ast.Constant):
                        if isinstance(node.iter.args[0].value, int) and node.iter.args[0].value > self.max_loop_iterations:
                            issues.append(f"Boucle 'for' avec un très grand nombre d'itérations ({node.iter.args[0].value}).")
        
        return issues
    
    def _check_dangerous_calls(self, tree: ast.AST) -> List[str]:
        """Vérifie les appels de fonction pour détecter des appels dangereux."""
        issues = []
        
        dangerous_functions = {
            'eval', 'exec', 'compile', '__import__', 'globals', 'locals',
            'vars', 'getattr', 'setattr', 'delattr', 'open', 'file',
            'execfile', 'system', 'popen', 'subprocess'
            # 'input' retiré de la liste pour permettre son utilisation
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in dangerous_functions:
                    issues.append(f"Appel de fonction dangereuse: {node.func.id}")
            
            # Vérifier les appels à des méthodes dangereuses
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in {'system', 'popen', 'call', 'Popen', 'shell', 'eval', 'exec'}:
                    issues.append(f"Appel de méthode dangereuse: {node.func.attr}")
        
        return issues

class CodeSandbox:
    """
    Classe pour exécuter du code Python de manière sécurisée dans un sandbox.
    
    Cette classe fournit un environnement d'exécution restreint qui protège contre :
    - Les boucles infinies (timeout)
    - Les attaques par déni de service (limitation des ressources)
    - L'accès à des fonctionnalités dangereuses (filtrage des builtins)
    - L'importation de modules non autorisés
    """
    
    def __init__(self, 
                 timeout_seconds: int = 60,
                 max_memory_mb: int = 100,
                 max_instructions: int = 1000000):
        """
        Initialise le sandbox avec les limites spécifiées.
        
        Args:
            timeout_seconds: Temps maximum d'exécution en secondes
            max_memory_mb: Mémoire maximum en Mo
            max_instructions: Nombre maximum d'instructions à exécuter
        """
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_instructions = max_instructions
        self.analyzer = CodeAnalyzer()
    
    def execute(self, code: str) -> Dict[str, str]:
        """
        Exécute le code Python de manière sécurisée.
        
        Args:
            code: Code Python à exécuter
            
        Returns:
            Dictionnaire contenant la sortie ou l'erreur
        """
        # Analyser le code avant exécution
        issues = self.analyzer.analyze(code)
        if issues:
            return {
                'output': '',
                'error': "Problèmes détectés dans le code:\n" + "\n".join(f"- {issue}" for issue in issues)
            }
        
        # Capturer la sortie standard et les erreurs
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        redirected_output = sys.stdout = StringIO()
        redirected_error = sys.stderr = StringIO()
        
        result = {
            'output': '',
            'error': ''
        }
        
        # Créer un environnement d'exécution sécurisé avec les builtins
        # Utiliser un dictionnaire pour globals qui sera aussi utilisé pour locals
        # Cela permet aux fonctions définies dans le code d'être visibles dans leur propre portée
        safe_globals = {
            '__builtins__': safe_builtins,
        }
        
        # Ajouter les modules autorisés
        for module_name in ALLOWED_MODULES:
            try:
                if '.' in module_name:
                    # Pour les sous-modules comme matplotlib.pyplot
                    parent, child = module_name.split('.', 1)
                    if parent in sys.modules:
                        parent_module = sys.modules[parent]
                        if hasattr(parent_module, child):
                            safe_globals[child] = getattr(parent_module, child)
                else:
                    # Pour les modules standards
                    if module_name in sys.modules:
                        safe_globals[module_name] = sys.modules[module_name]
            except ImportError:
                pass  # Ignorer les modules non disponibles
        
        # Thread pour l'exécution du code
        execution_thread = threading.Thread(target=self._execute_in_thread, 
                                           args=(code, safe_globals, safe_globals, result))
        execution_thread.daemon = True
        
        try:
            # Démarrer le thread d'exécution
            execution_thread.start()
            
            # Attendre que le thread se termine avec un timeout
            execution_thread.join(self.timeout_seconds)
            
            # Vérifier si le thread est toujours en vie (timeout)
            if execution_thread.is_alive():
                result['error'] = f"L'exécution du code a dépassé le temps imparti ({self.timeout_seconds} secondes)."
        except Exception as e:
            result['error'] = str(e) + '\n' + traceback.format_exc()
        finally:
            # Restaurer stdout et stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Si aucune sortie n'a été produite mais qu'il n'y a pas d'erreur,
            # récupérer la dernière expression évaluée
            if not result['output'] and not result['error']:
                try:
                    # Évaluer la dernière expression
                    tree = ast.parse(code)
                    last_node = tree.body[-1]
                    if isinstance(last_node, ast.Expr):
                        last_expr = ast.unparse(last_node)
                        try:
                            value = eval(last_expr, safe_globals, safe_globals)
                            if value is not None:
                                result['output'] = str(value)
                        except:
                            pass
                except:
                    pass
        
        return result
    
    def _execute_in_thread(self, code: str, globals_dict: Dict, locals_dict: Dict, result: Dict):
        """
        Exécute le code dans un thread séparé avec des limitations de ressources.
        
        Args:
            code: Code Python à exécuter
            globals_dict: Dictionnaire global pour l'exécution
            locals_dict: Dictionnaire local pour l'exécution
            result: Dictionnaire pour stocker le résultat
        """
        try:
            # Limiter les ressources système (uniquement sur Unix)
            if RESOURCE_MODULE_AVAILABLE:
                # Limiter la mémoire
                resource.setrlimit(resource.RLIMIT_AS, 
                                  (self.max_memory_mb * 1024 * 1024, 
                                   self.max_memory_mb * 1024 * 1024))
                
                # Limiter le temps CPU
                resource.setrlimit(resource.RLIMIT_CPU, 
                                  (self.timeout_seconds, self.timeout_seconds))
                
                # Limiter le nombre de processus
                resource.setrlimit(resource.RLIMIT_NPROC, (0, 0))
                
                # Limiter la taille des fichiers
                resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
            
            # Compiler le code
            compiled_code = compile(code, '<string>', 'exec')
            
            # Exécuter le code avec un compteur d'instructions
            with InstructionCounter(self.max_instructions):
                exec(compiled_code, globals_dict, locals_dict)
            
            # Récupérer la sortie
            result['output'] = sys.stdout.getvalue()
            
        except TimeoutException as e:
            result['error'] = str(e)
        except MemoryLimitException as e:
            result['error'] = str(e)
        except InstructionCountExceededException as e:
            result['error'] = str(e)
        except Exception as e:
            result['error'] = str(e) + '\n' + traceback.format_exc()

# Fonction pour exécuter du code Python de manière sécurisée
def execute_python_code_safely(code: str, timeout_seconds: int = 60) -> Dict[str, str]:
    """
    Exécute du code Python de manière sécurisée et capture la sortie ou les erreurs.
    
    Args:
        code: Code Python à exécuter
        timeout_seconds: Temps maximum d'exécution en secondes
        
    Returns:
        Dictionnaire contenant la sortie ou l'erreur
    """
    sandbox = CodeSandbox(timeout_seconds=timeout_seconds)
    return sandbox.execute(code)
