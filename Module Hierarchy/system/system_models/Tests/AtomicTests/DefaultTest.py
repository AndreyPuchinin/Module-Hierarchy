from system_models.Tests.AtomicTests.AtomicTest import AtomicTest

class DefaultTest(AtomicTest):
    """
    АТОМАРНЫЙ ТЕСТ: Проверка соответствия заявленных и фактических дефолтов.
    
    Находит все сеттеры (set_X), проверяет наличие соответствующего 
    приватного атрибута (_X) с дефолтным значением после __init__.
    """
    
    def run(self, model_class, model_instance):
        """
        Проверяет, что каждый сеттер имеет соответствующий дефолт.
        """
        if model_instance is None:
            return {
                "test_name": "DefaultTest",
                "status": "skipped",
                "message": "Could not create model instance",
                "details": None
            }
        
        try:
            import inspect
            
            # 1. Находим все сеттеры
            setters = []
            for name, method in inspect.getmembers(model_instance, predicate=inspect.ismethod):
                if name.startswith("set_"):
                    setters.append(name)
            
            if not setters:
                return {
                    "test_name": "DefaultTest",
                    "status": "warning",
                    "message": "No setters found - cannot verify defaults",
                    "details": None
                }
            
            # 2. Проверяем каждый сеттер на наличие дефолта
            mismatches = []
            matched = []
            
            for setter_name in setters:
                # Извлекаем имя атрибута: set_volume_pattern → volume_pattern
                attr_name = setter_name[4:]  # Убираем "set_"
                private_attr = f"_{attr_name}"
                
                # Проверяем наличие атрибута
                if hasattr(model_instance, private_attr):
                    default_value = getattr(model_instance, private_attr)
                    matched.append({
                        "setter": setter_name,
                        "attribute": private_attr,
                        "default_value": str(default_value),
                        "status": "ok"
                    })
                else:
                    mismatches.append({
                        "setter": setter_name,
                        "expected_attribute": private_attr,
                        "status": "missing"
                    })
            
            # 3. Формируем результат
            total_setters = len(setters)
            matched_count = len(matched)
            mismatch_count = len(mismatches)
            
            if mismatch_count == 0:
                status = "passed"
                message = f"All {matched_count} setters have corresponding defaults"
            else:
                status = "failed"
                message = f"{mismatch_count} of {total_setters} setters lack default values"
            
            return {
                "test_name": "DefaultTest",
                "status": status,
                "message": message,
                "details": {
                    "total_setters": total_setters,
                    "matched": matched_count,
                    "mismatches": mismatch_count,
                    "matched_setters": matched,
                    "missing_defaults": mismatches
                }
            }
        except Exception as e:
            return {
                "test_name": "DefaultTest",
                "status": "failed",
                "message": f"Error checking defaults: {str(e)}",
                "details": None
            }
