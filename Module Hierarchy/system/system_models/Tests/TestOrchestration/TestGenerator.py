from system_models.Tests.AtomicTests.AtomicTest import AtomicTest
from system_models.Scoping.ScopeBuilder import ScopeBuilder

class TestGenerator:
    """
    ГЕНЕРАТОР ТЕСТОВ (Верхняя точка Ромба МИ).
    
    Оркестрирует набор AtomicTest для любой Модели.
    Не содержит тестовой логики - только управляет тестами.
    
    ПРИНЦИП ДИНАМИЧЕСКОЙ НЕЯВНОЙ СИГНАТУРЫ:
    - generate() имеет минимальную сигнатуру
    - Тесты добавляются через сеттер add_test()
    - Использует ScopeBuilder для организации результатов
    """
    
    def __init__(self):
        """
        Инициализация генератора с пустым набором тестов.
        """
        self.scope_builder = ScopeBuilder()
        self._tests = []
        self._output_directory = ""
        self._test = None
    
    # ==========================================
    # СЕТТЕРЫ (Управление набором тестов)
    # ==========================================
    
    def set_test(self, atomic_test):  # было add_test
        """Добавляет атомарный тест в набор."""
        # Проверяем, что тип параметра подходящий
        if isinstance(atomic_test, AtomicTest):
            self._tests.append(atomic_test)
    
    def set_output_directory(self, path):  # было set_output_dir (уже начиналось с set_, но для единообразия)
        """Устанавливает директорию для вывода JSON-файлов."""
        self._output_dir = path
    
    def clear_tests(self):  # было remove_all_tests - это не сеттер, а команда
        """Очищает набор тестов."""
        self._tests = []
    
    # ==========================================
    # ФУНКЦИИ МЕХАНИКИ (Запуск)
    # ==========================================
    
    def generate(self, model_class, model_name=None):
        if model_name is None:
            model_name = model_class.__name__
        
        model_instance = self._create_instance(model_class)
        
        self.scope_builder.reset_to_root()
        
        # ✅ Записываем данные в КОРНЕ (путь = [])
        self.scope_builder.put_value("model_name", model_name)
        self.scope_builder.put_value("instance_created", model_instance is not None)
        
        # ✅ Переходим в test_results одним вызовом
        self.scope_builder.navigate_to(["test_results"])
        
        results = []
        for test in self._tests:
            result = test.run(model_class, model_instance)
            results.append(result)
        
        self.scope_builder.put_value("tests", results)
        self.scope_builder.put_value("total_tests", len(results))
        
        passed = sum(1 for r in results if r["status"] == "passed")
        failed = sum(1 for r in results if r["status"] == "failed")
        warnings = sum(1 for r in results if r["status"] == "warning")
        skipped = sum(1 for r in results if r["status"] == "skipped")
        
        self.scope_builder.put_value("statistics", {
            "passed": passed,
            "failed": failed,
            "warnings": warnings,
            "skipped": skipped,
            "total": len(results)
        })
        
        self.scope_builder.reset_to_root()
        return self.scope_builder.build()
    
    def _create_instance(self, model_class):
        """
        ВНУТРЕННЯЯ МЕХАНИКА: Пытается создать экземпляр Модели.
        """
        try:
            return model_class()
        except TypeError:
            try:
                return model_class(sample_rate=44100)
            except:
                return None
        except:
            return None
    
    def to_json(self, indent=2):
        """
        МЕХАНИКА: Сериализует результаты в JSON.
        """
        return self.scope_builder.to_json(indent)
