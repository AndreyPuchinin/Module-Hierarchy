import inspect
import os
from datetime import datetime
from system_models.Scoping.ScopeBuilder import ScopeBuilder # Относительный импорт внутри MH/system

class Logger:
    """
    АТОМАРНАЯ МЕХАНИКА ЛОГИРОВАНИЯ.
    
    Системная Модель. 
    Принцип Компактности: метод add_error имеет сигнатуру (message).
    Контекст (user/system/network) задается через сеттер set_log_context.
    """
    
    def __init__(self):
        self.scope_builder = ScopeBuilder()
        self._log_context = "default" # Контекст по умолчанию
        self._timestamp_format = "%Y-%m-%d %H:%M:%S"
        
        # Инициализация базовой структуры
        self.scope_builder.navigate_to(["default", "errors"])
        self.scope_builder.put_value("list", [])
        self.scope_builder.reset_to_root()
    
    # ==========================================
    # СЕТТЕРЫ (Управление состоянием)
    # ==========================================
    
    def set_log_context(self, context_name):
        """
        Устанавливает активный контекст логирования (ветку дерева).
        Например: "user", "system", "network", "database".
        """
        self._log_context = str(context_name)
        # Инициализируем ветку, если её нет
        self.scope_builder.navigate_to([self._log_context, "errors"])
        if self.scope_builder.get_value("list") is None:
            self.scope_builder.put_value("list", [])
        self.scope_builder.navigate_to([self._log_context, "warnings"])
        if self.scope_builder.get_value("list") is None:
            self.scope_builder.put_value("list", [])
        self.scope_builder.navigate_to([self._log_context, "messages"])
        if self.scope_builder.get_value("list") is None:
            self.scope_builder.put_value("list", [])
        self.scope_builder.navigate_to([self._log_context, "notes"])
        if self.scope_builder.get_value("list") is None:
            self.scope_builder.put_value("list", [])
        self.scope_builder.reset_to_root()
    
    # ==========================================
    # ФУНКЦИИ МЕХАНИКИ (Нулевая сигнатура + message)
    # ==========================================
    
    def add_error(self, message):
        """Добавляет ошибку в ТЕКУЩИЙ контекст."""
        self._append_log("errors", message, level="ERROR")
    
    def add_warning(self, message):
        """Добавляет предупреждение в ТЕКУЩИЙ контекст."""
        self._append_log("warnings", message, level="WARNING")

    def add_message(self, message):
        """Добавляет предупреждение в ТЕКУЩИЙ контекст."""
        self._append_log("messages", message, level="MESSAGE")

    def add_note(self, message):
        """Добавляет предупреждение в ТЕКУЩИЙ контекст."""
        self._append_log("notes", message, level="NOTE")
    
    def _append_log(self, category, message, level):
        """Внутренняя механика записи."""
        try:
            # 1. Переходим в нужную ветку текущего контекста
            self.scope_builder.navigate_to([self._log_context, category])
            
            # 2. Получаем список
            logs_list = self.scope_builder.get_value("list")
            if logs_list is None:
                logs_list = []
            
            # 3. Формируем запись (с автоматическим стеком)
            log_entry = {
                "timestamp": datetime.now().strftime(self._timestamp_format),
                "level": level,
                "message": str(message),
                "stack": self._get_stack_trace()
            }
            
            logs_list.append(log_entry)
            self.scope_builder.put_value("list", logs_list)
            self.scope_builder.reset_to_root()
            
        except Exception:
            pass # Логгер никогда не падает
    
    def _get_stack_trace(self):
        """Собирает стек вызовов (пропуская внутренние методы Логгера)."""
        stack = inspect.stack()
        trace = []
        for frame_info in stack[3:]: 
            trace.append({
                "module": os.path.basename(frame_info.filename),
                "line": frame_info.lineno,
                "function": frame_info.function
            })
        return trace
    
    def get_all_logs(self):
        return self.scope_builder.build()
