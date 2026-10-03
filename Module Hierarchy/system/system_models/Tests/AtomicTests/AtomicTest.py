class AtomicTest:
    """
    АТОМАРНЫЙ ТЕСТ-КЕЙС (Нижняя точка Ромба МИ).
    
    Базовый Контракт для всех атомарных тестов.
    Не содержит реализации - только определяет Сигнатуру.
    
    СИГНАТУРА (Контракт):
    Вход:
        - model_class (class) - класс Модели для тестирования
        - model_instance (object) - экземпляр Модели (или None, если не удалось создать)
    Выход:
        - dict: {"status": str, "message": str, "details": any}
          status: "passed" | "failed" | "skipped" | "warning"
    """
    
    def run(self, model_class, model_instance):
        """
        МЕХАНИКА: Запускает атомарный тест.
        
        СИГНАТУРА:
        Вход: model_class (class), model_instance (object)
        Выход: dict - результат теста
        """
        raise NotImplementedError("AtomicTest is a contract. Implement run() in concrete tests.")
