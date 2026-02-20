class MemoryManager:
    def __init__(self):
        self._memory = {}
    def remember(self, key: str, value: str) -> None:
        self._memory[key] = value
