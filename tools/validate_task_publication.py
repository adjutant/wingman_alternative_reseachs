# /// script
# requires-python = ">=3.12"
# dependencies = ["Markdown==3.7", "beautifulsoup4==4.12.3"]
# ///
"""Check that the task study publishes the recorded reports and verdicts faithfully."""
from datetime import datetime, timezone
import argparse
import hashlib
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
import markdown

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'task-management'


def plain(document):
    return re.sub(r'\s+', ' ', document.get_text(' ', strip=True)).strip()


def rendered_text(path):
    return plain(BeautifulSoup(markdown.markdown(path.read_text(),
                 extensions=['tables', 'fenced_code', 'toc', 'sane_lists']), 'html.parser'))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((STUDY / 'checkouts.json').read_text())
    catalog = json.loads((STUDY / 'catalog.json').read_text())
    expected = {item['slug']: item for item in manifest['repositories']}
    issues = []
    if {item['slug'] for item in catalog['projects']} != set(expected):
        issues.append('Catalog and checkout manifest differ')
    overview = BeautifulSoup((STUDY / 'index.html').read_text(), 'html.parser')
    matrix = overview.select_one('#comparison-table')
    matrix_rows = matrix.select('tbody tr') if matrix else []
    if len(matrix_rows) != len(expected):
        issues.append('HTML matrix row count differs from study scope')
    found = {}
    for row in matrix_rows:
        link = row.select_one('th a')
        slug = link['href'].split('/')[0] if link else ''
        if slug in found:
            issues.append(f'Duplicate HTML matrix row: {slug}')
        found[slug] = row
    if set(found) != set(expected):
        issues.append('HTML matrix codebases differ from study scope')
    matrix_md = BeautifulSoup(markdown.markdown((STUDY / 'REQUIREMENT_MATRIX.md').read_text(),
                              extensions=['tables']), 'html.parser')
    md_rows = matrix_md.select('tbody tr')
    md_verdicts = {row.select_one('td a')['href'].split('/')[0]:
                   [cell.get_text(strip=True) for cell in row.select('td')[1:]] for row in md_rows}
    if set(md_verdicts) != set(expected) or len(md_rows) != len(expected):
        issues.append('Markdown matrix codebases differ from study scope')
    pages = [STUDY / 'index.html', STUDY / 'purpose.html']
    checked_verdicts = 0
    for slug, item in expected.items():
        report = ROOT / item['assessment']
        review = json.loads(report.with_name('review.json').read_text())
        verdicts = review['requirement_verdicts']
        page = STUDY / slug / 'index.html'
        pages.append(page)
        document = BeautifulSoup(page.read_text(), 'html.parser')
        article = document.select_one('article.technical')
        if not article or plain(article) != rendered_text(report):
            issues.append(f'Published prose differs from Markdown assessment: {slug}')
        if review['commit'] not in document.get_text():
            issues.append(f'Published source commit missing: {slug}')
        row = found.get(slug)
        cells = row.select('td[data-feature]') if row else []
        if len(cells) != 24:
            issues.append(f'HTML matrix requires 24 verdicts: {slug}')
        if md_verdicts.get(slug) != [verdicts[f'T{i:02}'] for i in range(1, 25)]:
            issues.append(f'Markdown matrix verdict mismatch: {slug}')
        for key, verdict in verdicts.items():
            identifier = f'task-{slug}-{key.lower()}'
            explained = document.find(id=identifier)
            if not explained or explained.select('td')[1].get_text(strip=True) != verdict:
                issues.append(f'Published explanation verdict mismatch: {slug}/{key}')
            cell = row.select_one(f'td[data-feature="{key}"]') if row else None
            cell_link = cell.select_one('a') if cell else None
            if not cell_link or cell_link.get_text(strip=True) != verdict or cell_link['href'] != f'{slug}/index.html#{identifier}':
                issues.append(f'HTML matrix verdict or explanation target mismatch: {slug}/{key}')
            checked_verdicts += 1
        if not document.select_one('a[href="../index.html"]'):
            issues.append(f'Task comparison return link missing: {slug}')
    for source, page in [(ROOT / 'AGENT_TASK_MANAGEMENT.md', STUDY / 'purpose.html'),
                         (STUDY / 'COMPARISON.md', STUDY / 'index.html')]:
        doc = BeautifulSoup(page.read_text(), 'html.parser')
        if plain(doc.select_one('article.technical')) != rendered_text(source):
            issues.append(f'Published text differs from source: {source.name}')
    purpose = BeautifulSoup((STUDY / 'purpose.html').read_text(), 'html.parser')
    for number in range(1, 25):
        if not purpose.find(id=f'task-purpose-t{number:02}'):
            issues.append(f'Baseline requirement anchor missing: T{number:02}')
    if 'task-management/index.html' not in (ROOT / 'index.html').read_text():
        issues.append('Collection overview does not link to task study')
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'Publication fidelity: complete report prose, pinned revisions, both verdict matrices, requirement explanation links and return navigation. Not a semantic or runtime certification.',
        'source_assessments': len(expected), 'published_task_pages': len(pages),
        'matrix_verdicts_checked': checked_verdicts, 'issues': issues,
        'published_sha256': {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                             for path in pages},
    }
    if args.write:
        (STUDY / 'publication.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: value for key, value in result.items() if key != 'published_sha256'}, indent=2))
    raise SystemExit(1 if issues else 0)


if __name__ == '__main__':
    main()
