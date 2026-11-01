import pytest

from jev_gateway.day6.environment import capture


def test_environment_requires_exact_source_revision(tmp_path):
    archive = tmp_path / 'source.zip'
    config = tmp_path / 'config.json'
    archive.write_bytes(b'archive')
    config.write_text('{}')
    with pytest.raises(ValueError, match='full Git commit'):
        capture(archive, 'HEAD', 'model', 'revision', 'float16', config)
