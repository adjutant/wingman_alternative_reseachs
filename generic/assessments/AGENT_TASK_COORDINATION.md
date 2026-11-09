# Task coordination for AI agents and subagents

Review date: November 8, 2026. This is the historical screening. The [active task-management study](../../task-management/index.html) uses a narrower selection. Recommendations here reflect the original screening.

**Start with Paperclip for a shared organization, Beads for a lightweight task graph, and Rhizome MCP for lease-based handoffs on one host.** Compare Muster when the main interface should be a shared agent board. Use Plane when conventional project management is the priority. Backlog.md is the clearest file-based option for humans and agents working in the same repository.

The important unit is a durable task with an owner, dependencies and a recoverable execution attempt. A board presents that state. An agent runtime performs the work. Some products provide both layers. Others provide one layer and need an adapter.

This study covers 17 candidate systems, three alternatives with restrictive licenses, and two communication or visualization companions with restrictive licenses. It includes GitHub projects and GitLab's own self-hosted tracker. The official Plane MCP server is an integration, not an additional tracker. GitHub hosting alone does not establish an open-source license.

The findings below distinguish implementation review from documentation review. None of the candidate applications or their test suites was started for this study. Recommendations identify evaluation paths, not measured reliability rankings. The original 75-project comparison remains a separate assessment against all 24 Wingman requirements.

## Decisions by use case

| Need | First candidates to evaluate | Reason and adoption boundary |
|---|---|---|
| Shared projects and durable specialist agents across hosts | Paperclip; Agent Swarm | Both already have source assessments in this collection. They connect task ownership to independently running agents through a central service. They bring more runtime and organization policy than a small tracker needs. |
| Small task graph that agents can query and claim from a CLI | Beads | Native dependencies, machine-readable commands, conditional claims and recovery primitives. Use one shared authority for concurrent ownership. Separate replicas synchronized later are not a globally exclusive queue. |
| Crash recovery and reviewer handoff on one machine | Rhizome MCP; agent-kanban-rs | Leases and execution state are explicit. Rhizome adds version-bound reviews and reservations. Both are local coordination tools; Rhizome deliberately rejects non-loopback HTTP bindings. |
| Shared browser board and MCP access without adopting an agent runtime | Muster | Agents, projects, cards, claims, dependencies and documents share one application. Its source history is short; validate the deployment and database mode you intend to use. |
| Very small service whose coordination code is easy to inspect | Agent HQ | Node standard-library server, SQLite, MCP adapter, claims, messaging and memory. The inspected HTTP routes lack authentication, and direct claims bypass readiness checks used by the next-task selector. |
| Markdown tickets committed with the product | Backlog.md | CLI, optional MCP, browser board, acceptance criteria and local mutation locks. These locks protect file updates. They do not establish a distributed worker lease. |
| Established project-management interface with agent access | Plane; OpenProject; Kanboard | Standard projects, tickets and APIs. Plane has an official open-source MCP adapter. A dispatcher still needs a claim, renewal and recovery contract. OpenProject's built-in MCP is an Enterprise add-on. |
| Visual coding execution, workspaces and review | Vibe Kanban; Gemba | Vibe Kanban starts agent workspaces from MCP. Gemba adds a board and dispatch layer over a work tracker. Neither should be assumed to replace a general shared task service without checking its ownership contract. |
| Existing GitLab projects and development workflow | GitLab Community Edition | Issues, boards, comments, milestones, APIs and merge requests can remain the shared record. Add worker coordination around that record. Check the tier of each required feature. |

For Wingman's Mac and Linux arrangement, evaluate **Paperclip against a smaller Muster-based tracker** first. Paperclip is the more complete organization and execution layer. Muster is closer to the requested shared project board. Beads is the strongest alternative when a CLI and a dependency graph matter more than a central browser application. These are architectural recommendations inferred from the mechanisms reviewed below.

## What agents need from a tracker

Agents must be able to create follow-up work, claim a task, explain a blocker, hand work to a reviewer and resume after losing a session. Human Scrum features are useful when they describe the product. Runtime coordination needs additional rules.

| Requirement | Evidence to seek |
|---|---|
| Durable identity | Distinguish an agent, a parent agent, a session, a task and each execution attempt. |
| Shared ownership | A competing claim has one winner at the authoritative store. An assignee label alone is insufficient. |
| Recovery | A crashed worker's claim can expire or be explicitly recovered. The replacement can read its checkpoint. |
| Dependencies | Ready-work selection respects blockers. Direct task claims must not silently bypass the same rule. |
| Delegation | Parent and child tasks preserve context, outcomes and the rule for completing the parent. |
| Handoff | A comment, result or artifact tells the next worker what changed and what remains. |
| Verification | Review refers to a particular task or artifact version. A later edit must not inherit an obsolete approval. |
| Inspection | A person can see owners, blockers, activity, questions and delivered artifacts. |
| Cross-host access | Independent workers use one service or a defined synchronization protocol. Shared files alone do not establish global ownership. |
| Agent interface | CLI, REST or MCP operations return bounded, structured results and useful conflict errors. |

**MCP Tasks and project tickets are different concepts.** MCP's task utility tracks a long-running protocol request. It does not by itself supply projects, epics, dependencies, agent ownership or a Kanban board. An MCP wrapper also does not add those guarantees to a tracker whose API only edits cards.

Protocol reference: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/utilities/tasks.mdx

## Agent-oriented task systems

The license column describes the inspected revision. “Source” means the named mechanism was read in implementation files. “Docs” means the listed behavior comes from upstream documentation. Neither means a runtime test passed here.

| System | Store and interface | Ownership and recovery observed | Human view and execution | License and evidence |
|---|---|---|---|---|
| Beads | Dolt; CLI, JSON and HTTP-related implementation paths | Conditional row-version claim; ready-task claim; leases and explicit reclaim | CLI; external viewers. No general coding-worker runtime in the task tracker | MIT. Source |
| Rhizome MCP | Per-project SQLite outside the source repo; MCP and CLI | Lease-token attempt gates; expiring attempts; version-bound review requests | Read-only status board and editor integration. Bring your own agents | Apache-2.0. Source and transport docs |
| agent-kanban-rs | One SQLite database; compact CLI output | Immediate transactions, conditional claims, lease expiry and dependency predicate | Terminal views; developer and reviewer workflow. Bring your own agents | MIT. Source |
| Backlog.md | Markdown files; CLI, optional MCP and local browser | Locks around local read-modify-write operations. No distributed worker lease established by this review | Board, acceptance criteria, plans and notes | MIT. Source |
| Muster | SQLite or PostgreSQL; REST and MCP | Transactional claims, expiry, heartbeat renewal and blocker checks | Shared project board, agent roster, documents and live events. Bring your own runtime | MIT. Source |
| Agent HQ | SQLite; HTTP API and stdio MCP proxy | Conditional claim and lease. Next-task selection filters blockers; direct claim does not | Live board, memory, messages, flow and cost ledger. Bring your own runtime | MIT. Source |
| Paperclip | PostgreSQL; company/project issue API | Conditional checkout ties agent, issue status and execution run; terminal-run cleanup | Organization, issue board, activity and runtime adapters | MIT. Existing pinned source, rechecked |
| Agent Swarm | Central SQLite behind HTTP/MCP | Conditional task claim; worker runner and cancellation/recovery paths | Task dashboard, agents, messages and worker execution | MIT. Existing pinned source, rechecked |
| DevBoard | Markdown/YAML files; Python CLI | Claim checks and file write are separate. Own design note acknowledges a race | Terminal board, priorities, WIP and dependency conventions | MIT. Source. Do not select for competing claims |

### Beads

Repository: https://github.com/gastownhall/beads

Beads is a task graph for agents. Issues carry dependencies and ownership. `bd ready` finds workable issues, and `bd ready --claim --json` combines selection with a claim. The inspected claim implementation compares the row version in the update condition. The ready-claim path reuses the ready-work predicate inside its transaction.

Current storage is Dolt. Embedded mode has one writer. Server mode supports concurrent writers. The inspected lease code defines a five-minute default and explicit reclaim after a worker stops heartbeating. This is more than an assignee field, but it does not supervise the coding process itself.

Use a shared authority for Mac and Linux workers. Dolt push/pull between separate databases is synchronization; it does not prevent two isolated replicas from assigning the same work before they reconcile. The current README also identifies JSONL as an export rather than the authoritative store. Older descriptions of Beads as SQLite plus JSONL do not describe this revision.

Source: `internal/storage/issueops/claim.go`, `claim_next.go`, `lease.go`; storage mode in `README.md` lines 151–165. Pinned source links and file hashes appear in the [evidence index](agent-task-coordination/EVIDENCE.md).

### Rhizome MCP

Repository: https://github.com/Odrin/rhizome-mcp

Rhizome separates the issue from each work attempt. A renewable lease controls the attempt. An active lease produces the in-progress view, and attempt mutations validate the lease token. A replacement worker can use saved attempt notes. Review requests refer to a particular issue version and event position, so review can be superseded when its target changes.

This is a good design to study for subagent handoff and recovery. It also supports resource reservations and a human status board. Reservations coordinate cooperating clients; they do not stop a process from editing a file outside the protocol.

Its HTTP contract accepts literal loopback addresses only. The browser board is read-only. It is therefore a local coordinator, not a ready-made LAN task service for two machines. Remote access would need a separately assessed adapter or transport. Do not assume a reverse proxy is supported by a server that also validates Host and Origin.

Source: attempt repository and application service. Transport and board boundaries: `docs/08-local-http-transport.md` and `docs/13-status-board.md`. The upstream cross-process claim-race test was read, not run.

### agent-kanban-rs

Repository: https://github.com/fxeqxmulfx/agent-kanban-rs

This small Rust CLI provides tasks, agents, dependencies, leases and review. Mutations use SQLite immediate transactions. The claim statement checks ownership, expiry, allowed state and the developer's dependency predicate. Claim-next selects and updates in the database. Reviewer operations record a decision for the task revision.

It is a compact alternative when all agents can use one local database and terminal commands. Agent registration and developer/reviewer roles describe cooperation inside that local trust boundary. They do not establish authenticated remote identities. There is no shared web service to deploy across hosts in the reviewed interface.

Source: `src/commands/lifecycle.rs`, especially transaction setup, claim predicates and review decisions; `src/commands/deps.rs`.

### Backlog.md

Repository: https://github.com/MrLesk/Backlog.md

Backlog.md keeps tasks as readable Markdown. It supplies acceptance criteria, definition-of-done items, plans, implementation notes, dependencies and board views. The current interface is CLI-first; MCP remains optional. It is a strong fit when the task record should travel with the source repository.

The inspected implementation protects task edits with a file lock and reloads the current task inside that lock. This is useful local concurrency control. It does not make an assignment a renewable worker lease, and independent Git clones do not share the same lock. Use explicit worker ownership outside this layer when independent agents choose tasks across machines.

The README also places its browser interface on localhost. Prefer it for repository work and reviewable tickets. Do not treat its browser as an authenticated central team service without a separate deployment assessment.

Source: `src/core/backlog.ts` lines 3070–3095 and `src/file-system/operations.ts`; current interface and browser posture in README.

### Muster

Repository: https://github.com/musterai/muster

This is the human-agent collaboration project from **musterai**, not other similarly named agent frameworks. It has projects, cards, agents, comments, documents and MCP access. Its claim operation opens a transaction, reads the card with locking requested, checks the holder and expiry, checks unresolved blockers, and writes the claim. Heartbeats renew claims; an expiry sweep releases them.

Muster is one of the closest matches to a shared Jira-style record that agents operate themselves. Claiming and moving a card into an active lane are separate operations. A worker protocol must handle interruption between them. It does not need to launch the coding agent to be useful as the shared tracker.

The deployment docs distinguish local open mode from enforced shared access, with OAuth/OIDC paths and non-loopback binding rules. Its repository dates from August 2026. Evaluate the actual database and authentication mode before using it as the organization record.

Source: `card-assignment.operations.ts`, `card-move.operations.ts`, database adapters and `tests/card-claim.test.ts`. Deployment statements are documented upstream; no deployment was run here.

### Agent HQ

Repository: https://github.com/tools-for-agents/agent-hq

Agent HQ combines a board, agents, memory, messages, activity and a run/cost ledger. The Node server uses the standard library and SQLite. A stdio MCP process proxies operations to its HTTP service. A conditional SQL update prevents a live claim held by another agent from being overwritten through the claim endpoint.

Two boundaries matter. The next-task selector filters unfinished dependencies and Done columns, but direct claim does not apply those filters. Its lease guard is also not an authorization boundary around all task edits. The inspected server routes have no authentication gate and accept actor identity from request data.

It is a useful small reference implementation for a trusted team. It needs stronger mutation rules and access control before it can serve as authoritative cross-host work allocation. Its concurrency test exercises worker-thread contention; that test was read, not run.

Source: `src/services.js` lines 630–705, `src/server.js`, `src/db.js` and `test/concurrency.test.js`.

### Paperclip

Repository: https://github.com/paperclipai/paperclip

Paperclip combines durable agents, reporting relationships, companies, projects, issues and execution runs. Checkout checks expected status and ownership, then conditionally writes the agent and run identifiers. Completion and terminal-run cleanup remain tied to the execution model. This is a much richer basis for agent coordination than a shared assignee label.

It is the first candidate to evaluate when Wingman needs one record connecting project leadership, worker assignments, detailed execution and human supervision. The cost is adopting a broader control plane and configuring its organization and runtime adapters. Wingman's named leadership roles and acceptance rules still need explicit policy.

This entry uses the preserved November 5 checkout, not an unpinned claim about upstream HEAD. Its full [technical assessment](../../paperclip/assessment/ASSESSMENT.md) covers lifecycle, dependencies, approvals, recovery and multi-host limits. Checkout was rechecked in `server/src/services/issues.ts` lines 12168–12303 for this study.

### Agent Swarm

Repository: https://github.com/desplega-ai/agent-swarm

Agent Swarm joins a central task service to independent worker runners. Tasks carry assignments, offers, parents, dependencies, priorities and routing context. The inspected `claimTask` uses a conditional update from unassigned to in-progress. Worker clients call the central service rather than sharing its SQLite file, which fits agents on separate hosts.

Evaluate it when worker dispatch, communication and task execution should come from one platform. It introduces more runtime machinery than a stand-alone board. The single-row claim establishes task ownership at that operation; it does not establish exactly-once external effects or product acceptance.

This entry also uses the preserved November 5 checkout. The full [technical assessment](../../agent-swarm/assessment/ASSESSMENT.md) explains cancellation, failure handling, conversations and worker/provider boundaries. The claim was rechecked in `src/be/db.ts` lines 3107–3159.

### DevBoard

Repository: https://github.com/RapidWebs-Enterprise/DevBoard

DevBoard provides file-based tasks, a Python CLI, priorities, dependencies, claims and WIP conventions. It is relevant to simple local task tracking, but its concurrency claim must be narrowed.

The core reads a task, checks availability, changes the owner and writes the file. Its accepted claim design note explicitly states that the read and write are separate and that locking could be added later. Two processes can therefore both pass the availability check. Atomic replacement of a file, even when used, would not make the whole read-check-write sequence atomic.

Do not select this revision for agents that independently compete for work. It could still serve a single writer or a human-dispatched workflow.

Source: `src/devboard/__init__.py` and `docs/adrs/0003-atomic-claims.md`. This is a source-level finding; no race experiment was run.

## Boards connected to coding execution

### Vibe Kanban

Repository: https://github.com/BloopAI/vibe-kanban

License: Apache-2.0.

Vibe Kanban connects issue tracking, coding workspaces, branches, sessions and review. Its MCP interface can create issues and start a workspace with a selected executor, repositories and an optional linked issue. This lets a coordinating agent create work and launch another coding session, rather than merely display a board.

The reviewed revision includes self-hosting instructions for its shared service. That is a different deployment from the local application. Evaluate it for parallel coding, isolated workspaces and human review. This review did not establish an exclusive worker-claim contract for arbitrary external agents. Starting a workspace linked to an issue should not be assumed to grant that guarantee.

Sources: pinned `crates/mcp/src/task_server/tools/task_attempts.rs`, issue and workspace tools, and `docs/self-hosting/deploy-docker.mdx`.

### Gemba

Repository: https://github.com/GembaCore/gemba-core

License: MIT.

Gemba separates its work tracker from its orchestration layer. The reviewed Beads adapter shells out to `bd` and maps tasks, status, assignees and labels into its WorkPlane interface. Native terminal orchestration adds sessions and dispatch. A tracker-only mode can provide the human board without starting agents.

This is a useful example of adding planning and operator views above a task graph. It is an additional layer, not a replacement storage engine. Its generic adapter design is not proof that every named tracker is implemented. Also pin the Gemba/Beads pair together: the Gemba revision predates the Beads revision inspected here, and compatibility between them was not tested.

Sources: `internal/adapter/bd/workplane.go`, native dispatch code, `docs/adaptors/beads.md` and the autonomous dispatch guide.

## Established trackers agents can operate

These products make sense when a person needs conventional projects, issues, history and permissions. Their documented APIs let agents participate. The listed API evidence does not establish automatic worker launch, expiring ownership or stale-worker fencing.

| System | Why it belongs here | Agent access and concurrency boundary | License and operating cost |
|---|---|---|---|
| Plane | Projects, work items, cycles, modules and browser planning | Official MCP server supports self-hosted base URLs. Work-item operations edit tracker state; add an explicit claim service or a single dispatcher | Core AGPL-3.0; MCP adapter MIT. Multi-service application |
| OpenProject | Work packages, hierarchy, relations, sprints and boards | REST updates use `lockVersion` optimistic locking. Useful protection against stale edits, not a worker lease. Built-in MCP is an Enterprise add-on | GPL-3.0 core. Larger application than a small board |
| Kanboard | Focused Kanban with tasks, subtasks, comments and automation | JSON-RPC task and subtask operations are straightforward to wrap. The inspected procedures do not establish a lease queue | MIT. PHP application; relatively small deployment |
| Vikunja | Projects, subtasks, relations, assignees, list/Gantt/table/Kanban views | Documented REST/OpenAPI access. A task relation is not proof that claiming or starting work is dependency-gated | Core AGPL-3.0-or-later; desktop GPL-3.0-or-later. Some features are Pro |
| Taiga | Scrum and Kanban concepts with stories, tasks, issues and milestones | REST API has version-based optimistic concurrency. Use it on updates; it does not recover a dead worker's assignment | MPL-2.0 backend. Frontend and supporting services need their own deployment |
| GitLab Community Edition | Issues, boards, comments, milestones and code review in one development service | Issues and boards APIs support agent clients. Assignees and labels are not an exclusive queue; a dispatcher or claim layer must enforce that rule | MIT community code; Enterprise features have separate terms and tier gates. Large if installed solely as a tracker |

### Plane and its official MCP integration

Core: https://github.com/makeplane/plane

MCP adapter: https://github.com/makeplane/plane-mcp-server

Plane is the first conventional tracker to compare with the agent-native shortlist. Its official Python MCP implementation resolves workspace credentials and supports a configurable Plane base URL. Work items expose tasks, epics, state, assignees and relations. Agents can share the same records that a person sees in the browser.

The integration solves agent access to project management. It does not, from the inspected work-item operations, supply the lease and execution-attempt contract needed for a distributed worker pool. Keep one dispatcher in charge of allocation or implement that contract beside Plane, with a clear rule for which record owns each field.

The current Python adapter replaces a deprecated Node adapter. Do not copy old Node-only setup instructions. The pinned core and adapter are recorded separately in the evidence manifest.

### OpenProject

Repository: https://github.com/opf/openproject

OpenProject's API requires the current `lockVersion` when updating a work package. Two workers should not treat a successful read as ownership. A conditional update can help an adapter detect a competing edit, but the adapter must still define who owns the task, when ownership expires and what completion is allowed.

Current edition details matter. Action boards became available in Community in version 17.3. The built-in MCP integration remains an Enterprise Professional feature or higher. Community users can build agent access through REST without assuming that paid MCP is included.

API: https://www.openproject.org/docs/api/endpoints/work-packages/

Community board change: https://www.openproject.org/blog/openproject-17-3-release/

MCP edition boundary: https://www.openproject.org/blog/openproject-17-8-release/

### Kanboard

Repository: https://github.com/kanboard/kanboard

Kanboard is a practical baseline for a small shared board. Its task and subtask JSON-RPC procedures support a thin agent adapter. It is worth comparing when agent-specific dashboards, memory and execution adapters are unnecessary. The remaining work is ownership and worker lifecycle policy, not natural-language access to a card.

Source: pinned `app/Api/Procedure/TaskProcedure.php` and `SubtaskProcedure.php`.

### Vikunja

Repository: https://github.com/go-vikunja/vikunja

Vikunja is a broader lightweight task manager with several human views. It can be an agent-accessible shared project record through its API. The reviewed feature and API documentation does not establish lease recovery or mandatory dependency checks at claim time. Community MCP adapters exist, but their presence should not be credited as built-in coordination guarantees.

Features: https://vikunja.io/features/

API: https://try.vikunja.io/api/v2/docs

### Taiga

Repository: https://github.com/taigaio/taiga-back

Taiga is relevant when actual Scrum planning matters: stories, tasks, issues and milestones already have an established data model. Its API documents optimistic concurrency using a version field. An agent adapter should preserve that field and handle conflicts. Worker heartbeats, expired claims and result verification remain separate concerns.

API: https://docs.taiga.io/api.html

### GitLab Community Edition

Source: https://gitlab.com/gitlab-org/gitlab

GitLab can keep tickets, discussions, code changes and review together. Agents can create issues, comment, change state and update board-related metadata through APIs. This is appealing when the projects already use GitLab. Installing the entire service solely to coordinate a few agents is a larger commitment than Beads, Muster or Kanboard.

The current board documentation distinguishes Free and paid capabilities. Free has multiple project boards and one group board. Features such as configurable boards and assignee lists have tier limits. This study does not treat GitLab Duo or other paid agent features as part of the open-source coordination baseline.

Boards: https://docs.gitlab.com/user/project/issue_board/

Issues API: https://docs.gitlab.com/api/issues/

Boards API: https://docs.gitlab.com/api/boards/

License: https://gitlab.com/gitlab-org/gitlab/-/blob/master/LICENSE

## License-constrained alternatives and companions

These projects are discoverable and relevant. Their inspected revisions should not be presented as ordinary MIT open-source choices. This classification follows the additional restrictions in their license files; it is not a full licensing review of every component.

| Project | Role | Finding at the inspected revision | Disposition |
|---|---|---|---|
| Task Master | PRD decomposition, task/subtask planning and CLI/MCP workflow | MIT text plus Commons Clause; package metadata says `MIT WITH Commons-Clause` | Separate source-available planning alternative. Do not list as unrestricted MIT |
| PLANKA | Human-facing Trello-style board | Community/Fair Use terms restrict commercial third-party hosting and distinguish Pro/Enterprise files | Separate source-available board. Not in the open-source shortlist |
| Beads Rust | SQLite/JSONL task graph and CLI | MIT text plus an OpenAI/Anthropic rider that withholds rights from named parties and their defined representatives | Separate restricted alternative. Do not treat as license-equivalent to Beads Go |
| MCP Agent Mail Rust | Agent identities, messages, threads and advisory resource reservations | Same named-party rider in the inspected license | Relevant communication companion, excluded from the open-source adoption shortlist at this revision |
| Beads Viewer | Graph analysis, terminal views and machine-readable triage | Same named-party rider in the inspected license | Relevant visualization companion, excluded from the open-source adoption shortlist at this revision |

Task Master: https://github.com/eyaltoledano/claude-task-master

PLANKA: https://github.com/plankanban/planka

Beads Rust: https://github.com/Dicklesworthstone/beads_rust

MCP Agent Mail Rust: https://github.com/Dicklesworthstone/mcp_agent_mail_rust

Beads Viewer: https://github.com/Dicklesworthstone/beads_viewer

The original Python Agent Mail repository now identifies the Rust rewrite as its successor. Treat it as a historical implementation, not a fresh recommendation. A communication layer also does not replace the task graph: a message thread and a file reservation answer different questions from ticket ownership and completion.

Historical Python project: https://github.com/Dicklesworthstone/mcp_agent_mail

## How to connect agents and subagents

The tracker should retain work across sessions and hosts. A parent agent can delegate by creating child tickets rather than relying on a temporary in-memory subagent list. Each worker receives a task identifier, context and acceptance criteria. It claims an execution attempt before making changes.

```text
Human and project leaders
          |
          v
Shared project and task record <----> Browser board
          |
    ready work / claims / results
          |
          +---- Mac worker ---- child task ---- reviewer
          |
          +---- Linux worker -- child task ---- reviewer
```

This is a proposed integration pattern, not a claim that every candidate implements the complete flow.

1. A leader creates a task with project context, outcome, acceptance criteria and dependencies.
2. The leader creates child tasks where the work can proceed independently.
3. A worker claims ready work and receives an attempt identifier and lease or equivalent ownership token.
4. The worker renews ownership and saves progress, blockers and artifact references.
5. A blocked worker records the question or dependency. It does not mark incomplete work done.
6. A worker submits a result for review against a specific artifact revision.
7. A reviewer accepts or returns that revision with concrete findings.
8. Parent completion checks required children and acceptance evidence.
9. Recovery closes or expires the old attempt before assigning a replacement.

A logical task owner should remain distinct from the temporary worker holding an execution lease. A lead can stay responsible while a coder, tester and reviewer make separate attempts. This distinction supports durable leadership without forcing a ticket to appear unowned between sessions.

### Contract for a conventional board adapter

Use this contract when Plane, Kanboard, Taiga, GitLab or another tracker supplies the project record but does not provide the worker queue. Keep one authoritative owner for execution state. Do not let the board and a second task store independently assign the same work.

| Operation | Required behavior |
|---|---|
| List ready | Return bounded results whose required blockers are complete. |
| Claim | Check eligibility and acquire ownership atomically. Return a conflict to a losing worker. |
| Renew | Require the current attempt token. Reject expired or superseded attempts. |
| Checkpoint | Append meaningful progress and artifact links with the attempt identity. |
| Submit | Pin the result and requested review to an artifact revision. |
| Review | Accept or reject that revision. Invalidate approval when its target changes. |
| Recover | Record why ownership ended. Give the replacement the prior checkpoint. |
| Finish | Enforce the definition of done and required review before closing the task. |

**A lease is not exactly-once execution.** A paused worker may resume after its lease expires. A replacement may already be working. The result, merge or delivery path must reject the old attempt where possible. External effects need idempotency or another guard. Task ownership also does not prevent two valid tasks from editing the same file; use workspaces, reservations or integration policy for that separate problem.

## Evaluation plan before adoption

Run these checks on a disposable project after selecting a candidate. They are proposed acceptance tests, not tests completed in this study.

| Scenario | Passing result |
|---|---|
| Two agents claim the same ready task concurrently | One succeeds. The loser receives a useful conflict and does no work. |
| Two agents claim different tasks | Both can proceed within configured limits. |
| Direct claim of a blocked task | The authoritative path rejects it, or a privileged override is explicit and recorded. |
| Worker dies after claiming | Ownership becomes recoverable. The next attempt can read its checkpoint. |
| Old worker returns after recovery | Its stale completion or publication is rejected where the system controls that effect. |
| Parent agent disappears after creating children | Another session can discover the children, dependencies and responsibility. |
| Code changes after review approval | The system requires review of the new target. |
| Mac and Linux claim concurrently | Both use the same authority, with the same conflict behavior. |
| Service restarts during a transition | Task, ownership, activity and notification state remain consistent or are repaired explicitly. |
| Human asks what is blocked | The board shows the responsible agent, blocker, question and next action. |

Start with the first five checks. They expose most differences between a visual task list and a task coordinator. Add real subagent and cross-host handoffs before selecting the shared record for Wingman.

## Evidence and revision boundaries

The [evidence index](agent-task-coordination/EVIDENCE.md) contains full commit identifiers, pinned implementation links and review scopes. The [source manifest](agent-task-coordination/sources.json) records retrieved file hashes and repository metadata. The [candidate table](agent-task-coordination/candidates.json) gives a machine-readable screening result. Documentation URLs were checked on November 8, 2026; unpinned documentation can change.

Paperclip and Agent Swarm use preserved local revisions assessed on November 5. New upstream file reads use the immutable revisions in the source manifest. Upstream test files establish what those tests are designed to check. They do not establish that the tests passed here. No candidate was installed, configured or started.

The practical next comparison is **Paperclip versus Muster for a shared service**, with **Beads as the lightweight task-graph alternative**. Use **Rhizome MCP or agent-kanban-rs** when coordination stays on one host. Use **Plane plus a defined worker contract** when a conventional project-management interface is the main requirement.
