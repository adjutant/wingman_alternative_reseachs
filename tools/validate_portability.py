"""Check assessment references against the repository boundary, without running candidates.

Git supplies the file inventory. A relocated report-only copy can instead supply
--file-list. Ignored source checkouts are optional only with --reports-only.
"""
from pathlib import Path
from html.parser import HTMLParser
from html import unescape
from urllib.parse import unquote, urlsplit
import argparse
import ast
import collections
import json
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXCEPTIONS = 'generic/assessments/portability-runtime-paths.json'
PATH_FIELDS = {'directory', 'report', 'baseline', 'independent_audit', 'assessment', 'assessment_path', 'report_path'}
# Generic roots: no username, drive, or temporary-directory prefix is assumed.
LITERAL = re.compile(r'''(?<![\w./:@<>*~=-])(?:file://|[A-Za-z]:[\\/]|\\\\[\w.-]+[\\/]|//[\w.-]+/|(?:~|\$[A-Za-z_]\w*|\$\{[A-Za-z_]\w*\}|%[A-Za-z_]\w*%)[\\/]|/)(?:[\w.$%{}[\]<>~+-]+[/\\])*[\w.$%{}[\]<>~+-]+(?:/)?''')
MD_LINK = re.compile(r'\[[^\n]*?\]\(<?([^\n)>]+)>?\)|^\[[^\]\n]+\]:\s*(\S+)', re.M)
IMPORT = re.compile(r'''(?:\bfrom\s*|\bimport\s*\(?\s*|\brequire\s*\(\s*)["']([^"'\n]+)["']''')

class HTMLReferences(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.refs = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in {'href', 'src', 'poster', 'data', 'xlink:href'} and value:
                self.refs.append(value)
            elif key == 'srcset' and value:
                self.refs.extend(p.strip().split()[0] for p in value.split(',') if p.strip())


def file_inventory(root):
    proc = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                          cwd=root, capture_output=True, check=True)
    return sorted(set(proc.stdout.decode().split('\0')) - {''})


def checkout_roots(root):
    paths = []
    for name in ['checkouts.json', 'task-management/checkouts.json']:
        for item in json.loads((root / name).read_text())['repositories']:
            path = root / item['directory']
            if not path.resolve().is_relative_to(root):
                raise ValueError(f'Checkout directory escapes repository in {name}')
            paths.append(path)
    return paths


def local_reference(root, owner, target, optional=(), reports_only=False):
    target = unquote(target.strip().split(' "', 1)[0])
    if target.startswith('\\\\') or re.match(r'^(?:[A-Za-z]:[\\/]|(?:~|\$[A-Za-z_]\w*|\$\{[A-Za-z_]\w*\}|%[A-Za-z_]\w*%)[\\/])', target):
        return 'outside repository'
    try:
        u = urlsplit(target)
    except ValueError:
        return 'invalid URL'
    if u.scheme == 'file':
        return 'file URL is not portable'
    if u.scheme or u.netloc:
        return None
    if target.startswith('/'):
        return 'absolute local reference'
    destination = (owner.parent / u.path).resolve() if u.path else owner.resolve()
    if not destination.is_relative_to(root):
        return 'outside repository (including symlink or encoded traversal)'
    if not destination.exists():
        if reports_only and any(destination.is_relative_to(p.resolve()) for p in optional):
            return None
        return 'missing local target'
    return None


def literals(text):
    for m in re.finditer(r'''file://[^\s`\"'<>|,;)*]+''', text):
        yield text.count('\n', 0, m.start()) + 1, m[0]
    for m in LITERAL.finditer(text):
        value = m[0]
        # Slash-separated prose, regex syntax, template suffixes and division are not paths.
        if value in {'/g', '/i', '/gi', '/gim'} or value.startswith('/.') and value == '/.':
            continue
        if m.start() and text[m.start()-1] in {'}', ']', '>'}:
            continue
        yield text.count('\n', 0, m.start()) + 1, value


def check_tree(root, names, reports_only=False):
    root = root.resolve()
    initial_issues = []
    try:
        optional = checkout_roots(root)
    except ValueError as exc:
        optional = []
        initial_issues.append({'problem':str(exc)})
    exceptions = json.loads((root / EXCEPTIONS).read_text())
    allowed = {(file, item['value']): item['reason'] for item in exceptions['reviewed_literals'] for file in item['files']}
    issues, inventory = initial_issues, []
    counts = collections.Counter()
    def ref(owner, target, kind):
        counts[kind] += 1
        problem = local_reference(root, owner, target, optional, reports_only)
        if problem:
            issues.append({'file': str(owner.relative_to(root)), 'kind': kind, 'target': target, 'problem': problem})
    def markdown(owner, text):
        for m in MD_LINK.finditer(text):
            ref(owner, m[1] or m[2], 'markdown')
    def json_paths(owner, node, trail=()):
        if isinstance(node, dict):
            for key, val in node.items():
                if key in PATH_FIELDS and isinstance(val, str):
                    # These fields are repository-relative in active manifests, not candidate code-path ledgers.
                    if owner.name in {'checkouts.json', 'coverage.json', 'progress.json'}:
                        ref(root / 'manifest.json', val, 'manifest')
                json_paths(owner, val, (*trail, key))
        elif isinstance(node, list):
            for item in node: json_paths(owner, item, trail)
    for name in names:
        path = root / name
        if not path.is_relative_to(root) or not path.resolve().is_relative_to(root):
            issues.append({'file':name, 'problem':'file or symlink escapes repository'});continue
        if not path.exists(): continue  # staged deletion
        if path.is_dir():
            issues.append({'file':name,'problem':'tracked directory or submodule is not an assessment file'});continue
        counts['files'] += 1
        try: text = path.read_text()
        except UnicodeError:
            counts['binary_files'] += 1;continue
        counts['text_files'] += 1
        if path.suffix == '.md': markdown(path, text)
        if path.suffix in {'.html', '.svg'}:
            for target in HTMLReferences(text).refs: ref(path, target, 'html_or_svg')
        if path.suffix == '.css':
            for target in re.findall(r'url\([\s\"\']*([^\)\"\']+)', text): ref(path,target,'css')
        if path.suffix in {'.js','.mjs','.ts','.tsx'}:
            for m in IMPORT.finditer(text):
                if m[1].startswith(('.', '/', '~', 'file:', '\\')) or re.match(r'^[A-Za-z]:', m[1]):
                    ref(path, m[1], 'source_import')
        if path.suffix == '.json':
            try:
                data=json.loads(text);json_paths(path,data)
                if path.name=='original-audit-prose.json':
                    for doc in data['documents']:markdown(path.parent/doc['path'],doc['text'])
            except (ValueError,KeyError) as exc:
                issues.append({'file':name,'problem':f'invalid JSON structure: {exc}'})
        if path.suffix == '.py':
            tree=ast.parse(text)
            for node in ast.walk(tree):
                # ROOT is the repository root in maintained scripts; going above it is forbidden.
                if isinstance(node, ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='ROOT' and node.attr in {'parent','parents'}:
                    issues.append({'file':name,'line':node.lineno,'problem':'tool derives a path above repository root'})
        for m in re.finditer(r'''(?<![\w/])(?:\.\./)+[^\s`\"'<>|,;)*]+''', text):
            target = m[0].rstrip('.')
            if name != EXCEPTIONS and not (path.parent / unquote(target)).resolve().is_relative_to(root) and (name,target) not in allowed:
                issues.append({'file':name,'line':text.count('\n',0,m.start())+1,'problem':'parent-relative literal escapes repository','target':target})
        literal_text = unescape(re.sub(r'<[^>]*>', ' ', text)) if path.suffix in {'.html', '.svg'} else text
        for line,value in literals(literal_text):
            counts['path_literals'] += 1
            # The table contains the exact reviewed literals; skip its self-description only.
            if name == EXCEPTIONS: continue
            reason=allowed.get((name,value))
            if reason:
                inventory.append({'file':name,'line':line,'classification':reason})
            else:
                issues.append({'file':name,'line':line,'target':value,'problem':'unreviewed non-relative path literal'})
    by_file = collections.defaultdict(collections.Counter)
    for item in inventory:
        by_file[item['file']][item['classification']] += 1
    reviewed = [{'file':name,'classifications':dict(categories)} for name,categories in sorted(by_file.items())]
    return {'scope':'All versioned assessment files and unignored additions; links, assets, imports, manifest paths, archived embedded Markdown, symlinks and generic absolute/home/Windows literals. Candidate checkouts are immutable optional inputs under declared repo/ paths. Runtime literals are reviewed individually, not allowed as file dependencies.',
            'reports_only':reports_only,'counts':dict(counts),'reviewed_runtime_literals':reviewed,'issues':issues}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--reports-only',action='store_true')
    p.add_argument('--file-list',type=Path)
    p.add_argument('--write',action='store_true')
    args=p.parse_args()
    names=json.loads(args.file_list.read_text()) if args.file_list else file_inventory(ROOT)
    report=check_tree(ROOT,names,args.reports_only)
    if args.write and not report['issues']:(ROOT/'generic/assessments/portability.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'counts':report['counts'],'issues':len(report['issues'])},indent=2))
    for issue in report['issues'][:30]:print(json.dumps(issue))
    raise SystemExit(bool(report['issues']))

if __name__=='__main__':main()
