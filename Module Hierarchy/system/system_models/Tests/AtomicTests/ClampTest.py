from system_models.Tests.AtomicTests.AtomicTest import AtomicTest

class ClampTest(AtomicTest):
    """
    АТОМАРНЫЙ ТЕСТ: Проверка ограничений значений (Clamping).
    
    Проверяет, что сеттеры корректно обрабатывают экстремальные значения
    (не падают, а обрезают или принимают).
    """
    
    def run(self, model_class, model_instance):
        """
        Тестирует сеттеры с экстремальными значениями.
        """
        if model_instance is None:
            return {
                "test_name": "ClampTest",
                "status": "skipped",
                "message": "Could not create model instance",
                "details": None
            }
        
        try:
            import inspect
            
            setters = []
            for name, method in inspect.getmembers(model_instance, predicate=inspect.ismethod):
                if name.startswith("set_"):
                    sig = inspect.signature(method)
                    params = [p for p in sig.parameters if p != 'self']
                    if len(params) == 1:
                        setters.append((name, method))
            
            if not setters:
                return {
                    "test_name": "ClampTest",
                    "status": "skipped",
                    "message": "No valid setters found to test",
                    "details": None
                }
            
            # Тестовые значения: очень большое, очень маленькое, ноль
            test_values = [-999999, 0, 999999]
            results = []
            
            for setter_name, setter_method in setters:  # Тестируем все сеттеры
                for test_val in test_values:
                    try:
                        setter_method(test_val)
                        results.append({
                            "setter": setter_name,
                            "test_value": test_val,
                            "status": "passed"
                        })
                    except Exception as e:
                        results.append({
                            "setter": setter_name,
                            "test_value": test_val,
                            "status": "failed",
                            "error": str(e)
                        })
            
            # Статистика
            total = len(results)
            passed = sum(1 for r in results if r["status"] == "passed")
            failed = total - passed
            
            if failed == 0:
                status = "passed"
                message = f"All {total} clamp tests passed - setters handle extreme values"
            else:
                status = "failed"
                message = f"{failed} of {total} clamp tests failed - setters may crash on extreme values"
            
            return {
                "test_name": "ClampTest",
                "status": status,
                "message": message,
                "details": {
                    "total_tests": total,
                    "passed": passed,
                    "failed": failed,
                    "results": results
                }
            }
        except Exception as e:
            return {
                "test_name": "ClampTest",
                "status": "failed",
                "message": f"Error running clamp test: {str(e)}",
                "details": None
            }
