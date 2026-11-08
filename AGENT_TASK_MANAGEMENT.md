# Shared task management for an agent organization

## Purpose

The system is the shared working record for a software team whose participants include autonomous agents, temporary subagents, project leaders and a human owner.
It connects product goals to planned work, accountable owners, implementation results and acceptance.
Several projects and several workers can progress at the same time.
The record survives a conversation ending, an agent restarting or a worker moving to another machine.

A person can inspect the same work that agents use to coordinate.
Agents can discover available work, accept responsibility, delegate bounded parts, report progress, ask for decisions and submit results.
The person should not have to relay routine messages between workers or repeatedly reconstruct their status.

The system can be a dedicated service, a repository-backed tracker or a component integrated with an agent runtime.
A browser board is one useful view.
Structured commands and APIs are equally important because agents must operate the underlying records reliably.

## 1. Participants and responsibility

| Participant | Responsibility |
|---|---|
| Human owner | Sets goals and priorities, resolves business decisions and accepts delivered outcomes. |
| Project leader | Maintains scope, organizes the backlog, coordinates contributors, follows blockers and communicates the project's condition. |
| Technical coordinator | Breaks a product outcome into implementable work, identifies dependencies, assigns suitable specialists and coordinates integration. |
| Worker agent | Takes a bounded assignment, reads its context, performs the work and records evidence and remaining issues. |
| Subagent | Performs delegated work with an explicit relationship to its parent assignment and a defined result. |
| Reviewer or tester | Checks a particular result against the agreed criteria and records an actionable decision. |

One person or agent can perform more than one role when the project is small.
The underlying records must still distinguish responsibility, execution and review.
New agent profiles should not require a new hardcoded task type or a separate tracking system.

A durable agent identity is separate from its current process or conversation.
A task is separate from an execution attempt.
A coordinator can remain accountable while several workers make successive attempts at the same task.

## 2. Projects and retained context

Each project has a stable identifier, purpose, scope, priorities and responsible leadership.
The system connects its backlog to specifications, decisions, discussions, source repositories and deliverables.
An incoming request can create a project or continue one whose context already exists.

The project view distinguishes completed outcomes, active work, ready work, future work and blockers.
A portfolio view exposes these distinctions across projects without combining their unrelated instructions or ownership.

Project knowledge belongs in durable records or linked artifacts.
Workers should be able to retrieve the current context without reading an entire historical conversation.
Old decisions remain inspectable, while superseded instructions are clearly identified.

## 3. Work records and decomposition

A task states the expected outcome and the evidence required to finish it.
It records project membership, priority, status, responsibility, dependencies, progress and relevant artifacts.
Stable identifiers allow comments, code changes, tests and agent sessions to refer to the same work.

Large outcomes can contain smaller assignments.
The relationship preserves why a child exists, who coordinates it and what must be true before the parent can finish.
An agent may create follow-up work discovered during implementation.
That work remains linked to the finding and the affected project.

Hierarchy and execution order are different relationships.
A child does not automatically depend on every sibling.
A parent should not close merely because one worker returned a successful response.

## 4. Planning and available work

The backlog supports ordering, grouping and reassessment.
Teams can use continuous flow or time-bounded planning where useful.
Iterations, milestones, estimates and capacity controls should support decisions without forcing unnecessary ceremony on a small task.

Dependencies identify work that cannot safely start yet.
Ready-work selection and direct claims must apply compatible eligibility rules.
The system detects or rejects dependency cycles where it promises a runnable graph.
Changing or cancelling a prerequisite has an explicit effect on dependent work.

The project leader can limit work in progress and see overloaded or idle participants.
A configured limit must state whether it is enforced, advisory or bypassable by an explicit operator action.

## 5. Ownership under concurrency

Independent agents can request the same work at the same time.
The authoritative claim operation must have one winner.
The losing agent receives a clear conflict and chooses other work.
Reading an unassigned task and later writing an assignee is insufficient unless the complete transition is protected.

Ownership can be assigned by a coordinator or acquired by an eligible worker.
These operations must agree about the current owner and the permitted next action.
Ordinary edits, bulk operations and alternate interfaces must not silently bypass the ownership contract.

The system distinguishes long-lived accountability from a temporary execution reservation.
Execution ownership identifies the worker, attempt and relevant session.
Retries should not duplicate assignments, comments, completion events or downstream effects when an operation offers idempotency.

## 6. Delegation and handoff

A parent agent can create independent child assignments and continue coordinating them.
Children can report directly to shared records rather than relying on a live parent process.
Another coordinator can recover the relationship if the original parent disappears.

Handoffs include the outcome achieved, changed artifacts, verification performed, unresolved questions and the next action.
Progress reports distinguish observed results from intentions.
Artifacts should identify the relevant version, branch, commit or output where that matters.

Workers can discuss interfaces, ask for help and notify the responsible participant.
Notifications should lead back to durable task or discussion records.
Polling is acceptable when it is bounded and can recover missed events.
A delivered notification is not proof that its recipient acted on it.

## 7. Blockers and decisions

A blocked task records the obstacle, its owner, what was tried and what would unblock it.
The obstacle may be another task, a technical problem, missing information or a human decision.
These cases should remain distinguishable.

The project leader follows stalled work and coordinates a response.
Workers can escalate a question without declaring the task complete.
A human answer remains associated with the correct project, task and question.
Resuming work uses the answer and the latest project context.

## 8. Failure and recovery

A worker can stop unexpectedly after claiming a task or after producing part of a result.
The system exposes stale work and provides a defined release, expiry or recovery operation.
The replacement worker can read the previous checkpoint and identify which artifacts are usable.

Heartbeat and lease mechanisms must explain renewal, expiry and ownership transfer.
If a stale worker returns after a replacement has started, attempt-sensitive mutations must reject it where the system controls the action.
A lease alone does not guarantee exactly-once execution or prevent an external side effect.

Cancellation, interruption, failure, abandonment and successful completion have distinct consequences.
The system explains how each affects children, dependencies, reservations, review and notifications.
Restarting the service should preserve or explicitly reconcile partially completed transitions.

## 9. Verification and completion

Each assignment has acceptance criteria or an equivalent definition of a satisfactory result.
Completion links implementation evidence, test results and review decisions.
A reviewer can request changes with a clear route back to the responsible worker.

An approval identifies the result it accepts.
Later changes must not silently inherit approval for an older result.
Task completion, code integration, project delivery and human acceptance are distinct events when the workflow requires them.

The system should support a lightweight process for small work and stronger gates for consequential changes.
Prompts that tell an agent to run tests are useful instructions.
They are not equivalent to an enforced transition rule or a verified test result.

## 10. Human inspection and control

The human can inspect projects, the backlog, current owners, active attempts, recent progress and required decisions.
Connected views link an overview to task detail, discussion, artifacts and execution evidence.
The interface should make stale status and uncertainty visible.

Common operations should be practical through a browser or terminal.
Readable labels, useful search, filtering, keyboard access and small-screen behavior support inspection.
An interface that only starts coding sessions does not by itself explain project progress or responsibility.

The human can change priorities, stop work, release an abandoned assignment and correct a mistaken state.
Privileged overrides are explicit and recorded.

## 11. Machines, access and operation

Workers on the Mac and Linux host can coordinate through the same authority.
If the system uses replicated local stores, it must explain conflict resolution and the limits of offline ownership.
Synchronization after the fact must not be presented as exclusive assignment across disconnected replicas.

Agents receive the access needed for their role and project.
The system distinguishes an actor label from authenticated identity.
Credentials, project isolation and permission checks must remain consistent across browser, CLI, API, MCP, background jobs and bulk operations.

The system can be installed, configured, backed up, restored and upgraded with understandable procedures.
Its dependencies and required external services are explicit.
Small deployments should not require disproportionate maintenance.
Larger deployments need bounded queries, predictable contention behavior and a documented availability model.

Data export and integration paths reduce dependence on one interface or runtime.
Licenses and paid-edition boundaries are assessed separately from technical fit.
Accessible source does not automatically establish unrestricted open-source adoption rights.

## 12. Assessment requirements

These requirements define the common comparison.
An assessment explains the actual mechanism and its boundary for every requirement.
They are not a numerical product score.

| ID | Requirement |
|---|---|
| T01 | Project registry and separation of concurrent projects |
| T02 | Durable task model with stable identifiers and outcomes |
| T03 | Hierarchy, decomposition and linked follow-up work |
| T04 | Dependencies, readiness and cycle handling |
| T05 | Agent identity separate from sessions and execution attempts |
| T06 | Structured agent interfaces through CLI, API or MCP |
| T07 | Atomic ownership and consistent claim authority |
| T08 | Capacity, work-in-progress limits and dispatch policy |
| T09 | Delegation, parallel children and parent completion |
| T10 | Project context, artifacts and versioned references |
| T11 | Durable progress, results and actionable handoffs |
| T12 | Communication, notifications and missed-event recovery |
| T13 | Blockers, questions and management or human escalation |
| T14 | Heartbeats, expiring ownership and stale-work discovery |
| T15 | Stale-attempt rejection and idempotent transitions |
| T16 | Resume, cancellation, failure and service recovery |
| T17 | Shared authority and coordination across execution hosts |
| T18 | Audit history and attribution of changes |
| T19 | Human overview, task detail, search and navigation |
| T20 | Backlog planning, milestones and optional iteration workflows |
| T21 | Acceptance criteria, review and controlled completion |
| T22 | Authentication, permissions, project isolation and overrides |
| T23 | Extensible roles, workflows, schemas and integrations |
| T24 | Installation, maintenance, portability and operating usability |

## 13. Assessment method and evidence

Assess a full local source checkout at an immutable commit.
Read the entry points, domain model, storage, mutation paths, clients, background work and relevant tests.
Trace an assignment from creation through selection, claim, execution, progress, review and termination.
Follow alternate paths that can change the same state.

Each report covers architectural coherence, feature completeness, implementation depth, operating costs and human and agent usability.
It identifies useful components, adoption gaps and concrete failure conditions.
For an absent mechanism, state which relevant interfaces and persistence paths were inspected.
Do not infer absence from a missing README section or one unsuccessful text search.

Use Exact, Similar, Resembles, Absent and Unclear with an explanation of the boundary.
Distinguish native enforced behavior, configurable policy, conventions, adapters and proposed additions.
Separate implementation evidence, test-source evidence, executed tests and observed product behavior.
Preserve full commits, local source links and line references.

Static review can establish code paths and expose defects.
It cannot establish successful installation, race-free production operation, performance, accessibility or product acceptance by itself.
Runtime tests, when performed, must state their commands, environment, scope and outcomes.

## 14. Reference work journey

1. A leader creates or selects the project and records the intended outcome.
2. The coordinator creates bounded assignments with acceptance criteria and dependency relationships.
3. Eligible workers claim independent ready tasks through the shared authority.
4. A worker delegates a child assignment while retaining a durable relationship to its parent.
5. Workers record checkpoints, discuss integration and raise blockers in the correct context.
6. A leader or the human resolves a decision and the affected work resumes.
7. A failed worker is recovered without giving its stale attempt authority over the replacement.
8. A worker submits a particular result for review and addresses requested changes.
9. Required children and acceptance evidence permit the parent outcome to finish.
10. Project delivery is presented for human acceptance, with the history retained for later changes.
