#!/usr/bin/env python3
"""Check task-management research coverage and evidence integrity.

This checks source preservation and report structure, not source semantics.
Use --require-complete for the final coverage gate. Partial progress must not
be described as completion merely because the default integrity check passes.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'task-management'


def command(directory, *args):
    return subprocess.check_output(['git', '-C', str(directory), *args])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-complete', action='store_true')
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    baseline = ROOT / 'AGENT_TASK_MANAGEMENT.md'
    baseline_hash = hashlib.sha256(baseline.read_bytes()).hexdigest()
    requirements = re.findall(r'^\| (T\d{2}) \|', baseline.read_text(), re.M)
    expected_requirements = {f'T{i:02}' for i in range(1, 25)}
    issues = []
    if len(requirements) != 24 or set(requirements) != expected_requirements:
        issues.append('Baseline must define T01 through T24 once each')
    manifest = json.loads((STUDY / 'checkouts.json').read_text())
    screening = json.loads((ROOT / 'generic/assessments/agent-task-coordination/sources.json').read_text())
    expected = {r['slug'] for r in screening['repositories']} | {'gitlab', 'agent-mail-python', 'taiga-front'}
    actual = [r['slug'] for r in manifest['repositories']]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        issues.append('Checkout manifest differs from the complete study scope')
    complete = []
    remaining = []
    checkouts = []
    for record in manifest['repositories']:
        slug = record['slug']
        repo = ROOT / record['directory']
        try:
            head = command(repo, 'rev-parse', 'HEAD').decode().strip()
            status = command(repo, 'status', '--porcelain').decode()
            paths = command(repo, 'ls-files', '-z')
            path_list = [p.decode() for p in paths.split(b'\0') if p]
            missing = [p for p in path_list if not os.path.lexists(repo / p)]
            sparse = [line for line in command(repo, 'ls-files', '-t').decode().splitlines() if line.startswith('S ')]
            if record['state'] != 'complete' or head != record.get('commit'):
                issues.append(f'{slug}: checkout is incomplete or HEAD changed')
            if status != record.get('git_status', '') or status:
                issues.append(f'{slug}: source checkout is not clean and preserved')
            if repo.stat().st_ino != record.get('directory_inode'):
                issues.append(f'{slug}: checkout directory was replaced')
            if hashlib.sha256(paths).hexdigest() != record.get('tracked_paths_sha256'):
                issues.append(f'{slug}: tracked path set changed')
            if missing or sparse:
                issues.append(f'{slug}: tracked worktree is missing or sparse')
            checkouts.append({'slug': slug, 'head': head, 'tracked_files': len(path_list),
                              'missing_paths': len(missing), 'sparse_paths': len(sparse), 'clean': not status})
        except (OSError, subprocess.SubprocessError) as error:
            issues.append(f'{slug}: cannot verify checkout: {error}')
        report = ROOT / record['assessment']
        ledger_path = report.with_name('review.json')
        if not report.exists() or not ledger_path.exists():
            remaining.append(slug)
            continue
        body = report.read_text()
        rows = re.findall(r'^\| (T\d{2}) \| (Exact|Similar|Resembles|Absent|Unclear) \|', body, re.M)
        verdicts = dict(rows)
        if len(rows) != 24 or set(verdicts) != expected_requirements:
            issues.append(f'{slug}: assessment needs 24 unique requirement verdicts')
        ledger = json.loads(ledger_path.read_text())
        if ledger.get('baseline_sha256') != baseline_hash:
            issues.append(f'{slug}: assessment baseline hash differs')
        if ledger.get('commit') != record.get('commit') or record.get('commit', '') not in body:
            issues.append(f'{slug}: assessment source revision differs')
        if ledger.get('requirement_verdicts') != verdicts:
            issues.append(f'{slug}: ledger verdicts differ from the report')
        for file in ledger.get('files', []):
            source = repo / file['path']
            raw = source.read_bytes()
            if hashlib.sha256(raw).hexdigest() != file['sha256']:
                issues.append(f"{slug}: evidence changed: {file['path']}")
            count = len(raw.splitlines())
            if any(not 1 <= start <= end <= count for start, end in file['ranges']):
                issues.append(f"{slug}: evidence range outside file: {file['path']}")
        if not ledger.get('files') or not ledger.get('lifecycle_review'):
            issues.append(f'{slug}: source evidence or lifecycle review is missing')
        if ledger.get('review_status') == 'source_review_complete':
            complete.append(slug)
        else:
            remaining.append(slug)
    docs = [baseline, STUDY / 'README.md', *STUDY.glob('*/assessment/*.md')]
    for doc in docs:
        body = doc.read_text()
        if re.search(r'\[[^\]]+\]\(https?://', body):
            issues.append(f'External URL must be bare: {doc.relative_to(ROOT)}')
        for target in re.findall(r'\[[^\n]*?\]\(([^\n)]+)\)', body):
            if re.match(r'\w+:|#', target):
                continue
            path = doc.parent / unquote(target.split('#')[0])
            if not path.exists():
                issues.append(f'Broken local link: {doc.relative_to(ROOT)} -> {target}')
        # A valid file link can still cite lines beyond the source. Check the
        # explicit prose ranges used by these assessments as well as the path.
        # This is a bounds check, not proof that the cited lines support prose.
        for match in re.finditer(r'\]\(([^\n)]+)\), lines ([\d–, and]+)', body):
            target, line_text = match.groups()
            if re.match(r'\w+:|#', target):
                continue
            path = doc.parent / unquote(target.split('#')[0])
            if not path.is_file():
                continue
            count = len(path.read_bytes().splitlines())
            cited = [int(value) for value in re.findall(r'\d+', line_text)]
            if any(not 1 <= value <= count for value in cited):
                issues.append(f'Source citation outside file: {doc.relative_to(ROOT)} -> {target}, lines {line_text.strip()} ({count} available)')
    if args.require_complete and remaining:
        issues.append(f'Assessments remain: {", ".join(remaining)}')
    result = {
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'scope': 'Checkout preservation, materialization, baseline/requirement coverage, source evidence hashes and local links. Not a semantic or runtime audit.',
        'required_repository_count': len(expected), 'checkout_count': len(checkouts),
        'baseline_sha256': baseline_hash, 'assessments_complete': complete,
        'assessments_remaining': remaining, 'required_complete_gate': args.require_complete,
        'issues': issues, 'checkouts': checkouts,
    }
    if args.write:
        (STUDY / 'progress.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'checkouts'}, indent=2))
    raise SystemExit(1 if issues else 0)


if __name__ == '__main__':
    main()
