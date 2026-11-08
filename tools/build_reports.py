# /// script
# requires-python = ">=3.12"
# dependencies = ["Markdown==3.7", "beautifulsoup4==4.12.3"]
# ///
"""Build local Wingman reports. Do not read or modify candidate source trees."""
from pathlib import Path
import csv
import hashlib
import html
import json
import os
import re
import shutil
from urllib.parse import unquote

import markdown
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
E = html.escape
coverage = json.loads((ROOT / 'coverage.json').read_text())
checkouts = json.loads((ROOT / 'checkouts.json').read_text())
metadata = {Path(x['directory']).parts[0]: x for x in checkouts['repositories']}
with (ROOT / 'tools/project_briefs.tsv').open() as stream:
    briefs = {x['slug']: x for x in csv.DictReader(stream, delimiter='\t')}
features = [(m[1], m[2].strip()) for m in re.finditer(
    r'^\| (F\d{2}) \| ([^|]+)\|',
    (ROOT / 'generic/assessments/ASSESSMENT_GUIDE.md').read_text(), re.M)]
assert len(features) == 24
assert len(briefs) == len(coverage['repositories']) == 75
task_checkouts = json.loads((ROOT / 'task-management/checkouts.json').read_text())
task_catalog = json.loads((ROOT / 'task-management/catalog.json').read_text())
task_briefs = {item['slug']: item for item in task_catalog['projects']}
task_features = [(m[1], m[2].strip()) for m in re.finditer(
    r'^\| (T\d{2}) \| ([^|]+)\|', (ROOT / 'AGENT_TASK_MANAGEMENT.md').read_text(), re.M)]
assert len(task_features) == 24
assert set(task_briefs) == {item['slug'] for item in task_checkouts['repositories']}

GROUPS = {
    'standing-teams': 'Standing teams', 'workbenches': 'Coding workspaces',
    'delivery-engines': 'Delivery engines', 'workflow-layers': 'Workflow layers',
    'infrastructure': 'Infrastructure', 'agent-harnesses': 'Agent runtimes',
}
NAMES = {'codex-autorunner': 'CAR / Codex Autorunner', 'open-swe': 'Open SWE / Robin',
         'openhands': 'OpenHands / Agent Canvas', 'agentopology': 'AgenTopology',
         'claw-empire': 'Claw-Empire', 'teammcp': 'TeamMCP', 'tinyagi': 'TinyAGI',
         'multica': 'Multica', 'scion': 'Scion', 'gstack': 'gstack', 'amux': 'amux',
         'hcom': 'Hcom', 'ax': 'AX', 'cmux': 'cmux', 'swe-agent': 'SWE-agent',
         'superplane': 'SuperPlane', 'openclaw': 'OpenClaw', 'openrig': 'OpenRig',
         'swarmos': 'SwarmOS', 'rocketride-server': 'RocketRide',
         'deepcode': 'DeepCode', 'myclaude': 'myclaude', 'ruflo': 'Ruflo',
         'multi-agent-shogun': 'Multi-Agent Shogun', 'agentrail': 'AgentRail',
         'companyhelm': 'CompanyHelm', 'gastown': 'Gas Town',
         'agent-of-empires': 'Agent of Empires', 'cli-agent-orchestrator': 'CLI Agent Orchestrator',
         'continuous-claude-v3': 'Continuous Claude v3', 'multiclaude': 'multiclaude',
         'oh-my-codex': 'oh-my-codex', 'oh-my-claudecode': 'oh-my-claudecode',
         'oh-my-openagent': 'oh-my-openagent'}

def name(slug):
    return NAMES.get(slug, slug.replace('-', ' ').title())

def rel(target, page):
    return os.path.relpath(target, page.parent)

report_map = {ROOT / x['report']: ROOT / Path(x['directory']).parts[0] / 'index.html'
              for x in coverage['repositories']}
report_map[ROOT / 'WINGMAN_PURPOSE.md'] = ROOT / 'generic/purpose.html'
report_map[ROOT / 'generic/assessments/ARCHITECTURE.md'] = ROOT / 'generic/index.html'
report_map[ROOT / 'generic/assessments/METHOD.md'] = ROOT / 'generic/method.html'
report_map[ROOT / 'generic/assessments/AGENT_TASK_COORDINATION.md'] = ROOT / 'generic/task-coordination.html'
report_map[ROOT / 'AGENT_TASK_MANAGEMENT.md'] = ROOT / 'task-management/purpose.html'
report_map[ROOT / 'task-management/COMPARISON.md'] = ROOT / 'task-management/index.html'
for item in task_checkouts['repositories']:
    report_map[ROOT / item['assessment']] = ROOT / 'task-management' / item['slug'] / 'index.html'
for x in coverage['repositories']:
    folder = (ROOT / x['report']).parent
    for chapter in folder.glob('*.md'):
        if chapter.name != 'ASSESSMENT.md':
            report_map[chapter] = (ROOT / Path(x['directory']).parts[0] / 'index.html',
                                   'support-' + chapter.stem.lower().replace('_', '-'))

def render(path, page, prefix):
    body = path.read_text()
    # External URLs remain complete and visible. Markdown's link extension is not used.
    body = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'\2', body)
    doc = BeautifulSoup(markdown.markdown(body, extensions=['tables', 'fenced_code', 'toc', 'sane_lists']), 'html.parser')
    for tag in doc.select('h1'):
        tag.name = 'h2'
    for tag in doc.select('[id]'):
        tag['id'] = prefix + '-' + tag['id']
    for tag in doc.select('a[href]'):
        href = tag['href']
        if href.startswith('#'):
            tag['href'] = '#' + prefix + '-' + href[1:]
        elif not re.match(r'\w+:', href):
            raw, sep, anchor = href.partition('#')
            dest = Path(os.path.normpath(path.parent / unquote(raw)))
            mapped = report_map.get(dest)
            if isinstance(mapped, tuple):
                dest, anchor = mapped
                sep = '#'
            elif mapped:
                dest = mapped
                anchor, sep = '', ''
            tag['href'] = rel(dest, page) + (sep + anchor if sep else '')
    for table in doc.select('table'):
        wrap = doc.new_tag('div', attrs={'class': 'table-scroll', 'tabindex': '0', 'role': 'region', 'aria-label': 'Technical comparison table'})
        table.wrap(wrap)
        for th in table.select('thead th'):
            th['scope'] = 'col'
        for row in table.select('tbody tr'):
            first = row.find(['td', 'th'])
            if first and re.fullmatch(r'T\d{2}', first.get_text(strip=True)):
                row['id'] = prefix + '-' + first.get_text(strip=True).lower()
    for block in doc.select('pre'):
        block['tabindex'] = '0'
        block['role'] = 'region'
        block['aria-label'] = 'Code or source excerpt'
    # Complete URLs appear as bare text. Break opportunities prevent overflow.
    for text in list(doc.find_all(string=True)):
        if text.parent.name in ('code', 'pre', 'a'):
            continue
        if re.search(r'https?://', str(text)):
            text.parent['class'] = list(text.parent.get('class', [])) + ['url-text']
    return str(doc)

def shell(page, title, subtitle, body, section, toc='', review_date='05 NOV 2026'):
    base = lambda p: E(rel(ROOT / p, page))
    links = [('index.html', 'Overview', 'overview'), ('generic/index.html', 'Architecture findings', 'architecture'),
             ('generic/purpose.html', 'Wingman purpose', 'purpose'), ('generic/method.html', 'Method and evidence', 'method'),
             ('task-management/index.html', 'Agent task management', 'tasks'),
             ('generic/task-coordination.html', 'Initial task screening', 'coordination')]
    nav = ''.join(f'<a class="nav-link {"active" if key == section else ""}" href="{base(path)}"'
                  f'{" aria-current=page" if key == section else ""}>{label}</a>' for path, label, key in links)
    groupnav = ''.join(f'<a class="nav-link" href="{base("index.html")}#group-{slug}">{label}</a>' for slug, label in GROUPS.items())
    css = base('assets/report.css'); js = base('assets/report.js')
    result = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="{E(subtitle, quote=True)}"><title>{E(title)} · Wingman Research</title>
<link rel="icon" href="{base('assets/icons/signal-dash.svg')}" type="image/svg+xml">
<link rel="stylesheet" href="{css}"><script defer src="{js}"></script></head>
<body><a class="skip-link" href="#content">Skip to content</a>
<aside id="sidebar" class="sidebar" aria-label="Research navigation">
<a class="brand" href="{base('index.html')}"><img src="{base('assets/icons/signal-dash.svg')}" width="20" height="12" alt="">WINGMAN<span>RESEARCH</span></a>
<p class="nav-label">Research collection</p><nav>{nav}</nav>
<p class="nav-label">Source groups</p><nav>{groupnav}</nav>
<div class="sidebar-bottom"><strong>Two source studies</strong><p>75 organization snapshots.<br>25 task coordination codebases.<br>Evidence at pinned revisions.</p><a href="{base('README.md')}">Open the file guide →</a></div></aside>
<div class="workspace"><header class="topbar"><div><button class="menu-toggle" type="button" aria-controls="sidebar" aria-expanded="false">Menu</button><a href="{base('index.html')}">Wingman Research</a><span class="crumb">/</span><span>{E(title)}</span></div><span class="topbar-note">SOURCE REVIEW · {E(review_date)}</span></header>
<main id="content" class="content"><div class="page-heading"><p class="eyebrow"><span></span>PERSONAL DEVELOPMENT ORGANIZATION</p><h1>{E(title)}</h1><p class="subtitle">{E(subtitle)}</p></div>
{toc}{body}
<footer><p>Wingman Research · Source findings at pinned commits. Read the evidence limits for each project.</p><a href="{base('index.html')}">Return to overview <img src="{base('assets/icons/arrow-right.svg')}" width="14" height="14" alt=""></a></footer>
</main></div></body></html>'''
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(result)

def generic_contents(body):
    doc = BeautifulSoup(body, 'html.parser')
    headings = doc.select('h2[id]')
    return '<nav class="contents" aria-label="Report contents"><strong>In this report</strong><div>' + ''.join(
        f'<a href="#{E(h["id"])}">{E(h.get_text())}</a>' for h in headings
    ) + '</div></nav>'

def build_project(item):
    slug = Path(item['directory']).parts[0]; project = ROOT / slug
    page = project / 'index.html'; brief = briefs[slug]; meta = metadata[slug]
    source = ROOT / item['report']
    doc = BeautifulSoup(render(source, page, 'assessment'), 'html.parser')
    toc = '<nav class="contents" aria-label="Report contents"><strong>In this report</strong><div>'
    toc += '<a href="#decision">Decision summary</a>'
    for heading in doc.select('h2[id]'):
        toc += f'<a href="#{E(heading["id"])}">{E(heading.get_text())}</a>'
    toc += '<a href="#source-record">Source and evidence</a></div></nav>'
    # Render the complete technical assessment after a short, authored decision brief.
    chapters = ''
    for chapter in sorted(source.parent.glob('*.md')):
        if chapter.name == 'ASSESSMENT.md': continue
        anchor = 'support-' + chapter.stem.lower().replace('_', '-')
        chapters += f'<section id="{anchor}" class="technical supporting">{render(chapter, page, anchor)}</section>'
    audit = E(rel(ROOT / item['independent_audit'], page))
    body = f'''<section id="decision" class="decision"><h2>Decision summary</h2>
<div class="brief-columns"><div><h3>Useful for Wingman</h3><p>{E(brief['use'])}</p></div><div><h3>Adoption boundary</h3><p>{E(brief['boundary'])}</p></div></div>
<p class="scope-note">Source assessment at the commit below. Runtime limits appear in the technical report.</p></section>
<dl class="facts"><div><dt>Source group</dt><dd>{E(GROUPS[meta['group']])}</dd></div><div><dt>Commit</dt><dd><code>{E(item['commit'])}</code></dd></div><div><dt>Coverage</dt><dd>24 Wingman features</dd></div></dl>
<article id="technical-assessment" class="technical">{str(doc)}</article>{chapters}
<section id="source-record"><h2>Source and evidence</h2><p class="url-text">{E(item['url'])}</p>
<ul><li><a href="repo/">Open the pinned source checkout</a></li><li><a href="assessment/ASSESSMENT.md">Read the Markdown assessment</a></li>
<li><a href="{audit}">Read the historical independent source audit</a></li><li><a href="../generic/method.html">Read the method and evidence limits</a></li></ul></section>
<nav class="report-switch" aria-label="Adjacent project reports">'''
    ordered = sorted(briefs); i = ordered.index(slug)
    for target, label in [(ordered[(i-1) % len(ordered)], 'Previous project'), (ordered[(i+1) % len(ordered)], 'Next project')]:
        body += f'<a href="../{target}/index.html">{label}: {E(name(target))}</a>'
    body += '</nav>'
    shell(page, name(slug), 'Technical assessment against Wingman’s development organization.', body, 'project', toc)

def build_master():
    page = ROOT / 'index.html'
    findings = '''<section id="findings"><h2>High-impact findings</h2><div class="findings">
<p><strong>Keep organization and execution separate.</strong> Durable projects, role ownership, decisions, and acceptance need explicit records. A coding session cannot supply all of them.</p>
<p><strong>Study several foundations.</strong> Paperclip, OpenRig, Multica, Crewly, and Agent Swarm provide useful organization mechanisms. Their workflow boundaries differ.</p>
<p><strong>Protect continuity and ownership.</strong> Separate agent, session, task, and attempt identity. Reject stale results. Distinguish delivery from handling and acceptance.</p>
<p><strong>Build the product journey.</strong> Connect discovery, specifications, technical assignments, integrated verification, and human acceptance. Keep that evidence after delivery.</p></div>
<p><a href="generic/index.html">Read the architecture findings →</a></p></section>'''
    intro = '''<section id="purpose"><h2>What Wingman must deliver</h2>
<p class="lead">One person directs a persistent software-development organization through conversation.</p>
<p>Butler receives Telegram requests. ProjectMaster identifies the product and supervises progress. ProductMaster defines the product. TechMaster assigns technical work. Independent specialists implement and verify it.</p>
<p>The organization supports parallel products and work across hosts. Shared records connect tasks, conversations, decisions, specifications, and deliverables. The executive view shows recent results, current work, next work, and blockers.</p>
<p><a href="generic/purpose.html">Read the full Wingman purpose →</a></p></section>'''
    stats = '<div class="summary"><div><strong>75</strong><span>Source checkouts</span></div><div><strong>24</strong><span>Common requirements</span></div><div><strong>6</strong><span>Source groups</span></div><div><strong>25</strong><span>Historical source audits</span></div></div>'
    reading = '''<section><h2>Choose a reading path</h2><div class="table-scroll"><table><thead><tr><th>Question</th><th>Start here</th><th>Main decision</th></tr></thead><tbody>
<tr><td>How can agents share tasks and hand off work?</td><td><a href="task-management/index.html">Agent task management</a></td><td>Read 25 codebase assessments against T01–T24: ownership, dependencies, recovery, review and agent interfaces.</td></tr>
<tr><td>How can a standing team work?</td><td><a href="paperclip/index.html">Paperclip</a>, <a href="openrig/index.html">OpenRig</a>, <a href="multica/index.html">Multica</a>, <a href="crewly/index.html">Crewly</a>, <a href="agent-swarm/index.html">Agent Swarm</a></td><td>Choose the agent, project, task, and authority model.</td></tr>
<tr><td>How can workers execute and recover?</td><td><a href="orca/index.html">Orca</a>, <a href="codex-autorunner/index.html">CAR</a>, <a href="agent-deck/index.html">Agent Deck</a>, <a href="scion/index.html">Scion</a></td><td>Choose session, attempt, delivery, and host contracts.</td></tr>
<tr><td>How can work reach accepted delivery?</td><td><a href="gstack/index.html">gstack</a>, <a href="gastown/index.html">Gas Town</a>, <a href="superplane/index.html">SuperPlane</a>, <a href="babysitter/index.html">Babysitter</a></td><td>Connect product definition to versioned verification evidence.</td></tr>
</tbody></table></div><p class="scope-note">These are source-study paths. They are not measured reliability rankings or deployment recommendations.</p></section>'''
    options = ''.join(f'<option value="{E(key)}">{E(label)}</option>' for key, label in GROUPS.items())
    table = f'''<section id="comparison"><h2>Compare the source assessments</h2><p>Choose a requirement group. Open a project to read the evidence and implementation limits.</p>
<form class="filters" role="search"><label class="search">Find a project<input type="search" id="project-search" placeholder="Project name or mechanism" autocomplete="off"></label>
<label>Source group<select id="group-filter"><option value="">All groups</option>{options}</select></label>
<label>Requirements<select id="lens-filter"><option value="priority">High-impact requirements</option><option value="organization">Organization and intake</option><option value="work">Work and collaboration</option><option value="runtime">Continuity and execution</option><option value="visibility">Visibility and acceptance</option><option value="all">All 24 requirements</option></select></label></form>
<p class="legend"><strong>Verdicts:</strong> Exact · Similar · Resembles · Absent · Unclear. Each verdict has a stated boundary. Counts are not a product score.</p>
<p id="result-count" class="result-count" role="status">75 projects</p>
<div class="table-scroll matrix-scroll" tabindex="0" role="region" aria-label="Project comparison"><table id="comparison-table"><thead><tr><th scope="col">Project / useful mechanism</th>'''
    for key, label in features:
        table += f'<th scope="col" data-feature="{key}"><a href="generic/method.html#feature-{key.lower()}" title="{E(label)}">{key}</a><span>{E(label)}</span></th>'
    table += '</tr></thead><tbody>'
    for item in sorted(coverage['repositories'], key=lambda x: Path(x['directory']).parts[0]):
        slug = Path(item['directory']).parts[0]; meta = metadata[slug]; brief = briefs[slug]
        search = E(' '.join([slug, brief['use'], brief['boundary']]).lower(), quote=True)
        table += f'<tr data-group="{E(meta["group"])}" data-search="{search}"><th scope="row"><a href="{slug}/index.html">{E(name(slug))}<img src="assets/icons/arrow-right.svg" width="13" height="13" alt=""></a><small>{E(brief["use"])}</small></th>'
        for key, _ in features:
            verdict = item['feature_verdicts'][key]
            table += f'<td data-feature="{key}" class="verdict {verdict.lower()}">{E(verdict)}</td>'
        table += '</tr>'
    table += '</tbody></table></div><p id="empty-result" hidden>No project matches these filters. Change the search or source group.</p></section>'
    catalog = '<section id="catalog"><h2>Reports by source group</h2><p>Groups describe the original research structure. Some projects now span several layers.</p>'
    for group, label in GROUPS.items():
        items = sorted([s for s in briefs if metadata[s]['group'] == group])
        count_label = 'project' if len(items) == 1 else 'projects'
        catalog += f'<section id="group-{group}" class="catalog-group"><h3>{E(label)} <span>{len(items)} {count_label}</span></h3><ul>'
        catalog += ''.join(f'<li><a href="{slug}/index.html">{E(name(slug))}</a></li>' for slug in items)
        catalog += '</ul></section>'
    catalog += '</section>'
    shell(page, 'Wingman research', 'Source evidence for a persistent, human-directed development organization.',
          stats + intro + findings + reading + table + catalog, 'overview')

def build_generic():
    docs = [('ARCHITECTURE.md', 'index.html', 'Architecture findings', 'architecture'),
            ('METHOD.md', 'method.html', 'Method and evidence', 'method'),
            ('AGENT_TASK_COORDINATION.md', 'task-coordination.html', 'Agent task coordination', 'coordination')]
    for filename, output, title, section in docs:
        page = ROOT / 'generic' / output
        body = render(ROOT / 'generic/assessments' / filename, page, section)
        if output == 'method.html':
            body += '<section><h2>Common Wingman requirements</h2><div class="table-scroll" tabindex="0" role="region" aria-label="Wingman requirements"><table><thead><tr><th scope="col">ID</th><th scope="col">Requirement</th></tr></thead><tbody>'
            body += ''.join(f'<tr id="feature-{key.lower()}"><th scope="row">{key}</th><td>{E(label)}</td></tr>' for key,label in features)
            body += '</tbody></table></div></section><p><a href="assessments/ASSESSMENT_GUIDE.md">Read the complete assessment guide</a></p>'
        subtitle = ('Open-source task boards, shared queues and handoffs for agents and subagents.'
                    if section == 'coordination' else 'Shared technical findings and evidence boundaries.')
        shell(page, title, subtitle, f'<article class="technical">{body}</article>', section,
              generic_contents(body), review_date='08 NOV 2026' if section == 'coordination' else '05 NOV 2026')
    page = ROOT / 'generic/purpose.html'
    body = render(ROOT / 'WINGMAN_PURPOSE.md', page, 'purpose')
    shell(page, 'Wingman purpose', 'The product baseline used for all 75 assessments.',
          '<article class="technical">' + body + '</article>', 'purpose', generic_contents(body))


def build_task_management():
    folder = ROOT / 'task-management'
    records = sorted(task_checkouts['repositories'], key=lambda item: item['slug'])
    reviews = {item['slug']: json.loads((ROOT / item['assessment']).with_name('review.json').read_text())
               for item in records}
    matrix_md = ['# Task-management requirement matrix', '',
                 'Derived from the 25 source-review ledgers at their pinned commits. Read each report for verdict boundaries. No candidate application or test suite was run. Verdict counts are not product scores.', '',
                 '| Codebase | ' + ' | '.join(key for key, _ in task_features) + ' |',
                 '|---|' + '---|' * len(task_features)]
    page = folder / 'index.html'
    options = ''.join(f'<option value="{E(key)}">{E(label)}</option>'
                      for key, label in task_catalog['families'].items())
    body = '''<div class="summary"><div><strong>25</strong><span>Codebase assessments</span></div><div><strong>24</strong><span>Task requirements</span></div><div><strong>600</strong><span>Explained verdicts</span></div><div><strong>0</strong><span>Candidate test suites run</span></div></div>
<p class="lead">Shared work that survives agent sessions.</p><p>Compare project records, ready work, ownership, delegation, recovery and acceptance. Each report traces a pinned source revision and states its evidence limits.</p>
<p><a href="purpose.html">Read the task-management baseline →</a> · <a href="REQUIREMENT_MATRIX.md">Open the Markdown matrix</a> · <a href="README.md">Source study guide</a></p>
<section id="comparison"><h2>Compare coordination mechanisms</h2>
<form class="filters" role="search"><label class="search">Find a codebase or mechanism<input type="search" id="project-search" placeholder="Name, lease, review, dependency…" autocomplete="off"></label>
<label>Source family<select id="group-filter"><option value="">All families</option>''' + options + '''</select></label>
<label>Requirements<select id="lens-filter"><option value="priority">Ownership and acceptance</option><option value="organization">Project organization</option><option value="work">Work and communication</option><option value="runtime">Failure and continuity</option><option value="visibility">Inspection and governance</option><option value="all">All 24 requirements</option></select></label></form>
<p class="legend"><strong>Verdicts:</strong> Exact · Similar · Resembles · Absent · Unclear. Open any verdict for its explanation. These are fit categories, not a reliability ranking.</p>
<p id="result-count" class="result-count" role="status">25 codebases</p>
<div class="table-scroll matrix-scroll" tabindex="0" role="region" aria-label="Task management requirement comparison"><table id="comparison-table" data-study="tasks"><thead><tr><th scope="col">Codebase / useful mechanism</th>'''
    for key, label in task_features:
        body += f'<th scope="col" data-feature="{key}"><a href="purpose.html#task-purpose-{key.lower()}" title="{E(label)}">{key}</a><span>{E(label)}</span></th>'
    body += '</tr></thead><tbody>'
    for index, item in enumerate(records):
        slug = item['slug']; brief = task_briefs[slug]; review = reviews[slug]
        search = E(' '.join([slug, brief['name'], brief['use'], brief['boundary']]).lower(), quote=True)
        body += f'<tr data-group="{E(brief["family"])}" data-search="{search}"><th scope="row"><a href="{slug}/index.html">{E(brief["name"])}</a><small>{E(brief["use"])}</small></th>'
        verdicts = review['requirement_verdicts']
        for key, _ in task_features:
            verdict = verdicts[key]
            body += f'<td data-feature="{key}" class="verdict {verdict.lower()}"><a href="{slug}/index.html#task-{slug}-{key.lower()}">{E(verdict)}</a></td>'
        body += '</tr>'
        matrix_md.append(f'| [{brief["name"]}]({slug}/assessment/ASSESSMENT.md) | ' + ' | '.join(verdicts[key] for key, _ in task_features) + ' |')
        project_page = folder / slug / 'index.html'
        project_body = render(ROOT / item['assessment'], project_page, 'task-' + slug)
        adjacent = '<nav class="report-switch" aria-label="Task study navigation">'
        adjacent += '<a href="../index.html">Return to the task comparison</a>'
        if index:
            previous = records[index - 1]['slug']
            adjacent += f'<a href="../{previous}/index.html">Previous: {E(task_briefs[previous]["name"])}</a>'
        if index + 1 < len(records):
            following = records[index + 1]['slug']
            adjacent += f'<a href="../{following}/index.html">Next: {E(task_briefs[following]["name"])}</a>'
        adjacent += '</nav>'
        shell(project_page, brief['name'] + ' · task management', brief['use'],
              '<article class="technical">' + project_body + '</article>' + adjacent,
              'tasks', generic_contents(project_body), review_date='09 NOV 2026')
    body += '</tbody></table></div><p id="empty-result" hidden>No codebase matches these filters. Change the search or source family.</p></section>'
    comparison = render(folder / 'COMPARISON.md', page, 'task-findings')
    body += '<article class="technical">' + comparison + '</article>'
    shell(page, 'Agent task management', '25 codebases assessed against shared project and task coordination requirements.',
          body, 'tasks', '<p><a href="#comparison">Requirement matrix</a></p>' + generic_contents(comparison),
          review_date='09 NOV 2026')
    (folder / 'REQUIREMENT_MATRIX.md').write_text('\n'.join(matrix_md) + '\n')
    purpose_page = folder / 'purpose.html'
    purpose = render(ROOT / 'AGENT_TASK_MANAGEMENT.md', purpose_page, 'task-purpose')
    shell(purpose_page, 'Agent task management baseline', 'The T01–T24 purpose used by all 25 task-management assessments.',
          '<p><a href="index.html">Return to the task comparison →</a></p><article class="technical">' + purpose + '</article>',
          'tasks', generic_contents(purpose), review_date='09 NOV 2026')

def main():
    for item in coverage['repositories']:
        item['report_sha256'] = hashlib.sha256((ROOT / item['report']).read_bytes()).hexdigest()
        build_project(item)
    (ROOT / 'coverage.json').write_text(json.dumps(coverage, indent=2) + '\n')
    build_master(); build_generic(); build_task_management()
    print('Built 107 HTML reports: the original 80 plus 25 task assessments, task baseline and task comparison.')

if __name__ == '__main__':
    main()
