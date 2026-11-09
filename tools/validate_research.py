"""Validate the current research structure. Does not certify source semantics."""
from pathlib import Path
import argparse
import collections
import hashlib
from html import escape
from html.parser import HTMLParser
import json
import os
import re
import subprocess
from urllib.parse import unquote, urlsplit

from checkout_task_management import excluded_repo_urls, repo_key
from repository_profiles import INVENTORY_HTML, INVENTORY_MD, PROFILE_NAME, inventory_markdown, load_profiles

ROOT = Path(__file__).resolve().parents[1]

class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = []; self.links = []; self.h1 = 0; self.assets = []; self.scripts = []; self.code_blocks = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs: self.ids.append(attrs['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'a' and 'href' in attrs: self.links.append(attrs['href'])
        if tag in ['script','img'] and 'src' in attrs: self.assets.append(attrs['src'])
        if tag == 'script': self.scripts.append(attrs.get('src'))
        if tag == 'link' and 'href' in attrs: self.assets.append(attrs['href'])
        if tag == 'pre': self.code_blocks.append(attrs)

def git(path, *args):
    proc = subprocess.run(['git','-C',str(path),*args], text=True, capture_output=True)
    return proc.stdout.strip() if proc.returncode == 0 else None

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    coverage = json.loads((ROOT / 'coverage.json').read_text())
    checkouts = json.loads((ROOT / 'checkouts.json').read_text())
    issues = []; repos = []; markdown_links = 0; html_links = 0
    if ROOT.is_symlink() or not ROOT.is_dir():
        issues.append('The repository root must be a real directory')
    if not (ROOT/'AGENTS.md').is_file() or (ROOT/'AGENTS.md').is_symlink():
        issues.append('AGENTS.md must be a regular file')
    if (ROOT/'AGENTS.m').exists() or (ROOT/'AGENTS.m').is_symlink():
        issues.append('Remove the misspelled AGENTS.m entry')
    expected = set()
    excluded = excluded_repo_urls()
    if {item['directory'] for item in checkouts['repositories']} != {item['directory'] for item in coverage['repositories']}:
        issues.append('Orchestration checkout manifest differs from assessment coverage')
    if any(repo_key(item['url']) in excluded for item in checkouts['repositories']):
        issues.append('Excluded repository remains in the active orchestration manifest')
    for item in coverage['repositories']:
        slug = Path(item['directory']).parts[0]; expected.add(slug)
        repo = ROOT/item['directory']; doc = ROOT/item['report']
        result = {'project': slug, 'head': git(repo,'rev-parse','HEAD'),
                  'git_status': git(repo,'status','--porcelain')}
        if result['head'] != item['commit'] or result['git_status'] != item['initial_git_status']:
            issues.append(f'Checkout changed: {slug}')
        body = doc.read_text(); rows = {}
        for line in body.splitlines():
            if not line.startswith('|'): continue
            match = re.search(r'\bF\d{2}\b',line)
            verdict = re.search(r'\b(Exact|Similar|Resembles|Absent|Unclear)\b', line)
            if match and verdict:
                if match[0] in rows: issues.append(f'Duplicate feature {match[0]}: {slug}')
                rows[match[0]] = verdict[0]
        if rows != item['feature_verdicts']: issues.append(f'Feature coverage or verdict mismatch: {slug}')
        if set(rows) != {f'F{i:02}' for i in range(1,25)}: issues.append(f'Incomplete feature matrix: {slug}')
        if item['commit'] not in body: issues.append(f'Commit missing in assessment: {slug}')
        result['assessment_sha256'] = hashlib.sha256(doc.read_bytes()).hexdigest()
        if result['assessment_sha256'] != item['report_sha256']: issues.append(f'Assessment hash mismatch: {slug}')
        repos.append(result)
    actual = {p.parent.parent.name for p in ROOT.glob('*/repo/.git')}
    if expected != actual: issues.append(f'Checkout set differs: {sorted(expected ^ actual)}')
    pages = [ROOT/'index.html', ROOT/INVENTORY_HTML, *[ROOT / slug / 'index.html' for slug in sorted(expected)],
             ROOT/'generic/index.html', ROOT/'generic/method.html', ROOT/'generic/purpose.html', ROOT/'generic/task-coordination.html']
    task_manifest = json.loads((ROOT / 'task-management/checkouts.json').read_text())
    if any(repo_key(item['url']) in excluded for item in task_manifest['repositories']):
        issues.append('Excluded repository remains in the active task manifest')
    task_pages = [ROOT / 'task-management/index.html', ROOT / 'task-management/purpose.html',
                  *[ROOT / 'task-management' / item['slug'] / 'index.html' for item in task_manifest['repositories']]]
    actual_task_pages = set((ROOT / 'task-management').glob('*/index.html'))
    if actual_task_pages != set(task_pages[2:]):
        issues.append(f'Task report pages differ from the manifest: {sorted(actual_task_pages ^ set(task_pages[2:]))}')
    profiles, inventory = load_profiles(ROOT, checkouts, task_manifest)
    if (ROOT / INVENTORY_MD).read_text() != inventory_markdown(ROOT, inventory):
        issues.append('Markdown repository inventory differs from the active profiles')
    inventory_html = (ROOT / INVENTORY_HTML).read_text()
    inventory_links = collections.Counter(Document(inventory_html).links)
    if inventory_html.count('<th scope="row">') != len(inventory):
        issues.append('HTML repository inventory row count differs from the deduplicated scope')
    for profile in profiles.values():
        href = str(profile.report.relative_to(ROOT)) + '#repository-profile'
        if inventory_links[href] != 1:
            issues.append(f'Repository inventory must link exactly once to {href}')
        report_html = profile.report.read_text()
        section = re.search(r'<section id="repository-profile".*?</section>', report_html, re.S)
        if not section or any(
            escape(value) not in section[0]
            for value in [*profile.table_values(), profile.fields['Snapshot date'], f'assessment/{PROFILE_NAME}']
        ):
            issues.append(f'Published profile is missing or incomplete: {profile.path.relative_to(ROOT)}')
    for primary, *_ in inventory.values():
        if any(f'>{escape(value)}</td>' not in inventory_html for value in primary.table_values()):
            issues.append(f'HTML repository inventory has missing data: {primary.path.relative_to(ROOT)}')
    pages = sorted(pages + task_pages)
    parsed = {p: Document(p.read_text()) for p in pages}
    for page, doc in parsed.items():
        if doc.h1 != 1: issues.append(f'Expected one h1: {page.relative_to(ROOT)}')
        if any(block.get('tabindex') != '0' for block in doc.code_blocks):
            issues.append(f'Code block lacks keyboard access: {page.relative_to(ROOT)}')
        duplicates = [k for k,v in collections.Counter(doc.ids).items() if v>1]
        if duplicates: issues.append(f'Duplicate HTML IDs: {page.relative_to(ROOT)} {duplicates}')
        if doc.scripts != [os.path.relpath(ROOT/'assets/report.js', page.parent)]:
            issues.append(f'Unexpected script: {page.relative_to(ROOT)}')
        for target in doc.links + doc.assets:
            u=urlsplit(target)
            if u.scheme or u.netloc:
                if target in doc.assets: issues.append(f'Remote asset: {target}')
                continue
            dest=Path(os.path.normpath(page.parent/unquote(u.path))) if u.path else page
            html_links += 1
            if not dest.resolve().is_relative_to(ROOT): issues.append(f'HTML link escapes repository: {page.relative_to(ROOT)} -> {target}')
            elif not dest.exists(): issues.append(f'Broken HTML link: {page.relative_to(ROOT)} -> {target}')
            elif u.fragment and dest.suffix=='.html':
                ids=parsed.get(dest)
                if ids and unquote(u.fragment) not in ids.ids:
                    issues.append(f'Broken HTML anchor: {page.relative_to(ROOT)} -> {target}')
    def local_link_exists(doc, target):
        dest = (doc.parent / unquote(target.split('#')[0])).resolve()
        return dest.is_relative_to(ROOT) and dest.exists()

    docs = [ROOT/'WINGMAN_PURPOSE.md', ROOT/'AGENT_TASK_MANAGEMENT.md', ROOT/'AGENTS.md', ROOT/'README.md',
            ROOT/INVENTORY_MD]
    docs += list(ROOT.glob('task-management/*.md'))
    docs += list(ROOT.glob('task-management/*/assessment/*.md'))
    docs += list(ROOT.glob('*/assessment/*.md'))
    docs += list(ROOT.glob('generic/assessments/*.md'))
    docs += list(ROOT.glob('generic/assessments/agent-task-coordination/*.md'))
    docs += list(ROOT.glob('generic/assessments/_audits/*.md'))
    for doc in docs:
        if not doc.exists(): issues.append(f'Missing guide: {doc.relative_to(ROOT)}'); continue
        body=doc.read_text()
        if re.search(r'^- \*\* ', body, re.M):
            issues.append(f'Stray bold marker in list: {doc.relative_to(ROOT)}')
        for target in re.findall(r'\[[^\n]*?\]\(([^\n)]+)\)',body):
            if re.match(r'\w+:|#',target): continue
            markdown_links += 1
            if not local_link_exists(doc, target): issues.append(f'Broken Markdown link: {doc.relative_to(ROOT)} -> {target}')
        for target in re.findall(r'^\[[^\]\n]+\]:\s*(\S+)',body,re.M):
            if re.match(r'\w+:|#',target): continue
            markdown_links += 1
            if not local_link_exists(doc, target):
                issues.append(f'Broken reference link: {doc.relative_to(ROOT)} -> {target}')
        if re.search(r'\[[^\]]*\]\(https?://',body): issues.append(f'External URL is not bare: {doc.relative_to(ROOT)}')
    result = {'scope':'Repository preservation, structure, feature coverage, local links, HTML anchors, and shared assets. Not a semantic or STE certification.',
              'repository_count':len(repos), 'repository_profiles':len(profiles), 'inventory_repositories':len(inventory),
              'html_count':len(pages), 'markdown_links_checked':markdown_links,
              'html_links_checked':html_links, 'issues':issues, 'repositories':repos}
    if args.write: (ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['repositories','issues']},indent=2))
    print(f'Issues: {len(issues)}')
    for issue in issues[:30]: print(issue)
    raise SystemExit(1 if issues else 0)

if __name__ == '__main__': main()
