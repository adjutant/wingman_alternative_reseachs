"""Read the Markdown repository profiles used by both published studies."""
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re


PROFILE_NAME = 'REPOSITORY_PROFILE.md'
INVENTORY_MD = 'REPOSITORY_INVENTORY.md'
INVENTORY_HTML = 'repositories.html'
SNAPSHOT_NOTE = (
    'Watches are GitHub subscribers. '
    'First and last commits are from the default branch at collection time. '
    'Technical findings describe the pinned assessments; the assessed commit can differ from the last commit.'
)
GROUP_NAMES = {
    'standing-teams': 'Standing teams and organization control planes',
    'workbenches': 'Coding workbenches and session orchestration',
    'delivery-engines': 'Delivery engines and task runners',
    'workflow-layers': 'Workflow and host orchestration layers',
    'infrastructure': 'Infrastructure and coordination primitives',
    'agent-harnesses': 'Personal assistants and base harnesses',
    'task': 'Task management and coordination companions',
}
METADATA_FIELDS = (
    'Name', 'Repository', 'Snapshot date', 'Default branch', 'Stars', 'Forks', 'Watches',
    'First commit', 'First commit SHA', 'Last commit', 'Last commit SHA', 'Counts source',
)
TABLE_FIELDS = ('Name', 'Repo link', 'Stars', 'Forks', 'Watches', 'First commit', 'Last commit', 'Description')


def repo_identity(url):
    return url.lower().removesuffix('.git')


@dataclass
class Profile:
    path: Path
    group: str
    fields: dict[str, str]
    findings: str

    @property
    def report(self):
        return self.path.parent.parent / 'index.html'

    def table_values(self):
        return [
            self.fields['Repository'],
            *(f"{int(self.fields[key]):,}" for key in ('Stars', 'Forks', 'Watches')),
            self.fields['First commit'],
            self.fields['Last commit'],
            self.findings,
        ]


def load_profiles(root, checkouts, task_checkouts):
    """Return each study profile, plus a deduplicated inventory grouped by upstream."""
    by_path = {}
    by_repo = {}
    for task_study, manifest in ((False, checkouts), (True, task_checkouts)):
        for item in manifest['repositories']:
            assessment = item['assessment']
            path = (root / assessment).with_name(PROFILE_NAME)
            content = path.read_text()
            header, marker, rest = content.partition('\n## Findings\n')
            findings = rest.split('\n## ', 1)[0].strip()
            pairs = re.findall(r'^- \*\*([^:]+):\*\* (.+)$', header, re.M)
            fields = dict(pairs)
            identity = repo_identity(item['url'])
            try:
                valid = (
                    tuple(key for key, _ in pairs) == METADATA_FIELDS
                    and marker and findings and '\n' not in findings
                    and repo_identity(fields['Repository']) == identity
                    and all(re.fullmatch(r'[0-9]+', fields[key]) for key in ('Stars', 'Forks', 'Watches'))
                    and all(re.fullmatch(r'[a-f0-9]{40}', fields[key]) for key in ('First commit SHA', 'Last commit SHA'))
                    and date.fromisoformat(fields['First commit']) <= date.fromisoformat(fields['Last commit'])
                    and date.fromisoformat(fields['Last commit']) <= date.fromisoformat(fields['Snapshot date'])
                )
            except ValueError:
                valid = False
            if not valid:
                raise ValueError(f'Invalid repository profile: {path.relative_to(root)}')
            profile = Profile(path, 'task' if task_study else item['group'], fields, findings)
            studies = by_repo.setdefault(identity, [])
            if studies and fields != studies[0].fields:
                raise ValueError(f'Repository snapshot differs between studies: {fields["Repository"]}')
            studies.append(profile)
            by_path[path] = profile
    return by_path, by_repo


def grouped_inventory(by_repo):
    for group, title in GROUP_NAMES.items():
        studies = [items for items in by_repo.values() if items[0].group == group]
        if studies:
            yield group, title, sorted(studies, key=lambda items: items[0].fields['Name'].casefold())


def inventory_markdown(root, by_repo):
    lines = ['# Repository inventory', '',
             f'{len(by_repo)} active repositories. Projects assessed in both studies have one row and two profile links.',
             '', snapshot_note(by_repo), '',
             '[HTML repository inventory](repositories.html) · [Research overview](index.html)', '']
    for _, title, group in grouped_inventory(by_repo):
        lines += [f'## {title}', '',
                  '| ' + ' | '.join(TABLE_FIELDS) + ' |',
                  '|---|---|---:|---:|---:|---|---|---|']
        for primary, *others in group:
            label = f'[{primary.fields["Name"]}]({primary.path.relative_to(root)})'
            for other in others:
                label += f' · [Task study]({other.path.relative_to(root)})'
            values = [label, *primary.table_values()]
            lines.append('| ' + ' | '.join(value.replace('|', '\\|') for value in values) + ' |')
        lines.append('')
    return '\n'.join(lines)


def snapshot_note(by_repo):
    dates = sorted({items[0].fields['Snapshot date'] for items in by_repo.values()})
    return f'GitHub snapshot dates: {", ".join(dates)}. {SNAPSHOT_NOTE}'
