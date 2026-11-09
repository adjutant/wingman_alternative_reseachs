"""Apply conservative prose edits. This is not a semantic review or STE checker."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def mask(text):
    saved = []
    def store(m):
        saved.append(m[0]); return f'\ue000{len(saved)-1}\ue001'
    # Keep code and link destinations byte-for-byte intact.
    text = re.sub(r'```[^\n]*\n[\s\S]*?```|`[^`\n]+`|\]\([^\n)]+\)|^\[[^\]\n]+\]:[^\n]+', store, text, flags=re.M)
    return text, saved

def restore(text, saved):
    return re.sub(r'\ue000(\d+)\ue001', lambda m:saved[int(m[1])], text)

def upper_first(text):
    match = re.search(r'[A-Za-z]', text)
    if not match: return text
    return text[:match.start()] + text[match.start()].upper() + text[match.end():]

def top_semicolons(text):
    depth = 0; positions = []
    for i, c in enumerate(text):
        if c == '(': depth += 1
        elif c == ')': depth = max(0, depth - 1)
        elif c == ';' and depth == 0: positions.append(i)
    return positions

def edit(body):
    text, saved = mask(body)
    text = re.sub(r'\bWINGMAN\b(?!_)', 'Wingman', text)
    # Each replacement retains an explicit subject in the new sentence.
    text = re.sub(r';\s+(?=(?:the|a|an|it|this|these|those|they|there|each|neither|both)\b)',
                  lambda m: '. ', text)
    text = re.sub(r'(?<=\. )(?P<word>the|a|an|it|this|these|those|they|there|each|neither|both)\b',
                  lambda m: m[0].capitalize(), text)
    text = re.sub(r'\b(?:Importantly|Notably|In particular),\s+([a-z])',lambda m:m[1].upper(),text)
    paragraphs = text.split('\n\n'); lists = 0
    for i, para in enumerate(paragraphs):
        if '\n' in para or para.startswith(('#','|','-','1.','\ue000')): continue
        positions = top_semicolons(para)
        colon = para.find(':')
        if len(positions) < 3 or colon < 0 or colon > positions[0]: continue
        # An inventory intro is required. Do not turn general narrative into fragments.
        if not re.match(r'^(?:\*\*)?(?:Use directly|Use as|Adapt|Build|Still build|Still to build|Reuse|Important implementation inspected|Implementation inspected)',para): continue
        intro = para[:colon+1].replace('**','')
        tail = para[colon+1:].strip().removeprefix('**').lstrip()
        parts=[]; start=0
        for pos in top_semicolons(tail): parts.append(tail[start:pos].strip()); start=pos+1
        parts.append(tail[start:].strip().removeprefix('and '))
        paragraphs[i] = intro + '\n\n' + '\n'.join('- ' + upper_first(p.rstrip('.')) + '.' for p in parts)
        lists += 1
    return restore('\n\n'.join(paragraphs), saved), lists

def main():
    scratch = ROOT / '.run'
    scratch.mkdir(exist_ok=True)
    backup = Path(tempfile.mkdtemp(prefix='prose-before-', dir=scratch))
    log=[]
    docs=sorted(ROOT.glob('*/assessment/*.md'))
    for path in docs:
        before=path.read_text(); after, count=edit(before)
        if before==after: continue
        dest=backup/path.relative_to(ROOT); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(path,dest)
        path.write_text(after)
        log.append({'path':str(path.relative_to(ROOT)), 'before_sha256':hashlib.sha256(before.encode()).hexdigest(),
                    'after_sha256':hashlib.sha256(after.encode()).hexdigest(), 'inventories_changed_to_lists':count})
    (ROOT/'generic/assessments/prose-edit-log.json').write_text(json.dumps({
        'scope':'Conservative terminology, clause, filler, and inventory edits. Full semantic prose review remains required.',
        'backup_note':'Local working backups are not assessment inputs; document hashes record the edit.',
        'documents':log},indent=2)+'\n')
    print(f'Edited {len(log)} documents. Converted {sum(x["inventories_changed_to_lists"] for x in log)} inventories to lists.')

if __name__=='__main__':main()
