from pathlib import Path

from src.driven.environment.action_output import ActionOutput


def test_write_when_outputs_are_given_then_each_is_appended_as_a_name_value_line(tmp_path: Path) -> None:
    # Given an output file already holding a line from an earlier step
    output_file = tmp_path / 'output'
    output_file.write_text('earlier=1\n', encoding='utf-8')

    # When two outputs are written
    ActionOutput(output_path=output_file.as_posix(), summary_path=(tmp_path / 'summary').as_posix()).write(
        outputs={'result': '{"code": 0}', 'assigned_issues': '[1]'},
        summary='### Auto assign\n'
    )

    # Then each output follows the earlier line as a name and value pair
    assert output_file.read_text(encoding='utf-8') == 'earlier=1\nresult={"code": 0}\nassigned_issues=[1]\n'


def test_write_when_a_summary_path_is_given_then_the_summary_is_appended(tmp_path: Path) -> None:
    # Given a step summary already holding the text of an earlier step
    summary_file = tmp_path / 'summary'
    summary_file.write_text('earlier\n', encoding='utf-8')

    # When the outputs and the summary are written
    ActionOutput(output_path=(tmp_path / 'output').as_posix(), summary_path=summary_file.as_posix()).write(
        outputs={'result': '{"code": 0}'},
        summary='### Auto assign\n'
    )

    # Then the summary follows the earlier text
    assert summary_file.read_text(encoding='utf-8') == 'earlier\n### Auto assign\n'


def test_write_when_no_summary_path_is_given_then_only_the_outputs_are_written(tmp_path: Path) -> None:
    # Given an output file in an otherwise empty directory
    output_file = tmp_path / 'output'

    # When the outputs and the summary are written without a summary path
    ActionOutput(output_path=output_file.as_posix(), summary_path='').write(
        outputs={'result': '{"code": 0}'},
        summary='### Auto assign\n'
    )

    # Then only the output file exists
    assert [entry.name for entry in tmp_path.iterdir()] == ['output']

    # And it holds the outputs
    assert output_file.read_text(encoding='utf-8') == 'result={"code": 0}\n'


def test_write_when_no_output_path_is_given_then_only_the_summary_is_written(tmp_path: Path) -> None:
    # Given a summary file in an otherwise empty directory
    summary_file = tmp_path / 'summary'

    # When the outputs and the summary are written without an output path
    ActionOutput(output_path='', summary_path=summary_file.as_posix()).write(
        outputs={'result': '{"code": 0}'},
        summary='### Auto assign\n'
    )

    # Then only the summary file exists
    assert [entry.name for entry in tmp_path.iterdir()] == ['summary']

    # And it holds the summary
    assert summary_file.read_text(encoding='utf-8') == '### Auto assign\n'
