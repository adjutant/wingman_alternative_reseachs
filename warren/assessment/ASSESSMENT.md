# Warren assessment against Wingman

Assessment date: 2026-11-05. Product: Warren, package `@os-eco/warren-cli` version 0.19.3. Upstream: https://github.com/jayminwest/warren . Local checkout: `research/warren/repo`. Assessed commit: `ce088e854c96492358b6f0a0e26695baf801968d` (read from the checkout, not inferred from a release). Baseline: [Wingman purpose](../../WINGMAN_PURPOSE.md); method: [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md).

**Verdict:** Warren is a substantial candidate for Wingman's execution and Git delivery layer, but a poor direct replacement for its continuing organization. It implements real, separately isolated coding workloads, repository registration, durable run records, scheduled dispatch, recovery, operational dashboards and PR-gated plan execution. It does not implement Butler, Telegram intake, standing ProductMaster/TechMaster teams, agent rooms, product discovery records, or durable individual-agent conversations. Its primary unit is an ephemeral **run**, not a persistent employee. Adopting it would leave Wingman's organizational control plane and most human collaboration experience to build.

This distinction is particularly important at this revision: conversations, Plot coordination and multi-worker placement were removed. Some comments and planner prompt text still describe those former systems. The current physical schema explicitly records their deletion ([SQLite schema][schema], lines 4–16). The current API and browser routes do not provide them ([HTTP routes][routes], lines 129–385; [SPA routes][app], lines 120–185). This report credits reachable implementation rather than those historical descriptions. No dependencies were installed, no services or agents were launched, and no checkout source was changed.

## Architecture and execution model

Warren is a Bun/TypeScript application with a React SPA, HTTP API, CLI and TypeScript client. Its composition root opens SQLite or Postgres through `openDatabase` and creates repository objects. It seeds the global role registry and resolves the forge and tracker. It builds one runtime provider. It then connects bridges, background detectors, the scheduler and plan coordinator. The important boundaries are `AgentDefinition` (prompt/configuration), `RunSpec` (resolved workload), `RuntimeProvider` (placement and lifecycle), `Forge` (Git service operations), and `IssueTracker` (work item operations). See [boot][boot], lines 95–227; [runtime contract][contract]; [tracker contract][tracker], lines 46–127. These are real interfaces with multiple implementations, rather than just deployment terminology.

The container supervisor is now a small wrapper around the Warren server, forwarding termination signals with a five-second grace and passing through exit codes. It does not run the former Burrow daemon or restart an internal worker service ([supervisor][supervisor], lines 4–21 and 71–109). The HTTP dispatch handler resolves request defaults, calls the shared `spawnRun`, starts a bridge and returns a run plus sandbox identity. HTTP dispatch is explicitly `mode: "batch"`. It is not a resumable organization chat session ([HTTP dispatch][http-dispatch], lines 374–443).

The runtime is selected once for the deployment. Local execution materializes a workspace from the project clone, gives the run its own Git directory and HOME, writes seed artifacts, builds a sandbox profile and asynchronously drives a real harness subprocess. LocalEngine's `create` returns after scheduling that drive loop; events then describe actual execution, not just a persona prompt ([local engine][engine], lines 120–214; [drive loop][drive], lines 162–221). Linux uses Warren's sandbox machinery around bwrap, macOS its sandbox-exec path. Docker swaps the spawn seam to a sibling container while reusing LocalEngine and host-visible workspaces ([Docker provider][docker], lines 2–24). Neither is distributed worker placement.

Kubernetes is the genuine distributed execution path: one bare pod per run, workspace init container, ConfigMap seed files, log streaming, pod status reconciliation, resource admission and in-pod finalization. The pod can execute on a cluster node while the same Warren control plane owns its records. Kubernetes does not resurrect the retired named-worker directory or assign enduring agents to arbitrary human-specified hosts. Its pod boundary has explicit capability differences: no preview ports, no long-lived conversation pods, coarse network policy, and no host workspace archive ([K8s provider][k8s], lines 2–18, 170–195; [pod builder][pods], lines 9–26 and 119–163).

Persistence is split deliberately. The database keeps agent definitions, registered repository facts, runs with frozen definitions/prompts, events, steering inbox rows, triggers, plan runs and their children. Git keeps code and optional Seeds/Mulch data. The live local/Docker provider keeps its process state in an **in-memory** store. A server restart loses that runtime state and reconciles old active rows as lost. An on-disk manifest permits later cleanup, not inference-session resurrection ([schema][schema], lines 56–180; [engine][engine], lines 11–25 and 192–214). Database-backed history therefore must not be mistaken for a continuously alive agent mind.

## Complete feature matrix

Verdicts use the guide's meanings. “Similar” credits substantial behavior with a concrete workflow or scope difference; “Resembles” credits a useful primitive that does not itself fulfill the feature.

| ID | Wingman capability | Verdict | Implementation evidence and concrete difference |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | Similar | [LocalEngine][engine], lines 120–214, and [drive][drive], lines 192–210, create isolated workspaces and actual harness processes. Repeated role dispatches are independent run instances. They are temporary coding jobs, not durable BackendCoder/FrontendCoder employees with their own continuing conversation. |
| F02 | Extensible agent profiles, roles and team composition | Similar | [Definition schema][agent-schema], lines 59–66, and [extra seed file][seed-file], lines 26–38 and 89–105, allow operator-defined named profiles at boot; seven [built-ins][builtins], lines 44–52, ship. Roles can carry prompts/model/runtime/skills and be dispatched repeatedly. No team object, manager relationship, automatic staffing or live profile editor was found. |
| F03 | Agent directory and visible working relationships | Resembles | [Agents API][agents-api], lines 110–127, and [agents UI][agents-ui], lines 16–27 and 67–92, list profile names, provenance, model and cap. This is a dispatchable definition inventory. It does not show individual workers, project membership, reporting lines or collaboration relationships. |
| F04 | Telegram as the main human channel and Butler-style routing | Absent | Searches for Telegram, Butler and the named Wingman roles across `src/` and `extensions/` found no implementation. The actual intake is CLI/API/SPA dispatch ([routes][routes], lines 181–241 and 269–385; [HTTP dispatch][http-dispatch], lines 416–443). No Telegram conversation-to-project router or answer-return correlation exists. |
| F05 | Cross-project registry, intake and existing/new project routing | Similar | [Projects schema][schema], lines 79–98, and [addProject][projects], lines 108–145, register repository URLs, reject duplicates, clone and persist them. Dispatch requires a resolved project id. The registry supports many repositories, but no natural-language new/existing product recognition, ambiguous-reference clarification or project creation from an idea. |
| F06 | Per-project product and technical leadership | Absent | The global agent registry has no project membership column ([schema][schema], lines 56–76); [built-ins][builtins], lines 44–52, contain planner and maintenance roles, not a product/technical leadership pair. [Plan dispatch][plan-dispatch], lines 65–107, uses one chosen role for children. No standing project leaders or their mutual clarification protocol were found in registry, planner, routes, tracker or schema. |
| F07 | Proportionate research, discovery and iterative human clarification | Resembles | [Planner prompt][planner], lines 41–79, asks the harness to read code, fetch references and ask questions. This is prompt-level planning guidance; its Plot/brainstorm prerequisites refer to removed infrastructure. Batch dispatch, steering and follow-up runs do not implement a durable discovery/question-answer cycle or choose discovery depth by product risk. |
| F08 | Product scope, specifications, acceptance scenarios and definition of done | Resembles | The planner mentions goal, constraints and success criteria and can produce tracker steps ([planner][planner], lines 41–79). Prompts/repository files can contain scope and tests. There are no maintained product-scope/specification/acceptance entities or a definition-of-done evaluator in the current schema and routes. An approved tracker plan is an execution prerequisite, not product acceptance. |
| F09 | Technical decomposition, assignment and shared task tracking | Similar | Planner's `sd plan submit` instructions, [IssueTracker][tracker], lines 66–127, and [plan creation][plan-create], lines 138–183, support structured child work items, status, metadata and accepted plans. The coordinator chooses the next pending child ([coordinator][coordinator], lines 201–321). This is issue/plan-driven delivery. There is no TechMaster assigning a mixed specialist team, and a plan-run uses a single agent profile for its ordered children. |
| F10 | Human-facing portfolio/project management dashboard | Resembles | [Projects UI][projects-ui], lines 31–39 and 127–135, shows repository freshness; [project inspector][project-ui], lines 28–38 and 79–96, adds defaults, triggers, ready plans and recent runs. Plan detail shows execution progress. Useful project/run navigation exists, but the repository inventory is not a product portfolio with goals, assignees, blockers, decisions, specifications and acceptance progress. |
| F11 | Agent chat application, rooms and direct collaboration | Absent | [Schema][schema], lines 9–16, explicitly records dropped conversations/messages/Plot tables. Current [routes][routes] and [SPA router][app] expose no rooms or conversation surface. A run steering inbox is one workload's control input, not agent-to-agent chat or Room1/Room2 history. |
| F12 | Management escalation and human decisions/approvals | Resembles | [Plan admission][plan-create], lines 45–49 and 151–158, requires accepted plan statuses; [merge policy][merge-policy], lines 117–148, refuses protected/config-changing auto-merge; [same-row resume][plan-resume], lines 2–29, explicitly handles human merge delay. These provide operator/forge decision boundaries, but there is no worker→project leadership→Butler escalation or correlated human decision queue. |
| F13 | Durable project knowledge and reusable directives | Similar | [Seed artifacts][seed], lines 11–46 and 74–100, transport expertise, workflow, skills and prompts; [prompt composition][dispatch], lines 463–476, injects repository context; [reap pipeline][pipeline], lines 9–18, merges optional tracker/memory deltas. Git-backed files and Mulch can retain knowledge across jobs. Wingman's product-specific DIRECTIVES/SCOPES/SPECS/HARNESS lifecycle and knowledge stewardship must be added. |
| F14 | Persistent identity, conversation and work continuity | Resembles | [Run schema][schema], lines 100–180, freezes role, prompt, project, runtime correlation, Git and outcome facts. [Continuation resolver][continuation], lines 68–116, creates a new run from a previous branch with a same-project check. The role is a reusable definition; run lineage is work continuity. Individual identity/conversation continuity is absent, and local runtime state is lost on server restart ([engine][engine], lines 16–22). |
| F15 | Proactive supervision, periodic wake and blocker follow-up | Similar | [Scheduler][scheduler], lines 4–20, periodically walks projects and dispatches configured work; [watchdog][watchdog], lines 13–45, detects silence and reconciles/cancels/reaps stuck jobs. [Plan tick][plan-tick], lines 102–138, progresses active plans; CI/healer loops dispatch repairs. This is effective operational supervision, but no ProjectMaster reasons over project blockers or contacts leaders through rooms. |
| F16 | Parallel products and concurrent specialists | Similar | [Dispatch lock][dispatch], lines 63–69, serializes a project's shared-clone preparation while allowing different projects to dispatch independently. Each resulting workload is isolated. K8s adds per-project limits ([dispatch][dispatch], lines 291–303). Concurrency exists, but automatic triggers default to a global concurrency of one ([automatic policy][automatic], lines 3–22), and each plan-run is serial. No adaptive specialist staffing. |
| F17 | Real multi-host execution with shared coordination | Similar | [K8sProvider][k8s], lines 2–18, and [pod builder][pods], lines 119–163, send workloads to a Kubernetes API and share control-plane state/callbacks. This can use multiple real cluster nodes. It is not merely a local subprocess. The prior named-worker placement system is retired ([dispatch][dispatch], lines 51–57, 185–188). It does not supply Wingman's enduring host-assigned agents or cross-host collaboration rooms. |
| F18 | Executive agent overview: current/recent/next work and blockers | Resembles | [Operations UI][operations], lines 18–29 and 45–65, shows health/capacity/lifecycle and workloads. [Active workload UI][active-ui], lines 21–27, explicitly uses the first prompt line as activity, not a live task summary. There is no per-person current/recent/next-work and blocker narrative. Run state and infrastructure warnings help an operator but do not fulfill executive organization visibility. |
| F19 | Individual agent summary timeline linked to underlying work | Resembles | [Run inspector][run-ui], lines 31–40, and [bridge][bridge], lines 65–89, expose ordered events and run lineage. This is detailed run history, not a concise timeline for a persistent individual across projects/tasks. The agents inventory has no individual detail timeline ([agents-ui][agents-ui], lines 67–92). |
| F20 | Drill-down into detailed per-agent coding workspace | Similar | [Run inspector][run-ui], lines 31–40, provides prompt, definition, runtime, spend, event tail, preview and controls for a concrete running instance. This is a strong coding-workload drill-down, but not a complete continuing personal workspace or embedded code editor/terminal; ordinary batch workspaces are cleaned up after extraction. |
| F21 | Live activity, lifecycle controls, steering and execution visibility | Similar | [Bridge][bridge], lines 65–99, resumes event ingestion from persisted sequence; [run UI][run-ui], lines 31–55, provides live tail/cancel/re-run/steer. [Steering guard][steer], lines 160–192, rejects unsupported delivery. Crucially shipped Pi declares `spawn-only` ([Pi role][pi-role], lines 60–66) even though its local adapter supports live stdin steering. No claim of universal mid-run steering or durable pause/resume is warranted. |
| F22 | Testing, integrated verification and product acceptance/delivery | Similar | [Coding role][pi-role], lines 33–39, mandates quality gates and commits; [reap][reap], lines 192–254, detects dropped commits/provider/finalization failures; [PR opening][pr-open], lines 133–173, and [coordinator][coordinator], lines 4–23, connect branch delivery and merge gating. CI fixer can repair failing checks. These deliver reviewable code, but tests are mostly harness instructions/forge checks, not an independent TestMaster validating product acceptance scenarios and stopping work on human acceptance. |
| F23 | Autonomous operation with human direction through the organization | Similar | Scheduled runs, patrol-created auto-plan runs, PR merge gating, bounded retries and repair loops can operate unattended under configuration ([scheduler][scheduler], lines 4–20; [pipeline][pipeline], lines 170–191; [coordinator][coordinator], lines 4–23). Humans direct workloads and merge policy. No autonomous product organization carries an idea from discovery through accepted delivery using distinct leaders and communication channels. |
| F24 | Chat, tracker and dashboards accommodate newly added agent profiles | Resembles | Extra seed definitions flow into generic `GET /agents`, UI mapping, run records and dispatch ([seed-file][seed-file], lines 89–105; [agents-ui][agents-ui], lines 67–89; [HTTP dispatch][http-dispatch], lines 378–411). Tracker metadata can name roles. New role names do not require hardcoded UI rows, but team relationships and chat participants cannot expand because those systems are absent. |

## Agent definition and lifecycle, in detail

### What an agent is, and how one is introduced

An `AgentDefinition` is a named, versioned configuration: section bodies, provenance, free-form frontmatter and optionally capability-gated prompt fragments. It is not a running process or a durable employee record. Seven built-ins cover two coding harness profiles plus planner, nightwatch, bugwatch, PR fixer and healer. The global `agents` table has a unique name and registration/refresh dates, with no project/team/manager association. The per-run snapshot does not foreign-key to the definition, preserving history when profiles change ([agent schema][agent-schema], lines 59–66; [built-ins][builtins], lines 44–52; [schema][schema], lines 56–76).

Boot first seeds built-ins, then `WARREN_SEED_AGENTS_FILE`. The latter accepts a JSON array, validates shape and names, and passes definitions to the same drift-aware seeder. Existing non-builtin rows are preserved; builtin-tagged rows can be updated when the definition changes. Thus extensibility is present, but adding a role normally requires operator configuration and server boot rather than a product manager creating an employee at runtime. The file-loading schema does not expose every property in the TypeScript definition—for example, its declared object fields do not include `gatedPrompts`—so parity with inline built-ins should be checked before relying on advanced authoring. See [boot seeding][agent-seeding], lines 25–44; [seed file][seed-file], lines 28–38, 53–79, 96–105; [seeder][builtins], lines 145–154.

The current adapter registry contains only Pi and Claude Code ([adapter registry][adapters], lines 50–57). Selecting an OpenAI model through Pi does **not** make that a real Codex agent. Wingman's explicit Codex-agent requirement would need a Codex runtime adapter with command construction, event parsing, tool/permission semantics, steering and completion behavior. Merely adding a Codex-named prompt profile would not satisfy that requirement.

### Creation, identity and routing

The caller supplies or resolves a project, role and nonempty task. `spawnRun` locks the project's clone-preparation section, checks the agent/project, validates push targets, resolves continuation or replay bases, fetches the repository and reads `.warren/config.yaml`. It folds per-request and project model/provider defaults onto the profile, resolves the effective cost cap, and gates optional Seeds/Mulch prompt fragments on actual capability. It validates the selected provider/model pairing and seed artifacts before creating a durable run row. Each run freezes the resolved definition, raw task, declared provider/model, trigger, project, optional issue and parent/retry relations ([dispatch][dispatch], lines 59–222).

That row's `runId` is the actual independent workload identity. A branch derived from the id becomes the delivery artifact. A runtime handle correlates the database row with the sandbox/pod and harness execution. A separate insert-only dispatch-context snapshot captures configuration/source facts even when runtime creation later fails. This helps reconstruct why an agent used a particular model or budget ([dispatch context][dispatch-context], lines 2–11 and 39–71). It does not establish a standing identity across jobs: two `pi` runs are separate executions sharing one profile name.

The resolved `RunSpec` contains origin, branch/base, runtime id, prompt, network intent, seed files, environment and project resource/image settings. `composeDispatchPrompt` concatenates the profile's `system` section, optional repository context and user task into the dispatched text; that section is not automatically a provider-enforced privileged system message. `provider.create` starts the workload, correlation ids are written together, and a dispatch lifecycle event fires. Partial failures compensate the runtime and roll back/terminalize the durable row ([dispatch][dispatch], lines 280–405 and 452–488). There is no semantic routing from a general human request to ProductMaster, nor a manager-agent selection layer here.

### Execution, tools and permissions

LocalEngine creates a private HOME and Git directory, materializes the workspace, writes `.warren/agent.json`, expertise/workflow/skill/prompt drops, then builds the sandbox. The drive loop runs the chosen adapter, pumps normalized stdout/stderr events, closes held stdin on the terminal envelope, and synthesizes a terminal envelope if the process exits without one. Cancellation and cgroup OOM have separate outcomes. This establishes real execution and concrete supervision ([engine][engine], lines 131–214; [drive][drive], lines 132–221; [drive tests][drive-tests], lines 192–248).

Pi runs with `--mode rpc`, per-run session storage and explicit provider/model; options under `frontmatter.pi` map to tool allow/deny flags, resource paths and extension controls ([Pi argv][pi-argv], lines 141–160; [adapter types][adapter-types], lines 203–238). Claude Code runs headlessly with JSON streams and `--dangerously-skip-permissions`; Warren deliberately relies on the outer sandbox rather than a human tool approval prompt ([Claude adapter][claude], lines 90–106). The default coding profiles request open networking. The `burrow_config` parser only reads the sandbox network field; extra TOML write-path restrictions are not automatically enforced ([network parser][burrow-config], lines 4–17 and 43–81).

Two limits matter for role separation. Planner's source-file write prohibition is in its prompt, not a proved filesystem path ACL ([planner][planner], lines 20–27). Also `frontmatter.tools` has a parser/validator in the definition schema, but the current adapter's concrete argv builder reads `frontmatter.pi` tool options. The source search did not establish enforcement of the generic `tools` bag on the current local path. Wingman should use the demonstrated Pi option path and verify actual sandbox/tool behavior before treating reviewer/planner profiles as hard read-only boundaries. A role name or prompt alone is insufficient isolation.

### Concurrency and scheduling

Several independent runs can exist at once, including repeated instances of the same profile on one repository. The dispatch lock protects shared clone preparation, not the full duration of a job. Each workload has its own working tree. Kubernetes additionally receives per-project concurrency/resource settings and admits pods against cluster/per-project limits. This is compatible with several products and specialists, but it is not a mixed team scheduler. A plan-run deliberately selects one child at a time, waits for its run and PR, then dispatches the next with the plan's single `agentName` ([dispatch][dispatch], lines 63–69 and 291–303; [plan dispatcher][plan-dispatch], lines 65–107).

The cron scheduler walks registered projects, reads triggers, dispatches due cron/scheduled issues, and persists fire bookkeeping. It uses a single-flight tick to drop overlapping cycles and drains before shutdown. The plan coordinator has a separate default ten-second loop. Automatic-run admission defaults to one concurrent automatic job and supports a timezone-qualified execution window. This is an operator-controlled background work engine, not a ProjectMaster periodically waking with a durable conversational identity ([scheduler][scheduler], lines 4–20; [trigger tick][trigger-tick], lines 4–34 and 159–193; [plan tick][plan-tick], lines 9–22; [automatic policy][automatic], lines 3–65).

### Persistence, continuation and interruption

Database event history is durable; bridge ingestion resumes from `maxSeqForRun`, and runtime/provider handles identify the workload to reconnect to ([bridge][bridge], lines 65–89). Persistence of the observation stream and persistence of a process are different: LocalEngine explicitly loses its in-memory run store on server restart. Docker reuses that engine. K8s pod status/logs can be reconciled independently while pods still exist, but its emptyDir workspace is not a persistent agent home.

“Continue with follow-up” creates a fresh run linked to the old one, usually based on its pushed branch; “re-run from scratch” inherits defaults but uses a fresh base; rescue can use a salvaged branch. The resolver rejects cross-project lineage. None of these operations demonstrates rehydrating a previous model conversation/session. Pi's session id and transcript files are useful runtime artifacts, not evidence that the next `POST /runs` resumes them ([continuation][continuation], lines 68–116; [HTTP dispatch][http-dispatch], lines 128–207; [run UI][run-ui], lines 119–152).

Cancellation calls `provider.cancel`, records intent and preserves the reap path rather than marking a row terminal early and losing partial work. The cancel path may reap immediately when status is terminal; otherwise terminal detection/watchdog reconciliation completes it. There is no current general pause/resume-run route in the canonical route table. The source file named `pause-resume.ts` currently implements steer, inbox and cancel, so its filename is not evidence of a checkpointed pause facility ([cancel][cancel], lines 11–47 and 126–145; [routes][routes], lines 269–385).

Steering is also layered. Local/Docker Pi can encode messages over held live stdin; Claude Code intentionally closes stdin and supports pending messages at spawn. The domain checks the frozen profile capability: `none` rejects, `spawn-only` rejects after queued, undeclared legacy profiles fail open. Shipped Pi and planner still declare spawn-only. Consequently a running default Pi job can reject an operator's steer despite the runtime's `midRunSteering: true`; changing this responsibly requires role policy and tests as well as adapter support ([Pi adapter][pi-adapter], lines 13–26; [Claude adapter][claude], lines 21–24; [steering][steer], lines 160–192; [Pi role][pi-role], lines 60–66). An inbox is directional control input, not an agent chat room.

### Failure, retry, completion and retirement

The heartbeat watchdog checks the latest event or start time, cancels silent workloads, and routes them through reap. It has a default 30-second tick and generous 45-minute silence budget, plus faster cancel reconciliation. This can misclassify sufficiently long silent tools. It is a configurable operational detector, not semantic awareness of a blocked product task ([watchdog][watchdog], lines 13–45 and 68–97).

Infra-lost/preempted runs can receive one replacement, linked by `retryOf`, with the original recorded spend deducted from the remaining cap. A retry, already-retried run, cancelled intent or plan-run child does not receive another run-level replacement. Plan-run child retry belongs to the coordinator, avoiding double-dispatch ([infra retry][infra-retry], lines 2–35 and 120–149). Transient provider failures have a separate classifier and current `MAX_PROVIDER_RETRIES = 2`; authentication, quota/rate-limit, invalid model and unrecognized errors fail closed rather than blindly retrying ([provider retry][provider-retry], lines 17–44, 79–93 and 101–132). These are new executions, not transparent continuation of uncommitted model state.

Reap owns terminalization and delivery. It asks the provider to finalize workspace-dependent operations, merges optional memory/tracker artifacts, commits narrowly scoped bookkeeping files, pushes the branch, opens a configured PR, and optionally launches a preview or dispatches newly created plans. Failure facts can override a successful harness exit: provider errors, dropped commits and failed finalization do not count as successful delivery. This is stronger than trusting a final answer, but successful push does not itself prove product acceptance ([reap][reap], lines 46–65, 164–254; [pipeline][pipeline], lines 9–18; [bookkeeping stage][stage], lines 33–55 and 98–127).

Before deleting a workspace whose push failed, Warren tries a rescue ref and durable Git bundle. If delivery and salvage both fail, local workspace teardown can be skipped for recovery. Kubernetes must salvage in-pod before its emptyDir disappears; merely skipping host-side teardown cannot preserve a vanished pod. Ordinary batch workspaces are then terminated. A live preview defers cleanup to its eviction lifecycle ([reap][reap], lines 257–279; [destroy][destroy], lines 23–33 and 71–108; [salvage tests][salvage-tests], lines 99–129). Durable run/event history remains, but deleting a project cascades to its runs/events. This should be considered before treating Warren as Wingman's permanent organizational record ([projects][projects], lines 13–24; [schema][schema], lines 110–114).

The special “resume plan-run” operation is narrower than generic agent resume. It permits only parent/child PR merge-timeout failures, reuses the same plan-run row and existing child PR, and resets the merge-wait clock. Other failures return a state conflict. It specifically prevents recreating a plan and accidentally skipping a closed-but-unmerged child ([plan resume][plan-resume], lines 2–29 and 66–104). There is no employee retirement workflow: normal retirement means tearing down the run's compute. The profile is a reusable registry row.

## Coordination mechanics and one implementation trace

Coordination is primarily **state machines plus Git**, not discussion. Database rows associate projects, runs and ordered plan children. Optional Seeds files carry issue/plan state and metadata. A `PlanCapableTracker` can supply a step DAG, but the actual plan coordinator shown here is a sequential next-pending-child walk, not a DAG-parallel specialist scheduler. An external tracker can instead supply an explicit ordered issue list without supporting plans ([tracker][tracker], lines 85–95; [plan creation][plan-create], lines 51–65; [coordinator][coordinator], lines 201–268). Merge is the integration barrier.

There are two event mechanisms. The durable event table and broker feed live run observers. An observe-only lifecycle bus delivers versioned, deep-frozen notification payloads to boot-wired consumers. Return values cannot veto dispatch, errors are caught, and it is not a durable message bus for peer agents ([lifecycle bus][bus], lines 2–31 and 51–58). Human intervention currently happens by dispatch/steer/cancel and forge review/merge, with protected-path auto-merge policy and accepted plan status. There is no first-class question record preserving who asked which human about which product decision.

Consider a concrete supported request: the operator registers a repository, then submits `POST /plan-runs` for an accepted tracker plan using the `pi` profile. This is a source trace of an implemented request shape, **not a runtime execution performed during this assessment**:

1. `POST /projects` reaches `addProject`, which normalizes/validates the URL, rejects an existing registration, clones and persists the project. This establishes a repository execution target, not a newly discovered product ([projects][projects], lines 108–145).
2. Plan creation checks the project/tracker, refreshes a Git-native tracker clone, verifies accepted status and open children, resolves the global role and transactionally creates plan-run/child rows. An explicit issue-id list takes a parallel validation route and retains the same subsequent serial execution model ([plan creation][plan-create], lines 20–28, 101–123, 138–183).
3. The next coordinator tick lists active plan runs. `advancePlanRun` checks prior child/parent merge state, finds the next pending issue, skips one already closed, reads issue status and renders the child id into the task template. Missing issues fail terminally; transient tracker errors wait ([plan tick][plan-tick], lines 102–121; [coordinator][coordinator], lines 201–268).
4. The plan dispatcher calls the same `spawnRun` as manual/API work, with the plan's role/project/ref and `{planRunId, planId, childSeq}` metadata, then attaches the same event bridge. No hidden specialist-agent hierarchy is introduced here ([plan dispatcher][plan-dispatch], lines 65–107).
5. `spawnRun` resolves/freeze settings and creates the isolated workload. In a local deployment the drive loop runs `pi --mode rpc`; in K8s the control plane creates the run pod and ingests its logs. The bridge commits events before publishing them, exposes live execution, accumulates cost and enforces an observed spend cap ([dispatch][dispatch], lines 195–238, 280–405; [bridge][bridge], lines 65–99; [budget][budget], lines 51–79).
6. The coding harness performs the issue, tests and commits under its prompt contract. Reap merges supported artifacts, pushes, records failure/delivery facts and opens a configured PR. Auto-merge is an opt-in arming decision based on policy from the PR **base**, forge capability and changed paths; config-changing or protected-path changes cannot self-authorize. Actual arming is wired ([merge policy][merge-policy], lines 70–101 and 117–148; [merge arm][merge-arm], lines 98–128).
7. The coordinator records `pr_open`, waits for actual merge, then marks the child merged, closes its issue via the configured hook, and dispatches the next. A legitimate empty push has a special trivial-merge route, but only if its issue still resolves. This avoids treating a missing issue as completed work ([in-flight][in-flight], lines 131–159 and 164–220; [coordinator][coordinator], lines 72–80). The inspected completion test asserts open PR→wait and merged PR→next dispatch ([completion tests][completion-tests], lines 16–40 and 79–113).
8. When every child is merged or skipped, the plan-run becomes succeeded. A stalled human merge can fail the wait budget and be explicitly resumed on the same row. That is delivery-chain completion; Wingman would still need to assemble product verification evidence, consult ProductMaster and record human product acceptance ([coordinator][coordinator], lines 201–211; [plan resume][plan-resume], lines 2–29).

## Major additional capabilities beyond the described Wingman product

**Workload infrastructure and resource boundaries.** Three providers let one execution contract target a host sandbox, sibling container or Kubernetes pod, with explicit capability degradation instead of pretending they are interchangeable. K8s resource/admission controls, image selection and Spot node selector/tolerations are operational capabilities Wingman's purpose does not specify. They let an operator control failure domains and compute cost, at the price of maintaining images, cluster credentials/networking and provider-specific acceptance tests ([Docker provider][docker], lines 69–93; [K8s provider][k8s], lines 170–195; [Spot placement][spot], lines 23–55). This provides cluster-based multi-host work, not a replacement for organizational host/agent directories.

**Spend accounting, behavioral analytics and bounded retries.** Warren tracks model/provider/token/cost facts and observes cost caps during execution. The bridge persists usage and explains cap-triggered cancellation. Enforcement happens when usage events arrive, so it is not an exact prepaid charge boundary and can overshoot between observations. Its analytics go beyond a progress dashboard into delivery economics, tool/command behavior and context-output proxies. The context-waste implementation explicitly distinguishes byte-size proxy from token attribution and excludes unknown cohorts instead of treating missing measurements as zero ([budget][budget], lines 2–19 and 51–79; [context analytics][context-waste], lines 2–27). Wingman could use these for operational decisions, but they should not be presented as product acceptance or individual performance truth.

**Delivery salvage and replay.** Private Git directories, branch lineage, base-commit pinning, rescue refs/bundles, dropped-commit detection and guarded retry budgets make failures recoverable and inspectable. Wingman could reuse this underneath its workers instead of building Git recovery from scratch. Durable storage/backup and retention policy remain necessary, particularly because a vanished K8s emptyDir may already be unrecoverable and project removal deletes associated history ([dispatch][dispatch], lines 104–111, 191–222; [reap][reap], lines 192–279; [destroy][destroy], lines 23–33).

**Reactive maintenance loops.** CI fixer polls PR checks and dispatches fixes onto the PR head, while healer accepts normalized production alerts, resolves a managed project and applies opt-in retry/cooldown policy. These supply autonomous maintenance after initial delivery, beyond Wingman's described stop-after-acceptance development cycle. They are bounded issue/alert-driven jobs, not a continuing operations department; turning them on requires credentials and an explicit product policy about whether accepted products may receive new changes. [Scheduler wiring][scheduler], lines 31–45 and 72–88; [healer decision][healer], lines 25–61 and 82–102; [healer lifecycle observer][healer-lifecycle], lines 14–23.

**Forge/tracker portability.** The forge registry supports GitHub token/App, Azure DevOps and GitLab as real provider selections, while the IssueTracker capability seam supports Git-native Seeds or external protocol bridges. Explicit ordered issues make serial plan execution useful even when a tracker lacks native plans. This could connect Wingman's tracker to Warren rather than forcing duplicate ticket state, but a translator must own status/metadata/acceptance semantics. One forge is boot-resolved for the process. This is not proven per-project heterogeneous forge routing. [Forge registry][forge], lines 11–35 and 56–63; [tracker contract][tracker], lines 46–127; [plan creation][plan-create], lines 51–65.

**Independent audit, judgment and campaign controllers.** Optional extension packages are separate programs, not features automatically running in the base installation. The audit collector polls run/event APIs with durable cursors and advances only after its idempotent sink accepts, giving at-least-once processing. It still relists runs, which has polling and retention implications ([audit collector][audit], lines 2–14 and 56–109). The judge drives a bounded Pi SDK session with three restricted tools to produce validated verdicts and provenance; its prompt-enforced reporting, page/spend caps and unjudged outcomes are explicit limitations. It assesses a transcript, not the actual product acceptance suite ([judge loop][judge], lines 2–26 and 69–95). The campaign controller adds its own durable leases, approvals, budget reservations, journals and response-loss discipline, with an optional policy-gated PR creation step. Its scope is a campaign policy, not Wingman's general conversation/organization model; operating it adds another durable service and policy layer ([campaign tick][campaign], lines 4–32, 142–163).

**Operator/spectator API projection.** A single trusted operator token and optional unauthenticated reduced public projection can share one deployment. Route capabilities are centrally declared; run-scoped callback actors are restricted to their own run's callback routes and liveness. This is useful for public observability and limiting workload callback credentials. It is not named-user RBAC, organization tenancy or a peer-agent permission hierarchy, so the human/agent trust model for Wingman still needs design ([auth][auth], lines 4–28, 56–118; [routes][routes], lines 89–127).

**Preview environments.** The local preview state machine allocates a port, optionally runs setup, launches a sidecar, probes TCP then HTTP, stores a live/failed state and defers workspace destruction while the preview remains live. That can make worker deliverables concretely reviewable. Current Docker/K8s providers explicitly disable preview ports, so cluster adoption requires another preview implementation or accepting the gap ([preview launch][preview], lines 2–8, 34–90; [Docker provider][docker], lines 69–93; [K8s provider][k8s], lines 170–195).

## Distinctive mechanisms and grounded innovation

No claim of historical novelty is made. The useful innovations here are concrete combinations and boundaries that Wingman can study.

1. **A provider-neutral finalize boundary that carries actual delivery evidence.** Warren does not equate process exit with success. The provider finalizes where the workspace physically lives, returns artifact deltas, push/dirtiness facts and events, then the domain classifies outcome, opens PRs and controls teardown. This enables the same delivery logic across host-visible and in-pod workspaces. Its limit is important: best-effort secondary steps can fail independently, and surviving a node loss is constrained by what was captured before the pod disappeared. [Reap pipeline][pipeline], lines 9–18; [reap][reap], lines 192–279.

2. **Retry lineage doubles as an operational bound.** The infra retry uses `retryOf` and existing-successor lookup as the one-retry budget and deducts recorded spend from the original cap. The provider-error path separately classifies transient failures and stamps event lineage, capped at two current retries. This enables unattended recovery without silently turning one human authorization into an unbounded loop. It cannot restore uncommitted reasoning/work, and accounting still depends on observed usage. [Infra retry][infra-retry], lines 10–35 and 120–149; [provider retry][provider-retry], lines 25–44 and 79–93.

3. **Merge-gated serial plans with same-row human-stall recovery.** Each child must actually merge before the next sees the integrated base. Resuming a timed-out plan preserves its existing PR/run association, avoiding a fresh plan skipping a closed issue whose code never merged. This is a pragmatic transaction-like coordination mechanism across tracker, Git and external human review. Its tradeoff is serial throughput and a definition of success centered on merging, not on product verification. [Coordinator][coordinator], lines 4–23; [plan resume][plan-resume], lines 2–29.

4. **Policy is resolved from a branch the executing agent cannot edit in the same change.** Auto-merge reads base-ref configuration, checks concrete changed paths and refuses empty/unreadable diffs, protected paths and config changes. That makes approval policy harder to self-modify through an agent's own PR. It enables bounded unattended delivery when the forge's required checks/reviews are correctly configured. It does not independently establish that those checks are sufficient or implement Wingman's human business decisions. [Merge policy][merge-policy], lines 17–29, 70–101, 117–148; [actual arming][merge-arm], lines 98–128.

5. **Observation extensions and controller extensions have different authority.** The internal lifecycle bus accepts versioned read-only envelopes with ignored returns/error isolation; external controllers use explicit HTTP commands and their own durable policy/journal. This keeps an observability subscriber from becoming an implicit veto in the run path and makes stronger authority reviewable. The bus itself is not durable, and extensions cannot recover deleted data merely from a callback. [Lifecycle bus][bus], lines 14–31; [campaign tick][campaign], lines 4–32.

6. **Capability-gated prompt composition limits fictional onboarding.** The dispatch composer only adds tracker/memory guidance when the project has the corresponding capability, instead of instructing every worker to call nonexistent tools. This is directly useful for Wingman's heterogeneous product environments. It governs prompt truthfulness, not whether all later model instructions or tool policies are enforced. [Dispatch][dispatch], lines 156–171; [Pi role][pi-role], lines 49–51. The stale Plot planner prompt and steering declarations show that this discipline is not complete throughout the revision.

## Practical fit and adoption boundary

Wingman could directly use Warren's **repository-to-isolated-run-to-Git-artifact** path: project registration, model/provider settings, seed files, state/events, cancellation, cost controls, branch push, PR creation, retry/salvage and operational run inspector. Its HTTP API is a plausible executor underneath TechMaster rather than an organization-wide replacement. The tracker/forge seams and optional external-controller pattern provide a path to retain a single authoritative Wingman tracker. K8s offers genuine distributed compute if a cluster is already the desired host model; local mode provides a smaller initial deployment.

Several adaptations are foundational. First, implement and verify a real Codex adapter rather than using Pi with an OpenAI model. Second, map Wingman's durable agent-instance ids and assignment ids into run metadata/dispatch context and store the many-runs-to-one-agent relationship in Wingman. Keep the organizational record outside project-delete cascades. Third, translate tracker states and ticket references deliberately; Warren's `succeeded`, issue `closed`, PR `merged` and Wingman's “product accepted” must remain distinct facts. Fourth, expose effective runtime/profile capabilities to Butler and dashboards so a human is never offered a live-steer, preview or resume behavior the selected path cannot deliver. Fifth, increase/configure the default automatic concurrency and add mixed-specialist dependency scheduling outside the serial plan-run model where appropriate.

The remaining Wingman product is substantial:

- Telegram Butler with contextual project intake and question/answer routing.
- portfolio ProjectMaster.
- per-product ProductMaster/TechMaster identities and leadership protocols.
- proportionate discovery.
- scopes, specifications, acceptance scenarios and definition-of-done records.
- role/team membership and adaptable staffing.
- Room1/Room2 or equivalent durable direct communication.

A shared task/comment/blocker/decision experience; executive and personal summary timelines; and coordinated TestMaster acceptance plus stopping/resuming at the product lifecycle boundary. Warren can run code that implements these, but running such a prompt is not the same as supplying those product capabilities.

The choice is therefore architectural. As an executor, Warren offers a meaningful amount of operational machinery that Wingman otherwise has to build. As the main organizational data model, its ephemeral workload focus, absent chat/discovery/leadership and intentionally single trusted operator would require extensive construction. A narrow integration that keeps Wingman responsible for people-like identities, conversations and product truth is better supported by this checkout than attempting to reinterpret the `agents` inventory and event log as the organization itself.

## Verification scope and limits

This is a read-only, local source assessment of the recorded commit. I read the root Warren `AGENTS.md` and found no more-specific `AGENTS.md` in its checkout. The assessment instruction to preserve source/no installs/services takes precedence over its contributor instructions to mutate Seeds/Mulch, run gates and push. I did not execute those contributor workflows, run tests, make network requests, launch sandboxes, inspect credentials or modify repositories. Runtime statements above mean “implemented by the traced code” unless explicitly called out as tested; no end-to-end behavior was exercised here.

Important implementation paths inspected include:

- the supervisor/server composition root.
- current route table and SPA router.
- SQLite schema.
- definition registry/seeding and built-in prompts.
- project management and clone preparation.
- HTTP/shared spawn/continuation.
- local engine/drive/adapter argv.
- Docker/K8s providers and pod builder.
- event bridge/budget/steering/cancel/watchdog.
- reap/pipeline/bookkeeping/salvage/destroy/merge policy.
- plan creation/coordinator/in-flight/tick/resume.
- scheduler/automatic admission.
- tracker/forge seams.
- preview orchestration and the audit/judge/campaign extension entry mechanisms.

Links above identify the code and inspected line ranges.

Relevant tests were **inspected, not executed**:

| Test source | Evidence read and what it covers |
|---|---|
| [Dispatch lifecycle tests][dispatch-tests], lines 43–81 | Successful dispatch emits the lifecycle payload. A failed provider create does not emit success. Uses fake runtime seams. |
| [Local drive tests][drive-tests], lines 178–248 | Workspace-ready signal, parsed event persistence, success, missing-terminal synthesis, cancellation and OOM classification using fake child processes. |
| [K8s provider tests][k8s-tests], lines 156–220 | Fake Kubernetes API receives pod and seed ConfigMap; handle mapping and callback environment are asserted. Does not prove a real cluster schedules or secures the pod. |
| [Plan completion tests][completion-tests], lines 16–113 | Open PR waits, merge timeout fails, merged PR advances to the next child. Uses stubbed forge reads. |
| [Steering tests][steer-tests], lines 220–299 | Invalid capability handling, legacy fail-open behavior, forwarded message fields and persisted `steer.sent` audit facts. Assertions do not establish all shipped profiles allow live steering. |
| [Salvage tests][salvage-tests], lines 99–129 | Rescue branch facts persist, the run remains failed when delivery failed, and safe teardown follows successful rescue; subsequent test covers bundle fallback. Fake filesystem/Git seams. |
| [Seed file tests][seed-file-tests], lines 30–85 | Valid JSON definition loading, malformed/missing payload refusal and name grammar. Not an operational test of custom Codex execution. |

Negative-feature checks were not based on README silence. I searched `src/` and `extensions/` (excluding bundles/dependencies/goldens) for Telegram, Butler, ProductMaster, TechMaster and Room1/Room2; no implementation hits were returned. I reviewed canonical HTTP/SPA routes and physical persistence schemas for chat, conversations, Plot, pause/resume, team and per-agent history. Schema comments explicitly identify removed conversations/Plot/workers, while routes provide runs, projects, agents, plan-runs, events, analytics and operational surfaces. I also searched runtime adapter registration and tool frontmatter consumers, distinguishing the two shipped harnesses from general model-provider labels and demonstrated `frontmatter.pi` argv behavior from generic tool-policy declarations.

Uncertainty remains around real harness-version compatibility, sandbox enforcement on each OS, live credential refresh, cluster networking/resource behavior, forge permission/check configurations, actual restoration after crashes, full extension integration and throughput/cost under production load. Some code comments describe earlier designs or unfinished wiring even where newer call sites exist. This report resolves specific discrepancies by following current consumers, but a runtime validation phase is still required before choosing Warren as Wingman's executor. No release documentation or optional extension was treated as proof that a base installation enables it automatically.

[schema]: ../repo/src/db/schema/sqlite.ts
[routes]: ../repo/src/server/handlers/route-table.ts
[app]: ../repo/src/ui/src/App.tsx
[boot]: ../repo/src/server/main/index.ts
[contract]: ../repo/src/runtime/contract.ts
[tracker]: ../repo/src/tracker/contract.ts
[supervisor]: ../repo/src/supervisor/main.ts
[http-dispatch]: ../repo/src/server/handlers/runs/dispatch.ts
[engine]: ../repo/src/runtime/local/engine.ts
[drive]: ../repo/src/runtime/local/drive.ts
[docker]: ../repo/src/runtime/docker/provider.ts
[k8s]: ../repo/src/runtime/k8s/provider.ts
[pods]: ../repo/src/runtime/k8s/pod-spec.ts
[agent-schema]: ../repo/src/registry/schema.ts
[seed-file]: ../repo/src/registry/builtins/seed-file.ts
[builtins]: ../repo/src/registry/builtins/index.ts
[agents-api]: ../repo/src/server/handlers/agents.ts
[agents-ui]: ../repo/src/ui/src/pages/agents.tsx
[projects]: ../repo/src/projects/manage.ts
[planner]: ../repo/src/registry/builtins/planner.ts
[plan-dispatch]: ../repo/src/plan-runs/dispatch.ts
[plan-create]: ../repo/src/plan-runs/create.ts
[coordinator]: ../repo/src/plan-runs/coordinator.ts
[projects-ui]: ../repo/src/ui/src/pages/projects.tsx
[project-ui]: ../repo/src/ui/src/pages/project-detail.tsx
[merge-policy]: ../repo/src/runs/reap/auto-merge-policy.ts
[plan-resume]: ../repo/src/plan-runs/resume.ts
[seed]: ../repo/src/runs/seed.ts
[dispatch]: ../repo/src/runs/spawn/dispatch.ts
[pipeline]: ../repo/src/runs/reap/pipeline.ts
[continuation]: ../repo/src/runs/spawn/continuation.ts
[scheduler]: ../repo/src/server/scheduler.ts
[watchdog]: ../repo/src/runs/watchdog.ts
[plan-tick]: ../repo/src/plan-runs/tick.ts
[automatic]: ../repo/src/triggers/automatic-capacity.ts
[operations]: ../repo/src/ui/src/pages/operations.tsx
[active-ui]: ../repo/src/ui/src/pages/operations/active-workloads.tsx
[run-ui]: ../repo/src/ui/src/pages/run-detail/index.tsx
[bridge]: ../repo/src/runs/stream/bridge.ts
[steer]: ../repo/src/runs/steer.ts
[pi-role]: ../repo/src/registry/builtins/pi.ts
[reap]: ../repo/src/runs/reap/run.ts
[pr-open]: ../repo/src/runs/reap/pr-open.ts
[agent-seeding]: ../repo/src/server/main/agent-seeding.ts
[adapters]: ../repo/src/runtime/adapters/index.ts
[dispatch-context]: ../repo/src/runs/spawn/dispatch-context.ts
[pi-argv]: ../repo/src/runtime/adapters/pi-argv.ts
[adapter-types]: ../repo/src/runtime/adapters/types.ts
[claude]: ../repo/src/runtime/adapters/claude-code.ts
[burrow-config]: ../repo/src/runs/burrow-config.ts
[trigger-tick]: ../repo/src/triggers/tick.ts
[cancel]: ../repo/src/runs/cancel.ts
[pi-adapter]: ../repo/src/runtime/adapters/pi.ts
[infra-retry]: ../repo/src/runs/retry/infra-lost-retry.ts
[provider-retry]: ../repo/src/runs/retry/provider-retry.ts
[stage]: ../repo/src/runs/reap/stage.ts
[destroy]: ../repo/src/runs/reap/destroy.ts
[bus]: ../repo/src/runs/lifecycle-bus.ts
[budget]: ../repo/src/runs/stream/budget.ts
[merge-arm]: ../repo/src/runs/reap/auto-merge-arm.ts
[in-flight]: ../repo/src/plan-runs/in-flight.ts
[spot]: ../repo/src/runtime/k8s/pod-spot.ts
[context-waste]: ../repo/src/runs/analytics/context-waste.ts
[healer]: ../repo/src/healer/dispatch.ts
[healer-lifecycle]: ../repo/src/healer/lifecycle.ts
[forge]: ../repo/src/forge/registry.ts
[audit]: ../repo/extensions/audit-log/src/collector.ts
[judge]: ../repo/extensions/judge/src/judge-loop.ts
[campaign]: ../repo/extensions/campaign-controller/src/tick/tick.ts
[auth]: ../repo/src/server/auth.ts
[preview]: ../repo/src/preview/launch/orchestrate.ts
[dispatch-tests]: ../repo/src/runs/spawn/dispatch.lifecycle.test.ts
[drive-tests]: ../repo/src/runtime/local/drive.test.ts
[k8s-tests]: ../repo/src/runtime/k8s/provider.test.ts
[completion-tests]: ../repo/src/plan-runs/coordinator.completion.test.ts
[steer-tests]: ../repo/src/runs/steer.test.ts
[salvage-tests]: ../repo/src/runs/reap/run.salvage.test.ts
[seed-file-tests]: ../repo/src/registry/builtins/seed-file.test.ts
