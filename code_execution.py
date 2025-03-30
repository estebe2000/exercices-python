"""
Module pour l'exécution de code Python.

Ce module contient les classes et fonctions nécessaires pour exécuter du code Python
de manière sécurisée, avec ou sans support pour la fonction input().
"""

import sys
import time
import uuid
import threading
import traceback
from io import StringIO
from typing import Dict, Any

from utils import safe_import, try_evaluate_last_expression
from code_sandbox import CodeSandbox, execute_python_code_safely

# Gestionnaire d'exécution asynchrone pour le support de input()
class AsyncCodeExecutor:
    def __init__(self):
        self.execution_queue = {}  # Stocke les exécutions en cours par ID
        
    def start_execution(self, code):
        # Générer un ID unique pour cette exécution
        execution_id = str(uuid.uuid4())
        
        # Initialiser l'état d'exécution
        self.execution_queue[execution_id] = {
            'code': code,
            'status': 'pending',
            'input_required': False,
            'input_prompt': '',
            'result': None,
            'locals': {},
            'output_buffer': StringIO(),
            'error_buffer': StringIO(),
            'start_time': time.time()
        }
        
        # Lancer l'exécution dans un thread séparé
        threading.Thread(target=self._execute_code, args=(execution_id,)).start()
        
        return execution_id
    
    def _execute_code(self, execution_id):
        # Récupérer l'état d'exécution
        execution = self.execution_queue[execution_id]
        code = execution['code']
        
        # Rediriger stdout et stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = execution['output_buffer']
        sys.stderr = execution['error_buffer']
        
        try:
            # Vérifier si le code contient des appels à input()
            if 'input(' in code:
                print("ℹ️ INFO: Votre code utilise la fonction input(). L'exécution s'arrêtera pour attendre votre saisie.")
                print("")
            
            # Créer une version modifiée de CodeSandbox qui supporte input()
            class InputSupportingSandbox(CodeSandbox):
                def __init__(self, async_executor, execution_id, **kwargs):
                    super().__init__(**kwargs)
                    self.async_executor = async_executor
                    self.execution_id = execution_id
                
                def _execute_in_thread(self, code, globals_dict, locals_dict, result):
                    # Ajouter notre fonction input() personnalisée
                    globals_dict['input'] = lambda prompt='': self.async_executor._handle_input(self.execution_id, prompt)
                    
                    # Exécuter le code avec les limitations de sécurité
                    super()._execute_in_thread(code, globals_dict, locals_dict, result)
            
            # Créer et utiliser notre sandbox personnalisé
            sandbox = InputSupportingSandbox(
                async_executor=self,
                execution_id=execution_id,
                timeout_seconds=30,  # Plus long pour permettre l'attente d'input
                max_memory_mb=100,
                max_instructions=1000000
            )
            
            # Exécuter le code dans le sandbox
            result = sandbox.execute(code)
            
            # Récupérer la sortie et les erreurs
            output = result.get('output', '')
            error = result.get('error', '')
            
            # Mettre à jour l'état d'exécution
            if error:
                execution['status'] = 'error'
                execution['result'] = {
                    'output': output,
                    'error': error
                }
            else:
                execution['status'] = 'completed'
                execution['result'] = {
                    'output': output,
                    'error': ''
                }
        except Exception as e:
            # Gérer les erreurs
            execution['status'] = 'error'
            execution['result'] = {
                'output': execution['output_buffer'].getvalue(),
                'error': str(e) + '\n' + traceback.format_exc()
            }
        finally:
            # Restaurer stdout et stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
    
    def _handle_input(self, execution_id, prompt):
        execution = self.execution_queue[execution_id]
        
        # Afficher le prompt
        print(prompt, end='')
        
        # Marquer que l'exécution attend une entrée
        execution['status'] = 'waiting_for_input'
        execution['input_required'] = True
        execution['input_prompt'] = prompt
        
        # Attendre que l'entrée soit fournie (avec un timeout)
        start_time = time.time()
        while execution['input_required'] and time.time() - start_time < 300:  # 5 minutes timeout
            time.sleep(0.1)
        
        # Si le timeout est atteint, lever une exception
        if execution['input_required']:
            execution['input_required'] = False
            raise TimeoutError("L'attente d'entrée utilisateur a expiré")
        
        # Afficher la valeur saisie
        input_value = execution.get('input_value', '')
        print(input_value)
        
        # Retourner la valeur fournie
        return input_value
    
    def provide_input(self, execution_id, value):
        if execution_id not in self.execution_queue:
            return False
            
        execution = self.execution_queue[execution_id]
        if not execution['input_required']:
            return False
            
        # Fournir la valeur et marquer que l'entrée n'est plus requise
        execution['input_value'] = value
        execution['input_required'] = False
        return True
    
    def get_execution_status(self, execution_id):
        if execution_id not in self.execution_queue:
            return None
            
        execution = self.execution_queue[execution_id]
        return {
            'status': execution['status'],
            'input_required': execution['input_required'],
            'input_prompt': execution['input_prompt'],
            'result': execution['result']
        }
    
    def cleanup_old_executions(self, max_age=3600):  # 1 heure
        current_time = time.time()
        for execution_id in list(self.execution_queue.keys()):
            execution = self.execution_queue[execution_id]
            if 'start_time' in execution and current_time - execution['start_time'] > max_age:
                del self.execution_queue[execution_id]


def safe_input(prompt=""):
    """
    Version sécurisée de input() qui affiche un message d'erreur au lieu de bloquer l'exécution.
    
    Args:
        prompt: Le message à afficher (ignoré dans cette implémentation)
        
    Returns:
        Une chaîne vide et affiche un message d'erreur
    """
    print("⚠️ ERREUR: La fonction input() n'est pas supportée dans cet environnement.")
    print("⚠️ Veuillez utiliser des variables prédéfinies au lieu de demander des entrées utilisateur.")
    return ""


def execute_python_code(code: str) -> Dict[str, str]:
    """
    Exécute du code Python et capture la sortie ou les erreurs.
    
    Args:
        code: Code Python à exécuter
        
    Returns:
        Dictionnaire contenant la sortie ou l'erreur
    """
    # Vérifier si le code contient des appels à input()
    if 'input(' in code:
        # Capturer la sortie standard pour afficher l'avertissement
        old_stdout = sys.stdout
        redirected_output = sys.stdout = StringIO()
        
        print("⚠️ ATTENTION: Votre code utilise la fonction input().")
        print("⚠️ Pour une meilleure expérience, utilisez 'Exécuter avec input()' au lieu de 'Exécuter le code'.")
        print("⚠️ L'exécution peut être interrompue si vous ne fournissez pas d'entrée dans les 60 secondes.")
        print("")
        
        # Restaurer stdout
        sys.stdout = old_stdout
        
        # Ajouter l'avertissement au résultat
        warning = redirected_output.getvalue()
    else:
        warning = ""
    
    # Exécuter le code dans le sandbox sécurisé
    result = execute_python_code_safely(code)
    
    # Ajouter l'avertissement si nécessaire
    if warning and result['output']:
        result['output'] = warning + result['output']
    elif warning:
        result['output'] = warning
    
    return result
