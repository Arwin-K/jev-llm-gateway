import json
from pathlib import Path


NOTEBOOK = Path(__file__).resolve().parents[2] / 'notebooks' / 'day6_nvidia.ipynb'


def test_day6_notebook_code_cells_are_valid_python():
    notebook = json.loads(NOTEBOOK.read_text())
    cells = [cell for cell in notebook['cells'] if cell['cell_type'] == 'code']

    assert cells
    for index, cell in enumerate(cells):
        source = ''.join(cell['source'])
        compile(source, f'{NOTEBOOK}#cell-{index}', 'exec')


def test_day6_notebook_keeps_serving_and_profile_runs_bounded():
    notebook = json.loads(NOTEBOOK.read_text())
    source = '\n'.join(''.join(cell.get('source', [])) for cell in notebook['cells'])
    benchmark = ''.join(notebook['cells'][7]['source'])

    assert "'--host', '127.0.0.1'" in source
    assert "'--port', '8000'" in source
    assert "'--label', 'baseline'" in source
    assert "'--diagnostic-only'" in source
    assert 'server.terminate()' in source
    assert 'server.wait(timeout=20)' in source
    assert 'finally:' in benchmark
    assert benchmark.index('finally:') < benchmark.index('server.terminate()')
    assert benchmark.index('finally:') < benchmark.index('log.close()')
