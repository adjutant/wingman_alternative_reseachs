"""Regression checks for boundary escapes; never runs candidate code."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import unittest

from validate_portability import ROOT, check_tree, literals, local_reference


class PortabilityTests(unittest.TestCase):
    def setUp(self):
        scratch=ROOT/'.run'
        scratch.mkdir(exist_ok=True)
        self.temp=TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'research'
        self.root.mkdir()
        self.write('generic/assessments/portability-runtime-paths.json', json.dumps({'reviewed_literals':[]}))
        for name in ['checkouts.json','task-management/checkouts.json']:
            self.write(name,json.dumps({'repositories':[{'directory':'candidate/repo'}]}))

    def write(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text);return p

    def check(self,name,text,**kwargs):
        self.write(name,text)
        return check_tree(self.root,[name],**kwargs)['issues']

    def test_arbitrary_unix_windows_home_and_file_urls(self):
        for target in ['/unfamiliar-volume/account/source.ts', 'Z:\\other\\source.ts',
                       '\\\\host\\share\\source.ts', '~/other/source.ts', '$HOME/other/source.ts',
                       'file:///arbitrary/source.ts', '$UNRELATED_STORAGE/deps/source.ts',
                       '%USERPROFILE%\\project\\source.ts']:
            with self.subTest(target=target):
                self.assertTrue(self.check('evidence.log',target))
                self.assertIsNotNone(local_reference(self.root,self.root/'index.html',target))

    def test_relative_and_encoded_escape(self):
        for target in ['../secret.md','%2e%2e/secret.md','%2foutside/source.md']:
            with self.subTest(target=target):
                self.assertTrue(self.check('README.md',f'[evidence]({target})'))

    def test_symlink_escape(self):
        outside=self.root.parent/'outside.md';outside.write_text('private')
        (self.root/'escape.md').symlink_to(outside)
        self.assertTrue(self.check('README.md','[evidence](escape.md)'))
        self.assertTrue(check_tree(self.root,['escape.md'])['issues'])

    def test_internal_parent_link(self):
        self.write('assets/local.css','body {}')
        self.assertEqual(self.check('guide/README.md','[asset](../assets/local.css)'),[])

    def test_source_import_and_asset_boundary(self):
        for name,text in [('probe.ts', "import x from '../foreign/source.ts';"),
                          ('assets/report.css','body { background: url(../../foreign.png) }'),
                          ('index.html','<img src="../foreign.png">')]:
            with self.subTest(name=name):self.assertTrue(self.check(name,text))
        self.assertEqual(self.check('probe.ts',"import x from 'package-name'; import fs from 'node:fs';"),[])

    def test_manifest_path_escape(self):
        self.assertTrue(self.check('checkouts.json',json.dumps({'repositories':[{'directory':'../foreign'}]})))

    def test_python_root_escape(self):
        self.assertTrue(self.check('tools/unsafe.py','file = ROOT.parent / "outside"'))
        self.assertTrue(self.check('tools/unsafe.py','file = ROOT / "../../outside"'))

    def test_archived_embedded_markdown(self):
        data={'documents':[{'path':'qa01.md','text':'[source](../../../../outside.md)'}]}
        self.assertTrue(self.check('generic/assessments/_audits/original-audit-prose.json',json.dumps(data)))

    def test_reports_only_allows_only_declared_checkouts(self):
        self.assertEqual(self.check('index.html','<a href="candidate/repo/src/a.ts">source</a>',reports_only=True),[])
        self.assertTrue(self.check('index.html','<a href="undeclared/repo/a.ts">source</a>',reports_only=True))
        self.assertTrue(self.check('index.html','<a href="missing.md">evidence</a>',reports_only=True))
        self.assertTrue(self.check('index.html','<a href="candidate/repo/a.ts">source</a>'))

    def test_runtime_classification_cannot_authorize_dependency(self):
        self.write('generic/assessments/portability-runtime-paths.json',json.dumps({'reviewed_literals':[
            {'value':'/runtime/state','files':['probe.ts'],'reason':'Candidate runtime description'}]}))
        self.assertTrue(self.check('probe.ts',"import x from '/runtime/state';"))
        self.assertTrue(self.check('other.log','/runtime/state'))

    def test_route_description_requires_review(self):
        self.assertTrue(self.check('evidence.log','GET /api/task status 200'))
        self.write('generic/assessments/portability-runtime-paths.json',json.dumps({'reviewed_literals':[
            {'value':'/api/task','files':['evidence.log'],'reason':'Recorded HTTP route'}]}))
        self.assertEqual(self.check('evidence.log','GET /api/task status 200'),[])


if __name__=='__main__':unittest.main()
