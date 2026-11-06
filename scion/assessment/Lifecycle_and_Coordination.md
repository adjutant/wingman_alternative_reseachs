# Scion: agent lifecycle and coordination mechanics

Companion to [the main assessment](ASSESSMENT.md). Same pinned revision and static-verification limits apply. Paths below resolve into the unmodified local checkout.

## 1. What is persistent, and what is a run?

Scion's durable agent record is an organizational/execution identity. `ID` is a UUID, `Slug` is unique within a project, and `Name` is a display name. It records template, project, broker, runtime, status, configuration, owner/creator, ancestry and generation. A new container/process run is not automatically a new agent identity. For the normal brokered coding-agent path, several instances of the same template really are independent agents: separate rows, homes, execution and native harness state. The optional managed-cloud path is different: it retains provider interaction/environment references without a local container or mounted home, as described in the main assessment. [Agent model](../repo/pkg/store/models.go), lines 34–155.

Do not collapse these concepts:

| Concept | Actual role | Wingman implication |
|---|---|---|
| Template | Reusable instructions/configuration/material used to define an agent | A reasonable place for BackendCoder or TestMaster profile definition. |
| Harness configuration | Provider/tool-specific executable, provisioner, credentials, readiness/delivery and capabilities | Codex compatibility is an operational property, separate from a job title. |
| Agent | Durable identity associated with a project, ownership and ancestry | Can be a directory member and tracker assignee. |
| Run/container | A particular execution of that agent | Must be distinguished in logs, cancellation and retry handling. |
| Native harness session | Coding tool's own conversation/checkpoint state in its home | Resume is harness-dependent. The Hub record alone cannot reconstruct it. |
| Hub conversation | Persisted human/agent DM or project-scoped group collaboration | Can support project-local Room2; cross-project Room1 needs an additional layer. Not the full native tool transcript. |
| Task prompt/task summary | Initial instruction or short current description | Does not supply a ticket's acceptance/dependency/history semantics. |

The agent state has infrastructure **phase** and runtime **activity**. Activity `completed` is separate from phase `stopped`. An agent can finish an assignment without ceasing to exist. `blocked` explicitly indicates intentional waiting, while `stalled` is an inferred operational problem. [State definitions](../repo/pkg/agent/state/state.go), lines 348–462. Wingman should preserve this distinction in executive views: “container running,” “waiting for a business decision” and “accepted product delivery” are different facts.

## 2. Definition and creation

The default template is intentionally generic. It references `agents.md` and `system-prompt.md`. The shipped system prompt is a placeholder, while the instructions require explicit status reporting for user questions, intentional blocking and task completion. That is a useful reporting convention but no predefined ProductMaster/TechMaster organization. [Template](../repo/pkg/config/embeds/templates/default/scion-agent.yaml), lines 15–19; [instructions](../repo/pkg/config/embeds/templates/default/agents.md), lines 1–29.

`CreateAgentRequest` can name project, broker, template, harness config/auth, profile, task, branch, workspace, labels and inline configuration. It supports provision-only and environment-gather/bootstrap paths. The Hub's attribution function records either a creating user's root ancestry or a creating agent's existing ancestry plus that parent. This is concrete hierarchical agent creation, rather than only a nested textual roleplay. The lineage is also relevant to permission decisions. [Creation request and attribution](../repo/pkg/hub/handlers_agents_core.go), lines 243–330 and 807–844.

`createAgentInProject` performs the extensive admission/configuration work before broker dispatch. The agent gets a project identity and explicit placement. The optional asynchronous launch protocol has a launch ID and broker-owner identity, distinct outcomes for missing environment versus accepted background launch, and eligibility checking. Its gate includes the experiment, request opt-in, a launching request rather than provision-only/reprovision, timeout and broker capabilities. “Async launch exists” therefore does not mean all calls are always asynchronous. [Creation implementation](../repo/pkg/hub/handlers_agents_core.go), lines 1585 onward and 2814–2991; [launch protocol](../repo/pkg/hub/launch_dispatch.go), lines 30–173.

Broker-side provisioning resolves the template/configuration, builds the home/workspace, writes agent state and prepares instructions/skills. The provisioning code has explicit containment, worktree and host-state handling. It is much more than copying one prompt into an LLM request. Prompt rendering and skill installation occur through separate mechanisms. [Provisioning](../repo/pkg/agent/provision.go), line 1890 onward; [instruction injection](../repo/pkg/agent/provision.go), lines 5051–5184; [skill installation](../repo/pkg/agent/provision.go), lines 5184–5405.

## 3. Execution, tools and authority

`AgentManager.Start` resolves retained/new agent material, checks resume preconditions, reads or replaces `prompt.md`, builds runtime configuration and calls `Runtime.Run`. Homes carry harness configuration and state; workspaces carry source/artifacts. The supported workspace choices include a shared workspace, private clones, worktrees over a shared base, and non-git shared/private directories. These modes govern whether colleagues see files immediately, need git integration, or can be moved together. [Start](../repo/pkg/agent/run.go), lines 291–404, 2798–2890; [workspace request modes](../repo/pkg/hub/handlers_projects_core.go), lines 60–77.

The current resolver is declarative/container-script oriented. A container-script harness has an on-disk bundle and runnable provisioner; unusable legacy/missing provisioners fail resolution. Generic declarative metadata can supply command/environment/capability/readiness/delivery behavior. This opens an extension point for different coding tools while keeping execution ownership in Scion. [Harness resolver](../repo/pkg/harness/resolve.go), lines 28–130.

Codex's bundle uses container-side Python provisioning for authentication, MCP translation and native config writing. It declares `C-c` interruption, delayed readiness, Enter submission, native instruction/skills paths and `resume --last`. Its default command bypasses Codex's own approvals/sandbox. Its capability table honestly reports incomplete support: model-call limit enforcement is unavailable, project MCP is not native, and the system prompt becomes instructions. [Codex config](../repo/harnesses/codex/config.yaml), lines 15–123. A Wingman deployment cannot assume that a configured maximum or generic prompt field has identical semantics across harnesses.

Platform authority is a separate layer. Ancestry/standing checks require a live, unheld chain and an active root human admitted to the project. Security role values are capabilities, not job responsibilities. Delegation grants name boundary, allowed permissions, expiry, purpose and credential TTL; v1 rejects subdelegation. Grant exchange/use still checks current authority. Soft/hard deletion, restore and reincarnation revoke grants through transaction hooks; agent/issuer suspension and issuer deletion use best-effort revocation after commit, backed by use-time/exchange denial. Suspension preserves grants associated with a newer run. [Standing](../repo/pkg/hub/agent_standing.go), lines 28–106, 150 onward; [delegation request](../repo/pkg/hub/handlers_agent_delegation.go), lines 64–135; [revocation](../repo/pkg/hub/agent_delegation_lifecycle.go), lines 31–87.

That separation is useful for Wingman: a ProductMaster may need to communicate and publish specifications without the same infrastructure permissions as a machine-maintenance agent. It also means that creating a child agent is both a work-delegation and an authority-admission event. It should not be modeled solely by an unrestricted shell spawn.

## 4. Routing and concurrent execution

The Hub routes commands to the agent's assigned broker. `HybridBrokerClient.route` distinguishes:

1. The current Hub replica owns the broker's control socket: send locally through it.
2. Another live replica owns it: record/forward durable intent and notify that owner.
3. No live owner but the broker exposes an endpoint: use direct HTTP.
4. No current route: retain pending intent for reconciliation on reconnect.

Stateless co-located broker identities have a separate replica-independent direct HTTP rule. [Router](../repo/pkg/hub/broker_routing.go), lines 30–118. This is actual multi-host/multi-replica machinery, not a list of terminal tabs.

Concurrent agents have separate runtime execution. Capacity limits/quotas can constrain launch placement. The capacity read model explicitly distinguishes resolved values and enforcement state: a configured value may be presented with `not_enforced`. [Capacity](../repo/pkg/hub/broker_capacity.go), lines 29–105. Thus concurrency is real, but the assessment does not infer a tested fleet size or promise 100 simultaneous healthy coding agents.

Distributed execution does not automatically unify source files. The shared-dir API states that a declaration does not create directories everywhere immediately; first use provisions backing storage, and Hub writes can only reach storage the Hub can resolve. A remote broker-local directory remains local unless the selected storage/export design shares it. [Shared-dir contract](../repo/pkg/hub/handlers_shared_dirs.go), lines 102–124. For Wingman, shared coordination can live in the Hub while product source placement remains stable per host.

## 5. Chat input is not a transactional task queue

The DM operation consolidates send budget/rate limiting, length validation, mode/cross-project authorization, attachments, message persistence, SSE, delivery rendering and dispatch. Adapter paths handle conversation resolution, group/human routing, wake and mentions. [DM operation contract](../repo/pkg/hub/agent_dm_operation.go), lines 37–143. This is a strong common delivery core. It also makes clear that persistence, transport delivery and agent understanding are separate stages.

Ordinary input uses a debounce buffer because multiple collaborators “typing” into a terminal concurrently can corrupt native harness input. It coalesces bursts, waits for harness readiness, serializes flushes per agent/project and retries bounded delivery failures. One agent's readiness wait does not block another agent's buffer. Interrupt input bypasses the normal buffer and is delivered immediately. The manager first checks for a definitively missing/stopped target, while transient lookup errors allow buffering; asynchronous failures can be reported back through a callback. [Buffer](../repo/pkg/agent/msgbuffer.go), lines 30–126, 200–307 onward; [manager message path](../repo/pkg/agent/manager.go), lines 632–711.

This provides steering and useful background operation. It is not an exactly-once semantic task executor. The DM result contract explicitly distinguishes accepted, failed, ambiguous and deferred results. Accepted means persisted and dispatch accepted, not harness consumption. Ambiguous means the send may have landed while bookkeeping or the request failed, and callers must not automatically replay it. A reincarnating target can receive a persisted deferred message without immediate dispatch. The next generation reads it through conversation catch-up. [DM outcome contract](../repo/pkg/hub/agent_dm_operation.go), lines 175–219. The buffer is not a shared backlog of acceptance-governed tickets. Wingman should add durable assignment states and acknowledgments above this layer rather than trying to infer completion from a successful message send.

Group conversations have an execution-aware default agent. When an agent posts without mentioning another agent, the group's default can receive a delivery copy. A sender never wakes itself; mention-copy message types do not recursively fan out; symmetric per-pair caps limit storms. Those controls matter for autonomous teams conversing without a human gating every turn. [Group default delivery](../repo/pkg/hub/group_default_agent_wake.go), lines 28–120. A project-local management room can therefore appoint a coordinator, but native groups do not span projects: creation requires a project ID and adding an agent from another project is refused ([conversation handlers](../repo/pkg/hub/handlers_conversations.go), lines 740–748 and 1070–1097). Cross-project `group[]` forwarding is also rejected before effects ([message handler](../repo/pkg/hub/handlers_agent_messaging.go), lines 3420–3450). This supports project-local Room2 or local management discussions; Wingman's shared Room1 spanning organization agents and product leaders requires an additional coordination layer or a deliberate change to project boundaries. The escalation policy itself must also come from Wingman instructions and records.

## 6. Telegram request trace

The current Telegram V2 plugin is worth distinguishing from the legacy V1 implementation still in the checkout. It has persisted group/topic links, user mappings, agent caches, registration, notifications and both polling/webhook handling. [V2 implementation](../repo/extras/scion-telegram/internal/telegram/broker_v2.go), lines 48–127, 390–442 and 2196 onward.

For a plain message in a linked product group:

1. `handleGroupMessage` loads the group link and applies a topic default override before the group default.
2. It resolves the sender to a linked Scion human and obtains the agent list as that sender. This avoids making the bot's broad service identity the effective human's visibility.
3. Explicit bot/agent mentions, replies to bot messages and default routing select recipients. A default must still exist in the sender-visible agent set; unknown/unavailable lists are distinct from proven absent agents.
4. The plugin creates structured messages with project/channel/thread/sender context and forwards them with authenticated inbound delivery.
5. The Hub's broker inbound and agent message adapters authorize and dispatch to the agent's assigned execution broker.
6. The manager submits input to the native harness. The agent can issue outbound messages or report a question/completion to trigger notifications.

Evidence: [V2 group route](../repo/extras/scion-telegram/internal/telegram/broker_v2.go), lines 2285–2671; [V2 delivery](../repo/extras/scion-telegram/internal/telegram/broker_v2.go), lines 3398 onward; [Hub inbound](../repo/pkg/hub/handlers_broker_inbound.go); [outbound message request/routing paths](../repo/pkg/hub/handlers_agent_messaging.go), lines 61–150.

`/setup` presents accessible projects, `/default` selects a group/topic agent, and `/agents` lists the linked project's agents. [Commands](../repo/extras/scion-telegram/internal/telegram/commands.go), lines 173–330, 387–419. This is substantial Telegram coordination infrastructure. It is still an explicit addressing model: a single Butler that semantically identifies projects, creates new ones and returns each answer to the correct ProductMaster would be additional behavior running on top.

## 7. Persistence, resume, wake and scheduling

Hub collaboration state persists independently of the viewing browser. Native harness continuity relies on the retained per-agent home/session. `Start` refuses a resume of an agent without its state directory; Codex's bundle supplies native resume arguments. A new prompt may replace `prompt.md`, while a resumed run is not automatically re-fed the original task. [Start/resume](../repo/pkg/agent/run.go), lines 291–404; [Codex resume declaration](../repo/harnesses/codex/config.yaml), lines 75–85.

Message wake is explicit lifecycle work. Admission runs before wake so a rejected message cannot start a target. A suspended agent is resumed under a start claim, quota re-reservation and run intent; readiness is awaited and remaining initializing input can be buffered. A managed cloud runtime explicitly refuses suspend/resume wake. Concurrent starts may defer delivery rather than duplicate the start. [Wake](../repo/pkg/hub/wake_dm.go), lines 35–180; [readiness polling](../repo/pkg/hub/wake.go), lines 41–103.

Cron schedules can send messages or dispatch agents, with author-time and fire-time authority checks. One-shot events are persisted and reloaded; overdue events can fire after downtime. Multi-replica claim support transitions the event before side effects, preventing several replicas from delivering the same timer independently. A handler error/panic is recorded as failure. This is useful scheduled work infrastructure, but not proof of automatic recovery from every failed handler: claiming before effects also means application-level idempotency/retry design remains important. [Schedule inputs](../repo/pkg/hub/handlers_schedules.go), lines 29–62, 140 onward; [timer recovery/claims](../repo/pkg/hub/scheduler.go), lines 511–650.

Notifications subscribe to status events and can deliver to another agent or a human. The fan-out example tells an orchestrator to request notifications and wait instead of polling researchers. [Notification dispatcher](../repo/pkg/hub/notifications.go), lines 37–117; [example](../repo/examples/orchestration-basics/fan-out-parallel/README.md), lines 39–62. Wingman can combine these: completion messages for routine handoffs, periodic ProjectMaster review for missed blockers. The platform does not decide what constitutes useful product-management intervention.

## 8. Failure, interruption and recovery boundaries

Run identity is a recurring safety mechanism. The Manager contract supports stopping an exact run and deleting a resolved runtime target rather than blindly re-resolving a reused slug. Hub status handlers mark reports with the authenticated token's run ID and guard against deletion/reincarnation/start-window regressions. Late status from an older container must not make a deleted or replaced agent look healthy. [Manager contract](../repo/pkg/agent/manager.go), lines 72–111; [status guards](../repo/pkg/hub/handlers_agent_lifecycle.go), lines 105–205.

Broker routing recognizes transient deferral and bounded retry separately from non-transient failure. The reconciliation loop drains persisted dispatch intent when the appropriate broker connection becomes available. [Retry](../repo/pkg/hub/broker_routing.go), lines 138 onward; [reconciliation](../repo/pkg/hub/reconcile.go), lines 31–102, 205 onward. This supports continuity across disconnected execution hosts. It does not itself restore lost source files or infer whether a partially completed code change is correct.

Stall detection and optional auto-suspend address operational waste. Auto-suspend runs through a bounded, deduplicated pending set and a server-owned worker. A slow/panicking batch does not hold the detection scheduler slot indefinitely. Overflow agents remain stalled rather than being silently counted as suspended. [Worker](../repo/pkg/hub/auto_suspend_worker.go), lines 30–71, 95–178. This is infrastructure supervision, distinct from a ProjectMaster discussing a stalled integration with ProductMaster and the coder.

The container's `sciontool` init/supervisor handles child execution and termination; configured duration limits signal the child and report a limit-exceeded status. Status values include explicit crash/exit reasons. [Supervisor](../repo/pkg/sciontool/supervisor/supervisor.go), lines 165–326; [init limit path](../repo/cmd/sciontool/commands/init.go), lines 1508–1607 and 2047–2096. The report does not infer a universal automatic “retry the failed coding task until product accepted” loop from these controls.

## 9. Completion, reincarnation and retirement

The default instructions tell agents to announce `task_completed` and stop asking further questions. This is self-reported task completion. The platform can notify a creator/subscriber; when the opt-in alpha artifact subsystem is enabled, versioned artifact bundles can be reviewed, but it does not independently determine that a product's definition of done was met. Wingman must distinguish a worker's claim, TestMaster's verification and human/product acceptance. [Default completion instructions](../repo/pkg/config/embeds/templates/default/agents.md), lines 21–29; [status command](../repo/cmd/sciontool/commands/status.go), lines 20–103.

Reincarnation is a managed identity-preserving replacement, not native transcript compaction. The API accepts handoff and a dry run, supports selected persistent configuration patches and rejects unsupported overrides such as changing harness config through that request. It returns a plan with old/new fields, warnings and target generation. The worker uses step-specific writes so fresh status/configuration fields are not overwritten by a stale full-row snapshot. It always starts a fresh native session, without the harness resume flag. A generated preamble tells the agent to verify its environment, catch up on saved conversations, notify the responsible owner and continue the handoff's immediate active work without repeating completed work. With no handoff, it must reconstruct context from branch, conversations and project scratchpad. [Reincarnation API](../repo/pkg/hub/handlers_agent_reincarnate.go), lines 37–140; [worker contract and fresh-session start](../repo/pkg/hub/reincarnate_worker.go), lines 31–116, 905–913 and 1646–1703.

Broker moves have an explicit eligibility contract: runtime target, workspace mode, reported storage, same export, actual workspace location, target profile/health/access/capability/capacity. A shared-export move carries the workspace. A forced recreate move permits fresh provisioning and calls out local state lost. Neither is arbitrary live process migration. [Move contract](../repo/pkg/hub/reincarnate_move.go), lines 33–142.

Deletion claims a leased sticky marker, publishes deleting state and starts a detached engine. A quick completion responds synchronously. A slow one returns accepted and reports later. Concurrent deletes join rather than independently tearing down the agent. Cleanup is run-aware, with file retention/deletion decisions and soft/hard deletion separated. Grant revocation participates in lifecycle transactions; expired soft-deleted rows have a purge contract. [Delete engine](../repo/pkg/hub/agent_delete_engine.go), lines 36–107; [purge/finalization contract](../repo/pkg/store/store.go), lines 201–244; [credential lifecycle](../repo/pkg/hub/agent_delegation_lifecycle.go), lines 31–87.

These are strong lifecycle foundations for a standing organization. Wingman still needs its own retirement policy: when to suspend after acceptance, retain knowledge, archive a project, reuse a specialist or create a fresh instance. Scion provides the mechanisms. The purpose document specifies the policy.

## 10. Evidence quality

The companion and main report are source-traced, not runtime-verified. This chapter was reconciled with the main assessment, including project-scoped group boundaries, managed-cloud execution exceptions, Codex harness capability declarations and lifecycle revocation boundaries. The main report identifies the test bodies actually inspected during the fresh assessment. This chapter does not add a claim that all nearby buffer, routing, UI or recovery tests were read or passed. No test was run, and no test result is used as evidence of live remote delivery.

A useful adoption experiment would put Hub and Telegram on the Mac and a broker on Endeavour. It would create two Codex agents under one project. Checks would cover a persisted group conversation, a question/reply exchange and a suspended-agent wake. They would also cover completion notification, restart continuity and product-source integration. That experiment is outside this research-only task and has not been performed here.
