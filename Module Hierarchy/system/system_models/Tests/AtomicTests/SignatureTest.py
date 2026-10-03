import inspect
from system_models.Tests.AtomicTests.AtomicTest import AtomicTest

class SignatureTest(AtomicTest):
    """
    АТОМАРНЫЙ ТЕСТ: Проверка сигнатуры конструктора.
    
    Проверяет, сколько параметров требует __init__ Модели.
    В идеале МИ-Модель должна иметь минимальную сигнатуру (0-1 параметр).
    """
    
    def run(self, model_class, model_instance):
        """
        Проверяет сигнатуру конструктора.
        """
        try:
            sig = inspect.signature(model_class.__init__)
            params = [p for p in sig.parameters if p != 'self']
            
            required_params = [
                p for p in params 
                if sig.parameters[p].default == inspect.Parameter.empty
            ]
            
            param_count = len(required_params)
            
            # Оценка: 0-1 параметр = отлично, 2 = warning, 3+ = failed
            if param_count <= 1:
                status = "passed"
                message = f"Constructor has {param_count} required parameter(s) - ideal for MH"
            elif param_count == 2:
                status = "warning"
                message = f"Constructor has {param_count} required parameters - acceptable but not ideal"
            else:
                status = "failed"
                message = f"Constructor has {param_count} required parameters - violates MH compactness"
            
            return {
                "test_name": "SignatureTest",
                "status": status,
                "message": message,
                "details": {
                    "required_params": param_count,
                    "param_names": [p for p in params]
                }
            }
        except Exception as e:
            return {
                "test_name": "SignatureTest",
                "status": "failed",
                "message": f"Could not inspect constructor: {str(e)}",
                "details": None
            }
