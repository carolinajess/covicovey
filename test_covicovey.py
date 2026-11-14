"""Test covicovey configuration and content."""

from pathlib import Path
from tomllib import loads

from html5lib import parse
from markdown import markdown
from zensical.config import parse_config

thanksgiving_post = Path('docs/2023/11/23/thanksgiving-songs.md')


def test_zensical_covey_path() -> None:
    project = loads(Path('zensical.toml').read_text())['project']
    assert project['site_url'] == 'https://cov.ing/covey/'
    assert project['site_dir'] == 'site/covey'


def test_thanksgiving_post_links() -> None:
    post = thanksgiving_post.read_text()
    assert 'openhymnal.org/Lyrics/For_The_Beauty_Of_The_Earth-Dix.html' in post
    assert 'openhymnal.org/Lyrics/We_Gather_Together-Kremser.html' in post
    assert 'musescore.com/user/1089156/scores/5849416' in post


def test_unicode_music_fence() -> None:
    config = parse_config('zensical.toml')
    html = markdown(
        thanksgiving_post.read_text(),
        extensions=config['markdown_extensions'],
        extension_configs=config['mdx_configs'],
    )
    assert '<figure class="unicoda-music">' in html
    assert html.count('class="measure"') == 11
    assert html.count('class="measure final"') == 1
    assert html.count('class="event"') == 44
    assert html.count('class="clef"') == 1
    assert 'class="key"' not in html
    assert html.count('class="meter"') == 2
    assert '\U0001d15f' in html  # MUSICAL SYMBOL QUARTER NOTE
    rows = parse(html, namespaceHTMLElements=False).findall('.//div[@class="lyrics"]')
    assert len(rows) == 12
    assert sum(map(len, rows)) == 44
    lyrics = [[(span.text or '').strip() for span in row] for row in rows]
    assert lyrics[0][3] == 'beau-'
    assert lyrics[3][-1] == 'skies,'
    assert lyrics[5][-1] == 'birth'
    assert lyrics[9][-1] == 'raise,'
    assert lyrics[11][-1] == 'praise.'
    assert all(span.attrib['data-pos'].startswith('A') for row in rows for span in row)
    assert 'https://raw.githubusercontent.com/google/fonts/main/ofl/notomusic/' in html
