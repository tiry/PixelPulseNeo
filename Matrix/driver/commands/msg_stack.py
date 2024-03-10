import threading

class MessageStack:
    
    def __init__(self) -> None:
        self.stack:list[dict[str,str]]  = []
    
    def push(self, message:dict[str,str]) -> None:
        self.stack.append(message)

    def pop(self) -> dict[str,str] | None:
        if len(self.stack) > 0:
            return self.stack.pop(0)
        return None


_instance: MessageStack | None = None
_lock: threading.Lock = threading.Lock()

def get_message_stack() -> MessageStack:
    global _instance

    if _instance is None:
        with _lock:
            if not _instance:
                _instance = MessageStack()
    return _instance


