from collections.abc import Mapping
from typing import final


@final
class ActionOutput:

    def __init__(self, output_path: str, summary_path: str) -> None:
        self._output_path = output_path
        self._summary_path = summary_path

    def write(self, outputs: Mapping[str, str], summary: str) -> None:
        if self._output_path != '':
            with open(file=self._output_path, mode='a', encoding='utf-8') as output:
                output.writelines(f'{name}={value}\n' for name, value in outputs.items())

        if self._summary_path != '':
            with open(file=self._summary_path, mode='a', encoding='utf-8') as step_summary:
                step_summary.write(summary)
