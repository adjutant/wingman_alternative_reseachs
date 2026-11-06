# multi-agent-shogun assessment for Wingman

Repository: https://github.com/yohey-w/multi-agent-shogun  
Local checkout: `researchs/multi-agent-shogun/repo`  
Inspected commit: `aff8dc8495da26a2aad582257457655fa953b57e`  
Assessment date: November 5, 2026  
Baseline: [WINGMAN_PURPOSE.md](../../WINGMAN_PURPOSE.md)

**Verdict:** A useful reference implementation for a persistent, human-directed hierarchy of real coding agents, especially its mailbox delivery, task recovery and explicit separation of management from execution. It is a partial organizational foundation for Wingman, rather than a complete implementation. Its center is a local tmux formation with agent-authored YAML and Markdown records. Wingman still needs project-specific product/technical leadership, Telegram routing, navigable agent collaboration rooms, distributed execution and connected executive/project/session views.

The strongest match is the organization operating through its own independent CLI agents. The most consequential difference is that much of the organization is a **prompt protocol**. Bash/Python infrastructure launches processes and delivers messages, but an LLM reads and changes tasks, resolves dependencies, performs acceptance and writes summaries. That is real executable behavior when the agent follows its instructions. It is not equivalent to a server enforcing those transitions transactionally.

This is a static assessment of the pinned source. No CLI agents, services, Android application or tests were launched. Findings describe implementation and inspected test intent, not measured operational reliability. External service and provider behavior was not independently exercised.

The supporting [execution and protocol audit](Execution_Protocol_Audit.md) traces creation and identifies reuse limits. Dynamic worker IDs can conflict with fixed panes. Recovery status schemas and generated instructions differ. Mailbox readers and writers do not share one transaction boundary. These qualify the strengths below. They do not change the fact that this is a real multi-process agent formation.

## 1. Product and execution architecture

The standard formation is Lord (human) → Shogun → Karo → seven Ashigaru workers plus Gunshi. Shogun takes direction and issues purpose/acceptance contracts; Karo decomposes and schedules; Ashigaru execute; Gunshi handles strategic analysis and qualitative review. These are separate processes, not one model role-playing a conversation. Roles may use different coding CLIs and models, while sharing the filesystem and message protocol.

The launch path is [shutsujin_departure.sh](../repo/shutsujin_departure.sh), notably lines 335–454, 552–672 and 700–939. It replaces the named tmux sessions and preserves previous queue files by default. It initializes them under `--clean`, creates a Shogun session and a 3×3 multiagent window, attaches stable `@agent_id`, `@model_name` and `@current_task` pane metadata, builds CLI commands and starts inbox watchers. The default topology is therefore ten agent processes on one machine.

The source has some dynamic formation support but it is not an unconstrained agent factory. [lib/agent_registry.sh](../repo/lib/agent_registry.sh), lines 11–125, reads ordered `cli.agents`, falls back to the historical formation when Karo is absent, and maps identities to panes. Separately, [the CLI adapter](../repo/lib/cli_adapter.sh), lines 1445–1467, extracts IDs beginning with `ashigaru`. The launcher still constructs nine subordinate panes and explicitly builds Karo/Ashigaru/Gunshi arrays. Its execution loops use contiguous `ashigaru1..count`, which can disagree with sparse/custom configured IDs. Arbitrary additional identities in a registry do not by themselves gain a generated role, process, workspace and complete UI integration. This distinction matters for Wingman's extensible profiles and many specialist instances.

The adapter [lib/cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 170–374 and 433–497, translates agent configuration into a CLI type, model and command. It includes branches for Claude, Codex, Copilot, Kimi, OpenCode, Cursor and Antigravity, but the file has overlapping allowed-CLI declarations and substantial CLI-specific behavior. Compatibility should be established per branch rather than inferred from the README's count of supported CLIs. Native coding, command execution, browsing and provider conversation storage come from those external CLIs; Shogun adds organization around them.

The coordination state is deliberately inspectable:

| Record | Actual responsibility |
|---|---|
| `queue/shogun_to_karo.yaml` | Purpose-bearing commands and their state. |
| `queue/tasks/ashigaruN.yaml`, `gunshi.yaml` | Current assignments associated with an agent slot. |
| `queue/tasks/pending.yaml` | Work awaiting prerequisites before assignment. |
| `queue/reports/*_report.yaml` | Worker outcomes, evidence paths and skill proposals. |
| `queue/inbox/{agent}.yaml` | Durable addressed notifications with sender, type, timestamp and unread state. |
| `projects/{id}.yaml`, `context/{id}.md` | Project metadata and knowledge. Actual project configuration is ignored/private, not present as an operational registry in this snapshot. |
| `dashboard.md`, `logs/daily/` | Agent-written secondary summaries and completed-command history. |

The distinction between primary YAML and secondary dashboard is explicitly documented in [AGENTS.md](../repo/AGENTS.md), especially the recovery and context sections. A stale Markdown summary is not intended to override task state.

## 2. Feature-by-feature comparison

Verdicts describe the complete Wingman capability named in the row: **Exact**, **Similar**, **Resembles**, **Absent**, or **Unclear**. Similar does not mean a small configuration change always closes the gap. Instruction-based behavior is identified explicitly.

| ID | Wingman capability | Verdict | Implemented behavior, evidence and remaining difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Separate CLI processes in tmux with stable identities; configurable models and task personas. [Launcher](../repo/shutsujin_departure.sh), lines 621–672, 700–939; [Ashigaru instructions](../repo/instructions/ashigaru.md), lines 118–124. Strong independent-worker substrate; standard roles are a fixed hierarchy and workers are reusable slots rather than durable BackendCoder/FrontendCoder/TestMaster instances per project. |
| F02 | Extensible profiles, roles and composition | **Resembles** | Ordered agent registry and per-agent CLI/model overrides exist. [Registry](../repo/lib/agent_registry.sh), lines 25–125; [instruction builder](../repo/scripts/build_instructions.sh), lines 53–150. Builder enumerates four roles and launcher fixes a nine-pane subordinate grid. Adding a wholly new profile requires coordinated code/instruction changes. |
| F03 | Agent directory and relationships | **Resembles** | Identity/model pane list in Android plus static hierarchy and task labels. [AgentsViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/AgentsViewModel.kt), lines 17–22, 87–151. No organization directory joining project/team, collaborators, tasks and timelines. |
| F04 | Telegram and Butler routing | **Similar** | A functional alternative mobile channel: ntfy listener persists incoming messages and wakes Shogun; Shogun routes commands or status queries and replies. [Listener](../repo/scripts/ntfy_listener.sh), lines 48–179; [Shogun role](../repo/instructions/roles/shogun_role.md), lines 104–143. No Telegram implementation found in runtime/Android/instructions searches. Shogun combines representative and strategic commander, without Butler→ProjectMaster→per-project-leader correlation. |
| F05 | Cross-project registry and intake | **Similar** | Setup creates a project list/current-project record: [first_setup.sh](../repo/first_setup.sh), lines 654–670. [Shogun instructions](../repo/instructions/shogun.md), lines 288–305, tell the agent to match names/aliases in private project metadata and echo its interpretation; commands carry `project`. Intake is agent reasoning over files, not a registry/routing service. Persistent new/existing-project discovery cases and correlated clarification answers are not established. |
| F06 | Per-project product and technical leaders | **Resembles** | Shogun handles purpose, Karo execution, Gunshi design/strategy/QC. [Gunshi role](../repo/instructions/roles/gunshi_role.md), lines 31–47. They are organization-wide shared roles, not a distinct ProductMaster and TechMaster pair with ongoing conversations for every product. |
| F07 | Proportionate discovery and human clarification | **Resembles** | Research/analysis personas, strategic evaluation and ambiguous SayTask-versus-execution routing exist. [Ashigaru instructions](../repo/instructions/ashigaru.md), lines 118–124; [Shogun instructions](../repo/instructions/shogun.md), lines 196–228. No implemented discovery case/clarification loop tailored to product size, tracked across multiple projects, was found in role/common instructions, scripts or Android models. |
| F08 | Scope, specs, acceptance scenarios and done definition | **Similar** | Commands require business north star, purpose and testable acceptance criteria; context template includes success, constraints and decisions. [Shogun role](../repo/instructions/roles/shogun_role.md), lines 35–60; [context template](../repo/templates/context_template.md), lines 4–31. This supplies a command contract, not a complete per-product scope/spec/test-scenario knowledge system or discovery-produced baseline. |
| F09 | Decomposition, assignment, shared tracking | **Similar** | Karo creates task YAML, assigns workers, uses `parent_cmd`, `blocked_by` and pending work, and consolidates reports. [Karo role](../repo/instructions/roles/karo_role.md), lines 37–83, 107–149; [task flow](../repo/instructions/common/task_flow.md), lines 9–111. A lightweight real shared tracker, executed through agents; lacks an enforced task API, general ticket comments/relationships and navigable project task UI. |
| F10 | Portfolio/project management dashboard | **Resembles** | `dashboard.md` includes in-progress/completed/action-needed material, rendered on web and Android. [Viewer](../repo/scripts/dashboard-viewer.py), lines 222–290; [Karo role](../repo/instructions/roles/karo_role.md), lines 96–136. Renderer exposes one document rather than portfolio→project→task→agent navigation. |
| F11 | Agent chat rooms and direct collaboration | **Resembles** | Addressed mailbox messages preserve sender/type/content; agents notify each other through the chain. [Inbox writer](../repo/scripts/inbox_write.sh), lines 9–15, 94–119. No participant-based rooms, discussion threads or human-readable chat application; normal worker→human and hierarchy-bypassing communication are expressly restricted. A transport is present, Room1/Room2 product collaboration is not. |
| F12 | Escalation and human decisions | **Similar** | Karo/Gunshi dashboard aggregation, action-needed notifications, Shogun as human representative, and Lord approval for strategic L6 decisions. [Karo role](../repo/instructions/roles/karo_role.md), lines 214–241; [Shogun role](../repo/instructions/roles/shogun_role.md), lines 94–122. Prompt-and-dashboard escalation lacks a structured, correlated question/approval object routed back to a responsible ProductMaster. |
| F13 | Durable project knowledge/directives | **Similar** | Per-project Markdown context, metadata, file memory and instruction templates survive sessions. [Context template](../repo/templates/context_template.md), lines 1–31; [AGENTS.md](../repo/AGENTS.md), lines 200–216. Content can hold Wingman directives, but `DIRECTIVES/SCOPES/SPECS/HARNESS` conventions and artifact connections must be added. |
| F14 | Identity/conversation/work continuity | **Similar** | Stable pane agent ID and YAML recovery preserve assignment identity/work; hooks restore persona/context. [Session hook](../repo/scripts/session_start_hook.sh), lines 22–89; [launcher](../repo/shutsujin_departure.sh), lines 393–454. CLI transcript persistence is external; restarts launch fresh processes and task changes may explicitly reset conversations. No central conversation-to-agent/project durable mapping was established. |
| F15 | Periodic supervision/blocker follow-up | **Resembles** | Watchers retry unread delivery and Karo scans reports whenever awakened. An optional standalone [watcher supervisor](../repo/scripts/watcher_supervisor.sh), lines 34–92, can restart missing watchers every five seconds when separately run; no non-test invocation was found in the checkout. The [standard launcher](../repo/shutsujin_departure.sh), lines 893–939, starts watchers directly. [Task flow](../repo/instructions/common/task_flow.md), lines 127–158, describes event-triggered report scans, not ProjectMaster's periodic semantic review of projects and unreported stalled work. |
| F16 | Parallel products/specialists | **Similar** | Multiple parent commands/projects share concurrent worker processes; instructions separate independent work and serialize conflicting writes. [Karo role](../repo/instructions/roles/karo_role.md), lines 138–149; [README](../repo/README.md), lines 639–645. A shared finite formation, not independently sized teams and leadership for each product. |
| F17 | Real multi-host execution/shared coordination | **Absent** | Launcher, registry and watchers target local tmux panes/files. SSH in [SshManager.kt](../repo/android/app/src/main/java/com/shogun/android/ssh/SshManager.kt), lines 133–188, is a phone controlling one remote server. [Copilot tool notes](../repo/instructions/cli_specific/copilot_tools.md), lines 54–58, mention provider-native remote delegation, but do not register remote Wingman-style workers in this formation. No distributed worker protocol, host placement registry or cross-host shared coordination found in launch/lib/scripts/common runtime paths. |
| F18 | Executive current/recent/next/blocker overview | **Resembles** | Agent-authored dashboard and current-task pane labels offer partial briefing. [Launcher](../repo/shutsujin_departure.sh), lines 655–672; [Karo role](../repo/instructions/roles/karo_role.md), lines 96–136, 254–258. No structured current/recent/next/blockers model for every agent, joined to project and underlying evidence. |
| F19 | Linked individual summary timeline | **Resembles** | Completion daily logs include worker artifacts and a command start/end timeline. [Karo role](../repo/instructions/roles/karo_role.md), lines 254–259. Archive files/history exist. There is no per-agent meaningful-activity timeline UI with links across tasks, conversations and tests. |
| F20 | Detailed agent coding workspace | **Similar** | tmux exposes each real coding CLI; Android enumerates panes, captures output and sends input. [AgentsViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/AgentsViewModel.kt), lines 87–168. Useful drill-down to a terminal, but no integrated structured conversation, tool-call, file/diff, test/artifact and task/chat workspace. |
| F21 | Live activity, lifecycle, steering, visibility | **Similar** | Output capture, direct pane input, CLI switching, context reset and activity labels are implemented. [AgentsViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/AgentsViewModel.kt), lines 71–168; [switch_cli.sh](../repo/scripts/switch_cli.sh), lines 316–390; [watcher](../repo/scripts/inbox_watcher.sh), lines 508–800. No unified managed fork/rename/archive/goal-budget lifecycle or structured queued steering/approval workflow. |
| F22 | Testing, integration, acceptance/delivery | **Similar** | Worker build verification, Gunshi qualitative QC, Karo purpose acceptance and daily outcomes are prescribed. [Ashigaru instructions](../repo/instructions/ashigaru.md), lines 62–76; [Karo role](../repo/instructions/roles/karo_role.md), lines 180–260. Strong process analogue; no mandatory per-product TestMaster, acceptance evidence service or delivery-state controller. Product correctness depends on agent execution and review. |
| F23 | Autonomous work under human direction | **Similar** | Shogun delegates and ends its turn while subordinate CLI agents run independently; events resume managers. [Task flow](../repo/instructions/common/task_flow.md), lines 113–158. Organization handles significant delegated work, but intake/discovery/delivery completeness and semantic periodic supervision remain unproven. |
| F24 | Views/coordination accommodate new profiles | **Resembles** | Addressed inbox can be created on demand and Android discovers panes dynamically. [Inbox writer](../repo/scripts/inbox_write.sh), lines 29–38; [AgentsViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/AgentsViewModel.kt), lines 93–151. Fixed role generation, launcher topology and canonical archival slots prevent treating this as full profile extensibility across chat/tracker/dashboard products. |

## 3. What an agent actually is, and how its lifecycle works

### Definition and creation

An agent is a long-running interactive coding CLI in a named tmux pane, coupled to an agent ID, instruction file, task slot, report slot and inbox. A task persona such as database engineer changes a worker's expertise instructions. It does not create a separate agent. The Shogun/Karo/Gunshi roles are standing identities, while `ashigaruN` is a reusable executor identity across projects.

| Concept | What is durable or independent |
|---|---|
| Role/profile | Instruction text for one of four recognized roles, combined with CLI configuration. |
| Agent instance | A named slot with its own interactive CLI process, task/report/inbox files and pane metadata. It is independent while running; its identity is not a separate database entity. |
| Session | CLI-owned conversation plus tmux terminal lifetime. Resetting a conversation need not change the slot or assignment. |
| Task | A purpose-linked YAML assignment; overwriting a slot changes its assignment without creating a worker. |
| Persona | Per-task expertise requested in instructions. Neither a process nor an independent identity. |

[scripts/build_instructions.sh](../repo/scripts/build_instructions.sh), lines 53–150, attempts to extract role front matter and composes `instructions/roles/*_role.md`, common protocol/task flow/forbidden actions, and CLI-specific instructions. It enumerates role×CLI variants, including generated Codex role files. This is more substantial than naming personas in a README: it produces concrete role instruction artifacts, although the checked-out Codex Karo artifact omits the original front-matter workflow. The agent creation boundary is a shell launch, not an API transaction that creates a project-scoped identity and all linked resources.

Configuration selects the CLI, model and optional environment/effort. The launcher stamps pane metadata before sending launch commands. The stable ID avoids confusing pane index with identity after pane rearrangement, a failure explicitly addressed by [instructions/ashigaru.md](../repo/instructions/ashigaru.md), lines 152–168. All workers start from the coordination repository and may be directed to external project paths. There is no automatic per-worker worktree or filesystem isolation in this launch path; conflicting writes are handled by the RACE-001 instruction to serialize or block.

### Tools, permissions and authority

Tools are primarily the capabilities of the chosen CLI and installed MCP integrations. Shogun does not implement its own coding-tool engine. The adapter defaults are highly autonomous: [lib/cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 246–274, uses a skip-permissions default for Claude and launches Codex with search plus approval/sandbox bypass. OpenCode has generated/configured permission support, but there is no uniform isolation policy applied to every CLI branch.

The command hierarchy, prohibition on contacting the human directly, per-worker file ownership and restrictions on destructive commands are largely instruction-level policy. There is some tool-level enforcement: [OpenCode permission configuration](../repo/config/opencode-permissions.yaml), lines 7–108, defines role-specific read/edit boundaries and denies direct inbox edits in favor of a tool. The inbox writer itself accepts arbitrary nonempty sender/type/target values and rejects self-send. It does not authenticate a process as the declared sender or enforce role authorization. On a trusted personal machine that may be a deliberate simplification. For Wingman it means the organizational policy layer and actual process/tool privilege need to be assessed separately, and permissions must be checked for each CLI.

### Assignment, scheduling and concurrency

Shogun writes a command with `north_star`, `purpose`, `acceptance_criteria`, `project` and priority. Karo acknowledges it, creates subtasks with `parent_cmd`, target path, Bloom level and prerequisites, and wakes available workers. Scheduling is agent reasoning over files, not a daemon acquiring task leases. A worker checks its own assignment, executes, writes a report and notifies the review/management chain.

The current common task protocol distinguishes pending work from assigned work and says prerequisite-blocked tasks must remain in `pending.yaml` until ready. Older Karo examples also show blocked tasks prewritten into worker slots. This is a meaningful consistency limitation: [instructions/common/task_flow.md](../repo/instructions/common/task_flow.md), lines 72–101, and [instructions/roles/karo_role.md](../repo/instructions/roles/karo_role.md), lines 74–83, preserve both patterns. A Wingman adaptation should make one schema and dispatcher authoritative rather than relying on agents to reconcile instructions.

Independent work can run concurrently, including commands for different projects. There is no separate concurrency budget per project and no elastic creation of new BackendCoders. Capacity is bounded by the configured/launched formation, model limits and manager/reviewer availability. Shared Karo and Gunshi can become serialization points even while workers are independent.

### Durable delivery versus process wake-up

The mailbox implementation is a particularly useful mechanism. [scripts/inbox_write.sh](../repo/scripts/inbox_write.sh), lines 40–145, assigns a timestamp/random ID, obtains a mkdir lock and optional flock, loads YAML, appends an unread message, writes a temporary file and renames it atomically. It retries lock/write failures up to three times. Beyond 50 messages it retains all unread messages and the newest 30 read entries, so unread work is prioritized over an absolute size cap.

The message itself stays in the file. [scripts/inbox_watcher.sh](../repo/scripts/inbox_watcher.sh), lines 875–968, sends only an `inboxN` nudge through the terminal. The receiving agent reads the actual content and marks it read. This decouples persistent communication from a potentially lossy keystroke channel. It is not exactly-once task execution: a delivered notification, a read flag and a correctly committed task outcome are different operations. Nor is the writer a durable room archive: old read messages can be pruned unless archival happens first.

Locking covers cooperating inbox writers, not every possible mutation. The common protocol instructs agents to mark messages read using Edit; OpenCode improves this through [a dedicated acknowledgment tool](../repo/.opencode/tools/mark-as-read.ts), lines 146–208, that checks current-agent identity and shares the writer's directory lock. However, [the archival utility](../repo/scripts/slim_yaml.py), lines 298–349, reads then rewrites the inbox through `save_yaml` without that inbox lock or atomic replacement. Its wrapper has a separate slimming lock. Concurrent arrival versus acknowledgment/archive is therefore not protected end to end. The writer also inserts message content into Python source rather than passing it as data (lines 80–101); its handling of arbitrary text deserves correction before reuse. The supporting audit explains these static findings without claiming a runtime reproduction.

The watcher combines Linux inotify/macOS fswatch events with a 30-second safety-net check (lines 1296–1359), active/self-watch detection, input throttling and CLI-specific recovery. Therefore “no polling” is best understood as avoiding repeated LLM supervision calls. The infrastructure does perform timed checks. This is sensible for token cost, but it is not a literal absence of polling or coordination overhead.

### Persistence and resume

Persistent work continuity comes from YAML/context reconstruction, while session conversation storage is delegated to the CLI. The default launcher preserves queues but kills and recreates named tmux sessions. It does not prove that a prior provider conversation is resumed. A restart can therefore preserve the work assignment while losing unrecorded conversational detail.

[scripts/session_start_hook.sh](../repo/scripts/session_start_hook.sh), lines 37–89, injects deterministic identity and recovery instructions for Claude startup/resume/clear/compact. Managers reread their persona and primary state; workers perform a lighter task/context recovery. Codex uses startup prompts and CLI-specific reset handling instead of that Claude hook. A stable agent ID survives as a slot identity. A single unbroken conversation is not guaranteed.

The reset mechanism deliberately trades conversational continuity for a clean task context. On new assignments or redo, the watcher may send `/clear`, `/new` or `/new-chat` according to CLI. A new task ID and `redo_of` distinguish corrections from the prior outcome. This can prevent stale instructions contaminating a retry, but requires complete task/context records to avoid losing useful reasoning.

### Interruption, failure, retry and recovery

The watcher avoids clearing a busy agent, translates reset commands per CLI, and attempts to guard cancellation/idle states when generating recovery notifications. See [scripts/inbox_watcher.sh](../repo/scripts/inbox_watcher.sh), lines 330–412, 532–800 and 1101–1265. The recovery guard reads top-level `status` (lines 369–375), whereas the launcher and role examples write nested `task.status`. This protection is not established for both schemas. Unread messages trigger increasingly forceful recovery, with different paths for Codex and command-layer agents. Busy state is derived from pane output and flags, not a structured execution event stream: [lib/agent_status.sh](../repo/lib/agent_status.sh), lines 33–128, inspects prompt/spinner/status text. The watcher also contains stale-busy recovery. These are substantial operational protections and also sources of CLI-version sensitivity.

For Claude, [scripts/stop_hook_inbox.sh](../repo/scripts/stop_hook_inbox.sh), lines 42–194, lets Shogun stop freely, recognizes certain completion/error phrases for notifications, checks unread messages and can block a stop with inbox instructions. It bounds recursive stop-hook handling and uses idle flags to avoid delivery deadlock. Its optional 55-second event wait is infrastructure waiting, not an agent repeatedly spending tokens to check its inbox. Other CLI paths do not inherit this exact behavior.

Failures are recorded in reports and reviewed by Gunshi/Karo; semantic task retries are management decisions. There is no general automatic retry budget, backoff policy, execution lease expiry or dead-letter task queue. The optional standalone [scripts/watcher_supervisor.sh](../repo/scripts/watcher_supervisor.sh), lines 34–92, restarts missing inbox watchers for existing panes when separately run. Searches found no non-test invocation. The [standard launcher](../repo/shutsujin_departure.sh), lines 893–939, starts watchers directly without wiring this supervisor. Even when enabled separately, it does not recreate dead coding agents, restore a lost conversation or decide that an apparently busy agent is failing its product assignment.

Live steering is possible by entering instructions in a terminal or through Android's pane input. [scripts/switch_cli.sh](../repo/scripts/switch_cli.sh), lines 316–390, exits the current CLI and detects the shell before switching. This is process control and fresh recovery, not transparent migration of a conversation between model providers. There is no uniform managed pause/fork/rename/compact/archive API or persistent input queue joined to task lifecycle.

### Completion, acceptance and retirement

Worker `done` is not intended to be sufficient for command completion. Gunshi performs qualitative review; Karo verifies the combined output against the original purpose, creates more work if the goal is unmet, records a daily summary and notifies the human. The mechanism is in [instructions/roles/karo_role.md](../repo/instructions/roles/karo_role.md), lines 180–260. Bloom-based QC distinguishes mechanical checks from qualitative judgment and adds Lord approval for L6. These are strong behavioral contracts but are not parser-enforced acceptance gates.

There is no native delivered-product lifecycle that stops a project's development/testing team after human acceptance. Completed commands are archived and worker slots become available. Projects can be archived through metadata conventions; agent retirement is effectively changing formation/configuration or terminating sessions. [scripts/slim_yaml.py](../repo/scripts/slim_yaml.py), lines 18–25, 186–292 and 300–413, archives terminal task/report/command/read-message state. Its canonical worker slot sets are still hardcoded, another limit on arbitrary profile expansion. `--clean` backs up selected prior records then resets task/report/inbox/dashboard files. This is an operational reset, not a per-agent audited retirement workflow.

## 4. One request through the actual coordination paths

Consider a human mobile request to add an API endpoint to an existing project. The following is an implementation trace, not a request executed during this assessment:

1. ntfy delivers the message to a long-lived JSON stream. `ntfy_listener.sh` filters outbound/nonmessage events, appends the request to `queue/ntfy_inbox.yaml` under a lock with atomic replacement, and writes a `ntfy_received` notification to Shogun's inbox (lines 142–173).
2. A watcher notices the inbox change and nudges Shogun. Shogun's role instructions classify it as a delegated command, read relevant project context, write the command contract and notify Karo. The classification/decomposition is performed by the live agent, not hardcoded NLP routing.
3. Karo acknowledges the command, decomposes the change into implementation and verification assignments, checks dependencies and available workers, and writes task YAML. It uses `inbox_write.sh` to notify the chosen worker. Any prerequisite work stays unassigned until ready under the current common protocol.
4. Worker recovery identifies its pane ID, reads its own task and project context, then uses its coding CLI's tools. It updates task/report records with outcome and evidence and notifies Gunshi for review. Integration conflicts are supposed to block for management rather than cause simultaneous writes to the same file.
5. Gunshi reviews the evidence, records findings and notifies Karo. Karo can reassign correction work with a new task ID/context reset, release dependent work or judge the aggregate result against the original acceptance contract.
6. Karo updates the dashboard, appends completed-command history and sends a mobile notification. Shogun reads the summary when answering the human. The normal protocol explicitly avoids Karo inbox notifications to Shogun, preserving the human-facing input pane.

The coordination product is thus **hierarchical command/task/report orchestration over addressed mailboxes**. It is neither chat-room-first collaboration nor a conventional ticket product. Wingman could reuse the durable-message separation, but its desired worker↔worker product discussion, participant-based management rooms and question routing need additional semantics and UI. The repository's hierarchy intentionally limits direct communication; Wingman's collaboration model deliberately permits richer lateral discussion.

## 5. Major capabilities beyond Wingman's stated product

### Heterogeneous CLI and model fleet

Wingman specifies Codex agents. Shogun can mix coding CLIs and model tiers, select a model for an agent, and switch an existing slot's CLI. Its Bloom-level routing helpers map task cognitive demands to configured capability tiers and subscription/cost groups. [lib/cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 649–883, implements capability/cost lookup and recommendation: configured preferences take priority, allowed cost groups filter candidates, and a fallback selects a sufficient capability tier or warns when insufficient. This is a substantial fleet-allocation capability rather than cosmetic model selection.

It would let Wingman reserve stronger models for design/review and use cheaper capacity for known procedures. Integration would require a provider-neutral execution and evidence schema; CLI-specific reset, permissions and activity behavior make this more than changing a model field. Bloom class and capability tiers are operator/agent assessments, not measured proof that a model can complete a task. There is also no demonstrated end-to-end cost optimum or hard organization spending cap.

The routing helpers do not own a scheduler: [find_agent_for_model](../repo/lib/cli_adapter.sh), lines 1291–1442, returns a matching idle Ashigaru, falls back to another idle worker, or returns `QUEUE`. It expressly leaves restart decisions to Karo. A missing pane is also allowed to return the configured candidate (lines 1372–1375). Moreover, generated Codex instructions omit the original Karo front-matter workflow containing dynamic routing Step 6.5. The helper implementation is concrete, but uniform automatic routing across all CLI/instruction variants is unverified.

### General white-collar delegation and a personal task system

The worker personas and templates support content, research, translation, operations and analysis as well as code. Shogun's **SayTask** path separates work delegated to agents from the human's own natural-language TODOs, including dates/categories and intent clarification. See [instructions/shogun.md](../repo/instructions/shogun.md), lines 196–228 and following task-management sections, plus `saytask/` samples. This is a different product surface from Wingman's software-development portfolio.

Its operational depth should not be overstated: much of SayTask is an agent instruction/data convention, and some input paths are explicitly marked future work. The value for Wingman is an optional distinction between “build this” and “remind me to do this,” not a prerequisite for the software organization. Streaks/frog displays themselves are minor and should not drive adoption.

### Mobile remote control of the actual coding fleet

The Android application uses SSH to enumerate and capture all subordinate panes, polls every five seconds, displays CLI output, and sends selected-agent input. It also renders the shared dashboard. [AgentsViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/AgentsViewModel.kt), lines 71–168; [DashboardViewModel.kt](../repo/android/app/src/main/java/com/shogun/android/viewmodel/DashboardViewModel.kt), lines 30–58. The combination of mobile command intake, notifications and terminal access is substantial operational capability.

Wingman already wants mobile visibility and workspace control, so this is an implementation example more than a missing Wingman product. What extends its Codex-centric formulation is direct SSH access to heterogeneous CLI panes without building a session-rendering server. The consequence is a weaker structured artifact/task integration and dependence on shell/tmux output. The SSH client is remote access to a host. It does not establish distributed agents across hosts.

### Bottom-up organizational learning

Workers include `skill_candidate` in reports, managers aggregate proposals and the human approves promotion into reusable skills. [instructions/ashigaru.md](../repo/instructions/ashigaru.md), lines 126–128, 188–210; [Shogun role](../repo/instructions/roles/shogun_role.md), lines 146–152. This is a concrete organizational-learning loop beyond merely preserving project specifications. It can turn repeatedly successful execution patterns into reusable procedures across products.

Discovery and promotion are agent/human judgments, not automated skill mining or a validated learning algorithm. Wingman could adopt the report field and approval path directly, then connect the resulting skill to versioned provenance, evaluations and affected profiles.

## 6. Distinctive mechanisms and their limits

**Persist content, nudge only the count.** The mailbox is independent of the terminal wake-up signal. This addresses real failure modes of typing long tasks into a busy TUI and enables recovery after missed signals. The design is small enough to inspect and change. Its limits are shared-filesystem scope, nontransactional task outcome/read acknowledgments, and terminal-based wake/recovery heuristics.

**Management is kept responsive by ending agent turns.** Shogun delegates immediately, Karo dispatches then stops, and events wake the next useful action. This avoids burning inference on repeated “are you done?” checks and leaves the human-facing agent available. It also means semantic supervision only runs when something wakes management. A silent worker failing without a report is not automatically equivalent to a project blocker review. Wingman needs to add its periodic ProjectMaster wake cycle deliberately.

**Identity and role recovery are treated as infrastructure concerns.** Pane metadata, generated role instructions, startup hooks and task-file reconstruction address role confusion after resets/compaction. This is more operationally specific than simply assuming a long-lived conversation remembers who it is. It still preserves identity as an execution slot rather than a first-class project/team entity independent of tmux.

**Quality and scheduling are separated.** Karo is a traffic controller, Gunshi provides qualitative review, and workers execute. Purpose acceptance is checked after constituent tasks complete, with north-star alignment explicitly carried into analysis reports. [Gunshi role](../repo/instructions/roles/gunshi_role.md), lines 59–74, makes business-goal alignment an output field rather than an implicit expectation. This is a useful response to “all subtasks done, goal still unmet.” It remains vulnerable to agent protocol drift and does not prove independent product acceptance.

**Cognitive-level routing connects organization and capacity.** Task Bloom levels influence both who should reason about work and which model is recommended. That ties review depth, strategy delegation and resource use together. The interesting innovation is this concrete connection, not a claim that Bloom routing or multi-agent hierarchies are historically unique. Capability tables and task labels need empirical calibration; defaulting unknown capability to a high ceiling does not itself establish safety or quality.

These are distinctive mechanisms within this checkout. This assessment makes no claim of worldwide priority, uniqueness or superiority over uninspected products. The README also records that the author later moved their personal practice toward a single-agent successor; that is project context, not evidence that the pinned code cannot operate or that the successor has been assessed here.

## 7. Practical adoption for Wingman

**Useful directly as design/code reference:**

- durable addressed mailboxes.
- event-triggered wake-up.
- stable agent identity independent of pane index.
- lightweight YAML task/report contracts.
- explicit outcome versus purpose acceptance.
- role-recovery hooks.
- separation of scheduling and qualitative review.
- skill-candidate reports.

These match the user's preference for an inspectable, lightweight coordination record.

**Requires adaptation:**

- replace Shogun's combined representative/strategist role with Butler and ProjectMaster.
- create project-scoped ProductMaster/TechMaster identities.
- map worker slots into persistent role instances and project teams.
- replace ntfy input with a Telegram adapter preserving question/project correlation.
- give all CLI work a consistent permission/host model.
- create authoritative state transitions instead of relying on multiple instruction variants.

A Codex-only implementation could substantially simplify the many provider-specific reset and screen-detection paths.

Still to build:

- The product discovery/clarification lifecycle.
- Project knowledge conventions with scope/spec/harness evidence.
- Room-based agent discussion and lateral collaboration. A real portfolio/project task application.
- Connected per-agent executive summaries/timelines and structured session workspaces.
- Distributed Mac/Linux worker placement with durable shared coordination.
- Semantic periodic supervision. A delivered-product acceptance/stop/resume lifecycle. The existing Android/tmux view can supply early operational access, but it does not fill those product surfaces.

For Wingman's target, this is best treated as a **coordination-protocol and operational-recovery reference**, with a potentially useful local execution bootstrap. Reusing the entire formation unchanged would force Wingman into a shared commander/reviewer and fixed-worker model that differs from its per-product leadership and extensible organization.

## 8. Verification scope and evidence limits

Inspected the pinned source's root:

- `AGENTS.md`.
- launch/configuration/CLI adapter paths.
- registry.
- instruction builder.
- role/common instructions.
- inbox writer/watcher.
- stop/start hooks.
- watcher supervisor.
- CLI switching.
- archival utility.
- context template.
- dashboard server.
- ntfy listener and Android agent/dashboard/SSH model paths.

Searched likely runtime/instruction/Android areas for Telegram, remote/distributed execution, rooms/threads/timelines, scheduling/supervision and project/acceptance mechanisms. Negative findings refer to those source areas. They do not assert that an operator could not add integrations externally.

Relevant tests were inspected as source:

| Test evidence | What it actually supports |
|---|---|
| [tests/test_inbox_write.bats](../repo/tests/test_inbox_write.bats), lines 92–171, 232–380, 446–453 | Test intent covers self-send rejection, message structure, retention of unread messages, concurrent writes and lock release. It does not prove semantic task delivery or exactly-once execution. |
| [tests/unit/test_agent_registry.bats](../repo/tests/unit/test_agent_registry.bats), lines 30–92 | Ordered configuration/fallback/pane mapping and supervisor configuration; not unconstrained dynamic creation of new roles. |
| [tests/unit/test_dynamic_model_routing.bats](../repo/tests/unit/test_dynamic_model_routing.bats), lines 397–710 | Configured capability/cost lookup, recommendation and switching decisions; not benchmarked model competence or lower real spending. |
| [tests/unit/test_stop_hook.bats](../repo/tests/unit/test_stop_hook.bats), lines 57–135 | Hook notification/block behavior under controlled inputs; not proof every supported CLI uses the hook. |
| [tests/unit/test_send_wakeup.bats](../repo/tests/unit/test_send_wakeup.bats), lines 818–915 | Auto-recovery deduplication and cancellation/idle guards; guard fixtures use top-level status and therefore do not cover nested `task.status` written by launch/role examples. |
| [tests/unit/test_slim_yaml.bats](../repo/tests/unit/test_slim_yaml.bats), lines 54–149 | Intended archival, schema compatibility, preservation of unread and old pending work; not a per-agent timeline product. |
| [tests/e2e/e2e_basic_flow.bats](../repo/tests/e2e/e2e_basic_flow.bats), lines 5–12, 52–145 | Uses mock CLIs to exercise assignment/decomposition/report flow. The mocks encode the expected behavior. This does not prove live LLMs will obey the organizational protocol. |
| [tests/e2e/e2e_blocked_by.bats](../repo/tests/e2e/e2e_blocked_by.bats), lines 48–126 | Explicitly simulates Karo unblocking task B by editing YAML. Demonstrates protocol test coverage, not an independently implemented scheduler. |
| [tests/e2e/e2e_redo.bats](../repo/tests/e2e/e2e_redo.bats), lines 107–130 and following | Mock-based redo/context-reset scenario and new task identity. No live-provider recovery reliability was measured. |

No dependencies were installed, submodules initialized, tests executed, live agents started, messages sent or source files changed. Generated instruction files are present and the Codex Karo variant was checked against its role source. These are instruction artifacts, not evidence of a live deployment. Local `config/settings.yaml` and active queue/project data are absent from this snapshot; assertions about actual operator configuration, agent uptime, mobile connectivity or completed software products remain unverified.
