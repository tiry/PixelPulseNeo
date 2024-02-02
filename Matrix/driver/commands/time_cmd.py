from Matrix.driver.commands.base import BaseCommand
import time

class TimeCmd(BaseCommand):
    def __init__(self):
        super().__init__("time", "Displays the current time")
        self.refresh_timer=1

    def render(self, parameters):
        ts = time.time()
        print(ts)
        return ts