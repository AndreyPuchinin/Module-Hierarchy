import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from system_models.Scoping.ScopeBuilder import ScopeBuilder
from system_models.Logging.Logger import Logger
from system_models.Tests.TestOrchestration.TestRunner import TestRunner
from system_models.Tests.TestOrchestration.TestGenerator import TestGenerator

def run_playground():
    print("="*60)
    print("ТЕСТИРОВАНИЕ МИ-МОДЕЛЕЙ ЧЕРЕЗ TestRunner")
    print("="*60)

    # Выводим абсолютный путь
    print()
    print(f"Текущая папка: {os.getcwd()}")
    
    # Создаем Оркестратор
    runner = TestRunner()
    
    # Устанавливаем директорию для вывода (относительный путь)
    runner.set_output_dir("")
    
    # Добавляем Модели для тестирования через сеттеры
    runner.add_model(Logger)
    runner.add_model(ScopeBuilder)
    runner.add_model(TestGenerator)
    runner.add_model(TestRunner)
    
    # Запускаем тестирование
    created_files = runner.run_all_tests()
    
    print("\n" + "="*60)
    print("СПИСОК СОЗДАННЫХ ФАЙЛОВ:")
    print("="*60)
    for filepath in created_files:
        print(f"  - {filepath}")

if __name__ == "__main__":
    run_playground()
