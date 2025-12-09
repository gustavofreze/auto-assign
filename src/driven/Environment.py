import os
from typing import Union, List


class Environment:

    def __init__(self, value: Union[str, bool, List[str]]):
        self.__value = value

    @staticmethod
    def get(variable: str):
        environment = os.getenv(key=variable)

        if not environment:
            raise EnvironmentError(f'Environment variable <{variable}> is missing.')

        return Environment(value=environment)

    def to_str(self) -> str:
        return str(self.__value)

    def to_bool(self) -> bool:
        if self.__value.lower() == 'true':
            return True

        return False

    def to_list(self) -> List:
        values: List[str]

        if isinstance(self.__value, str) and ',' in self.__value:
            values = [value.strip() for value in self.__value.split(',')]
        else:
            values = [self.__value] if isinstance(self.__value, str) else [str(self.__value)]

        return [value for value in values if value]
