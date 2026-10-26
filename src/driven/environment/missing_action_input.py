from typing import final


@final
class MissingActionInput(Exception):

    def __init__(self, variables: tuple[str, ...]) -> None:
        super().__init__(f'Required environment variables are missing <{", ".join(variables)}>.')
        self.variables = variables
