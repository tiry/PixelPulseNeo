import time
from Matrix.driver.commands.base import BaseCommand

class TimeCmd(BaseCommand):
    def __init__(self) -> None:
        super().__init__("time", "Displays the current time")
        self.refresh_timer = 0.5

    def render(self, args=[], kwargs={}) -> float:
        ts: float = time.time()
        print(ts)
        return ts
