from Matrix.driver.commands.base import BaseCommand
import time

class TimeCmd(BaseCommand):
    def __init__(self):
        super().__init__("time", "Displays the current time")
        self.refresh_timer=0.5

    def render(self, args=[], kwargs={}):
        ts = time.time()
        print(ts)
        return ts