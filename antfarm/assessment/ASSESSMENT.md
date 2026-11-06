# Antfarm assessment against Wingman

- **Product:** Antfarm, an OpenClaw workflow installer and task-run coordinator; package version 0.5.1.
- **Repository:** https://github.com/snarktank/antfarm
- **Checkout:** `research/antfarm/repo`.
- **Actual revision:** `a442ad7dcb8cf8746175cc4a2e2dcafd501156cf`.
- **Assessment date:** 2026-11-05.
- **Reference:** [Wingman purpose](../../WINGMAN_PURPOSE.md) and [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md).

**Verdict:** Antfarm provides useful workflow-engine patterns for Wingman's execution layer. It provisions separate OpenClaw agents and coordinates coding, verification, and PR work through durable SQLite runs. Its main unit is a bounded sequential workflow run. Wingman still needs continuing products, project leaders, rooms, durable product knowledge, and separately managed specialists. The inspected state machine has material verification and retry gaps. Repair those paths and run integration checks before adopting the runtime.

This assessment distinguishes executable TypeScript, generated agent instructions and externally delegated OpenClaw behavior. It makes no claim that an OpenClaw agent actually completed a task during this review. All line references describe this checked-out revision.

## Architecture and actual execution model

The executable entry point is [src/cli/cli.ts](../repo/src/cli/cli.ts), lines 18–33 and 128–697. The CLI dispatches install/uninstall, run/status/stop/resume, step operations, dashboard daemon management and medic operations. There is no in-repository LLM inference loop, terminal agent driver or Codex adapter. OpenClaw supplies model sessions, tool execution, cron dispatch and message delivery. Antfarm supplies bootstrap configuration, workflow state and prompts telling those sessions how to operate its CLI. The runtime requirement is Node 22+ with native `node:sqlite`; [package.json](../repo/package.json), lines 1–24, declares TypeScript, JSON5 and YAML dependencies. The README's “zero external dependencies” wording should therefore be read as a deployment-positioning claim, not a literal package/runtime description.

**Install path.** [workflow-fetch.ts](../repo/src/installer/workflow-fetch.ts), lines 24–64, lists package-bundled `workflows/` directories. It copies the selected workflow into the user's state directory. It does not fetch arbitrary third-party repositories. [workflow-spec.ts](../repo/src/installer/workflow-spec.ts), lines 6–37 and 46–124, parses YAML. It checks required IDs, workspaces, inputs, and loop references. [agent-provision.ts](../repo/src/installer/agent-provision.ts), lines 29–99, copies bootstrap files into persistent per-workflow workspaces. It also creates OpenClaw agent directories.

[install.ts](../repo/src/installer/install.ts), lines 209–272, upserts namespaced agents into OpenClaw configuration. It adds the agent-to-agent allowlist, installs guidance and skills, and records metadata. It preserves the default main agent (lines 18–46). It does not create a new agent fleet for every task.

**Run path.** [run.ts](../repo/src/installer/run.ts), lines 9–74, loads the installed workflow and generates a UUID and run number. One database transaction inserts the run and ordered steps. The first step becomes `pending`. All other steps become `waiting`. The function then ensures that workflow cron jobs exist. Each step targets `${workflow.id}_${step.agent}`. Run context stores the task as free text. A model normally discovers and reports the repository path and branch. A project registry does not select them. Cron-setup failure marks the new run failed.

**Execution path.** [agent-cron.ts](../repo/src/installer/agent-cron.ts), lines 128–197, constructs one isolated cron job per configured agent. A polling agent is prompted to run `step peek`, then `step claim`, then call OpenClaw `sessions_spawn` with the claimed JSON and a separate work-model prompt. The work session is instructed to do the job and pipe `KEY: value` output to `step complete`, or call `step fail`; see lines 54–88. Thus the transition from polling to execution is a model-followed instruction, not a direct TypeScript session-spawn API call with a durable job acknowledgment. The initial claim can survive a failed spawn and must later be recovered as abandoned work. Agent execution does not depend on the dashboard being open.

**Persistence and surfaces.** [db.ts](../repo/src/db.ts), lines 6–104, opens local SQLite in WAL mode. Tables store `runs`, `steps`, and `stories`. Records include context JSON, outputs, retry counters, and timestamps. [events.ts](../repo/src/installer/events.ts), lines 6–45, adds a best-effort JSONL stream. That stream is not the authoritative transaction log. [dashboard.ts](../repo/src/server/dashboard.ts), lines 21–115, exposes workflows, run/step/story records, events, and medic state through HTTP. Its HTML presents a workflow-stage board and run-detail panel. It does not provide an agent IDE, organization directory, or product portfolio.

The conceptual flow is:

```text
Human/main OpenClaw conversation or CLI
  → workflow run → SQLite run + ordered steps
  → OpenClaw isolated cron turn for each configured role
  → peek/claim CLI → OpenClaw spawned work session
  → tools operate on target repo → complete/fail CLI
  → context merge + story/step transitions → next role
  → PR/review instructions → completed run + cron cleanup
                         ↘ JSONL events / webhooks / dashboard
Medic cron → database health checks → resets/failure/alerts
```

## Feature comparison

“Absent” below concerns Antfarm's implementation. It does not imply that OpenClaw could not provide a related facility separately. The searches and external-runtime boundary are detailed under verification scope.

| ID | Wingman capability | Verdict | Implemented evidence and concrete difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | [agent-provision.ts](../repo/src/installer/agent-provision.ts), lines 49–93, and [install.ts](../repo/src/installer/install.ts), lines 209–265, create distinct OpenClaw IDs, directories and tool policies; [agent-cron.ts](../repo/src/installer/agent-cron.ts), lines 140–150, requests separate work sessions. These are real runtime agent configurations, not just personas in one prompt. However, one installed role ID serves all runs of that workflow. There is no workload-driven pool of per-project BackendCoder/FrontendCoder instances. Actual execution is delegated to OpenClaw. |
| F02 | Extensible profiles, roles and team composition | **Similar** | [types.ts](../repo/src/installer/types.ts), lines 17–28 and 75–85, describes agents, models, files, skills and steps. [workflow-spec.ts](../repo/src/installer/workflow-spec.ts), lines 46–124, validates additions. New named agents can be added in package-local YAML and Markdown; tool-role categories are a fixed TypeScript union/policy table. No autonomous team resizing, profile catalog UI or project-level instance allocation exists. |
| F03 | Directory and visible working relationships | **Resembles** | [dashboard.ts](../repo/src/server/dashboard.ts), lines 15–34, exposes step-to-agent associations; [index.html](../repo/src/server/index.html), lines 356–387, shows agent IDs on step rows. There is no agent directory, project/team membership, leadership graph or link to an agent's personal workspace. |
| F04 | Telegram main channel and Butler routing | **Resembles** | [main-agent-guidance.ts](../repo/src/installer/main-agent-guidance.ts), lines 10–37, teaches an existing OpenClaw main agent to start/status workflows. [step-ops.ts](../repo/src/installer/step-ops.ts), lines 961–1003, can escalate to the main session. No Telegram transport, chat/project correlation or Butler role is implemented here. An existing OpenClaw Telegram setup would be an external dependency, not Antfarm's routing layer. |
| F05 | Cross-project registry and new/existing intake | **Absent** | [db.ts](../repo/src/db.ts), lines 29–69, has runs/steps/stories, not projects; [cli.ts](../repo/src/cli/cli.ts), lines 672–685, requires an explicitly selected workflow and creates a new run. [status.ts](../repo/src/installer/status.ts), lines 36–74, searches task text/IDs, which is run lookup rather than project intake. |
| F06 | Per-project product and technical leadership | **Resembles** | The planner in [feature-dev/workflow.yml](../repo/workflows/feature-dev/workflow.yml), lines 16–26 and 87–114, performs decomposition. It is a temporary stage; no durable ProductMaster/TechMaster pair stays assigned to a product or discusses implementation changes with workers. |
| F07 | Proportionate discovery and iterative clarification | **Resembles** | [feature-dev/workflow.yml](../repo/workflows/feature-dev/workflow.yml), lines 90–104, requires codebase exploration; [bug-fix/workflow.yml](../repo/workflows/bug-fix/workflow.yml), lines 83–135, adds reproduction/root-cause investigation. There is no product/market discovery cycle, durable question records, human-answer routing or discovery depth selected by product circumstances. |
| F08 | Scope, specs, acceptance scenarios and DoD | **Similar** | [step-ops.ts](../repo/src/installer/step-ops.ts), lines 214–260, persists structured stories with descriptions and acceptance criteria, capped at 20. The feature plan requires mechanically verifiable criteria and tests, YAML lines 97–110. This provides task acceptance material, not complete product scopes/specs or a human-approved product definition of done. Completion does not mechanically validate most declared `expects` contracts. |
| F09 | Decomposition, assignment and shared task tracking | **Similar** | [run.ts](../repo/src/installer/run.ts), lines 34–46, assigns ordered steps; [step-ops.ts](../repo/src/installer/step-ops.ts), lines 152–169 and 553–639, tracks stories and claims one. SQLite is a shared durable coordination record. Dependencies are ordering constraints, not a ticket dependency graph; assignees are workflow agents, and there are no general ticket comments, reassignment or project backlog. |
| F10 | Portfolio/project dashboard | **Similar** | [dashboard.ts](../repo/src/server/dashboard.ts), lines 40–56 and 78–115, and [index.html](../repo/src/server/index.html), lines 256–325 and 356–389, implement run boards, step statuses, story details and outputs. This is a genuine task-run dashboard, but groups by workflow rather than persistent product and lacks project goals, leadership, specifications and human decision queues. |
| F11 | Agent chat, rooms and direct collaboration | **Absent** | Shared context and verification feedback are mediated by [step-ops.ts](../repo/src/installer/step-ops.ts), lines 694–706 and 818–835. [install.ts](../repo/src/installer/install.ts), line 51, denies workflow agents `message` and `sessions_send`. No room/message/member schema or chat UI exists. A coordinator's exceptional escalation message is not peer discussion. |
| F12 | Management escalation and human approvals | **Resembles** | [step-ops.ts](../repo/src/installer/step-ops.ts), lines 961–1003 and 1060–1095, routes explicit retry-exhaustion alerts to a configured session, treating `human` as `agent:main:main`; [medic-cron.ts](../repo/src/medic/medic-cron.ts), lines 13–30, prompts critical alerts. There is no Room2→Room1 management deliberation, approval object, pending decision state or answer-to-origin routing. |
| F13 | Durable project knowledge and directives | **Similar** | [agent-provision.ts](../repo/src/installer/agent-provision.ts), lines 56–98 and 129–172, installs reusable Markdown instructions and skills; [step-ops.ts](../repo/src/installer/step-ops.ts), lines 128–146 and 1010–1029, reads and archives run-scoped progress. Developer instructions preserve patterns in AGENTS.md and git. This is agent/workflow/run knowledge, not product-scoped SCOPES/SPECS/HARNESS with continuing discovery records. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | Stable namespaced agent IDs and directories survive runs; SQLite stores outputs/context, and [cli.ts](../repo/src/cli/cli.ts), lines 541–655, resumes failed runs. Work sessions are intentionally fresh and history maintenance defaults prune external session records ([install.ts](../repo/src/installer/install.ts), lines 53–59). No Antfarm conversation history or project conversation continuity model is implemented. |
| F15 | Proactive supervision and blocker follow-up | **Similar** | [medic-cron.ts](../repo/src/medic/medic-cron.ts), lines 65–90, schedules a five-minute watchdog; [checks.ts](../repo/src/medic/checks.ts), lines 34–209, detects stuck steps, stalled/dead runs and orphaned crons. [medic.ts](../repo/src/medic/medic.ts), lines 39–125, remediates technical state. It does not interview project leaders, resolve product blockers, reprioritize assignments or maintain portfolio progress. |
| F16 | Parallel products and concurrent specialists | **Resembles** | Multiple independent runs can exist, and [agent-cron.ts](../repo/src/installer/agent-cron.ts), lines 203–249, shares crons until all runs of a workflow finish. However, [step-ops.ts](../repo/src/installer/step-ops.ts), lines 494–507, requires all preceding steps to be done/skipped; story implementation is serial. No product boundaries, per-run worktrees, worker pools or robust atomic ownership protect parallel specialist work. |
| F17 | Multi-host execution with shared coordination | **Absent** | [gateway-api.ts](../repo/src/installer/gateway-api.ts), lines 14–55, targets a loopback OpenClaw gateway; [db.ts](../repo/src/db.ts), lines 6–23, uses a local home-directory database. No host registry, SSH/remote worker protocol, replicated/shared coordination or host-aware task routing appears in implementation. Workflow agents also have `nodes` denied, install line 51. |
| F18 | Executive agent current/recent/next/blocker overview | **Resembles** | [index.html](../repo/src/server/index.html), lines 288–325 and 356–389, shows active stages and agent assignments, with upcoming stages inferable from order. It does not produce a per-agent executive briefing, completed outcome summary, planned-next account or blocker aggregation across products. |
| F19 | Individual agent summary timeline with evidence links | **Resembles** | [events.ts](../repo/src/installer/events.ts), lines 10–26 and 101–116, records run/step/story transitions; [index.html](../repo/src/server/index.html), lines 393–438, renders run activity. This is a run event log, not an agent-owned timeline, and lacks links to underlying sessions, diffs, commands or tests. Some events omit `agentId`. |
| F20 | Detailed per-agent coding workspace | **Absent** | The complete route set in [dashboard.ts](../repo/src/server/dashboard.ts), lines 73–148, returns records and HTML; [index.html](../repo/src/server/index.html), lines 356–389, expands textual step output. No terminal, editor, full conversation, tool-call stream, artifact viewer, usage view or session deep link exists. OpenClaw's own interface remains external and unverified. |
| F21 | Live activity, lifecycle, steering and execution visibility | **Resembles** | The run panel refreshes every five seconds ([index.html](../repo/src/server/index.html), lines 243–248); CLI stop/resume and cron repair exist ([cli.ts](../repo/src/cli/cli.ts), lines 475–481 and 541–668). These expose coarse database state, not live model/tool output. Stop does not terminate spawned sessions. There are no conversation fork/rename/compact/archive, attachment/steering queue, budgets or goal controls. |
| F22 | Testing, integrated verification and acceptance/delivery | **Similar** | [feature-dev/workflow.yml](../repo/workflows/feature-dev/workflow.yml), lines 181–195, 220–260 and 262–389, specifies per-story tests, independent checks, E2E integration, PR creation and posted review. This is substantial development-delivery workflow. Product acceptance and deployment are absent, most success gates trust agent reports, and the verify-each reachability defect undermines the intended pipeline at this revision. |
| F23 | Autonomous operation with human organizational direction | **Similar** | [run.ts](../repo/src/installer/run.ts), lines 55–74, starts periodic autonomous progression, and [agent-cron.ts](../repo/src/installer/agent-cron.ts), lines 128–197, schedules independent polling. A human/main agent can initiate a bounded task and get alerts. There is no standing organization that owns evolving products, product discovery and acceptance across sessions. Autonomy depends on model adherence to CLI/spawn instructions and external OpenClaw availability. |
| F24 | New profiles fit chat/tracker/dashboards | **Resembles** | New YAML steps/agent names flow through generic step storage and dashboard rows ([run.ts](../repo/src/installer/run.ts), lines 38–46; [dashboard.ts](../repo/src/server/dashboard.ts), lines 21–34). This accommodates additional workflow agents in run tracking. There is no corresponding chat or directory extensibility, and dashboard definitions are read from package-bundled files rather than installed runtime definitions. |

## Agent definition and lifecycle

### Definition, creation and identity

An Antfarm “agent” has two layers: a durable OpenClaw agent configuration with workspace/bootstrap files, and short-lived OpenClaw sessions executing polling or claimed work. A run, step and story are durable task records, not agents or OS processes. Antfarm does not itself allocate one agent process per story. The only OS process it explicitly spawns for its own UI is the detached dashboard Node daemon ([daemonctl.ts](../repo/src/server/daemonctl.ts), lines 32–59).

YAML defines agent IDs, display names, descriptions, role category, optional work/poll models, timeout and workspace files/skills ([types.ts](../repo/src/installer/types.ts), lines 19–33). Bundled agents receive AGENTS.md for operating instructions, SOUL.md for persona and IDENTITY.md for identity. The feature workflow actually defines **six agent configurations and seven steps**, because its developer also creates the PR ([feature-dev/workflow.yml](../repo/workflows/feature-dev/workflow.yml), lines 16–85 and 301–302). The README's “7 agents” does not describe seven independent feature-workflow identities.

Provisioning derives the stable ID from workflow and local agent, and the workspace from workflow and `baseDir`. Runs do not add a project/run suffix to the agent identity. Separate workflows get distinct developers, but two feature-development runs share `feature-dev_developer` and its workspace. The target repository is distinct from the instruction workspace and is passed through context. Files are preserved by default when already present ([workspace-files.ts](../repo/src/installer/workspace-files.ts), lines 21–33); reinstalling a workflow refreshes copied definitions/configuration but need not replace old agent instructions. That supports local learning/customization but can leave installed behavior behind a package update.

### Tools, permissions and routing

Role inference selects analysis for planner/reviewer/investigator, verification for verifier, testing for tester, scanning for scanner, PR for pr and coding otherwise ([install.ts](../repo/src/installer/install.ts), lines 158–180). All use OpenClaw's coding profile; selected roles deny direct write/edit/apply_patch, testers add browser/web, scanners add web search/fetch. Workflow agents cannot directly use gateway, cron, message, nodes, canvas or sessions_send (lines 49–145). Critically, read-only is a **tool-list policy**, not a filesystem sandbox: analysis/verifier roles retain `exec`, so these denies alone do not prevent writes through shell commands. Antfarm does not implement an OS sandbox, repository ACL or restricted command runner.

The installer sets `subagents.allowAgents: []` on workflow agent records (lines 156 and 216–223), yet polling prompts require those same agents to call `sessions_spawn` for their own ID. It separately updates `tools.agentToAgent.allow` ([subagent-allowlist.ts](../repo/src/installer/subagent-allowlist.ts), lines 26–46). Whether an empty per-agent allowlist permits same-agent self-spawn is an OpenClaw policy question. This checkout alone does not establish successful spawning. It warrants an explicit compatibility check, not an assumption that adding the global communication allowlist settles spawn permissions.

Step routing itself is concrete SQL: claim finds one pending step assigned to that namespaced ID, excluding failed/cancelled runs and requiring preceding steps done/skipped. It resolves context placeholders and fails the run on missing input keys ([step-ops.ts](../repo/src/installer/step-ops.ts), lines 485–532 and 629–671). There is no conversational routing to another product specialist or remote host.

### Execution, concurrency and continuity

The default cron period is five minutes, with nominal one-minute staggering and a two-minute polling timeout ([agent-cron.ts](../repo/src/installer/agent-cron.ts), lines 7–8, 91–92 and 160–191). Polling model precedence is per-agent, workflow, then configured/default model. A work model can be chosen independently. Every cron uses an isolated session, and a model is instructed to spawn the work session after claiming. `fresh_session` is parsed into `freshSession` by the spec loader, but searches found no runtime use of that property. The fresh-session behavior comes from the common isolated/spawn architecture, not a per-loop flag switch.

Stories are read in index order and one current story is stored on the loop step. Outputs and acceptance criteria persist in SQLite; run-scoped progress files and git commits reconstruct useful context for later fresh sessions. This is deliberate task continuity with disposable model context, rather than a conversation continuously growing with the product. Completion archives/deletes the active progress file into `archive/<runId>/progress.txt` in the developer workspace ([step-ops.ts](../repo/src/installer/step-ops.ts), lines 1010–1029). External OpenClaw history retention is configured to 24-hour cron retention and seven-day maintenance defaults if absent, so durable identity should not be confused with indefinite conversation retention.

Multiple runs are allowed and their workflow crons are shared, but there is no explicit worker capacity, task lease token or run isolation. Claim's SELECT and UPDATE are separate operations. The single-step UPDATE checks `pending`, but its affected-row count is ignored before returning work, and loop/story updates are unconditional (step-ops lines 494–507, 587–593, 644–671). Concurrent claimers could receive the same work. Shared role workspaces and agents operating `git checkout` in target repositories also need external serialization or worktrees. A common prompt uses a fixed `/tmp/antfarm-step-output.txt` path, introducing another cross-session collision risk (agent-cron lines 68–75). None of these races was exercised in this review.

### Failure, retry, recovery and interruption

Explicit failure retries the same single step or current story, normally twice before run failure. It stores the reason on exhaustion and can alert the main session (step-ops lines 1035–1102). The special verify-each handler recognizes `STATUS: retry`, selects the most recently completed story, returns it to pending, stores `verify_feedback`, and re-enables the implementation loop; other statuses count as passed (lines 779–844). This is a specialized feedback cycle, not a general dependency/workflow graph.

Abandoned work is identified by timestamps, not process/session liveness. The threshold is the largest role timeout (30 minutes) plus five minutes. Cleanup gives ordinary abandoned steps up to five abandonment counts, handles current loop stories with their own retry budgets, and repairs some done-loop/stuck-next-stage situations (lines 264–383). Its process-local five-minute throttle restarts for each separately launched CLI process, so it is not a global throttle across agents. The separate medic uses similar thresholds and logs corrective actions, but has its own reset implementation. It can fail a zombie run and remove idle crons. This recovers database progress after likely crashes, but there is no heartbeat lease extension, spawned-session ID or proof that a supposedly abandoned worker has stopped writing.

CLI resume only accepts a failed run, resets a failed step or linked loop/verification state and recreates crons ([cli.ts](../repo/src/cli/cli.ts), lines 541–655). It resumes work records rather than a paused model conversation. Story retry counts and abandonment counts are not generally reset by this command even when step retry counts are reset, limiting the effective fresh retry budget. A cron setup failure that left no step failed cannot follow the normal “find failed step” resume path without further repair.

`workflow stop` marks the run cancelled, marks unfinished steps failed and removes crons when no sibling run remains ([status.ts](../repo/src/installer/status.ts), lines 87–140). It does **not** cancel an OpenClaw spawned work session, signal its commands or stop edits already in progress. Moreover, `completeStep` guards only failed runs, not cancelled runs, whereas `advancePipeline` guards both (step-ops lines 688–692 and 916–919). Late completion can still mutate cancelled-run context, stories and step state, although the final advance guard prevents ordinary pipeline continuation. `failStep` has no equivalent terminal-run guard. This is a materially weaker execution-control boundary than Wingman needs.

### Completion, acceptance and retirement

The common contract requires the agent to report `step complete` or `step fail`. For ordinary completion, Antfarm parses uppercase keys, merges them into the run's shared context, stores output, marks the step done and advances (step-ops lines 679–774). A run is completed when no waiting or incomplete step remains, then progress is archived and idle workflow crons are removed (lines 913–957). Product acceptance, deployment and accepted-delivery stopping are not separately modeled. PR creation and review are model instructions to `gh`, not TypeScript verification of a merged or accepted product.

Individual durable agent configs remain installed after runs finish. Workflow uninstall removes their config entries, allowlist membership, workspace, run/step/story records and agent directories including sessions ([uninstall.ts](../repo/src/installer/uninstall.ts), lines 137–186). The CLI blocks uninstall while active runs exist unless forced ([cli.ts](../repo/src/cli/cli.ts), lines 493–506). Full uninstall also stops the dashboard and removes state/database/logs (uninstall lines 189–278). This is destructive retirement of a workflow installation. There is no archive/fork/rename/compact lifecycle for a single specialist conversation.

## Coordination mechanics and a request trace

Antfarm's collaboration is **data handoff**. A step emits uppercase keys. The engine lowercases names and merges strings into a shared per-run context. Later input templates resolve `{{repo}}`, `{{branch}}`, `{{test_cmd}}`, `{{changes}}` and related fields. Story metadata adds `current_story`, completed stories, remaining count, progress and feedback. This permits decoupled agents to consume structured results without retaining one shared conversation. It also means later agents can overwrite earlier keys. There is no authored/versioned decision object, task comment stream or context access control. Events add coarse observations of transitions, and webhooks notify an external receiver, but neither supplies a room where agents deliberate.

Consider the repository's documented `feature-dev` request, “Add user authentication with OAuth” ([README.md](../repo/README.md), lines 80–101). This is a source trace of that command's intended path, not a run executed during assessment:

1. CLI `workflow run feature-dev <task>` passes the title to `runWorkflow` (cli lines 672–685). It creates one run and the plan/setup/implement/verify/test/pr/review step rows, with only plan pending (run lines 21–46).
2. The planner's isolated cron turn peeks, claims and is instructed to spawn the planner work session. The planner explores the target repository and reports repo, branch and `STORIES_JSON` (feature YAML lines 87–114). `completeStep` merges context and inserts at most 20 validated story records (step-ops lines 214–260, 694–709), then promotes setup.
3. Setup receives resolved repository/branch, creates the branch and establishes build/test baseline (YAML lines 116–145). Its output supplies commands that downstream implementation expects. Ordinary pipeline advancement promotes implement.
4. The developer claims the earliest pending story, persists current-story context, and receives the story plus progress and feedback (step-ops lines 553–639). It is instructed to implement only that story, write tests, commit and rewrite its progress file (YAML lines 147–199).
5. On developer completion, the engine marks the story done and sets verify pending while leaving implement running (step-ops lines 716–744). The intended next action is independent verification, with retries feeding specific issues back to the developer.
6. **At this revision the intended trace encounters a reachability conflict:** the verifier's claim query rejects any step whose earlier step is not done/skipped (lines 494–505). Implement is an earlier running step by design. Therefore normal verifier claim cannot reach the pending verification step. Cleanup deliberately skips resetting an empty-current-story loop while its verifier is pending/running (lines 285–295), so that path does not resolve the conflict. Medic can later reset the loop, but that is not successful verification and can reorder or repeat work. The code supports the intended verify-each mechanism, but does not establish its operational success.
7. Repairing this conflict would make verifier feedback or story continuation reachable. When all stories finish, the handler marks the loop and verifier done. Integration testing, PR creation, and review then follow (step-ops lines 779–906; YAML lines 262–389). Ordinary tester/reviewer completion does not check `expects`. A `STATUS: retry` output can therefore still become done. The claim transition and final acceptance handling both need repair.
8. Retry-exhaustion escalation loads the installed step's failure policy and maps `human` to the main OpenClaw session (step-ops lines 971–1003). The message identifies run, workflow, step and reason, but there is no registered decision, awaiting-answer state or automatic routing of the human's reply back into that failed assignment.

## Material implementation limits

These are static code findings, not runtime reproduction claims. They affect how much confidence Wingman should place in the available primitives.

1. **Verification-loop reachability conflicts with strict predecessor gating.** The trace above ties the competing transitions to exact source paths. No exception in `claimStep` recognizes a loop's own `verifyStep`. This is more than a missing dashboard feature: it blocks the central feature/security workflow design under the normal claim path.
2. **Declared success and failure policies are only partially implemented.** `expects` is required and stored, but not read by `completeStep`; ordinary steps mark done for any submitted output. `retry_step` appears in types/YAML/docs but searches find no execution handler that redirects to it. `failStep` retries the current step. Only the special verify-each path interprets retry output, and it accepts anything other than `retry` as success. Test/review changes-requested output can therefore advance. [types.ts](../repo/src/installer/types.ts), lines 35–59; [run.ts](../repo/src/installer/run.ts), lines 34–46; [step-ops.ts](../repo/src/installer/step-ops.ts), lines 679–774, 785–798 and 1035–1102.
3. **Bug-fix has an initially missing feedback variable.** Its single `fix` input includes `{{verify_feedback}}` (bug-fix YAML lines 183–184), but that workflow defines no default context and the single-step claim path does not inject an empty feedback value. Only loop claim does so (step-ops lines 625–627). Given the normal preceding outputs, the new missing-template-key guard at lines 658–661 fails that run before the first fix. An agent could happen to emit an extra key, but that is not the declared handoff contract.
4. **Claims and completion need stronger ownership/idempotency.** Claims are not transactional leases, have no claim/session token and ignore the single-update affected-row count. Completion does not require the step to be running or verify the caller; story insertion is not wrapped in the creation transaction and duplicate completions can insert extra stories before other transitions. The SQLite record is inspectable, but that alone does not establish reliable exactly-once task execution. Relevant paths are step-ops lines 214–260, 485–507, 587–593, 644–671 and 679–709.
5. **Timeout configuration is not carried into work-session spawn.** Agent `timeoutSeconds` is provisioned as metadata, and role policies contain timeouts, but installer comments explicitly omit per-agent timeouts from OpenClaw config (install lines 224–227). Cron scheduling uses only polling timeout, and the spawn instruction includes agentId/model/task without runtime timeout (agent-cron lines 147–150, 165–188). The 35-minute abandoned threshold is therefore based on policy constants rather than proof of the actual spawned session's timeout or liveness.
6. **State/configuration roots are inconsistent.** [paths.ts](../repo/src/installer/paths.ts), lines 17–46, honors `OPENCLAW_STATE_DIR` and `OPENCLAW_CONFIG_PATH` for installer paths, while db.ts lines 6–7, events.ts lines 6–7, gateway-api.ts line 20 and step-ops.ts lines 116–124 hardcode the standard home path. The latter paths also use JSON.parse where the installer accepts JSON5. Nondefault profiles/configs can consequently split state or lose progress/gateway lookup. This matters before introducing per-host or per-product deployments.
7. **Watchdog behavior is technical and partly overlapping.** Medic's reset does not use cleanup's special verify-loop exception or per-story reset logic (medic lines 43–83 versus step-ops lines 284–325). Resetting a stale step does not stop its old session. Wingman needs one consistent recovery/lease model, not merely multiple periodic observers.

## Additional capabilities beyond Wingman's described product

**A dedicated security remediation pipeline.** Wingman explicitly places security outside TestMaster's responsibility. Antfarm supplies scanner→prioritizer→setup→fix-loop→verifier→integration test→PR. [security-audit/workflow.yml](../repo/workflows/security-audit/workflow.yml), lines 93–167, covers dependency audits, secrets, auth/session handling and common vulnerability classes, then deduplicates and ranks fixes by exploitability/impact. Lines 250–337 require regression tests that would fail without the patch, bypass-case reasoning and before/after audit comparison. This is valuable as a separate security team/workflow template. It remains model-directed auditing rather than a security-analysis engine, caps tracked fixes at 20 and needs corrected loop/gating behavior. Adding it to Wingman would require a distinct role, findings/deferral records and appropriate permissions rather than quietly expanding TestMaster.

**An explicit bug reproduction and root-cause sequence.** [bug-fix/workflow.yml](../repo/workflows/bug-fix/workflow.yml), lines 83–135 and 166–198, separates triage, reproduction/severity, investigation and regression-test implementation. Wingman describes general implementation/testing but not this detailed incident-style protocol. These prompts can improve defect handling and evidence before assigning a fix. Their current missing feedback default and ineffective general `retry_step` semantics must be fixed if reusing the runner, while the role separation itself is reusable now.

**Outbound event webhooks.** [events.ts](../repo/src/installer/events.ts), lines 45–83, posts run/step/story events to a run- or workflow-configured URL, supports an authorization fragment and applies a five-second request timeout. This offers a useful bridge from execution to Wingman's tracker, Butler notifications or event ingestion. Delivery is fire-and-forget, exceptions are swallowed and there is no durable outbox, replay cursor, delivery acknowledgment or deduplication contract. Wingman should treat it as best-effort notification and use its authoritative work database to reconcile missed updates.

**Operational self-repair with a persisted health history.** The medic's modular checks, automatic reset/fail/cron cleanup and last-500 check history ([medic.ts](../repo/src/medic/medic.ts), lines 142–197) exceed a mere “wake and inspect” prompt by providing executable database diagnostics and remediation. They are valuable for Wingman's infrastructure supervision. They do not replace leadership blocker follow-up, and production integration needs session-aware leases, cancellation and one recovery policy.

**Provisioning and retirement of a complete workflow installation.** Installation manages bootstrap files, external local skills, default-agent preservation, global configuration and guidance; removal deletes workflow-owned state. [agent-provision.ts](../repo/src/installer/agent-provision.ts), lines 108–172, copies external skills from known local OpenClaw skill locations and warns when missing. This is a useful packaging unit for standardized teams. It assumes a shared OpenClaw configuration and package-local definitions, so Wingman would need a profile/instance distinction and controlled update/retirement policy to avoid losing long-lived organization records.

## Grounded innovation and distinctive mechanisms

The strongest mechanism is **durable work reconstruction with fresh model sessions**: small acceptance-bearing stories, common context templates, git commits and run-scoped progress enable useful task continuation without requiring a single ever-growing chat. The code implements the record construction and reconstruction directly (step-ops lines 128–146, 214–260, 600–639), and the developer prompt explicitly teaches reusable codebase patterns. This is an architectural choice Wingman can use for disposable workers while retaining persistent product leadership. Its limit is that reconstruction is an agent-written lossy summary. It does not preserve full conversations or resolve conflicting edits. The repo explicitly attributes its fresh-session design to the Ralph loop; no historical novelty claim is warranted.

The **two-phase polling/work model split** supports inexpensive availability checks and a stronger model for actual work. Polling `peek` avoids cleanup and template work. The work phase receives the exact claimed JSON. See agent-cron lines 128–157 and step-ops lines 447–464. This could reduce idle-model cost. The polling prompt still embeds the full work instructions. A model must perform the handoff. `peek` counts pending and waiting rows. An agent can therefore wake and attempt a claim before its step is reachable. The assessment did not measure costs, reliability, or same-agent spawn authorization.

The **story-specific verification feedback loop** is more precise than simply retrying a failed workflow. It carries explicit issues back to the last completed story, maintains a per-story retry budget and continues later stories only after the loop advances (step-ops lines 779–906). That is a useful fit for developer/verifier separation. However, its present predecessor-gating conflict means the mechanism is an incomplete realization at this revision. The design should be borrowed together with a corrected state machine and real end-to-end verification.

Finally, **run-scoped cron lifetime** shares the polling infrastructure across concurrent runs of the same workflow and removes it when no active run remains (agent-cron lines 203–249). It is a concrete way to stop idle orchestration cost after task completion, aligning with Wingman's accepted-delivery quiescence. It does not retire the agent identities, prove sessions stopped, or repair a partially created cron fleet: `workflowCronsExist` accepts any matching cron as evidence that setup exists, lines 219–239. These are distinctive implementation choices in this codebase, not claims of uniqueness across agent systems.

## Practical use for Wingman

Use directly as source material:

- The planner/story/acceptance format.
- Separate developer/verifier/tester prompts.
- Defect-reproduction and security-audit protocols.
- Namespaced agent bootstrap packaging.
- Run/step/story vocabulary.
- Coarse event shapes.
- Executable medic checks. They provide a compact, inspectable execution skeleton and concrete quality expectations. License is MIT ([LICENSE](../repo/LICENSE)). This assessment is not a license-compliance audit.

Adapt before using the runtime:

- Introduce first-class project, profile, instance and session identities.
- Replace the OpenClaw prompt-mediated spawn path with a controlled Codex execution adapter if Codex is the required agent runtime.
- Correct verify-loop reachability and implement general output/acceptance/failure-policy validation.
- Use transactional ownership with lease/session IDs.
- Isolate repository work with host-aware worktrees.
- Scope temporary files.
- Propagate actual work timeouts.
- Make cancellation terminate work.
- Unify state/config roots.
- Preserve durable events/decisions through a reliable outbox. These are necessary changes for reliable execution, independent of the larger product surface.

Still build the Wingman organization:

- Butler and Telegram routing.
- Portfolio registry and intake.
- Durable ProductMaster/TechMaster leadership and discovery.
- Human question/approval correlation.
- Room1/Room2 and direct peer discussion.
- Project directives and their lifecycle.
- Scalable specialist allocation. A shared multi-host coordinator.
- Executive per-agent briefings/timelines.
- Per-agent coding workspaces with full conversations, commands, edits, tools, usage, steering and lifecycle controls. The run dashboard could be embedded as an execution view, but should not become the product model for those broader capabilities.

The best fit is therefore **a reference execution layer or a repaired subordinate workflow service**, below Wingman's product/organization layer. Adopting it as the foundation would commit Wingman to replacing or greatly expanding most of the requested standing-organization and human-facing semantics.

## Verification scope and limits

This was a fresh local source review. The checkout revision and clean status were inspected with git. Applicable `AGENTS.md` was read before checkout inspection; role-specific AGENTS documents were also reviewed as definition evidence. No source files were changed, dependencies installed, workflows provisioned, gateways contacted, services launched, browser sessions used or model runs performed. Only this assessment file was written. No test pass/fail result or reproduced runtime defect is claimed.

Important implementation inspected:

- CLI command routing and resume.
- Database schema/migrations.
- Workflow parsing/fetching.
- Paths/config handling.
- Agent provisioning, role policies and subagent allowlist.
- Bootstrap preservation and main-agent guidance.
- Cron prompt generation and run-scoped cleanup. The entire step state machine.
- Status/cancellation.
- Events/webhooks.
- Dashboard backend and principal rendering/refresh functions.
- Watchdog checks/remediation/scheduling.
- Uninstall paths.
- Frontend-change detection.
- All three bundled workflow definitions and agent operating instructions.

Relevant tests inspected include:

- [tests/two-phase-integration.test.ts](../repo/tests/two-phase-integration.test.ts), lines 1–151, and [tests/two-phase-cron.test.ts](../repo/tests/two-phase-cron.test.ts), lines 1–62: prompt-string/model/ID assertions. Their “integration” naming does not establish a real gateway claim→spawn→complete cycle.
- [tests/multiline-output-parsing.test.ts](../repo/tests/multiline-output-parsing.test.ts), lines 14–125: direct tests of the compiled parser's multiline/context behavior.
- [tests/terminal-state-guards.test.ts](../repo/tests/terminal-state-guards.test.ts), lines 98–239: an in-memory schema with simulated guard logic, rather than calls through the production complete/advance functions. It principally addresses failed states and does not establish cancelled-session behavior or real concurrency safety.
- [tests/peek-step-polling.test.ts](../repo/tests/peek-step-polling.test.ts), lines 93–135: assumes `ANTFARM_DB_PATH` isolation although production db.ts does not consume that variable. Its header says waiting steps should return NO_WORK, while the implementation counts waiting rows. This weakens its value as an unexamined runtime oracle.
- [src/installer/status.test.ts](../repo/src/installer/status.test.ts), lines 1–182: production `stopWorkflow` tests that use `getDb` and can invoke cron teardown. They were read, not run against the user's OpenClaw state.

Negative-feature searches covered `src/`, `workflows/`, and `docs/`. Terms included Telegram, Butler, project registry, clarification, approvals, rooms, hosts, SSH, worktrees, and session spawn/send. Further searches covered `retry_step`, `freshSession`, and `expects`. The review then inspected the schema, all dashboard routes, and lifecycle implementations. These findings concern Antfarm's local code. They do not establish a separately configured OpenClaw's behavior. Tool-policy enforcement, spawn authorization, model behavior, history retention, cron execution, browser skills, and external PR delivery remain unexercised.
