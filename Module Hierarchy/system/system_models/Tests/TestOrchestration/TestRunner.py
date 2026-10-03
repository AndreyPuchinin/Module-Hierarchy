import os
import json
from system_models.Tests.TestOrchestration.TestGenerator import TestGenerator
from system_models.Tests.AtomicTests.SignatureTest import SignatureTest
from system_models.Tests.AtomicTests.SetterTest import SetterTest
from system_models.Tests.AtomicTests.ClampTest import ClampTest
from system_models.Tests.AtomicTests.DefaultTest import DefaultTest

class TestRunner:
    """
    ВЕРХНЯЯ ТОЧКА РОМБА МИ - ОРКЕСТРАТОР ТЕСТИРОВАНИЯ.
    
    Принимает классы Моделей через сеттеры.
    Создает отдельные JSON-файлы для каждой тестируемой Модели.
    Выводит информацию о созданных файлах и путях к ним.
    
    ПРИНЦИП ДИНАМИЧЕСКОЙ НЕЯВНОЙ СИГНАТУРЫ:
    - run_all_tests() имеет минимальную сигнатуру (без параметров)
    - Все Модели и пути передаются через сеттеры (по одному аргументу)
    """
    
    def __init__(self):
        """
        Инициализация оркестратора с дефолтными значениями.
        """
        self._models_to_test = []
        self._output_dir = "test_reports"
        
        # Создаем Генератор тестов и добавляем стандартные атомарные тесты
        self._test_generator = TestGenerator()
        self._test_generator.set_test(SignatureTest())
        self._test_generator.set_test(SetterTest())
        self._test_generator.set_test(ClampTest())
        self._test_generator.set_test(DefaultTest())
    
    # ==========================================
    # СЕТТЕРЫ (Управление тестированием)
    # ==========================================
    
    def add_model(self, model_class):
        """
        Добавляет класс Модели для тестирования.
        
        СИГНАТУРА:
        Вход: model_class (class) - класс Модели
        Выход: None
        """
        self._models_to_test.append(model_class)
    
    def set_output_dir(self, path):
        """
        Устанавливает директорию для вывода JSON-файлов.
        Поддерживает абсолютные и относительные пути.
        
        СИГНАТУРА:
        Вход: path (str) - путь к директории
        Выход: None
        """
        if path != "":
            self._output_dir = path
    
    def add_custom_test(self, atomic_test):
        """
        Добавляет кастомный атомарный тест в Генератор.
        
        СИГНАТУРА:
        Вход: atomic_test (AtomicTest) - экземпляр атомарного теста
        Выход: None
        """
        self._test_generator.set_test(atomic_test)
    
    # ==========================================
    # ФУНКЦИИ МЕХАНИКИ (Запуск)
    # ==========================================
    
    def run_all_tests(self):
        """
        МЕХАНИКА: Запускает тестирование всех добавленных Моделей.
        Создает отдельный JSON-файл для каждой Модели.
        
        СИГНАТУРА:
        Вход: None
        Выход: list[str] - список путей к созданным файлам
        """
        if not self._models_to_test:
            print("⚠️  Нет Моделей для тестирования. Добавьте Модели через add_model()")
            return []
        
        # Создаем директорию, если её нет
        os.makedirs(self._output_dir, exist_ok=True)
        
        created_files = []
        
        for model_class in self._models_to_test:
            model_name = model_class.__name__
            
            print(f"\n{'='*60}")
            print(f"🔍 Тестирование Модели: {model_name}")
            print(f"{'='*60}")
            
            # Генерируем тесты
            report = self._test_generator.generate(model_class, model_name)
            
            # Создаем JSON-файл
            filename = f"{model_name}_test_report.json"
            filepath = os.path.join(self._output_dir, filename)
            
            # Записываем ВЕСЬ отчет в файл
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            created_files.append(filepath)
            
            # Выводим информацию о файле
            print(f"\n✅ Создан файл: {filepath}")
            print(f"   Путь: {filepath}")
            print(f"   Модель: {model_name}")
            
            # Статистика
            stats = report.get("test_results", {}).get("statistics", {})
            print(f"   Пройдено: {stats.get('passed', 0)}")
            print(f"   Провалено: {stats.get('failed', 0)}")
            print(f"   Предупреждения: {stats.get('warnings', 0)}")
        
        print(f"\n{'='*60}")
        print(f"📊 Итого создано файлов: {len(created_files)}")
        print(f"{'='*60}")
        
        return created_files
    
    def clear_models(self):
        """
        Очищает список Моделей для тестирования.
        
        СИГНАТУРА:
        Вход: None
        Выход: None
        """
        self._models_to_test = []
