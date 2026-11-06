# TeamMCP assessment against Wingman

- **Product:** TeamMCP, an MCP/HTTP collaboration server with independently launched coding clients, shared messaging/tasks/state, and a Vue dashboard. Package version: 1.1.0.
- **Repository:** https://github.com/cookjohn/teammcp
- **Local checkout:** `researchs/teammcp/repo`
- **Actual assessed commit:** `c82572da10c290429fa53b7d2706ee4687b3fe6f`
- **Assessment date:** 2026-11-05.
- **Method:** read-only inspection of this revision, compared with [WINGMAN_PURPOSE.md](../../WINGMAN_PURPOSE.md), following [ASSESSMENT_GUIDE.md](../../generic/assessments/ASSESSMENT_GUIDE.md). No checkout-specific `AGENTS.md` was found. The supplied global instructions apply. No dependencies installed, processes launched, external services contacted, or source files changed.

## Fit verdict

**A substantial collaboration foundation, but not a ready Wingman implementation.** TeamMCP gets unusually close to Wingman's standing-team substrate: real coding-client processes, named persistent identities, reporting relationships, project-keyed shared state, channels/DMs, task history, human approvals, and a terminal dashboard. Its strongest reuse case is the organizational record and communication plane. Its product contract deliberately leaves the actual coordination to agents; “CEO,” “PM,” and “CTO” are names, prompts, permissions and reporting edges rather than an implemented product-development organization.

Wingman still needs a portfolio registry/intake policy, per-project ProductMaster/TechMaster staffing, proportionate discovery, scope/specification/acceptance records, reliable supervision, Telegram Butler, cross-host runtime placement, and the connected executive briefing/timeline/workspace experience. TeamMCP can deliver messages and assign tasks. The source does not establish reliable progression from an idea through discovery, implementation, integrated verification and human acceptance. It also does not establish suspension until the next request.

**The checked-out runtime has material integration defects.** The macOS start path reads a later-declared `const agentInfo` before initialization. The normal Mac start therefore has a static JavaScript temporal-dead-zone failure. Codex runtime dispatch is present in the Windows process manager, while the Linux/Mac start paths remain Claude launchers. The Codex runner depends on the PTY daemon and Windows-specific executable/input defaults. These are important blockers for Wingman's Mac plus Arch Linux, Codex-only execution requirement. See [Mac process manager][PMM], lines 52–56 and 276, [Windows process manager][PMW], lines 164–182, [Linux process manager][PML], lines 237–287, and [Codex runner][CR], lines 42–63, 179–188. These are source findings, not reproduced runtime failures.

## Architecture and actual execution model

The package exposes `teammcp` through [package.json][PKG], lines 1–18. The [CLI][CLI], lines 63–78, requires `TEAMMCP_HOME` and `AGENTS_BASE_DIR`, then spawns Node on `server/index.mjs`. Starting with `npm start` instead invokes that server directly. This matters because the advertised wizard/default-directory experience and the CLI's strict environment requirements are not identical.

The [server entry point][I], lines 1–41 and 99–146, loads persisted user configuration first, starts a plain Node HTTP server, delegates REST/static routes to `handleRequest`, adds SSE, initializes credential management, and attaches terminal WebSockets. It defaults to binding `0.0.0.0:3100`. There is no workflow graph executing product stages in the entry point. The organizational work comes from external coding clients that call the REST API through MCP.

[Database initialization][DB], lines 10–66, opens `TEAMMCP_HOME/data/teammcp.db` with SQLite WAL, foreign keys and a five-second busy timeout. Durable tables contain agent records, reporting edges, channels/membership, messages/read cursors, tasks/history, project-keyed state/change history, approvals, audit reports, schedules, files/folders, coding metrics, memories and memory session summaries. This is one central database, not replicated coordination state across hosts. Agent work directories live separately under `AGENTS_BASE_DIR/<name>`.

The [process-manager dispatcher][PM], lines 1–34, imports a Windows, Mac or Linux implementation according to the **server machine's** OS. It does not choose a host for each agent. On Linux, `node-pty` launches Claude in that agent's directory; on Mac the intended path generates a shell script and uses Terminal.app; on Windows it launches Claude via local PTY or an optional detached PTY daemon, and dispatches `runtime=codex-pty` to the Codex runner. These are real subprocesses with independent coding contexts. They are not model personas multiplexed inside one controller, but their continuity and tool semantics are inherited from the respective coding clients.

Agents use an MCP stdio bridge that translates tools into authenticated HTTP requests and subscribes to `/api/events`. The [main MCP client][MC], lines 1305–1445 and 1605–1617, converts relevant SSE messages to Claude channel notifications. Windows additionally enables the external `fakechat` plugin, installs it if necessary, and replaces its bridge file with the checked-in TypeScript bridge: [PMW], lines 387–400, 454–498, 647–654. That path changes files in shared/global plugin locations as well as per-agent configuration. It is not a self-contained TeamMCP-only harness.

The optional PTY daemon is a local execution-survival layer. It communicates through named pipes on Windows or a Unix socket on Mac/Linux, not a remote worker RPC: [daemon IPC][IPC], lines 1–15. [Server startup][I], lines 43–65 and 148–259, subscribes to its output, wires watchdog recovery and reattaches existing PTYs/scrollback after server restart. The browser's [terminal component][TV], lines 107–159 and 179–205, renders raw PTY bytes in xterm and forwards user keys. Closing a dashboard view disconnects the browser socket. It does not itself retire the agent.

## Complete feature matrix

Verdicts describe the implementation at this commit, with runtime/platform limitations applied. “Similar” credits a substantial equivalent, while “Resembles” credits only a primitive or narrower behavior.

| ID | Capability | Verdict | Implementation evidence and concrete difference from Wingman |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | [PML], lines 87–138, 240–287, launches a real Claude process per agent directory; [PMW], lines 164–182, dispatches Codex PTY. Multiple named instances can share a role. Wingman's Codex agents on both intended hosts are not delivered by the current platform paths, and the Mac launch bug applies. |
| F02 | Extensible agent profiles, roles and team composition | **Similar** | Registration accepts free-text name/role; [DB], lines 311–325; reporting/runtime/auth can be patched in [R], lines 1800–1838. `CLAUDE.md`, rules and skills define behavior ([PML], lines 110–138, 197–235). `agent_profiles` is knowledge-relevance metadata, not a reusable role-template/instance system: [DB], lines 1408–1415, 1820–1843. Dynamic expert design and retirement are not an implemented elastic staffing algorithm. |
| F03 | Agent directory and visible working relationships | **Similar** | [AV], lines 166–214, builds a searchable list and reporting tree from registered names/roles/status/`reports_to`; [R], lines 1775–1785, provides records. It lacks Wingman's joined project/team/current-assignment/personal-timeline directory view. |
| F04 | Telegram main channel and Butler routing | **Resembles** | An alternative human gateway exists: WeChat input is recorded as Chairman and pushed to CEO/Audit, [I], lines 530–545; CEO/related DM replies forward to WeChat, [R], lines 944–974. No Telegram implementation found in server, clients, templates, dashboard or integrations. CEO routing is a Butler-like starting point, without project clarification correlation. |
| F05 | Cross-project registry/intake and existing/new routing | **Resembles** | `state_kv.project_id`, profile participating-project strings and project-specific channels can represent several products: [DB], lines 1328–1338, 1408–1415. There is no project entity, registry CRUD/intake endpoint, semantic request matching, project creation/staffing transaction or retained execution-host mapping. State UI takes a manually entered project ID: [SV], lines 12, 31–37. |
| F06 | Per-project product and technical leadership | **Resembles** | PM/Product/CTO names appear in configurable manager/admin lists, [DB], lines 1000–1013, 1437–1440, and the sample registry defines management roles, [AR], lines 8–68. Reporting edges are generic/global. No mechanism creates a ProductMaster and TechMaster pair for every project or preserves project-specific leadership responsibilities. |
| F07 | Proportionate research/discovery and human clarification | **Resembles** | Chat, state and approval primitives support asking questions. `routeTask` recommends discussion based on field ownership/uncertainty, [DB], lines 2050–2148. This is shared-state write routing, not domain/market research or an iterative product discovery policy sized to a request. Searches of runtime, tools and templates found no such product pipeline. |
| F08 | Scope, specs, acceptance scenarios and definition of done | **Resembles** | Agents can store arbitrary JSON state, files and task results, [DB], lines 1328–1338; [R], lines 1559–1613, 2562–2610. No typed scope/specification/acceptance objects, DIRECTIVES convention, required readiness checks or definition-of-done gate found. These would be an application layer over the storage. |
| F09 | Technical decomposition, assignment and shared tracking | **Similar** | Durable tasks have assignee, parent, source message, labels, result/due date/metadata/history, [DB], lines 959–1064. REST validates and notifies assignments and changes, [R], lines 2097–2187, 2266–2374. Decomposition is agent judgment; subtasks are containment, with no dependency DAG or readiness scheduler found. Statuses are only todo/doing/done. |
| F10 | Human portfolio/project management dashboard | **Resembles** | There is an actual task list/detail UI, [TasksView][TASKUI], lines 34–68, and project-state/approval UI, [SV], lines 31–69. Task filters are status/assignee ([TaskList][TL], lines 29–52). No portfolio goals/progress/teams/specs/deliverables view or integrated project navigation exists. Credit a task/state console, not a full portfolio dashboard. |
| F11 | Agent chat application, rooms and direct collaboration | **Exact** | Persistent group/topic/DM channels, membership, messages, replies and mentions are implemented: [DB], lines 33–65; [R], lines 773–899, 934–990, 1967–2032; rendered by [ChannelsView][CHV]. Room1/Room2 can be configured as channels and arbitrary new roles can participate. Delivery/filtering caveats below affect reliability, not the existence of chat. |
| F12 | Management escalation and human decisions/approvals | **Similar** | Reporting-edge notifications, field-owner/upper-approver proposals and privileged Chairman resolution are real: [SSE], lines 527–560; [DB], lines 1470–1494, 1579–1633. Events reach approver/Chairman and WeChat, [EB], lines 63–78; [I], lines 561–587. Escalation is partly hardcoded to CEO/Audit. The automatic overdue/blocker escalation loop is disabled ([I], lines 349–493). |
| F13 | Durable project knowledge and reusable directives | **Similar** | Versioned state/change logs and shared files persist; reusable local rules/skills are copied during start, [DB], lines 1497–1547; [PML], lines 197–235. Optional memory engine extracts/retrieves lessons, [MEM], lines 432–480, 529–569. No enforced project SCOPES/SPECS/HARNESS directory, artifact completeness or authoritative knowledge hierarchy. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | Named API identity, SQLite messages/read cursors and tasks outlive processes, [DB], lines 24–65, 311–325. Inbox catch-up summarizes busy channels, [R], lines 1253–1320. Mac/Linux Claude intend `--continue`; daemon PTYs survive HTTP-server restart. Codex starts fresh after process death rather than resuming a recorded thread ([CR], lines 78–94, 179–216, 370–388); identity continuity is stronger than universal conversation continuity. |
| F15 | Proactive supervision, wake and blocker follow-up | **Resembles** | Enabled scheduled-message dispatch runs every minute, [I], lines 495–528; schedules persist with a limited cron parser, [DB], lines 2211–2247. Crash detection/restart exists in [SSE], lines 149–278. Task overdue/check-in/30-60-120 minute blocker escalation is inside an uninvoked `_DISABLED_TASK_MANAGER`, [I], lines 349–493. A scheduled prompt can wake an online manager, but there is no active portfolio review cycle by default. |
| F16 | Parallel products/concurrent specialists | **Similar** | Independent processes and directories plus arbitrary channels/project IDs allow simultaneous teams, [PML], lines 80–107, 279–321; [DB], lines 1328–1338. No global serial worker queue restricts them. Product isolation is by convention; shared repositories/worktrees, resource caps and coherent per-product team placement are not managed. |
| F17 | Real multi-host execution/shared coordination | **Resembles** | Remote HTTP/SSE clients can use `TEAMMCP_URL`, and an HTTP MCP gateway exists, [MC], lines 1305–1317; [GW], lines 24–55. This permits remote participants in central chat/state. Server-managed processes and daemon RPC are local; no remote-host registry, authenticated execution worker, host selection, workspace sync or migration. No distributed runtime was exercised; remote connection support is also marked coming soon in [README][READ], lines 208–215. |
| F18 | Executive overview: current/recent/next/blockers | **Resembles** | Monitor displays online/idle/dead, tool-call/failure counts and last-seen, [MON], lines 47–61, 109–147. Task/state records contain additional facts but the UI does not synthesize per-agent current work, outcomes, next assignment and blockers into Wingman's briefing. |
| F19 | Individual summary timeline linked to work | **Resembles** | Monitor offers a raw tool-use timeline ([MON], lines 131–147); optional session reviews produce summary/key_actions/lessons ([MEM], lines 380–407), and memories have a timeline UI ([MT], lines 124–135). These are not a per-agent plain-language development feed with task/chat/change/test-result links and planned-next distinctions. Memory agent filters are even a fixed list ([MT], line 59). |
| F20 | Detailed per-agent coding workspace drill-down | **Similar** | The browser can select an agent's native terminal and view actual coding-client UI/output, [TV], lines 49–63, 107–159, 179–205. Agent detail also offers output/error records ([AV], lines 78–86, and its detail template). It is terminal access plus logs; no unified task-to-timeline-to-conversation/artifact/review workspace or host routing. Mac intended sessions are Terminal.app, not the same PTY path. |
| F21 | Live activity/lifecycle/steering/execution visibility | **Similar** | Real start/stop/sendkeys/screenshot endpoints, [R], lines 1875–1939; output/tool hooks, [PML], lines 173–195; raw terminal input/output, [TV], lines 135–159, 203–205. Resume toggle is stored. Conversation fork/rename/compact/archive, goals/budgets and durable queued attachments are not managed by TeamMCP; native client commands may offer some actions independently. |
| F22 | Testing/integrated verification/product acceptance | **Resembles** | A worker can execute tests in its coding harness, create review tasks, attach results and request state approval. [Rules][RULE], lines 40–49, prescribe tests before push; [review skill][REVIEW], lines 20–46, describes review handoff. No implemented integrated test/acceptance/release gate. Review skill's `in-review` status conflicts with actual API enum ([R], lines 2106–2109, 2281–2283), weakening the prescribed workflow. |
| F23 | Autonomy with human direction through organization | **Similar** | Real persistent workers receive messages, call tools and delegate by prompt; Chairman→CEO command-chain convention is in [RULE], lines 7–28. Permission-bypassing spawn flags permit autonomous execution ([PML], lines 248–251; [CR], lines 149–158). There is no deterministic end-to-end organization that ensures discovery, quality, acceptance, escalation and stopping; autonomy is enabled, organizational outcomes remain agent-dependent. |
| F24 | New profiles supported across chat/tracker/dashboards | **Similar** | Directory/tree, channels, assignees and task records use runtime names rather than a fixed starting roster: [AV], lines 18–57, 189–214; [DB], lines 42–46, 959–979. Fixed privileges (`Chairman`, `CEO`, `HR`, `Audit`) and memory filter roster remain ([R], lines 1800–1804; [EB], lines 81–83; [MT], line 59). Full new-profile executive/timeline integration is absent with those views themselves. |

## Agent definition, creation and lifecycle

### What is durable, and what is only a prompt

A TeamMCP **agent** begins as an `agents` database row keyed by a globally unique name. A human can be registered in the same table as an AI worker. Registration alone creates no model session or process. The API key identifies the row to the shared services. It does not identify an independently sandboxed OS user. A process becomes available only after the launch path succeeds or an externally operated MCP client connects.

The free-text role, per-directory `CLAUDE.md`, copied shared rules/skills and underlying client configuration determine behavior. A backend engineer can be two independent named rows, each with its own work directory/process. There is no first-class `BackendCoder` profile definition from which instances inherit versioned tools, capabilities or lifecycle policy. The separate `agent_profiles` table instead records relevant/critical state fields, participating projects/channels and last-known versions. Treating that table as a full role-definition system would overstate it.

A **task** is a durable tracker object, not an execution process. A **coding session** belongs to Claude/Codex; coding metrics and memory-session rows reference it but do not make it a TeamMCP execution object. A **PTY handle** is the running terminal/process attachment. It can survive server restart through the optional daemon but is lost when that runtime dies. Shared **messages/state** survive independently and can reconstruct useful context after any fresh client start. This separation explains why persistent agent identity does not automatically mean persistent conversation.

### Configuration and creation

1. The [wizard][WIZ] collects configuration and registers human/worker records; [agent UI][AV], lines 18–57, follows a register-then-patch sequence for runtime/auth/reporting.
2. `POST /api/register` is a separately rate-limited, optional-registration-secret route. [R], lines 254–304, calls `registerAgent`; [DB], lines 311–325, returns an existing row unchanged if the name already exists, otherwise creates the key and joins `general`. Thus repeated registration is identity reuse, not creating another instance. The optional directory creation is best effort and can fail while registration still returns success.
3. Management patches can set `reports_to`, `use_resume`, supported runtime and credentials ([R], lines 1800–1838). Role changes are not exposed in that patch. There is no validated per-project staffing transaction or requirement that the named superior belongs to the same project.
4. Launch scaffolds directory/config/MCP credentials and a minimal identity prompt if missing. On Linux the scaffold explicitly asks the main session to delegate longer work to subagents to stay receptive ([PML], lines 110–138). This is an instruction to the external harness, not a TeamMCP subagent scheduler with registered child identities.

The source therefore supports dynamic registration, but the README's claim that the system automatically invents domain-expert roles and elastically retires workers ([READ], lines 42–43) is not established by an implemented staffing controller. No register-agent MCP tool appears among the main bridge's enumerated tools; agents could use shell/HTTP or externally provisioned configurations. The included [AgentRegistry catalog][AR] lists CEO/Product/PM/CTO and specialist capabilities, but this is declarative integration data rather than the runtime creating project teams from intent.

### Execution, permissions and routing

The REST start endpoint checks that the caller is authorized, the target exists, and it is not already considered online. It delegates to `startAgent` ([R], lines 1875–1888). Process privileges are name/role based—Chairman/CEO/HR or selected role strings ([PML], lines 424–429). Task management uses configurable manager **names**; state administration uses another name list. These lists are not one general capability policy.

Linux prepares `.mcp.json`, Claude instructions/config and tool hooks, then starts Claude with permission bypass and the development channel ([PML], lines 90–108, 173–195, 240–287). Shared config directories may be linked or copied from the user's Claude configuration (lines 140–164); independence of conversation and process does not mean isolated credentials/plugins/filesystem access. Windows likewise shares several plugin/cache directories and rewrites a fakechat bridge in global locations ([PMW], lines 485–517).

Codex's runner creates `<agent>/.codex`, copies global configuration/auth, forces medium reasoning effort, `approval_policy="never"` and `sandbox_mode="danger-full-access"`, and injects the TeamMCP MCP configuration through CLI args ([CR], lines 78–166). These are material policy choices, not a generalized per-role permission editor. The runner requires a connected daemon. Its default executable is a developer-specific Windows path, and submit uses a Windows terminal key sequence (lines 49–63). Windows explicitly dispatches to it; equivalent dispatch is absent from Mac/Linux launchers.

Directed communication is routed using channel membership, mentions, DM recipients and reporting edges, not by resolving a product identifier from a human's natural-language request. The main Claude bridge injects DMs, explicit mentions, System messages and Chairman messages for direct reports, while unmentioned group discussion is left for inbox polling ([MC], lines 1370–1412). The team rules also require ordinary workers to delegate long work rather than block their main session ([RULE], lines 14–28). That can improve responsiveness if the client obeys, but TeamMCP does not enforce delegation or guarantee concurrent turns.

### Concurrency and continuity

Each distinct name can have a real process, so specialists can work concurrently. The process map refuses a duplicate tracked launch ([PML], lines 80–85). The Codex runner first reuses/adopts an existing daemon handle to avoid duplicate PTYs ([CR], lines 190–216). There is no project worktree provisioning, branch ownership, file locking or cross-agent merge manager. Shared work must be coordinated through chat/tasks and client-level tools.

SQLite stores messages and read cursors; inbox catch-up returns actual recent messages for quiet channels and mentions/recent first-line summaries for busy ones ([R], lines 1253–1320). It is a bounded catch-up heuristic, not a full semantic account of all missed decisions. In the live SSE path, some recipients are marked read on delivery, and the bridge filter can ignore an unmentioned group message. Delivery/acknowledgement should not be interpreted as agent comprehension or task completion.

Claude's resume switch defaults on in the database ([DB], lines 96–97, 356–362). Mac constructs `--continue` with a fallback fresh launch ([PMM], lines 272–295); Linux adds the flag to its arguments ([PML], lines 237–251). Windows's displayed launch argument construction ([PMW], lines 647–654) has no `--continue` despite the setting. Codex's fresh launch arguments contain MCP settings but no stored thread resume instruction ([CR], lines 78–94). `resumeAllOnBoot` starts every registered Codex PTY row, not just a separately persisted desired-running set (lines 370–388). A manually stopped Codex worker can therefore be started again after a server reboot if the daemon is available. The stopped set is in-memory. Hot server restart with a surviving daemon is much stronger: it preserves the actual process and current conversation rather than reconstructing it.

### Scheduling, interruption and recovery

Enabled scheduled messages are persisted and dispatched every 60 seconds. The cron parser implements selected minute/daily/weekly/monthly patterns, not arbitrary cron semantics ([DB], lines 2223–2290). This can send a recurring supervision instruction to a manager, but it does not independently establish a sleeping manager that will always start when offline. The substantial overdue/check-in/idle-task escalation implementation is explicitly disabled and has no timer invocation ([I], lines 349–493).

Stopping marks an intentional stop and kills the PTY/PID, removing tracking and PID files ([PML], lines 324–352). Steering can happen through DM/channel input, privileged `sendkeys`, or the terminal; interruption is native client terminal input or whole-process stop. There is no separate durable cancellation token linking task cancellation to runtime interruption. Reopening/marking a task does not itself start/stop its worker.

SSE disconnect crash detection waits, suppresses alerts for intentionally stopped agents, publishes a warning, and optionally restarts under a rate limit ([SSE], lines 149–278). This is transport-based liveness, which can differ from process or productive-work liveness. The optional daemon adds watchdog restart/deduplication and server reattachment ([I], lines 186–259). Neither mechanism retries a particular failed coding task with a bounded attempt ledger or validates its outcome. Recovery state such as in-memory stop/restart maps is weaker across full server shutdown than durable tracker data.

### Completion, acceptance and retirement

Task status transitions to `done` accept a result string and notify creator/assignee. The database writes change/history timestamps, and the route can update linked project state automatically ([R], lines 2315–2371). Completion is a tracker statement by an authorized actor. It does not prove tests pass or that ProductMaster/human accepted delivery. The linked-state auto-update explicitly calls `setState(..., {isApproval:true})` (lines 2363–2370), so it bypasses normal ownership/approval checks. This would need review before using state approvals as product gates.

The review skill is procedural text, not an acceptance engine. It even instructs `status="in-review"`, rejected by the implementation's three-value status enum ([REVIEW], lines 20–27; [R], lines 2106–2109). Rules prescribe testing and human-authorized push, but the launched clients bypass normal tool permission dialogs. Those organizational instructions require compliance by the model and cannot be treated as enforced release policy.

Process stop retains the durable agent row/history/work directory. No implemented agent retirement/archive/delete endpoint or automatic idle-team cleanup was found in the router/DB. The frontend store contains a `deleteAgent` call to `DELETE /api/agents/:name` ([agent store][AS], lines 59–62), but the server route inventory has no matching handler. Channel archival and memory retention are separate implemented concepts. They do not retire worker identities. There is also no TeamMCP conversation fork/rename/compact/archive API.

## Coordination trace: human request to tracked result

The following is a static trace through actual implemented functions, not a run performed during this assessment. It uses WeChat because that is the implemented mobile human ingress.

1. **Human ingress:** the optional WeChat bridge callback in [I], lines 537–545, saves the human's text to `general` as `Chairman`, preserving source/context metadata, then sends a message event to CEO and Audit. This is concrete organizational routing but does not look up a project.
2. **Attention:** [SSE], lines 475–509, sends to a connected Claude channel or dispatches Codex events through `deliverInboxEvent`. The Claude bridge's `reports_to` check governs Chairman group-message injection ([MC], lines 1370–1434). Codex instead builds a bracketed-paste prompt with channel/from/content and instructs immediate MCP reply/ack ([CR], lines 312–360). No structured discovery or existing/new-project choice occurs automatically.
3. **Assignment:** the CEO can turn a source message into a task, assigning a named worker. [R], lines 2116–2133, validates that the source message has not already produced a task; [DB], lines 1022–1064, persists task/history and inserts `task_id` into that message's metadata. The route notifies the assignee through both task event and a persistent DM (lines 2170–2183). This source-message linkage is useful Wingman provenance.
4. **Work and discussion:** the worker marks doing, executes coding tools in its independent client, and uses channels/DMs for questions. PostToolUse/Stop hooks can feed output metrics ([PML], lines 173–195). Tasks only encode parent/child containment, not “wait until API contract task accepted”; agents must negotiate dependencies themselves.
5. **Decision:** if a worker changes another owner's state field or an approval-required field, [DB], lines 1473–1494, writes a pending proposal instead of the new state. [EB], lines 63–78, pushes to approver/Chairman. [I], lines 561–587, saves and sends a WeChat approval notification. Chairman can resolve on any owner's behalf; approval applies the proposed value, records history, and notifies the proposer ([DB], lines 1579–1633). A regular state approval is not an LLM product clarification cycle or tool sandbox.
6. **Result:** a done transition writes task history and emits completion DMs; linked state may be set automatically ([R], lines 2315–2371). A worker/CEO can DM Chairman and the route forwards CEO or WeChat-chain replies, including attachments, to WeChat ([R], lines 944–974). No subsequent integrated verification/definition-of-done calculation runs, and there is no enforced accepted-delivery stopping rule.

Two delivery gaps constrain this trace. First, the optional server priority-batching path emits `message_batch`, but the inspected main MCP client and TypeScript bridge handle only individual `message`, status and approval-resolution events. The Codex runner rejects every non-`message` event ([SSE], lines 380–392; [MC], lines 1399–1445; [bridge][BR], lines 184–199; [CR], lines 312–314). Enabling batching can therefore omit prompt delivery rather than merely reduce interruption. Second, server-side directed-message retrieval attaches `_memories`, but the main MCP client/TypeScript bridge copy only string metadata and do not render that array. The separate `plugin-dist` MCP copy does render memory hints ([dist client][DIST], lines 1476–1491). It is the path used by Codex, yet Codex's prompt builder consumes only channel/from/content. Memory injection is implemented at the server but is not established end-to-end across the actual launch paths. These are integration findings from code comparison, not exercised message-loss measurements.

## Major additional capabilities beyond Wingman's description

### Governed shared-state changes and internal audit

State fields carry an owner, optional upper approver, subscribers and monotonically increasing version. Writes run in a SQLite transaction, support optional expected-version conflict detection, propose unauthorized changes, append a change log and publish subscriber events ([DB], lines 1445–1551). Audit reports are protected by no-update/no-delete database triggers (lines 1384–1406). Compliance/efficiency/anomaly queries can identify frequent field changes or rejected proposals (lines 1660–1811).

This is more formal state governance than Wingman's lightweight shared-record description. It could protect scope, architecture decisions and acceptance authority while retaining traceability. Integration would require a canonical field schema and consistent Wingman profile capability policy. It currently has name-based exemptions, optional version checks and the task-completion bypass described above; using arbitrary state fields as all product records would also lose document structure and artifact links.

### Knowledge-staleness checks and decision routing

Knowledge profiles record state-field versions last seen by an agent. `checkKnowledgeGaps` compares them with current state, retrieves missed change reasons and identifies critical fields ([DB], lines 1875–1954). For onboarded non-admin writers, `setState` can reject writes until the last knowledge check is recent (lines 1449–1460). `routeTask` then recommends write/proposal/discussion based on ownership, required approvals, uncertainty, change frequency and atomic changes across owners (lines 2050–2148).

This could reduce decisions based on stale product context. The check records timestamp/version acknowledgement. It does not establish understanding. Agents maintain their own profiles, and admins/unprofiled agents bypass the check. `last_known_versions` uses the field alone as a key. State uses `(project_id, field)` ([DB], lines 1957–1982). Reusing the same field names across products can conflate awareness unless keys are namespaced. Routing returns recommendations rather than executing a discussion/staffing workflow.

### Memory ingestion, retrieval, lessons and retention

The optional memory engine captures selected events/messages and coding metrics, assigns TTLs, deduplicates and creates searchable memory records with source references ([MEM], lines 156–212, 432–480). Idle-session review stores LLM summaries, key actions and lessons (lines 380–407). Providers extend processing; retrieval combines FTS, short conversation context and optional LLM reranking ([memory injector][MI], lines 100–173, 203 onward). Dashboard exposes memories, LLM configuration/cost and daemon health.

This expands Wingman's persistent knowledge into an event-to-lesson service. It also adds external LLM configuration, retention governance, relevance evaluation and cost. The engine is opt-in (`MEMORY_ENGINE=on`); comments cite past write amplification, so it must not be described as automatically reliable always-on memory ([MEM], lines 529–557). Retention sweeps/watchdog are separately gated ([I], lines 290–331). Source TTL/compaction policy is useful operational work, not a guarantee that important project decisions are retained forever. The delivery inconsistencies above also prevent crediting universal automatic recall.

### Credential lifecycle and provider administration

Named credential profiles share encrypted provider credentials across agents with per-agent model override; deletion refuses profiles still in use ([DB], lines 418–460). There are dashboard token, OAuth refresh/status, credential lease/revocation and provider-probe endpoints ([R], lines 466–684, 1842–1872). Windows Path A uses short-lived credential injection, while other OS paths explicitly reject it ([PML], lines 65–75; [PMM], lines 61–74). Windows also starts a local provider transformation router when needed ([PMW], lines 523–545).

This is substantial operational capability beyond Wingman's stated development organization. It could centralize administration for many workers, but is heavily Claude/provider/Windows-oriented. It needs a distinct Codex-compatible host credential policy and must be kept separate from Wingman's business approvals.

### Native process survival and live terminal access

The split HTTP server/PTY daemon permits dashboard/server restart without deliberately killing the coding runtime, replays bounded scrollback, and reattaches handles. This is useful for maintaining long-running agents independently of the viewing interface. It brings a local IPC protocol, spawn validation, watchdog and replay complexity rather than a distributed execution platform. In addition, the inspected `/ws/terminal` upgrade handler performs no authentication before forwarding keyboard bytes ([PTY manager][PTY], lines 88–159), even though the frontend fetches a dashboard token for REST. Coupled with the default all-interface bind, network exposure requires concrete access-control repair before adopting this terminal control surface. This is a specific implementation risk, not a general claim that every deployment is externally reachable.

### File collaboration and ecosystem integration

Channel-associated uploaded files/folders and message/task attachments provide shared artifact exchange ([R], lines 1559–1764). WeChat additionally carries files/images. AgentRegistry catalogs and the AgentGateway HTTP MCP wrapper make coordination primitives consumable by other MCP/HTTP agents ([AR]; [GW], lines 24–55). They add integration options, but not cross-host lifecycle control or a synchronized product filesystem. A remote agent still needs its own runtime, source checkout and permissions.

## Grounded mechanisms worth borrowing

These are distinctive mechanisms in this implementation, not claims of historical or industry-wide novelty.

1. **Persistent peer identity separate from process lifetime.** A named row/API key, reporting edge, inbox and tracker records remain while the coding client restarts. This matches Wingman's continuing organization better than task-only ephemeral agents. The limits are name-based access rules, inconsistent resume paths and no durable retirement state.
2. **Message-to-task-to-state provenance.** Converting a message to a task records a reverse task link on the original message, maintains task history, sends assignment/result DMs and can update linked state. It offers a compact basis for connected work views. The current UI does not complete the executive timeline/session graph, and automatic state update bypasses acceptance authority.
3. **Version-aware agent context and owner-aware discussion routing.** The gap detector and routing rules explicitly connect knowledge freshness, field ownership and decision authority. Wingman could apply this to scope/specification changes, with project-scoped version keys and server-enforced gates. This does not replace discovery or validate the agent's reasoning.
4. **Delivery attention policy.** Reporting edges, directed mentions, inbox summaries, priority batches and staggered fan-out aim to avoid every agent responding to every message. This is useful for standing teams where message storms consume resources. The checked-in consumers do not consistently support batched events or memory enrichments, so the protocol needs conformance tests before adoption.
5. **Server/runtime separation with reattachment.** Keeping PTYs in a daemon preserves a real native coding workspace across coordinator restarts. It enables live human intervention without the browser owning the runtime. Wingman needs this idea extended to authenticated remote-host workers and structured Codex conversation operations rather than terminal input heuristics.

## Practical adoption path and remaining work

**Directly reusable concepts/code after normal evaluation:** durable chat/channel/DM and task/history schema; message-to-task provenance; owner/version/subscriber state records; approval/change-log presentation; dynamic name/role directory and reporting tree; MCP/HTTP boundary; shared file exchange. The MIT license is declared in [package.json][PKG], line 5, and [LICENSE][LIC]. A fork would still need implementation validation before treating these as production components.

Adapt substantially:

- Replace the WeChat/Chairman/CEO assumptions with Telegram Butler and project-correlated questions.
- Make privileges derive from extensible profiles rather than special names.
- Add explicit project membership and project-to-source/host records.
- Use a maintained Codex interface on both Mac and Linux.
- Fix launch/resume/stop/retire semantics.
- Reconcile the three bridge copies and guarantee event delivery/ack behavior.
- Secure terminal upgrades.
- Decide whether optional memory complements authoritative DIRECTIVES or is unnecessary complexity.

Build for Wingman:

- A real project registry and existing/new/ambiguous intake.
- Per-product ProductMaster/TechMaster provisioning and specialist instance management.
- Discovery sizing and clarification loops.
- Scope/specification/acceptance/definition-of-done records.
- Task dependencies and integration ownership.
- Periodic portfolio/blocker supervision.
- Integrated testing/product acceptance/delivery stopping. A host registry with remote execution/continuity. An executive per-agent now/recent/next/blocker model and linked summary timeline.
- Connected chat/task/artifact/session drill-down and the desired conversation lifecycle/goals/budget controls.

For Wingman, choosing TeamMCP means building an organizational application on a substantial collaboration service while also repairing and replacing parts of its runtime. It is a stronger basis for chat/tracker/state than for the Codex execution and complete product journey. The checked-out revision should not be adopted unchanged for the specified two-host environment.

## Verification scope and limits

Inspected entry/configuration paths:

- package/CLI.
- user/runtime entry point.
- DB initialization/migrations.
- REST route inventory and relevant handlers.
- platform process-manager dispatcher and Mac/Linux/Windows start/stop paths.
- Codex PTY runner.
- daemon IPC/reattach wiring.
- SSE routing/restart/batching.
- MCP clients and TypeScript channel bridge.
- event bus.
- shared-state/approval/knowledge/task/schedule code.
- memory ingestion/injector.
- Vue directory/task/state/monitor/memory/terminal components.
- organizational rules/review skill.
- AgentRegistry and HTTP gateway integrations.

Targeted searches covered `server`, `mcp-client`, `dashboard/src`, `templates`, `bin` and `integration` for Telegram, project registry/intake, discovery, acceptance/definition of done, task dependency concepts, agent retirement/delete/archive, and conversation fork/compact operations. Generated dashboard bundles and lockfiles were excluded from substantive analysis. Negative judgments rely on that route/schema/tool/template search plus the concrete primitives inspected. They do not claim that an external model could never invent the behavior using shell commands.

Relevant tests inspected: [credential merge protection test][TEST], lines 1–69, tests a locally replicated merge helper rather than importing the production merge function. It is limited evidence of runtime correctness. [Codex inbox E2E script][E2E], lines 1–44, sends a DM to a named live local agent and polls for a tagged response, with deployment-specific credentials/configuration. It is an ad hoc live harness, not a portable isolated test suite; credentials are deliberately not reproduced here. The Enter-variant probe and runner comments show terminal-version sensitivity, not verified current compatibility. Package scripts expose no standard comprehensive test command ([PKG], lines 13–21).

**No tests or runtime flows were executed.** No assurance is made about actual launch success, multi-host use, throughput, long-term uptime, data-loss claims, model compliance with role prompts, WeChat availability, memory quality or end-to-end delivery. README production metrics and claims about competing frameworks were not independently validated. Static defects/inconsistencies are identified as such; claimed external or future capabilities are not substituted for checked-out implementation.

[R]: ../repo/server/router.mjs
[I]: ../repo/server/index.mjs
[DB]: ../repo/server/db.mjs
[PKG]: ../repo/package.json
[CLI]: ../repo/bin/teammcp.mjs
[PM]: ../repo/server/process-manager.mjs
[PML]: ../repo/server/process-manager-impl-linux.mjs
[PMM]: ../repo/server/process-manager-impl-mac.mjs
[PMW]: ../repo/server/process-manager-impl-win.mjs
[CR]: ../repo/server/codex-pty-runner.mjs
[SSE]: ../repo/server/sse.mjs
[MC]: ../repo/mcp-client/teammcp-channel.mjs
[DIST]: ../repo/plugin-dist/mcp-client/teammcp-channel.mjs
[BR]: ../repo/templates/channel-bridge/server.ts
[IPC]: ../repo/server/pty-daemon-ipc.mjs
[PTY]: ../repo/server/pty-manager.mjs
[EB]: ../repo/server/eventbus.mjs
[MEM]: ../repo/server/memory.mjs
[MI]: ../repo/server/memory-injector.mjs
[AV]: ../repo/dashboard/src/components/agents/AgentsView.vue
[AS]: ../repo/dashboard/src/stores/agents.js
[TV]: ../repo/dashboard/src/components/terminal/TerminalView.vue
[MON]: ../repo/dashboard/src/components/monitor/MonitorView.vue
[SV]: ../repo/dashboard/src/components/state/StateView.vue
[MT]: ../repo/dashboard/src/components/memory/MemoryTimeline.vue
[TASKUI]: ../repo/dashboard/src/components/tasks/TasksView.vue
[TL]: ../repo/dashboard/src/components/tasks/TaskList.vue
[CHV]: ../repo/dashboard/src/components/channels/ChannelsView.vue
[WIZ]: ../repo/dashboard/src/components/wizard/SetupWizard.vue
[RULE]: ../repo/templates/rules/team-rules.md
[REVIEW]: ../repo/templates/skills/submit-for-review/SKILL.md
[AR]: ../repo/integration/agentregistry/teammcp-agents.yaml
[GW]: ../repo/integration/agentgateway/teammcp-http-server.mjs
[READ]: ../repo/README.md
[TEST]: ../repo/server/__tests__/credential-manager-merge-protection.test.mjs
[E2E]: ../repo/scripts/codex-test/test-inbox-e2e.mjs
[LIC]: ../repo/LICENSE
