# gstack assessment against Wingman

Assessment date: **2026-11-05**. Repository: https://github.com/garrytan/gstack . Local checkout: `researchs/gstack/repo`. Inspected commit: **`f8085aa0e499085c411f712d6d5c00a81d1b104a`**. The checked-in package identifies version `1.94.39` ([package.json](../repo/package.json), lines 1–9).

**Verdict:** gstack is a substantial engineering workflow and verification layer that Wingman could adopt selectively. It is not a self-contained replacement for Wingman's persistent, multi-product Codex organization. The distinction matters at this revision: gstack now includes a Captain/controller crew model, executable review dispatch, durable planning state machines, approval records and sophisticated merge trains. Calling it merely a collection of personas would miss real coordination machinery. Conversely, the workers, shared machines, messages, thread directory and scheduling in the Captain/Capy model are largely supplied by the external host, while gstack supplies instructions, artifacts and engineering gates. Its CEO and engineering-review skills do not instantiate standing ProductMaster and TechMaster agents.

The strongest fit is product clarification → executable specification → reviewed implementation → evidence-bound delivery. The largest gaps are the organization service, portfolio intake, stable agent identities, Telegram routing, peer rooms, proactive cross-project supervision and connected web/mobile dashboards. Assess these separately from the browser daemon: that daemon is an automation tool server, not a workforce scheduler.

This report follows [Wingman's purpose](../../WINGMAN_PURPOSE.md) and the [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md). Evidence links are relative to this report; line numbers refer to the inspected checkout. “Implemented” below can mean executable local machinery or an explicit host-driven workflow. Those are distinguished. Nothing was installed, no services or model sessions were launched, and no runtime tests were executed for this assessment.

## Architecture and execution model

### The host executes skills; gstack provides methodology and bounded tools

The top-level [AGENTS.md](../repo/AGENTS.md), lines 1–6, accurately describes the basic unit as a `SKILL.md` specialist workflow. A skill has metadata, triggers, tool declarations, preambles and procedural instructions. For example [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 1–43, declares a controller skill with Bash/file tools and AskUserQuestion, then explains a crew of host threads. Loading that file changes what the current host agent does. It does not create a new process or durable employee.

`setup` selects and installs host-specific renders, with Claude the default and Codex among the experimental hosts ([setup](../repo/setup), lines 24–49, 80–104, 232–294). Consequently, Codex compatibility is a documented integration target, but not evidence that every Claude- or Capy-specific behavior is equally supported on Codex. Templates and section files are rendered by the generation pipeline. The package's actual command entry points include build, type checking, free-test shards and documentation generation ([package.json](../repo/package.json), lines 11–33). The report treats the source templates and executable helpers as the behavioral source, rather than inferring capability from the skill catalog alone.

The execution graph is approximately:

```text
human in an agent host
  → skill prompt / generated host instructions
  → current host agent reads code, asks questions, writes plan/spec
  → gstack CLIs create run manifests, attempts, receipts and approvals
  → host subagents / local CLI reviewer / direct model API execute bounded work
  → tests, GitHub CI, PR and merge-train helpers bind evidence to source trees
  → host presents report and continues or stops

optional host controller (Capy Captain)
  → lane threads, branch/file ownership, shared-drive artifacts
  → READY reports → gate/train/slot verification → merge → digest/report
```

Some arrows are enforced code paths; some are instructions for an LLM and external host. A host failing to relay a Captain message is not repaired by a gstack messaging server, because none is implemented here.

### Planning and review are real state machines

The unattended planning runner stores phases, voices, attempts, amendments, spending, round limits and carry-forward state in a durable manifest. [lib/autoplan-state.ts](../repo/lib/autoplan-state.ts), lines 15–83, makes these concepts explicit. The fixed artifact set includes `run.json`, `attempts.jsonl`, `run.lock`, `spend.json`, `plan-active.md` and `restore.md` (lines 96–113). JSON writes use a temporary file and rename. The attempts journal is appended separately. This is durable workflow state, not a database of autonomous employee conversations.

[lib/autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 210–284, performs these steps:

1. Read the manifest and refuse stopped or gated work.
2. Check deadlines and pending amendments.
3. Open the next phase and calculate spending reservations.
4. Prevent overspending and create attempt IDs.
5. Journal dispatch intent and enter `awaiting_result`.

An `ATTEMPT` record does not prove that a reviewer ran. The host or selected runner must execute it and attach a result. [autoplan/DRIVER.md](../repo/autoplan/DRIVER.md), lines 22–38 and 61 onward, supplies the orchestration loop.

The outside-voice abstraction distinguishes `codex-cli`, `api` and `host-subagent` rather than pretending all are equivalent. [lib/outside-voice-runner.ts](../repo/lib/outside-voice-runner.ts), lines 25–60, records repository access and whether execution happens locally. The Codex runner resolves a model and sandbox, starts `codex exec` with JSON events and output files, enforces timeout, records usage and classifies unavailable/unverified/failed results (lines 112–160). An API voice sees supplied prompt bytes, not the repository (lines 164–169). Cross-family checking is explicit in lines 63–91. This is a strong boundary for honest multi-agent evidence.

### Captain coordination depends on host primitives

The crew model has an owner, one controller and lanes. Lanes own named files and branches, stop at an unstamped READY, and never merge. The controller maintains rules, digest, notes and approvals, then drives merge trains ([docs/captain.md](../repo/docs/captain.md), lines 17–67). The shared drive contains `AGENTS.md`, `CREW.md`, `DIGEST.md`, `NOTES.md`, reports, handoffs and approved plans. These are concrete, inspectable coordination artifacts. The mounted drive itself is a Capy prerequisite, not a storage service included in gstack.

Unlike Wingman's Room2 peer collaboration, this design deliberately sends **all** ownership questions, cross-thread messages, new scope and handoffs through the controller ([docs/captain.md](../repo/docs/captain.md), lines 122–126). It favors one place holding state and one committer per tree over decentralized specialist discussion. That is an architectural choice Wingman would have to change or limit to release management.

[lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 1–17, 49–95, 176–223, and 260–280, implements host integration. It loads a persistent pass manifest and sends exact briefs. It calls Capy `tools.subagent.create/start/list/stop` on `machine: 'shared'`. It polls readers and collects results within bounded windows. Later calls resume from disk. External Capy supplies the threads, machines, and API behavior. This checkout cannot establish Capy's internal durability or multi-host scheduling guarantees.

### Persistence is split by purpose

[lib/state-root.ts](../repo/lib/state-root.ts), lines 1–28, centrally resolves `GSTACK_STATE_ROOT → GSTACK_HOME → GSTACK_STATE_DIR → gstack plugin data → ~/.gstack`. Under that root, project slugs scope decisions, task lists, learnings, checkpoints and timeline events. This is useful per-repository continuity, not a portfolio registry with project lifecycle, leadership and assignments.

Merge-train records have a distinct distributed durability mechanism: local JSON records are mirrored as Git notes under `refs/notes/gstack-trains`, before dependent remote effects. Records represent trains, READY receipts, attempts, freezes and waves, and can be reconstructed on a replacement machine ([lib/ship-queue-train-record.ts](../repo/lib/ship-queue-train-record.ts), lines 1–25, 37–99). This shares release state across machines through Git. It does not share all agents' conversations or establish host placement for product development.

### The browser is a separate tool plane

The browser path first tries Aside, then falls back to gstack's persistent Chromium daemon. The CLI's actual command path posts to localhost `/command` ([browse/src/cli.ts](../repo/browse/src/cli.ts), lines 1109–1110). The server has an explicit idle-shutdown loop ([browse/src/server.ts](../repo/browse/src/server.ts), lines 702–717). The architectural explanation and state-file/health model are in [ARCHITECTURE.md](../repo/ARCHITECTURE.md), lines 5–58 and 74–102. Browser persistence means tabs/cookies survive successive browser commands. It does not mean coding agents persist as organization members.

The fallback browser also has a real Claude terminal companion. [browse/src/terminal-agent.ts](../repo/browse/src/terminal-agent.ts), lines 1–36 and 57–148, describes and implements session records, live WebSocket attachment, PTY state, scrollback and a bounded detach window. This is material for F20/F21, but is a local browser-side terminal rather than a directory of all workers' detailed sessions.

## Feature matrix

No “Exact” verdict is needed to acknowledge substantial value: the Wingman features combine specific organizational, persistence and presentation requirements which gstack generally addresses only in a host-specific or repository-scoped form.

| ID | Capability | Verdict | Implementation evidence and concrete difference from Wingman |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Real local `claude -p` implementation sessions can be spawned from a spec, and Capy review workers are created through host tools: [spec/sections/gate-and-file.md](../repo/spec/sections/gate-and-file.md), lines 399–461; [lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 176–223, 278. Most named skills are procedures for the current agent. No standing BackendCoder/FrontendCoder identities or employee-instance registry. |
| F02 | Extensible profiles, roles and team composition | **Similar** | Skills and specialist checklists are extensible; review planning has named specialist classes in [lib/review-depth.ts](../repo/lib/review-depth.ts), lines 25–37. Crew parameters and arbitrary lane briefs allow varying team size: [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 35–43, 62–94. This configures methodology and host workers, not durable profile types joined to organization-wide agents. |
| F03 | Agent directory and visible relationships | **Resembles** | The digest lists thread, ownership, state and last report; owner/controller/lane relationships are documented: [captain/templates/DIGEST.md](../repo/captain/templates/DIGEST.md), lines 24–33; [docs/captain.md](../repo/docs/captain.md), lines 29–48. No native searchable agent directory or identity/relationship graph was found in the implementation/UI paths. |
| F04 | Telegram and Butler routing | **Resembles** | The OpenClaw integration explicitly instructs repository resolution, `sessions_spawn(runtime: 'acp')`, report-back and retaining the user in Telegram: [openclaw/agents-gstack-section.md](../repo/openclaw/agents-gstack-section.md), lines 5–42. [docs/OPENCLAW.md](../repo/docs/OPENCLAW.md), lines 3–8, states this is a prompt bridge. No Telegram bot transport or Butler service is implemented by gstack. |
| F05 | Cross-project registry, intake and project routing | **Resembles** | Repository slugs scope artifacts; OpenClaw instructions resolve a named repo and ask when its path is unknown ([openclaw/agents-gstack-section.md](../repo/openclaw/agents-gstack-section.md), lines 10–12). This lacks a portfolio registry, existing/new-product classification, new-project creation and leadership allocation. State-root and project buckets are storage addressing, not project intake. |
| F06 | Per-project product and technical leadership | **Resembles** | CEO/eng phases and Captain/lane responsibilities provide product and technical perspectives: [autoplan-state.ts](../repo/lib/autoplan-state.ts), lines 45–83; [docs/captain.md](../repo/docs/captain.md), lines 29–48, 134–164. CEO/eng are review phases, not independently available persistent leaders for each product. Captain concentrates coordination in one controller. |
| F07 | Proportionate discovery and iterative clarification | **Similar** | `/spec` forces why, scope, code-grounded questioning and draft review: [spec/SKILL.md.tmpl](../repo/spec/SKILL.md.tmpl), lines 81–180. Office-hours considers user goals and planning distinguishes fixes, lean features and full runs ([office-hours/SKILL.md.tmpl](../repo/office-hours/SKILL.md.tmpl), lines 99–110; [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 299–308). Strong methodology, but questions occur through the host/controller rather than project-correlated Butler conversations. |
| F08 | Scope, specs, acceptance scenarios and done criteria | **Similar** | Spec templates include scope, execution sequencing, dependency graph and measurable definition of done ([spec/SKILL.md.tmpl](../repo/spec/SKILL.md.tmpl), lines 135–176, 260–417). Filing/archive flow connects the issue and local spec. The unit is usually one issue/feature. There is no enforced product-wide `DIRECTIVES/SCOPES/SPECS/HARNESS` record model. |
| F09 | Decomposition, assignment and shared task tracking | **Similar** | Spec execution plans and crew briefs allocate work; `gstack-tasks` persists review tasks and reconciles carried/done/dropped items ([bin/gstack-tasks](../repo/bin/gstack-tasks), lines 21–38, 68–99). Crew digest records lane ownership. These are real tracking primitives, but no unified ProjectTracker with arbitrary worker assignments, ticket state and shared comments across products. |
| F10 | Portfolio/project management dashboard | **Resembles** | `/landing-report` renders a read-only workspace version/ship queue ([landing-report/SKILL.md.tmpl](../repo/landing-report/SKILL.md.tmpl), lines 6–8, 81–121); digest is Markdown. Neither is a portfolio application presenting projects, specifications, tasks and responsible agents. No such native dashboard routes/components were found. |
| F11 | Agent chat app, rooms and direct collaboration | **Resembles** | Capy host messages and shared reports support controller-mediated communication. The crew explicitly forbids peer-to-peer routing ([docs/captain.md](../repo/docs/captain.md), lines 122–126). No gstack chat application, Room1/Room2 persistence or direct specialist room conversation implementation. External host chat remains external. |
| F12 | Escalation and human decisions/approvals | **Similar** | Plan gates, owner briefs, approval records and relayed owner words are substantive: [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 266–319; [test/capy-captain-flow.test.ts](../repo/test/capy-captain-flow.test.ts), lines 54–85. Gate revision/recommendation hashes bind the reply. This replaces a multi-level room escalation chain with owner → controller → lane. |
| F13 | Durable project knowledge and directives | **Similar** | Plans/spec archives, decisions, learnings, checkpoints and repo-scoped retrieval persist knowledge. [context-save/SKILL.md.tmpl](../repo/context-save/SKILL.md.tmpl), lines 149–228; [bin/gstack-brain-context-load.ts](../repo/bin/gstack-brain-context-load.ts), lines 3–24. Wingman's directive hierarchy and product knowledge ownership need mapping; optional gbrain sync adds an external dependency. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | Planning attempts and train state have durable IDs; checkpoints preserve decisions, remaining work, repo/worktree/HEAD; `/spec` prints native `claude --resume` guidance ([autoplan-state.ts](../repo/lib/autoplan-state.ts), lines 15–83; [context-save/SKILL.md.tmpl](../repo/context-save/SKILL.md.tmpl), lines 149–228; [spec/sections/gate-and-file.md](../repo/spec/sections/gate-and-file.md), lines 458–464). Continuous agent identity and full conversation retention rely on the host. |
| F15 | Proactive supervision and periodic wake | **Resembles** | Captain digest identifies stale lanes/READYs and prescribes follow-up; daily flaky-pass automation has a supplied prompt ([captain/templates/DIGEST.md](../repo/captain/templates/DIGEST.md), lines 32–33; [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 250–264, 321–343). No native ongoing ProjectMaster scheduler, autonomous wake registry or organization blocker supervisor; scheduled thread creation belongs to the host. |
| F16 | Parallel products and concurrent specialists | **Similar** | Independent worktrees, lanes, reviewer processes and Capy subagents genuinely allow concurrency ([spec/sections/gate-and-file.md](../repo/spec/sections/gate-and-file.md), lines 405–458; [lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 176–278). Project-scoped state avoids some cross-repo mixing. Multiple products remain separate host/repository workstreams, without a portfolio coordinator allocating teams. |
| F17 | Multi-host execution with shared coordination | **Resembles** | Real remote compute is implemented: Ubicloud provisions VMs, waits for SSH, synchronizes repository/worktree state, runs checks remotely and returns artifacts ([scripts/ubicloud/ubi-runner.sh](../repo/scripts/ubicloud/ubi-runner.sh), lines 971–1023, 1116–1201). Other real remote surfaces include browser tunnel pairing, iPhone tailnet, remote CI and Git-note train recovery ([browse/src/routes/pairing.ts](../repo/browse/src/routes/pairing.ts), lines 13–45; [ios-qa/daemon/src/index.ts](../repo/ios-qa/daemon/src/index.ts), lines 1–13; [ship-queue-train-record.ts](../repo/lib/ship-queue-train-record.ts), lines 1–9). Capy also supplies external-host workers. These are substantive distributed job/tool primitives, but no native Mac/Endeavour standing Codex placement, host registry or shared full-organization protocol. |
| F18 | Executive current/recent/next/blocker overview | **Similar** | Captain digest has Needs you, New and In progress with thread, ownership, age and blocker states. It is rewritten every controller turn ([captain/templates/DIGEST.md](../repo/captain/templates/DIGEST.md), lines 1–33). This is a meaningful executive briefing primitive, not merely an event log. It is crew-level Markdown, lacks standardized per-agent next-work fields and connected web/mobile executive views. |
| F19 | Individual summary timeline with underlying links | **Resembles** | Timeline log records skill started/completed, branch, outcome, duration and session ([bin/gstack-timeline-log](../repo/bin/gstack-timeline-log), lines 2–10); read helper filters project/branch. It is a project session/event history, not a per-employee narrative feed linked to tasks/chats/artifacts. Stop-hook completions may say `unknown` and cannot reliably attribute the current native session ([hosts/claude/hooks/timeline-stop-hook.ts](../repo/hosts/claude/hooks/timeline-stop-hook.ts), lines 3–48). |
| F20 | Detailed individual coding workspace | **Similar** | Browser sidebar has a PTY-backed Claude session, streamed output, session IDs and replay ([browse/src/terminal-agent.ts](../repo/browse/src/terminal-agent.ts), lines 1–36, 86–148). Native host sessions provide fuller coding tools. No integrated navigation from an organization agent directory to every worker's files, tools, tests and artifacts. |
| F21 | Live activity, lifecycle controls, steering and visibility | **Similar** | Native terminal input/attach/restart and Capy subagent start/list/stop provide real controls; runner timeout/cancel and durable planning status are implemented ([terminal-agent.ts](../repo/browse/src/terminal-agent.ts), lines 57–148; [capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 176–223; [outside-voice-runner.ts](../repo/lib/outside-voice-runner.ts), lines 124–160). No single workforce UI for fork/rename/compact/archive/queued attachments, budgets and execution host routing. |
| F22 | Testing, integrated verification and acceptance/delivery | **Similar** | Strongest execution fit: QA/verify/ship workflows, staged specialist review, receipts, CI and train-prefix verification. [bin/gstack-review-dispatch](../repo/bin/gstack-review-dispatch), lines 43–91; [lib/ship-queue-train-verify.ts](../repo/lib/ship-queue-train-verify.ts), lines 1–15, 118–167; [spec/SKILL.md.tmpl](../repo/spec/SKILL.md.tmpl), lines 479–487. Shipping evidence is stronger than a simple green checklist, but product acceptance by a standing ProductMaster/TestMaster organization is not implemented. |
| F23 | Autonomous organization under human direction | **Resembles** | Unattended planning and crew lane discipline support sustained bounded work, with recorded human gates ([autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 210–284; [docs/captain.md](../repo/docs/captain.md), lines 128–164). The host must initiate/continue workers, supply messaging and scheduling, and the controller remains one host agent. No self-contained continuing organization from Telegram intake to multi-product delivery. |
| F24 | Chat/tracker/dashboards grow with new profiles | **Resembles** | Generic lane names, arbitrary skill/checklist additions and parameterized crew templates accept new worker kinds. Digest rows are flexible text ([captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 62–94; [captain/templates/DIGEST.md](../repo/captain/templates/DIGEST.md), lines 24–28). There are no native chat/tracker/dashboard schemas to extend consistently when adding an organizational profile. |

## Agent definition and lifecycle in detail

### What is actually an agent?

Four distinct entities must not be conflated. A **skill** is a prompt/procedure loaded into an existing host session. A **planning run** is an on-disk state machine coordinating review phases and artifacts. A **reviewer** is a bounded host subagent, local Codex CLI subprocess, or remote model call. A **crew lane** is an external-host thread with branch/file ownership and an explicit completion contract. The browser terminal's Claude PTY is another real local coding session, but not a standing project role.

The model preference helper reinforces this distinction: it selects a preferred model for lanes, subagents and reviewers, with request/config/preferences/host precedence, and exempts cross-family outside voices and evaluation arms ([lib/agent-model.ts](../repo/lib/agent-model.ts), lines 5–53, 75–86). A model choice is not an agent identity or team membership declaration.

### Definition, creation and identity

Skill definitions carry metadata and allowed tools; specialist review checklists define what to inspect. Captain configuration supplies repository, base, required checks, train policy, spend and controller identity; lane briefs supply ownership and scope. There is no persisted “create BackendCoder instance” API. The controller creates a host thread/subagent, then gives it those instructions.

The `/spec` procedure files and archives an issue, checks dirty-worktree handling, and pins a commit. It creates a unique branch/worktree suffix and the worktree. It then starts `GSTACK_SESSION_KIND=spawned claude -p`. stdin receives the archived specification and autoplan contract. See [spec/sections/gate-and-file.md](../repo/spec/sections/gate-and-file.md), lines 365–461.

Skill instructions initiate this background process. They do not register an enduring organizational worker. PID, branch/path, and issue/specification IDs identify the work. Native Claude identifies the conversation. If worktree creation fails, documented fallback can use the current directory (lines 430–434). Isolation is therefore conditional.

Capy reviewers instead get manifest reader identifiers, prompts, host paths and recorded state transitions. The program records intent before host creation and records the returned path afterward; pending/rejected work is started as capacity becomes available ([lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 176–200, 260–280; [bin/gstack-review-dispatch](../repo/bin/gstack-review-dispatch), lines 67–91). Their host identity belongs to a task, not a persistent organization directory.

### Execution, tools and permissions

Host skills use the tools exposed by their harness. A YAML `allowed-tools` declaration is a host instruction/configuration surface. It is not gstack's own universal process sandbox. The local outside Codex reviewer does have a selected sandbox and read-only repository-review capability in the runner contract. API review explicitly has no filesystem access. Host-subagent access is marked `host`, avoiding a false promise of a common security boundary ([lib/outside-voice-runner.ts](../repo/lib/outside-voice-runner.ts), lines 29–35, 112–148).

Browser pairing has a separate capability system. Setup-key exchange issues an expiring client token; root-only `/pair` resolves scopes, control access, rate limits and own-tab policy, and narrowing a grant revokes old access before issuing replacement keys ([browse/src/routes/pairing.ts](../repo/browse/src/routes/pairing.ts), lines 29–45, 52–116). That governs browser operations, not arbitrary coding-agent shell permissions. The terminal companion is loopback-only with WebSocket origin validation and internal-grant cookies ([terminal-agent.ts](../repo/browse/src/terminal-agent.ts), lines 6–15).

### Routing and concurrency

There are several routes: user → current skill; OpenClaw → ACP spawned Claude; Captain → lane; planning phase → native/outside reviewer; CLI → browser daemon. OpenClaw's five dispatch tiers choose simple, medium, heavy, full or plan-only methodology ([openclaw/agents-gstack-section.md](../repo/openclaw/agents-gstack-section.md), lines 19–51). This can be reused as intake policy, but it does not look up a project registry or attach a persistent ProductMaster.

Concurrency exists at the process, worktree and host-subagent levels. Same-run mutation is serialized by a lock which refuses live owners and reclaims dead-owner locks ([lib/autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 40–76). Review manifests distinguish readers/stages so red-team review receives earlier specialists' findings. File ownership is a Captain policy rather than a distributed lock over product files; integration is serialized by READY pins and train slots. Wingman would still need to decide how concurrent agents share source, how tickets lease ownership and how conflicting decisions are reconciled outside the release queue.

### Persistence and resumption

Planning IDs survive process death through manifests and journals. `next` redisplays open attempts instead of minting duplicates; completed voices are not resurrected. Resume replays terminal journal outcomes, rebinds completed results only when hashes match, and marks unaccounted dispatches `execution_unknown` ([lib/autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 247–279, 487–545). It does not blindly repeat possibly paid calls. Explicit redispatch supersedes the unknown attempt and preserves unknown spend before a new reservation (lines 261–275).

Checkpoints capture semantic work state: what was done, decisions and remaining work, with branch, origin, worktree and HEAD metadata ([context-save/SKILL.md.tmpl](../repo/context-save/SKILL.md.tmpl), lines 76–119, 149–228). Restore prefers current-branch checkpoints, retains cross-branch fallback, and distinguishes foreign/unverified project buckets ([context-restore/SKILL.md.tmpl](../repo/context-restore/SKILL.md.tmpl), lines 36–48, 93–166). This is a prompt-driven context handoff, not serialized restoration of every live tool/process or native conversation. `claude --resume` remains the native conversation route for the spawned implementation path.

The terminal has stable non-secret session IDs, one-time attach grants, in-memory PTY records and bounded replay. A detached session survives only the configured window, default 60 seconds; scrollback is capped ([terminal-agent.ts](../repo/browse/src/terminal-agent.ts), lines 57–81, 121–148). This should not be confused with indefinite background workforce continuity. Process identity and cleanup use structured PID/generation/start-time records rather than regex-based killing ([terminal-agent-control.ts](../repo/browse/src/terminal-agent-control.ts), lines 1–15, 121–164).

### Scheduling, interruption and cancellation

Captain says to update the digest every turn, act on stalls and schedule a daily flaky-fix lane. Its supplied automation is a prompt for the host to schedule, not a gstack clock or durable wake queue ([captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 250–264, 321–343). Browser idle checks and terminal watchdogs supervise tool processes. They do not wake product management agents to inspect work.

The outside CLI runner's `cancel()` sends SIGTERM; timeouts send SIGTERM then schedule SIGKILL and return distinct cancelled/timeout statuses ([lib/outside-voice-runner.ts](../repo/lib/outside-voice-runner.ts), lines 124–160). Capy pass code stops a stuck outside reviewer, records unavailable coverage rather than a clean review, and stops on other failed/ambiguous reader states ([lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 5–17, 129–137, 200–223). There is no single gstack cancellation API that retires an entire project team, cancels every host process and updates an organizational agent directory.

### Failure, retry and recovery

The recovery machinery is unusually explicit for a workflow layer. Planning journals dispatch before the final manifest write, reserves potential spend and refuses unknown executions. Plan edits can require amendments/reviews instead of silently reusing old approval. A spend-cap stop remains incomplete, not success. Native versus outside model-family checks prevent two voices from being credited as independent families when they are not.

Release failure is handled separately. A train stores pinned PR heads, prefix trees, gate attempts and landed slots. Verification checks both the current head and the expected base/prefix. A partial publication mismatch writes a freeze locally and to Git notes before dispatching a backstop ([lib/ship-queue-train-verify.ts](../repo/lib/ship-queue-train-verify.ts), lines 1–15, 143–167). A new machine can reconstruct freeze state. This is durable recovery for a release protocol, not automatic repair of arbitrary worker blockers.

### Completion, acceptance and cleanup

Different entities have different terminal states. A review voice completes when its output is classified and bound. A planning run can be reviewed, gate-pending, incomplete, refused or complete. An approved plan is permission to build, not proof of product completion. A lane completes its task at READY plus its report; merge/delivery is owned by the controller. A train completes only after verified slot merges. `/spec` instructs `/ship` to close the source issue only if the PR delivers the full archived spec and acceptance criteria, not simply because the branch name resembles an issue ([spec/SKILL.md.tmpl](../repo/spec/SKILL.md.tmpl), lines 479–487).

Cleanup follows those boundaries. Train terminal states allow branch pruning ([ship-queue-train-record.ts](../repo/lib/ship-queue-train-record.ts), lines 21–25). Captain archives only its own crew threads according to their plan, while owner threads remain owner-controlled ([docs/captain.md](../repo/docs/captain.md), lines 34–42). Capy instructions stop a finished `/ship` child after the parent subscribes to its PR and takes ownership ([capy/skill/gstack/SKILL.md](../repo/capy/skill/gstack/SKILL.md), line 58). The `/spec` path preserves user stashes rather than automatically dropping them (gate-and-file, lines 464–471). No universal agent retirement/tombstone lifecycle exists beyond host threads, process cleanup and workflow records.

## Coordination mechanics and a concrete request trace

The native coordination medium is files and typed artifacts, complemented by GitHub issues/PRs/checks and host messages. Task rows are findings from plan review, with IDs, priority, component, title, source finding, estimated effort and files. Carry-forward dispositions track done/dropped work and reasons, and supersede reconciled earlier lists ([bin/gstack-tasks](../repo/bin/gstack-tasks), lines 21–38, 79–99). They are not a general issue-dependency scheduler; dependencies and sequencing can be written in a spec, while a host controller decides assignment/order.

A concrete checked-in request is the webhook retry-backoff scenario in [test/capy-captain-flow.test.ts](../repo/test/capy-captain-flow.test.ts), lines 20–47. It proposes 500 ms to 30 s exponential backoff, jitter and persisted attempt count, triggered by “webhooks vanish under load.” The fixture traces actual CLIs on a simulated Capy host. It is stronger than a README example, but was inspected rather than executed here:

1. The controller/lane writes a plan containing ELI5, before/after, why, trigger, decisions and implementation plan. Test lines 54–60 call the autoplan runner and supply native/outside phase results. The runner creates state, snapshots and attempts; CEO/eng phases close only after results are bound.
2. The run reaches `gate_pending` and emits a `RELAY` command rather than treating reviewers' recommendations as owner permission (test lines 61–63). The run's artifact IDs and gate revision correlate the request and decision.
3. `gstack-owner-brief render --captain --json` renders the human-facing brief, checks required sections and exposes `gate_rev` and `rec_hash` (test lines 65–70). The behavior is implemented in [lib/captain-brief.ts](../repo/lib/captain-brief.ts), alongside the gate/owner-brief helpers. The controller must send this via its host's communication tool; gstack does not deliver a Telegram message.
4. The relayed answer calls `answer --gate-rev … --reply … --rec-hash … --by agent:GSTA-1 --owner-reply …`. The test checks `APPROVED` (lines 72–75). Owner words are attached to a specific recommendation snapshot, reducing stale-approval ambiguity.
5. `gstack-approvals import --autoplan …` records the owner decision and mirrors it into the shared approvals directory. A second identical import is skipped (lines 77–85). This is persisted decision evidence, not a conversation-room event.
6. The lane implements in its owned branch, runs `/ship`, and requests READY. [lib/ship-queue-train-ready.ts](../repo/lib/ship-queue-train-ready.ts), lines 1–19, 98–104, and 145–167, selects a screen explicitly. It binds that selection to a receipt. A prior red screen cannot count as a new opportunity at the same merge SHA. The READY contract also requires a pinned head, required CI, pregate, and ship receipt. See [captain/SKILL.md.tmpl](../repo/captain/SKILL.md.tmpl), lines 96–129.
7. The controller builds a train from frozen pins; integration is tested on prefix trees. A slot is stamped on call, verified before merge and verified again afterward. [test/ship-queue-train-verify.test.ts](../repo/test/ship-queue-train-verify.test.ts), lines 21–85, traces two slots, an out-of-order refusal, a stray-file mismatch, durable freeze, fresh-state reconstruction and repair. This connects branch work to delivered source evidence without claiming that the webhook feature itself was built by that test.
8. The controller updates Needs you/New/In progress and appends notes. The lane writes Outcome/PR/Needs/Cost/Lesson/Approvals. Host subscriptions and scheduled wakes continue the conversation externally. No Room2 broadcast or product registry transaction occurs in this path.

The key dependency is source identity: plans, reviewer inputs, PR heads, CI and trees must refer to the same work. This is more carefully enforced than task ownership or human-message delivery. A Wingman integration should retain these typed receipts while supplying reliable organization events, ticket transactions and host routing around them.

## Major capabilities beyond Wingman's described product

### Evidence-preserving specialist review and model diversity

The review dispatcher renders exact specialist prompts, verifies what was sent, collects raw labeled findings, and rejects judgment that drops or downgrades findings. It distinguishes refusal/empty output from “no findings” and checks the reviewed checkout/tree ([bin/gstack-review-dispatch](../repo/bin/gstack-review-dispatch), lines 43–66; [lib/review-ledger.ts](../repo/lib/review-ledger.ts), lines 1–41 and 256 onward). Staged manifests coordinate specialist → red-team → adversarial voices. Wingman describes functional testing but does not specify this evidence chain or cross-model adversarial process.

Value: prevent a coordinating agent from compressing away inconvenient review findings or claiming an unavailable reviewer was clean. Integration consequence: preserve prompt/output bytes, model family, tree identity and review dispositions as first-class tracker artifacts. Enforced severity preservation can also retain false-positive noise. A separate explicit resolution policy is needed, rather than silently lowering labels.

### Release trains, stamp equivalence and distributed recovery

READY pins, one full gate on a train, prefix trees, stamp-only changes, post-merge verification, freeze/backstop repair and Git-note recovery go substantially beyond Wingman's delivery outline. The train record contains enough state to distinguish dispatch-unknown, gate-pending, incomplete, red, merging and superseded outcomes ([lib/ship-queue-train-record.ts](../repo/lib/ship-queue-train-record.ts), lines 21–99). Generic policy inspection also reads branch protection and workflow requirements before recommending a usable train configuration ([lib/ship-queue-train-init.ts](../repo/lib/ship-queue-train-init.ts), lines 1–10, 25–69).

Value: concurrent specialists can integrate without letting late release metadata invalidate all evidence or letting a partial merge disappear from memory. Integration consequence: adopt repository-specific ship policies, GitHub permissions, expected-head merging and a single release owner; mirror failures and freeze state into Wingman's tracker instead of just printing them in a terminal. Git notes are useful backup transport but do not replace transactional organization storage.

### Browser, authenticated remote browser and real-device QA

Aside/fallback browser tooling covers persistent browser state, visual evidence and real logged-in sessions. Pairing adds scoped remote browser clients; iOS QA has a Mac-side device tunnel broker with optional Tailscale identity/allowlist/capability gating ([browse/src/routes/pairing.ts](../repo/browse/src/routes/pairing.ts), lines 29–116; [ios-qa/daemon/src/index.ts](../repo/ios-qa/daemon/src/index.ts), lines 1–27, 57–99). The iOS broker caches one bootstrap across concurrent callers and guards stale tunnel invalidation. This is a real remote execution surface, even though it is not distributed agent management.

Value: TestMaster could test authenticated flows or a USB-attached iPhone while executing elsewhere. Integration consequence: Wingman needs to separate tool capability from agent identity, route credentials/owner actions correctly, serialize conflicting device/browser interactions and attach evidence to the right project. Aside is optional and platform-specific; fallback behavior and dependencies need host-specific validation.

### Contained security assessment with explicit assurance levels

Wingman places security outside TestMaster. gstack's `/cso` adds runtime/scanner catalogs, contained preparation/execution, structured findings, repair bundles, and external assertion witnesses. [lib/cso/verification.ts](../repo/lib/cso/verification.ts), lines 43–79, records before/after observations and policy/source/harness hashes. It also records `testCompletionAssurance: 'self_reported'`. [lib/cso/contracts.ts](../repo/lib/cso/contracts.ts), lines 106–112 and 352–354, separates runtime-tested and tested assurance. A reported passing command alone does not establish independent verification.

Value: add a security specialist with auditable coverage instead of silently expanding TestMaster. Integration consequence: Docker/native helper prerequisites, platform-qualified images and trust boundaries need an explicit deployment plan; static-only and runtime-tested results must remain visibly different. This assessment did not exercise containment or authenticate catalog qualification.

### Cross-session memory and research retrieval

Beyond saved plans, gbrain integration can ingest timelines/decisions/learnings and retrieve context at skill start. The loader dispatches vector/list/filesystem queries with repo filters, bounded timeouts and an untrusted-data envelope ([bin/gstack-brain-context-load.ts](../repo/bin/gstack-brain-context-load.ts), lines 3–24). This goes beyond simply having directive files by adding a retrieval layer and cross-machine sync options.

Value: bring earlier decisions and recurring findings into the next specialist session. Integration consequence: preserve authoritative directive files and provenance; retrieval is advisory and can be unavailable. Optional sync/privacy settings and external gbrain availability must not silently become prerequisites for basic project continuity.

### Paid-work budgets and workflow-quality evaluation

Autoplan reserves potential model spend before dispatch, accounts for unknown executions and stops when the next voices would cross the cap ([lib/autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 242–279). Capy pass programs read real thread token/credit counters ([lib/capy-review-pass.js](../repo/lib/capy-review-pass.js), lines 81–84), while gstack has a separate extensive free/paid evaluation infrastructure. The repository's validation rules distinguish rule, behavior and judge cases and forbid arbitrary retry-to-green ([AGENTS.md](../repo/AGENTS.md), Validation discipline).

Value: Wingman can put economic and evidentiary bounds around autonomous coordination, not just per-agent token limits. Integration consequence: reconcile unknown costs and host counters, distinguish verification code from paid model behavior, and keep capability claims tied to observed runs. Test infrastructure itself is not an always-on agent organization.

### Ephemeral remote compute with ownership and recovery

The Ubicloud runner implements remote workloads with owner/TTL-named VMs, quota preflight, SSH, and watchdogs. Detached phases support reattachment and checkpoints. Cleanup includes an owner-scoped reaper. See [scripts/ubicloud/ubi-runner.sh](../repo/scripts/ubicloud/ubi-runner.sh), lines 22–101, 269–329, 401–491, and 758 onward.

Provisioning creates a VM with a temporary SSH key and records state across signals. It waits for a running address, then checks SSH readiness (lines 971–1023). Repository packing uses Git transport for a consistent refs snapshot. It preserves the index, staged blobs, tracked files, and nonignored untracked files. It handles linked-worktree metadata and synchronizes the archive remotely (lines 1100–1187). Artifact pulls return selected remote files (lines 1190–1201).

This can move verification workloads and evidence between machines. It does not provide persistent distributed-agent placement. TTL enforcement requires a later invocation of the owner's reaper. It is not an independently hosted expiry guarantee. See [ubicloud/SKILL.md.tmpl](../repo/ubicloud/SKILL.md.tmpl), lines 69–100 and 112–137.

Value: TechMaster can allocate temporary build/evaluation capacity with attributable ownership and bounded hanging commands. Integration consequence: cloud credentials/costs, quota accounting, cleanup after a controller disappears and remote receipt ingestion need explicit Wingman ownership. A VM runner is not an Endeavour agent supervisor.

### Design generation, document artifacts and bounded production monitoring

The design CLI exposes model-backed mockup generation, variants, iteration, comparison, checking and design-to-code prompts; generation sends a receipted provider request with timeout and persists session/output/accounting ([design/src/cli.ts](../repo/design/src/cli.ts), lines 1–36; [design/src/generate.ts](../repo/design/src/generate.ts), lines 1–57). PDF orchestration renders Markdown, diagram fences, images and document figures through the chosen browser engine ([make-pdf/src/orchestrator.ts](../repo/make-pdf/src/orchestrator.ts), lines 1–44, 87–250). These are substantial deliverable-generation tools beyond Wingman's stated coordination product, not additional autonomous job roles.

The `/canary` workflow also prescribes a bounded post-deploy observation loop with screenshots, console-message identity, navigation timing, text snapshots and broken-link baseline comparison ([canary/SKILL.md.tmpl](../repo/canary/SKILL.md.tmpl), lines 31–85). It is agent-driven monitoring for a selected run, not a production alert service or ProjectMaster scheduler. Value: FrontendCoder can explore alternatives, ProductMaster can share reviewable artifacts, and release owners can observe production after delivery. Integration consequence: artifact ownership, paid provider access, browser permissions and monitor lifetime must be attached to the responsible project/agent; long-term operations remain separate infrastructure.

## Distinctive mechanisms and grounded innovation assessment

These are distinctive combinations visible in this checkout, not claims of historical novelty or industry uniqueness.

**Dispatch-intent journaling plus conservative economic recovery.** Planning records an attempt before work, distinguishes submitted/cancelled/superseded/unknown execution and keeps unknown reservations on crash. Resume only rebinds a result when its file hash matches; redispatch is explicit. This enables resumable paid multi-voice workflows without pretending every lost response was free or every retry harmless. The limit is that it protects the workflow ledger, not the underlying model service's exactly-once execution, and does not preserve arbitrary coding-process state ([autoplan-run.ts](../repo/lib/autoplan-run.ts), lines 247–279, 487–545).

**Approval attached to reviewed recommendations, with relay provenance.** The Captain flow carries gate revision/recommendation hash, owner words and relaying agent, then imports that record idempotently. This is a promising Butler pattern: human-facing prose remains readable while machine state prevents a reply from being applied to a different gate. It cannot prove the external host really delivered a human's message; authentication and trustworthy routing remain the host's responsibility ([test/capy-captain-flow.test.ts](../repo/test/capy-captain-flow.test.ts), lines 54–85; [capy/skill/gstack/captain.md](../repo/capy/skill/gstack/captain.md), lines 103–128).

**Review transport as an auditable no-loss protocol.** Render/sent/output/judgment hashes turn “I asked specialists” into reconstructible evidence. Reader manifests make stage ordering and missing coverage explicit; collection rejects wrong-tree and non-review output. This enables stronger accountability between a TechMaster-like coordinator and reviewers. It does not establish that every finding is correct, and its prose parsing and clean markers still require careful tests ([bin/gstack-review-dispatch](../repo/bin/gstack-review-dispatch), lines 43–91; [test/review-dispatch.test.ts](../repo/test/review-dispatch.test.ts), lines 163–292).

**Tree-equivalence-aware release acceptance and a recoverable freeze.** The queue reasons about tested prefix trees and allowed stamp changes rather than accepting any later green head. Unexpected publication after a partial merge becomes a durable freeze before a backstop is dispatched. Git notes let another controller machine recover that state. This enables disciplined parallel release integration with lower repeated full-gate cost. Its limits are declared stamp policy, GitHub workflow/branch-protection semantics, exclusive release ownership and remote-access availability. It does not solve arbitrary concurrent source edits ([ship-queue-train-verify.ts](../repo/lib/ship-queue-train-verify.ts), lines 1–15, 118–167; [ship-queue-train-record.ts](../repo/lib/ship-queue-train-record.ts), lines 1–9).

**Explicitly scoped remote tool identity.** Pairing narrows a browser client's grant without leaving old broad setup keys alive; iOS remote access binds Tailscale identity to capabilities. This enables a remote worker to borrow a human machine's browser/device safely within a defined tool scope. It remains tool-level delegation, not a global agent trust/identity system ([browse/src/routes/pairing.ts](../repo/browse/src/routes/pairing.ts), lines 61–109; [ios-qa/daemon/src/index.ts](../repo/ios-qa/daemon/src/index.ts), lines 3–13).

The architecture's most transferable innovation is therefore the conversion of selected coordination promises into typed, hash-bound, resumable protocols. The less formal parts—crew chat routing, ownership, digest updates and scheduled supervision—remain instructions to a capable host/controller. Wingman should adopt the former without mistaking the latter for an implemented organization backend.

## Practical fit and remaining work

**Use directly as a methodology/tool library:** `/spec`'s evidence-grounded clarification, product and engineering review sections, specialist checklists, QA procedures, explicit unknown/unavailable evidence statuses, checkpoint conventions and generic Captain briefing/report templates. Selected executables could supply reviewer ledgers, plan manifests, approval records and release gates after evaluating their dependency/support boundaries. The Ubicloud runner is also a concrete candidate for optional heavy remote jobs: it provisions/synchronizes/executes/collects/cleans up, with quota and hang controls. It would complement execution capacity, while a separate Wingman host adapter would still manage standing Codex agents on Mac and Endeavour. The checked-in Codex host being experimental argues for a targeted adapter spike before broad rollout, not an assumption of full parity with Claude/Capy.

Adapt into Wingman contracts:

- Map spec/plan/task artifacts to `DIRECTIVES` and ProjectTracker.
- Assign real ProductMaster/TechMaster/worker identities independently of skill names.
- Put project/agent/host IDs on every attempt, approval and timeline event.
- Turn `NEXT`, READY, budget-stop and freeze outputs into tracker updates/events.
- Connect human briefs to Butler's project-correlated Telegram conversation. Keep controller-only release authority while allowing the Room2 direct collaboration Wingman actually requires. Use gstack's run IDs and hashes for evidence, while Wingman remains the source of truth for work ownership and accepted scope.

Build around it:

- Telegram transport and Butler service.
- Cross-project registry/intake.
- Durable agent directory and profile lifecycle.
- Independently resumable Codex sessions.
- Team/host placement across Mac and Endeavour.
- Shared chat rooms with participant/project/task links.
- General ticket dependency/assignment state.
- Periodic ProjectMaster supervision.
- Executive and project web/mobile applications.
- Per-agent narrative summaries/timelines.
- Integrated session drill-down and steering controls. These are primary Wingman product components, not minor setup tasks solved by installing gstack.

The most sensible architectural role is an **engineering execution layer below Wingman's organization and project services**. A release-focused Captain pattern could guide TechMaster's integration responsibilities, but replacing Butler/ProjectMaster/ProductMaster/TechMaster with one Captain would materially change the intended organization. Multiple gstack installations and shared Git notes help distribute tools and release state. They do not, by themselves, create shared conversations, cross-host agent supervision or a portfolio control plane.

## Verification scope and limits

Read applicable checkout [AGENTS.md](../repo/AGENTS.md) before substantive inspection. No ancestor `AGENTS.md` files were present in the traversed workspace ancestry. The supplied global user instructions were followed. `captain/templates/AGENTS.md` is a template for future crews, not governing instructions for this report. Repository sources were read-only; only this assessment file was created.

The implementation review covered these areas:

- Setup, package, architecture, Captain procedures, and Capy/OpenClaw integration.
- `/spec`, gate/file/process-creation sections, and context save/restore templates.
- State roots, model selection, planning state/run/recovery, and outside-review runners.
- Review dispatch, Capy passes, task reconciliation, and train ready/record/init/verify modules.
- Browser pairing, terminal processes, timeline/Stop hooks, memory retrieval, and iOS daemon.
- CSO verification/contracts, Ubicloud, design generation, PDF orchestration, and canary templates.

The cited line ranges support each conclusion. Documentation-only behavior remains identified as host procedures or instructions.

Relevant tests inspected, **not executed**:

- [test/autoplan-run-recovery.test.ts](../repo/test/autoplan-run-recovery.test.ts), lines 26–105 and 130–240: open-attempt reuse, receipt/family/stale-result refusal, phase closure, crash/unknown/resume and sealed-result behavior.
- [test/autoplan-run-concurrency.test.ts](../repo/test/autoplan-run-concurrency.test.ts), lines 26–105: live/empty lock handling, concurrent submits/next, revision ownership and acknowledgment idempotence.
- [test/capy-captain-flow.test.ts](../repo/test/capy-captain-flow.test.ts), lines 1–8 and 54–92: simulated-host CLI relay/approval flow and a non-Capy negative control. This does not exercise the real hosted Capy system.
- [test/ship-queue-train-verify.test.ts](../repo/test/ship-queue-train-verify.test.ts), lines 21–85, 92–135 and later stamp checks: fixture-backed prefix acceptance, wrong head, freeze, reconstruction and repair. GitHub behavior is simulated by fixtures.
- [test/review-dispatch.test.ts](../repo/test/review-dispatch.test.ts), lines 41–101, 163–292: prompt integrity, collection, dropped/downgraded finding refusal and missing-reader conditions.
- [test/captain-skill.test.ts](../repo/test/captain-skill.test.ts), lines 20–111: skill/contract/template presence. These are largely source/content assertions, not proof a real autonomous Captain reliably runs a crew.
- [test/state-root-parity.test.ts](../repo/test/state-root-parity.test.ts), lines 72–145: Bash/TypeScript state/config precedence parity.

Missing-feature conclusions used implementation inventory/searches across `lib/`, `bin/`, `captain/`, `capy/`, `openclaw/`, browser routes/terminal code, context helpers and timeline/dashboard/session files. Searches covered Telegram/Butler/project routing, registry, chat/rooms, scheduler/wake/supervision, directory/dashboard and host/session control terms. This located the OpenClaw Telegram prompt bridge, real timeline helpers, digest, browser terminal, remote tool protocols and scheduled-automation template, which are credited above. It did not locate a native Telegram transport, project-portfolio backend, chat-room service, agent directory application or periodic organization scheduler. Negative findings concern this checkout; external Capy, OpenClaw, Aside and gbrain may supply additional capabilities outside its implementation.

No claims here verify real model quality, successful paid evals, browser/device operation, containment security, production merges or multi-machine continuity. Existing historical logs elsewhere in the Wingman workspace were not used as proof for this revision. This is a fresh source-grounded assessment of the stated commit, with host-dependent behavior and runtime uncertainty retained explicitly.
