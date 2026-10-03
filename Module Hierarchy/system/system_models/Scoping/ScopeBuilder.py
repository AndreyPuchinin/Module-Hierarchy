import json

class ScopeBuilder:
    """
    АТОМАРНАЯ МЕХАНИКА ПОСТРОЕНИЯ И НАВИГАЦИИ ПО JSON-ОБЛАСТЯМ.
    
    Системная Модель. Пуленепробиваемая защита от распаковки строк.
    """
    
    def __init__(self):
        self._root = {}
        self._current_path = []

    # ==========================================
    # СЕТТЕРЫ / НАВИГАТОРЫ (Управление путём)
    # ==========================================
    
    def navigate_to(self, path):
        """
        МЕХАНИКА НАВИГАЦИИ: Переходит по указанному пути.
        
        ЗАЩИТА: Если передана строка, она считается ОДНИМ ключом 
        (или разбивается по точкам, например "user.errors", для удобства).
        Если передан список, он используется как есть.
        """
        if isinstance(path, str):
            self._current_path = path.split('.') if '.' in path else [path]
        else:
            self._current_path = list(path)
        
        current = self._root
        for key in self._current_path:
            if key not in current:
                current[key] = {}
            current = current[key]
    
    def add_scope(self, key):
        """Добавляет дочернюю область к текущему пути."""
        self._current_path.append(str(key))
        self.navigate_to(self._current_path)
        
    def remove_scope(self):
        """Поднимается на уровень вверх (аналог cd ..)."""
        if self._current_path:
            self._current_path.pop()
    
    def reset_to_root(self):
        """Сбрасывает указатель пути в корень, не удаляя данные."""
        self._current_path = []

    # ==========================================
    # МЕХАНИКА ДАННЫХ (Чтение/Запись в текущей области)
    # ==========================================
    
    def put_value(self, key, value):
        """Записывает значение в текущую область."""
        current = self._root
        for key_path in self._current_path:
            if key_path not in current:
                current[key_path] = {}
            current = current[key_path]
        current[key] = value
    
    def get_value(self, key):
        """Читает значение из текущей области."""
        current = self._root
        for key_path in self._current_path:
            if key_path not in current:
                return None
            current = current[key_path]
        return current.get(key)
    
    def build(self):
        return self._root
    
    def to_json(self, indent=2):
        return json.dumps(self._root, indent=indent, ensure_ascii=False)
    
    def clear(self):
        """Полностью очищает структуру и сбрасывает путь."""
        self._root = {}
        self._current_path = []
