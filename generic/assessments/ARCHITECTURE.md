# Architecture findings for Wingman

## Main finding

Wingman needs a persistent development organization. A coding-agent launcher provides only part of that system.
The source assessments identify three useful layers: organization, execution, and engineering process.
These layers can share a product. Their contracts still need separate review.

An organization layer owns project identity, roles, work assignments, decisions, and portfolio state.
An execution layer owns sessions, processes, workspaces, attempts, and recovery.
An engineering process connects discovery, specifications, implementation, verification, and accepted delivery.
The comparison table describes source behavior in these layers. It does not rank production reliability.

## Candidate groups

| Layer | Useful source studies | What to inspect | Main Wingman gap |
|---|---|---|---|
| Standing organization | [Paperclip](../../paperclip/index.html), [OpenRig](../../openrig/index.html), [Multica](../../multica/index.html), [Crewly](../../crewly/index.html), [Agent Swarm](../../agent-swarm/index.html) | Agent records, assignment authority, durable decisions, wake policy | The full Butler and project-leadership workflow needs explicit implementation. |
| Coding workspace | [Orca](../../orca/index.html), [CAR](../../codex-autorunner/index.html), [Maestro](../../maestro/index.html), [Agent Deck](../../agent-deck/index.html) | Native session identity, task attempts, inbox recovery, detailed workspace | Portfolio discovery and authoritative product acceptance remain separate work. |
| Distributed execution | [Scion](../../scion/index.html), [Hcom](../../hcom/index.html), [SwarmOS](../../swarmos/index.html), [OpenClaw](../../openclaw/index.html) | Host registration, delivery acknowledgment, remote placement, recovery | A remote process does not establish shared product state or common files. |
| Engineering process | [gstack](../../gstack/index.html), [Babysitter](../../babysitter/index.html), [Ralph Orchestrator](../../ralph-orchestrator/index.html) | Reviewed plans, evidence receipts, state transitions, recovery checkpoints | A process layer can depend on a separate host for agents and messages. |

## Identity and ownership

Use separate identifiers for project, agent, session, task, and attempt.
An agent ID names a continuing responsibility. A session ID names a provider conversation.
A task ID names an assignment. An attempt ID names one execution of that assignment.
Include the host and current ownership version when a worker reports an outcome.

This separation prevents a common failure. A worker can finish after the supervisor has replaced it.
The system must reject a result from the old attempt when it targets the replacement attempt.
An atomic task claim prevents two workers from winning the same claim.
It does not prevent repeated external effects after an uncertain network result.

Orca ties control messages and completion reports to execution attempts.
OpenRig separates a continuing seat from its replaceable conversation.
Paperclip separates the company agent from a run and its authorized issue work.
These are useful designs for Wingman. They do not prove that the same model session must run forever.

## Message states

| State | Required evidence | What the state does not prove |
|---|---|---|
| Accepted | The receiver stored the request or admitted it to a queue. | The destination has not necessarily received it. |
| Delivered | The runtime received the request for the intended target. | The agent has not necessarily acted on it. |
| Handled | The destination recorded a handling result for that request. | The resulting product has not necessarily passed verification. |
| Work complete | The current owner settled the assignment with an outcome. | The outcome is not independent product acceptance. |
| Product accepted | Required checks and the authorized acceptance decision refer to the delivered version. | Later changes need their own acceptance evidence. |

A message record should include sender, recipient, project, task, attempt, and correlation ID.
Store a reply-to ID for questions. Keep a separate deduplication key for retries.
An ordinary discussion message should not silently become an authorized product change.
Live steering needs the expected active turn ID. A queued follow-up has a different execution contract.

Agent Swarm separates discussion, tasks, and steering records.
CAR separates queued execution from interrupt-and-restart behavior.
Agent Deck uses durable inbox delivery and deduplication.
Wingman should preserve these distinctions in its tracker and UI.

## Recovery contract

Persist the intended operation before starting the external action.
Record the native execution identity as soon as the runtime supplies it.
After restart, inspect that identity before starting another attempt.
Represent an uncertain outcome explicitly. Do not convert a timeout into proof of failure.

Use a durable outbox for network delivery. Use an inbox or receipt table for duplicate input.
Commit task ownership changes in the same transaction as the related state transition.
Use bounded leases only for the authority that the lease actually controls.
A lease expiry cannot prove that a detached process stopped.
Reconcile process state, task ownership, and provider state before replacing work.

## Four kinds of continuity

| Kind | Durable record | Recovery question |
|---|---|---|
| Agent identity | Role, project, reporting relationship, permissions | Which responsibility continues after a process exits? |
| Conversation | Provider thread binding and transcript | Can the runtime resume this conversation safely? |
| Work | Task, attempt, owner, blockers, outcome | Which assignment is still active? |
| Product knowledge | Scope, specification, decisions, test evidence | Which product definition governs the next action? |

Agent Swarm reconstructs context in fresh Codex conversations at the assessed revision.
CAR retains managed-thread bindings and execution history.
Neither approach alone proves that all four kinds of continuity remain consistent.
Wingman must connect them with explicit IDs and versioned records.

## Product discovery and acceptance

ProductMaster must resolve uncertainty before TechMaster commits a broad implementation plan.
Use a short discovery cycle for a small mockup. Use deeper research for a substantial product.
Record each question, answer, assumption, decision owner, and affected scope version.
Keep researchable facts separate from choices that require the human's judgment.

A useful discovery experiment starts with the same vague request for each candidate.
For example, use “Build a loan origination system” without supplying a hidden specification.
Observe whether the system identifies users, product boundaries, workflow, integrations, and acceptance needs.
This is an experiment design. The retained research does not establish a measured winner for that experiment.

Link each acceptance scenario to the relevant specification and delivered version.
TestMaster records actual checks and unresolved defects.
The authorized decision then accepts or rejects that delivery.
After accepted delivery, stop active development until a new request arrives.
A successful CLI exit, a green task badge, or an agent's completion message cannot replace this contract.

## Remote execution

Review four properties separately: remote control, remote execution, shared coordination, and shared files.
An HTTP endpoint can provide control without placing a worker on another host.
An SSH process can run remotely without sharing task authority.
A central task API can coordinate workers without copying their source workspaces.

For a two-host experiment, disconnect one host during delivery and reconnect it later.
Check ordered import, duplicate delivery, stale ownership, question routing, and cleanup.
Verify the file version used by each worker. Do not infer consistency from a shared path string.
The project reports state each candidate's source boundary for these properties.

## Executive visibility

The executive view needs recent results, current work, next work, blockers, and required decisions.
Every summary should link to its task, conversation, attempt, or artifact.
Keep the summary timestamp and evidence version visible.
Show uncertainty when the underlying records disagree.

A terminal grid provides execution detail. A transcript provides conversation history.
A task activity chart provides timing and status.
Wingman needs those views and an understandable account of each agent's responsibilities and progress.
The individual agent timeline must connect the summary to the underlying work.

## Next engineering decisions

1. Select the organization model before selecting a terminal UI.
2. Define project, agent, task, attempt, and decision identifiers.
3. Define delivery, handling, completion, and acceptance states.
4. Prove one product journey from Telegram intake to accepted delivery.
5. Prove restart recovery and two-host behavior for that same journey.
6. Add portfolio summaries after the underlying records can support them.

These steps are proposed Wingman design work. They are not implemented changes to the Wingman application.
