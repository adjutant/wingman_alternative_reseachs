"""HTTP checks for the report server. Does not run candidate product code."""
from contextlib import contextmanager
from http.client import HTTPConnection
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread
import unittest

from serve_reports import make_server


class ReportServerTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'reports'
        self.root.mkdir()
        files = {
            'index.html': '<h1>Overview</h1>',
            'repositories.html': '<h1>Repository inventory</h1>',
            'REPOSITORY_INVENTORY.md': '# Repository inventory',
            'project/index.html': '<h1>Project</h1>',
            'project/assessment/ASSESSMENT.md': '# Assessment',
            'project/assessment/REPOSITORY_PROFILE.md': '# Repository profile',
            'project/repo/source.txt': 'source checkout',
            'project/repo/.git/config': 'private Git config',
            'assets/report.css': 'body { color: navy; }',
            'assets/report.js': 'console.log("report");',
            'generic/purpose.html': '<h1>Purpose</h1>',
            'generic/task-coordination.html': '<h1>Agent task coordination</h1>',
            'AGENT_TASK_MANAGEMENT.md': '# Task baseline',
            'task-management/index.html': '<h1>Task management</h1>',
            'task-management/purpose.html': '<h1>Task baseline</h1>',
            'task-management/checkouts.json': json.dumps({'repositories': [{'slug': 'candidate'}]}),
            'task-management/candidate/index.html': '<h1>Candidate assessment</h1>',
            'task-management/candidate/assessment/review.json': '{}',
            'task-management/candidate/repo/source.txt': 'candidate source',
            'task-management/candidate/repo/.git/config': 'private candidate Git config',
            'task-management/unlisted/index.html': 'not a report',
            '.git/config': 'private Git config',
            '.env': 'private configuration',
            'private.txt': 'unpublished file',
            'coverage.json': json.dumps({'repositories': [{'directory': 'project/repo'}]}),
        }
        for name, body in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(body)
        outside = self.root.parent / 'outside.txt'
        outside.write_text('outside report root')
        (self.root / 'assets/escape.txt').symlink_to(outside)
        (self.root / 'assets/source.txt').symlink_to(self.root / 'project/repo/source.txt')

    @contextmanager
    def serving(self, include_source=False):
        server = make_server('127.0.0.1', 0, self.root, include_source)
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield server.server_port
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def request(self, port, path, method='GET'):
        connection = HTTPConnection('127.0.0.1', port, timeout=3)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_reports_assets_and_head(self):
        with self.serving() as port:
            for path in ['/', '/repositories.html', '/REPOSITORY_INVENTORY.md', '/project/',
                         '/generic/purpose.html', '/generic/task-coordination.html',
                         '/project/assessment/ASSESSMENT.md', '/project/assessment/REPOSITORY_PROFILE.md',
                         '/assets/report.css', '/assets/report.js']:
                with self.subTest(path=path):
                    self.assertEqual(self.request(port, path)[0], 200)
            status, headers, body = self.request(port, '/assets/report.css', 'HEAD')
            self.assertEqual(status, 200)
            self.assertIn('text/css', headers['Content-type'])
            self.assertGreater(int(headers['Content-Length']), 0)
            self.assertEqual(body, b'')

    def test_private_paths_and_directory_listing_are_blocked(self):
        with self.serving() as port:
            for path in ['/.git/config', '/.env', '/private.txt', '/project/repo/source.txt', '/assets/escape.txt', '/assets/source.txt', '/assets/%2e%2e/.git/config', '/assets/%00.txt', '/assets/%5cprivate.txt']:
                with self.subTest(path=path):
                    self.assertEqual(self.request(port, path)[0], 403)
            self.assertEqual(self.request(port, '/project/assessment/')[0], 404)

    def test_source_is_an_explicit_option_and_git_stays_private(self):
        with self.serving(include_source=True) as port:
            self.assertEqual(self.request(port, '/project/repo/source.txt')[2], b'source checkout')
            self.assertEqual(self.request(port, '/project/repo/.git/config')[0], 403)

    def test_task_study_routes_and_source_boundary(self):
        for include_source in [False, True]:
            with self.subTest(include_source=include_source), self.serving(include_source) as port:
                for path in ['/AGENT_TASK_MANAGEMENT.md', '/task-management/',
                             '/task-management/purpose.html', '/task-management/checkouts.json',
                             '/task-management/candidate/', '/task-management/candidate/assessment/review.json']:
                    self.assertEqual(self.request(port, path)[0], 200, path)
                self.assertEqual(self.request(port, '/task-management/candidate/repo/source.txt')[0],
                                 200 if include_source else 403)
                for path in ['/task-management/candidate/repo/.git/config',
                             '/task-management/unlisted/index.html', '/task-management/private.txt']:
                    self.assertEqual(self.request(port, path)[0], 403, path)


if __name__ == '__main__':
    unittest.main()
