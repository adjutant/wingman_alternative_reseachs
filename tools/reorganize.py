"""One-time migration. Run only against the original workspace layout."""
from pathlib import Path
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile

W = Path(__file__).resolve().parents[2]
R = W / 'researchs'
manifest = json.loads((W / 'alternatives/checkouts.json').read_text())
coverage = json.loads((W / 'alt_researchs/coverage.json').read_text())
generic = R / 'generic/assessments'
generic.mkdir(parents=True, exist_ok=True)
backup = Path(tempfile.mkdtemp(prefix='wingman-old-research-'))
shutil.copytree(W / 'other-research', backup / 'other-research')
mapping = {}
for item in manifest['repositories']:
    slug = Path(item['directory']).name
    mapping[W / 'alternatives' / item['directory']] = R / slug / 'repo'
for path in (W / 'alt_researchs').rglob('*'):
    if not path.is_file():
        continue
    rel = path.relative_to(W / 'alt_researchs')
    if path.name.endswith('_Assessments.md'):
        dest = R / path.name.removesuffix('_Assessments.md') / 'assessment/ASSESSMENT.md'
    elif rel.parts[0].endswith('_Extra_Info'):
        dest = R / rel.parts[0].removesuffix('_Extra_Info') / 'assessment' / Path(*rel.parts[1:])
    else:
        dest = generic / rel
    mapping[path] = dest
mapping[W / 'alternatives/WINGMAN_PURPOSE.md'] = R / 'WINGMAN_PURPOSE.md'
mapping[W / 'alternatives/README.md'] = generic / 'CHECKOUT_INDEX.md'
mapping[W / 'alternatives/checkouts.json'] = R / 'checkouts.json'
old_hashes = {str(p.relative_to(W)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in mapping if p.is_file()}
states = []
for item in manifest['repositories']:
    old = W / 'alternatives' / item['directory']
    def git(*args):
        return subprocess.check_output(['git', '-C', str(old), *args], text=True).strip()
    states.append({'slug': old.name, 'old_path': str(old.relative_to(W)),
                   'head': git('rev-parse', 'HEAD'), 'status': git('status', '--porcelain'),
                   'inode': old.stat().st_ino})
for old, new in mapping.items():
    new.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(old), str(new))

def translated(path):
    path = Path(os.path.normpath(path))
    if path in mapping:
        return mapping[path]
    for old, new in mapping.items():
        if path.is_relative_to(old):
            return new / path.relative_to(old)
    return path

for old, new in mapping.items():
    if new.suffix != '.md':
        continue
    body = new.read_text()
    def link(match):
        label, target = match.groups()
        if re.match(r'\w+://|#|mailto:', target):
            return match.group(0)
        raw, sep, anchor = target.partition('#')
        dest = translated(old.parent / raw)
        return '[' + label + '](' + os.path.relpath(dest, new.parent) + (sep + anchor if sep else '') + ')'
    body = re.sub(r'\[([^\n]*?)\]\(([^\n)]+)\)', link, body)
    # Plain path labels and inline code also need current workspace paths.
    for src, dst in sorted(mapping.items(), key=lambda pair: len(str(pair[0])), reverse=True):
        body = body.replace(str(src), str(dst))
        body = body.replace(str(src.relative_to(W)), str(dst.relative_to(W)))
    new.write_text(body)

for repo, state in zip(manifest['repositories'], states):
    slug = state['slug']
    repo['previous_directory'] = repo['directory']
    repo['directory'] = f'{slug}/repo'
    repo['absolute_path'] = str(R / slug / 'repo')
    repo['assessment'] = f'{slug}/assessment/ASSESSMENT.md'
    repo['report'] = f'{slug}/index.html'
    # Keep original clone history as historical data. Current fields above govern paths.
for repo in coverage['repositories']:
    slug = Path(repo['directory']).name
    repo['directory'] = f'{slug}/repo'
    repo['report'] = f'{slug}/assessment/ASSESSMENT.md'
    repo['independent_audit'] = 'generic/assessments/' + repo['independent_audit']
coverage['baseline'] = 'WINGMAN_PURPOSE.md'
(R / 'checkouts.json').write_text(json.dumps(manifest, indent=2) + '\n')
(R / 'coverage.json').write_text(json.dumps(coverage, indent=2) + '\n')
(generic / 'coverage.json').unlink()

# Retain raw experimental evidence. Old test runs do not prove new runtime behavior.
for slug, folder in [('orca','orca'), ('agent-swarm','agent-swarm'),
                     ('codex-autorunner','car'), ('gstack','gstack')]:
    src = W / 'other-research/evidence' / folder
    if src.exists():
        shutil.move(str(src), str(R / slug / 'assessment/evidence'))
(R / 'migration.json').write_text(json.dumps({
    'source_document_sha256': old_hashes, 'checkouts_before': states,
    'discarded_old_research_sha256': {
        str(p.relative_to(W / 'other-research')): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (W / 'other-research').rglob('*') if p.is_file()},
    'temporary_backup': str(backup),
    'policy': 'Retain all current assessments and repos. Retain old focused experiment evidence. Replace old opinions with curated findings.'
}, indent=2) + '\n')
shutil.rmtree(W / 'alternatives')
shutil.rmtree(W / 'alt_researchs')
shutil.rmtree(W / 'other-research')
(W / 'research').symlink_to('researchs', target_is_directory=True)
print(f'Moved {len(states)} repositories. Old research backup: {backup}')
