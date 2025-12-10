import json
from dataclasses import dataclass

from src.driver.console.models.Code import Code


@dataclass
class Result:
    def __init__(self, code: Code):
        self.__code = code

    @staticmethod
    def success() -> Result:
        return Result(code=Code.SUCCESS)

    @staticmethod
    def unexpected_failure() -> Result:
        return Result(code=Code.UNEXPECTED_FAILURE)

    @staticmethod
    def assignment_failure() -> Result:
        return Result(code=Code.ASSIGNMENT_FAILURE)

    @staticmethod
    def configuration_missing() -> Result:
        return Result(code=Code.CONFIGURATION_MISSING)

    def code(self) -> Code:
        return self.__code

    def to_json(self) -> str:
        return json.dumps({"code": self.__code.value})
