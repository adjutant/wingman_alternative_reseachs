#!/usr/bin/env python3
"""Serve the research reports on a local network with no extra dependencies."""
from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = {
    'index.html', 'README.md', 'AGENTS.md', 'WINGMAN_PURPOSE.md', 'AGENT_TASK_MANAGEMENT.md',
    'coverage.json', 'checkouts.json', 'migration.json', 'validation.json',
}


class ReportHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, directory=ROOT, projects=(), task_projects=(), include_source=False, **kwargs):
        self.root = Path(directory).resolve()
        self.projects = frozenset(projects)
        self.task_projects = frozenset(task_projects)
        self.include_source = include_source
        super().__init__(*args, directory=str(self.root), **kwargs)

    def is_public(self, parts):
        if any(part.startswith('.') for part in parts):
            return False
        if not parts:
            return True
        if len(parts) == 1 and parts[0] in ROOT_FILES:
            return True
        if parts[0] == 'assets':
            return True
        if parts[0] == 'generic':
            return len(parts) == 1 or parts[1] in {
                'index.html', 'purpose.html', 'method.html', 'task-coordination.html', 'assessments',
            }
        if parts[0] == 'task-management':
            if len(parts) == 2 and parts[1] in {
                'index.html', 'purpose.html', 'README.md', 'COMPARISON.md', 'REQUIREMENT_MATRIX.md',
                'COMPLETION_AUDIT.md', 'checkouts.json', 'progress.json', 'catalog.json', 'publication.json',
            }:
                return True
            if len(parts) >= 2 and parts[1] in self.task_projects:
                return len(parts) == 2 or parts[2] in {
                    'index.html', 'assessment', *({'repo'} if self.include_source else set()),
                }
            return len(parts) == 1
        if parts[0] in self.projects:
            return len(parts) == 1 or parts[1] in {
                'index.html', 'assessment', *({'repo'} if self.include_source else set()),
            }
        return False

    def send_head(self):
        # Check both the URL and resolved path so symlinks cannot bypass the boundary.
        path = unquote(urlsplit(self.path).path)
        parts = tuple(part for part in path.split('/') if part)
        if '\x00' in path or '\\' in path or not self.is_public(parts):
            self.send_error(403, 'This path is not part of the hosted reports')
            return None
        try:
            resolved = (self.root.joinpath(*parts)).resolve()
            relative = resolved.relative_to(self.root)
        except (OSError, RuntimeError, ValueError):
            self.send_error(403, 'This path is outside the report directory')
            return None
        if not self.is_public(relative.parts):
            self.send_error(403, 'This path is not part of the hosted reports')
            return None
        return super().send_head()

    def list_directory(self, path):
        self.send_error(404, 'No report index at this path')
        return None


def make_server(host, port, directory=ROOT, include_source=False):
    root = Path(directory).resolve()
    manifest = json.loads((root / 'coverage.json').read_text())
    projects = {Path(item['directory']).parts[0] for item in manifest['repositories']}
    task_manifest = root / 'task-management/checkouts.json'
    task_projects = {item['slug'] for item in json.loads(task_manifest.read_text())['repositories']} if task_manifest.exists() else set()
    handler = partial(ReportHandler, directory=root, projects=projects, task_projects=task_projects,
                      include_source=include_source)
    return ThreadingHTTPServer((host, port), handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host', default='0.0.0.0', help='Bind address (default: all IPv4 interfaces)')
    parser.add_argument('--port', type=int, default=8765, help='TCP port (default: 8765)')
    parser.add_argument('--include-source', action='store_true', help='Also serve code links under project repo/ folders')
    args = parser.parse_args()
    try:
        server = make_server(args.host, args.port, include_source=args.include_source)
    except (OSError, ValueError) as error:
        parser.exit(1, f'Cannot start report server: {error}\n')
    with server:
        address, port = server.server_address
        print(f'Listening on {address}:{port}; reports from {ROOT}', flush=True)
        if address != '0.0.0.0':
            print(f'Open http://{address}:{port}/', flush=True)
        print('Press Ctrl-C to stop.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
