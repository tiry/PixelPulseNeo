from Matrix.driver.commands.base import BaseCommand
import time


class FakerCmd(BaseCommand):
    def __init__(self) -> None:
        super().__init__("faker", "Fake command to test input and output")

    def render(self, args=[], kwargs={}):
        # print(f"execute Faker Render with kwargs={kwargs}")
        if "mock_return" in kwargs.keys():
            mock_type = kwargs["mock_return"]

            if mock_type == "Exception":
                raise Exception("Faker Execption")
            elif mock_type == "EchoArgs":
                return args

        ts: float = time.time()
        # print(ts)
        return ts
