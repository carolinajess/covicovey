"""Test covicovey configuration and content."""

from pathlib import Path
from tomllib import loads


def test_zensical_covey_path() -> None:
    project = loads(Path('zensical.toml').read_text())['project']
    assert project['site_url'] == 'https://cov.ing/covey/'
    assert project['site_dir'] == 'site/covey'


def test_thanksgiving_post_links() -> None:
    post = Path('docs/2023/11/23/thanksgiving-songs.md').read_text()
    assert 'openhymnal.org/Lyrics/For_The_Beauty_Of_The_Earth-Dix.html' in post
    assert 'openhymnal.org/Lyrics/We_Gather_Together-Kremser.html' in post
    assert 'musescore.com/user/1089156/scores/5849416' in post
