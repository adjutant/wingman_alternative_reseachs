#!/usr/bin/env python3
"""Materialize the task-management study's pinned source checkouts.

Never installs or executes a candidate application. Existing source checkouts
are verified and reused without fetching, resetting or changing configuration.
New checkouts contain the full tracked tree; LFS payload download is disabled.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
from threading import Lock

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / 'task-management'
MANIFEST = STUDY / 'checkouts.json'
LOCK = Lock()


def stamp():
    return datetime.now(timezone.utc).isoformat()


def git(directory, *args, timeout=1800):
    env = dict(os.environ, GIT_LFS_SKIP_SMUDGE='1', GIT_TERMINAL_PROMPT='0')
    process = subprocess.run(
        ['git', '-c', 'core.hooksPath=/dev/null', '-C', str(directory), *args],
        env=env, capture_output=True, timeout=timeout,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.decode(errors='replace')[-2500:])
    return process.stdout


def save(data):
    temporary = MANIFEST.with_suffix('.json.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.replace(MANIFEST)


def inspect(record):
    directory = ROOT / record['directory']
    head = git(directory, 'rev-parse', 'HEAD').decode().strip()
    if record.get('requested_commit') and head != record['requested_commit']:
        raise RuntimeError(f'HEAD differs from requested commit: {head}')
    status = git(directory, 'status', '--porcelain').decode()
    if status:
        raise RuntimeError('Source checkout is not clean; it was left unchanged')
    paths = git(directory, 'ls-files', '-z')
    tree = git(directory, 'ls-tree', 'HEAD').decode()
    sparse_paths = [line[2:] for line in git(directory, 'ls-files', '-t').decode().splitlines()
                    if line.startswith('S ')]
    if sparse_paths:
        raise RuntimeError(f'{len(sparse_paths)} tracked paths are excluded by sparse checkout')
    # Missing paths are checked without following tracked symlinks. Submodule
    # directories may be empty; record them rather than implying recursive clone.
    tracked = [path.decode() for path in paths.split(b'\0') if path]
    missing = [path for path in tracked if not os.path.lexists(directory / path)]
    if missing:
        raise RuntimeError(f'{len(missing)} tracked paths are missing: {missing[:5]}')
    submodules = git(directory, 'ls-files', '--stage').decode()
    submodules = [line.split('\t', 1)[1] for line in submodules.splitlines() if line.startswith('160000 ')]
    instruction_paths = [path for path in tracked if Path(path).name in {'AGENTS.md', 'CLAUDE.md', 'GEMINI.md'}]
    return {
        'commit': head, 'git_status': status, 'tracked_file_count': len(tracked),
        'tracked_paths_sha256': hashlib.sha256(paths).hexdigest(),
        'root_tree_sha256': hashlib.sha256(tree.encode()).hexdigest(),
        'directory_inode': directory.stat().st_ino,
        'missing_tracked_paths': [], 'sparse_paths': [], 'submodule_paths': submodules,
        'instruction_paths': instruction_paths,
        'lfs_payloads': 'Not downloaded; tracked pointer files retained when present',
        'verified_at': stamp(),
    }


def checkout(record, data):
    directory = ROOT / record['directory']
    with LOCK:
        record['state'] = 'verifying' if directory.exists() else 'fetching'
        record['started_at'] = stamp()
        record.pop('error', None)
        save(data)
    if not directory.exists():
        directory.mkdir(parents=True)
        git(directory, 'init', '--quiet')
        git(directory, 'remote', 'add', 'origin', record['url'])
    if record['mode'] == 'new' and not record.get('commit'):
        with LOCK:
            record['state'] = 'fetching'
            save(data)
        git(directory, 'fetch', '--quiet', '--no-tags', '--depth=1', '--filter=blob:none',
            'origin', record.get('requested_commit') or 'HEAD')
        with LOCK:
            record['state'] = 'materializing'
            save(data)
        git(directory, 'checkout', '--quiet', '--detach', 'FETCH_HEAD')
    result = inspect(record)
    with LOCK:
        record.update(result)
        record['state'] = 'complete'
        record['completed_at'] = stamp()
        save(data)
    return f"{record['slug']}: {result['commit'][:12]}, {result['tracked_file_count']} tracked files, clean"


def initial_manifest():
    sources = json.loads((ROOT / 'generic/assessments/agent-task-coordination/sources.json').read_text())
    entries = []
    for source in sources['repositories']:
        slug = source['slug']
        reuse = slug in {'paperclip', 'agent-swarm'}
        entries.append({
            'slug': slug, 'url': source['url'], 'requested_commit': source['commit'],
            'directory': f'{slug}/repo' if reuse else f'task-management/{slug}/repo',
            'mode': 'preserved' if reuse else 'new', 'state': 'pending',
            'assessment': f'task-management/{slug}/assessment/ASSESSMENT.md',
            'role': 'integration' if slug == 'plane-mcp' else 'system or companion',
        })
    entries.extend([
        {'slug': 'gitlab', 'url': 'https://gitlab.com/gitlab-org/gitlab.git',
         'directory': 'task-management/gitlab/repo', 'mode': 'new', 'state': 'pending',
         'assessment': 'task-management/gitlab/assessment/ASSESSMENT.md', 'role': 'system'},
        {'slug': 'agent-mail-python', 'url': 'https://github.com/Dicklesworthstone/mcp_agent_mail.git',
         'requested_commit': '9138f34b1ed220235dbfeaa3f1fc9fe4444f4e72',
         'directory': 'task-management/agent-mail-python/repo', 'mode': 'new', 'state': 'pending',
         'assessment': 'task-management/agent-mail-python/assessment/ASSESSMENT.md', 'role': 'historical companion'},
        {'slug': 'taiga-front', 'url': 'https://github.com/taigaio/taiga-front.git',
         'directory': 'task-management/taiga-front/repo', 'mode': 'new', 'state': 'pending',
         'assessment': 'task-management/taiga-front/assessment/ASSESSMENT.md', 'role': 'frontend supporting Taiga'},
    ])
    return {'baseline': 'AGENT_TASK_MANAGEMENT.md', 'created_at': stamp(),
            'scope': 'All repositories in the task coordination study, GitLab, the historical Python communication companion, and the Taiga frontend.',
            'checkout_policy': 'Full tracked worktrees at pinned commits; no sparse checkout; source code ignored by outer research Git; no candidate application executed.',
            'repositories': sorted(entries, key=lambda r: r['slug'])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workers', type=int, default=4)
    parser.add_argument('--only', action='append', default=[])
    args = parser.parse_args()
    STUDY.mkdir(exist_ok=True)
    data = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else initial_manifest()
    save(data)
    selected = [r for r in data['repositories'] if not args.only or r['slug'] in args.only]
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = {pool.submit(checkout, record, data): record for record in selected}
        for job in as_completed(jobs):
            record = jobs[job]
            try:
                print(job.result(), flush=True)
            except Exception as error:
                with LOCK:
                    record['state'] = 'failed'
                    record['error'] = str(error)
                    save(data)
                failures.append(record['slug'])
                print(f"{record['slug']}: FAILED: {error}", flush=True)
    print(json.dumps({'complete': sum(r['state'] == 'complete' for r in data['repositories']),
                      'total': len(data['repositories']), 'failed_this_run': failures}), flush=True)
    raise SystemExit(1 if failures else 0)


if __name__ == '__main__':
    main()
