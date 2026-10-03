import inspect
from system_models.Tests.AtomicTests.AtomicTest import AtomicTest

class SetterTest(AtomicTest):
    """
    АТОМАРНЫЙ ТЕСТ: Проверка сеттеров.
    
    Проверяет, что все методы, начинающиеся с set_, имеют ровно 1 параметр.
    Это критическое правило МИ!
    """
    
    def run(self, model_class, model_instance):
        """
        Проверяет все сеттеры на соответствие правилу МИ (1 параметр).
        """
        if model_instance is None:
            return {
                "test_name": "SetterTest",
                "status": "skipped",
                "message": "Could not create model instance",
                "details": None
            }
        
        try:
            setters = []
            for name, method in inspect.getmembers(model_instance, predicate=inspect.ismethod):
                if name.startswith("set_"):
                    sig = inspect.signature(method)
                    params = [p for p in sig.parameters if p != 'self']
                    
                    is_valid = len(params) == 1
                    setters.append({
                        "name": name,
                        "param_count": len(params),
                        "is_valid_mh_setter": is_valid
                    })
            
            # Статистика
            total = len(setters)
            valid = sum(1 for s in setters if s["is_valid_mh_setter"])
            invalid = total - valid
            
            if total == 0:
                status = "warning"
                message = "No setters found - model may not follow MH pattern"
            elif invalid == 0:
                status = "passed"
                message = f"All {total} setters follow MH rule (1 parameter each)"
            else:
                status = "failed"
                message = f"{invalid} of {total} setters violate MH rule (must have exactly 1 parameter)"
            
            return {
                "test_name": "SetterTest",
                "status": status,
                "message": message,
                "details": {
                    "total_setters": total,
                    "valid_setters": valid,
                    "invalid_setters": invalid,
                    "setters": setters
                }
            }
        except Exception as e:
            return {
                "test_name": "SetterTest",
                "status": "failed",
                "message": f"Error testing setters: {str(e)}",
                "details": None
            }
