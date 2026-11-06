# AO agent lifecycle and continuity mechanics

Companion to [Agent Orchestrator assessment](ASSESSMENT.md), at revision `fc92e7ec6f43fc06317cd47cdf8813956612fe50`. Static implementation review, 2026-11-05; no runtime or tests executed. Re-audited against the master report and cited source on 2026-11-05. This chapter adds detail without changing the master verdict.

## 1. Identity has several independent lifetimes

| Concept | Actual meaning | Wingman implication |
|---|---|---|
| Project | Durable registry row with path, kind, repository identity and configuration. | A useful product workspace identity. It does not contain product ownership/discovery/acceptance by itself. |
| Harness | Provider/CLI adapter identity and capability set. | Codex is an execution technology, not an employee role. |
| AO session | Persistent execution/work ownership, optionally associated with a project, with worker/orchestrator kind, title, metadata and lifecycle facts. | Useful binding target for a Wingman agent instance, but it is not already the employee/profile/team model. |
| Native provider conversation | Opaque provider context handle. | Preserve separately from AO IDs; not every harness proves identity interchangeability. |
| Controller generation/runtime launch | One particular owner of a live provider/runtime. | Fence obsolete events so a replaced process cannot update the current agent. |
| Chat turn | One queued/dispatched provider request with outcome and history. | A turn is not a ticket, product or standing employee. |
| Report | Worker-originated checkpoint/input/stuck/done claim with output references and delivery lifecycle. | A meaningful coordination event; do not promote it automatically to verified task completion. |
| Review run | Separate reviewer execution against an owned worker's PR/head. | Useful quality role, distinct from TestMaster's integrated product acceptance. |
| Side conversation | Separate native context/host attached to a session and explicit boundary. | Useful focused questions; not a project room or a new permanent employee. |

The distinctions come directly from [project.go](../repo/backend/internal/domain/project.go), lines 27–91; [session.go](../repo/backend/internal/domain/session.go), lines 19–26, 226–237 and 264–290; [report.go](../repo/backend/internal/domain/report.go), lines 55–135; and [side_chat.go](../repo/backend/internal/domain/side_chat.go), lines 8–46.

## 2. Definition → durable creation → one controller

The caller selects a registered project and submits a worker prompt or requests its orchestrator. Project configuration supplies reusable rules and defaults. The session manager resolves the harness and mode. It combines project, role, and request settings. It checks model and permission support before durable creation. An unsupported explicit Chat request fails. An inherited Chat preference can fall back to TUI for selected capability or readiness errors. This preserves the caller's explicit interaction contract.

Creation can use a client request key/hash to return an already committed session on retry. Scheduled runs have a separate durable automation-run association. Hidden task-preparation rows reserve speculative workspaces, then become real sessions at claim/commit rather than multiplying unused worktrees on every interaction. A session receives an artifact directory and composed task/system instructions; AO provisions its workspace and attachments before the mode-specific launch. Role rules become provider instructions, not an enforced filesystem permission boundary.

Chat can return early with a durable `provisioning` session. That row has progress steps (`fetch`, `worktree`, `setup`, `agent`) and a persistent error message if startup fails. Queued input can survive startup failure and await retry. This is an important boundary: “addressable in the dashboard” does not yet mean “agent running.” AO's explicit provisioning facts give Wingman a way to show the truth.

Source: [manager.go](../repo/backend/internal/session_manager/manager.go), lines 989–1188, 1205–1238 and 1370–1429; [delegation.go](../repo/backend/internal/service/session/delegation.go), lines 52–133; [session.go](../repo/backend/internal/domain/session.go), lines 334–353 and 418–478.

After shared setup, exactly one mode launches. TUI uses native runtime I/O; Chat starts a protocol controller and delivers an initial prompt as a turn or drains a durable queue. It has no agent pane into which text should be injected. The Chat launcher contract retains semantic message identity and sender attribution for relayed session messages. The mode-aware boundary avoids accidentally delivering the same task through both a terminal paste and a protocol call.

Source: [chat_spawn.go](../repo/backend/internal/session_manager/chat_spawn.go), lines 15–59; [manager.go](../repo/backend/internal/session_manager/manager.go), lines 1395–1435.

## 3. Live execution and truthful observation

AO's durable activity facts are separate from the board's derived status. The read model combines session activity, signal freshness, termination and SCM facts. There is a grace period for an expected terminal hook that has not arrived. An unobserved worker need not be confidently labelled idle. PR state is also separate from runtime activity. These distinctions prevent a single status enum from having to represent all execution and delivery facts at once.

The reaper polls runtime liveness and sends observations to lifecycle logic. It does not write session rows directly. An adapter or probe error does not establish process death. A circuit breaker requires at least five dead conclusions in one pass. It also requires dead conclusions to exceed half of all observations. The breaker changes those conclusions to failed probes. This can delay recognition of genuine simultaneous exits. It prevents a temporary backend outage from terminating the entire board.

Source: [status.go](../repo/backend/internal/service/session/status.go), lines 10–39; [reaper.go](../repo/backend/internal/observe/reaper/reaper.go), lines 1–6, 19–33 and 139–190.

## 4. Three different ways to continue work

### Adopt a still-live provider

The strongest continuity case is not resume at all. A detached per-session host still owns the provider process while the desktop/daemon disappears. The new daemon authenticates to that host and reattaches. A host descriptor retains session identity, protocol, ownership fingerprint, address and PID. Explicit “already attached,” “ownership inconclusive,” “not running” and “incompatible” errors prevent treating every reconnect failure as permission to spawn a duplicate provider.

ACP retains initialization state, session state, request correlation, and pending requests. Its prompt journal appends provider frames before daemon delivery. The journal has a 256 MiB limit. Event and request identities survive daemon reattachment. Replacement hosts use different identities. A pending completion needs acknowledgment before another prompt can overwrite its recovery state. This protects the gap between provider completion and SQLite projection.

The mechanism primarily survives supervisor replacement while the host lives. It is not a VM checkpoint or durable serialization of arbitrary running tools after host/machine loss. The journal appender shown here writes bytes but is not evidence of a full power-loss-safe distributed transaction. Avoid expanding its guarantees beyond the implementation.

Source: [persistenthost/host.go](../repo/backend/internal/adapters/chatdriver/persistenthost/host.go), lines 74–141; [acp_journal.go](../repo/backend/internal/adapters/chatdriver/persistenthost/acp_journal.go), lines 11–61; [acp_relay_restart_test.go](../repo/backend/internal/adapters/chatdriver/persistenthost/acp_relay_restart_test.go), lines 10–86.

### Resume a provider conversation after actual controller/host failure

AO persists native handles separately from its session ID and rotates controller generations for replacement owners. Native resume capability and provider history are adapter-dependent. The restore path returns whether it used native resume, saved-prompt fallback or fresh launch. These are semantically different outcomes. A terminated session needs enough workspace metadata to be restorable, and fallible restore I/O runs before durable resurrection.

For Wingman, fallback should be visible in the agent timeline: “native conversation resumed” and “fresh process started with task context” preserve different amounts of working context. Simply retaining an AO row does not prove that the provider kept all previous reasoning/history.

Source: [session.go](../repo/backend/internal/domain/session.go), lines 226–237; [manager.go](../repo/backend/internal/session_manager/manager.go), lines 3045–3104 and `restoreArgv` beginning at line 7105.

### Continue an interrupted task with a reminder

The Continue mechanism locates the interrupted turn in the active lineage. It derives bounded task context and stores that reminder with the new request. It refuses continuation when it cannot establish the stopped task. The reminder omits reasoning and tool outputs. It is not an execution checkpoint. It cannot restore a command at its exact instruction pointer.

Source: [continuation.go](../repo/backend/internal/service/chat/continuation.go), lines 15–59 and 62–87.

## 5. Interface handoff, branching and fork limits

The public interface transition API durably records source, target and policy, then runs the drain/interrupt transition in background so the request timeout does not own its lifetime. It checks whether the session is terminated, the target differs, the workspace exists and native conversation identity can be established. Source intake is fenced while ownership moves. Some adapter paths permit explicitly degraded identity reset; such paths must not be described as preservation of the same native context.

This is a good model for Wingman's detailed agent workspace: the dashboard can change interaction mode without granting two controllers authority over one agent. It is not live migration between the Mac and Endeavour. The same session/workspace remains on its owning execution host.

Chat also supports rollback, message edits that branch before a prior prompt, and activation of stored conversation branches. However, the standalone `ForkConversation` function explicitly says it is **not reachable over HTTP** pending a coherent second-session/workspace-state decision. Native provider history fork copies conversational memory, not filesystem changes; giving a new worktree to an agent that remembers edits missing from that tree would be misleading. Thus full-session fork must remain a Wingman gap/adaptation even though provider branch tools exist.

Source: [interface_transition.go](../repo/backend/internal/session_manager/interface_transition.go), lines 167–222 and 278–292; [history.go](../repo/backend/internal/service/chat/history.go), lines 110–162 and 865–879. [Native ownership integration tests](../repo/backend/internal/session_manager/interface_transition_history_integration_test.go), lines 22–37, cover transcript preservation/unavailability, identity change and project coordinator replacement under controlled external I/O.

## 6. Steering, queued input and human decisions

AO separates queueing, steering, and interruption. Cancelling a queued item does not cancel the running turn. Queue edits and reordering apply to undispatched items with conflict and idempotency checks. Steering requires provider capability. It retains the provider turn ID and records a delivery result. Provider acceptance can occur before persistence becomes certain. A typed uncertainty state prevents automatic double delivery in that case. The CLI offers receipt recovery. Provider acceptance alone does not prove agent action.

Approvals and structured input are native-provider interactions. These are valuable execution controls and can return a human answer to the correct provider request. They do not contain Wingman's product-question lifecycle: a question such as “which lending jurisdiction?” still needs project discovery context, Butler transport and an accountable agent, rather than merely a provider permission dialog.

Source: [queue.go](../repo/backend/internal/service/chat/queue.go), lines 23–108; [steer.go](../repo/backend/internal/service/chat/steer.go), lines 15–74; [send.go](../repo/backend/internal/cli/send.go), lines 99–148; [ChatTimelineItems.tsx](../repo/frontend/src/renderer/components/chat/ChatTimelineItems.tsx), lines 57–70, maps approval/input/usage/error activity kinds to presentation icons. The controller, rather than this icon map, owns native interaction handling.

## 7. Wake, completion, retirement and cleanup are different operations

The automation scheduler creates durable run occurrences and claims with leases before spawning. It reconciles existing run/session associations on retry, distinguishes completed launch from a seed and supports bounded catch-up. These are scheduled executions. A new scheduled worker is not automatically the same persistent organizational employee.

Optional worker Chat hibernation conserves resources after a settled idle period when no active view/work/pending interaction prevents it and native resume is available. Opening a view or sending work can wake the cold session. View lease expiry and a 90-second idle threshold are implementation facts, not a product completion judgment. Orchestrators are excluded by the cheap durable eligibility check.

Worker done reports are meaningful progress claims with references, but do not mutate authoritative lifecycle. PR-based automatic termination is an optional delivery rule: no open PR remains, at least one merged and the worker is quiescent. This differs from product acceptance, especially for multi-application products or artifacts without PRs.

Kill uses a guarded multistep operation with its own teardown budget. Browser or request cancellation must not leave a dead provider with a logically live row. Cleanup processes terminated records and checks workspace ownership. Cleanup generations prevent an earlier episode from claiming current success. The system reports skipped or refused cleanup. Repeated cleanup does not revisit settled workspaces. Pre-remove scripts apply only to AO-managed workspaces. Forced orchestrator replacement has a separate cleanup policy. Wingman's reusable agent profiles still need an explicit retirement workflow.

Source: [scheduler.go](../repo/backend/internal/service/automation/scheduler.go), lines 52–98 and 135–179; [hibernate.go](../repo/backend/internal/service/chat/hibernate.go), lines 16–24 and 63–110; [session.go](../repo/backend/internal/domain/session.go), lines 449–457; [report/service.go](../repo/backend/internal/service/report/service.go), lines 94–141; [reactions.go](../repo/backend/internal/lifecycle/reactions.go), lines 82–118; [manager.go](../repo/backend/internal/session_manager/manager.go), lines 2670–2733 and 5532–5623; [workspace_cleanup.go](../repo/backend/internal/session_manager/workspace_cleanup.go), lines 55–71 and 92–145.

The practical design lesson for Wingman is to retain these separate lifetimes: employee identity, assignment, native context, live controller, report delivery, code-delivery outcome, accepted product outcome and workspace reclamation. AO provides substantial machinery for several of them, but collapsing them into a single “agent status” would discard one of its strongest architectural ideas.
