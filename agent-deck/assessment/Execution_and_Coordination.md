# Agent Deck: execution and coordination details

Supporting chapter for [the assessment](ASSESSMENT.md), at commit `2e897f2a62f6dd570628d2021a0994a3a7db1f4f`. Paths below refer to the same read-only source snapshot. Findings are static source analysis, not a runtime exercise.

## Request path: Telegram to a worker and back

### 1. Channel authentication and coordinator selection

The Python bridge builds an aiogram dispatcher only if Telegram is configured and the library is available. It permits one configured Telegram user ID. Private messages are addressed to the bot automatically; group messages require a reply to the bot or an explicit mention. The generic text handler discovers conductor names, parses a prefix, chooses the matching conductor or default, applies an optional pre-message hook and ensures the target conductor is running.

Evidence: [conductor_bridge.py](../repo/internal/session/conductor_bridge.py), lines 2642–2708 and 2848–2907.

This is a usable Butler transport. It is **not** product-aware intake: the bridge does not look up a product registry, infer that “continue yesterday's CRM” belongs to an existing project, or create an organization hierarchy. Those decisions are made by whichever conductor receives the text. The prefix/default rule also does not preserve an explicit pending-question-to-project mapping on its own.

### 2. Input serialization and response correlation

`send_to_conductor` uses the CLI rather than direct arbitrary terminal injection from Python. Blocking sends use structured `session send --wait --json` output to correlate a submitted turn with its response. A timeout after an accepted turn can return a receipt. A pending-reply watcher observes that accepted work instead of immediately resubmitting. An in-memory ownership map serializes concurrent remote requests for the same `(profile, session)`.

Evidence: [conductor_bridge.py](../repo/internal/session/conductor_bridge.py), lines 1102–1238 and 1508–1597.

This avoids a common conversational orchestration defect: reading whichever output happens to be latest and returning it to the wrong human request. The code still has harness-dependent exactness; comments distinguish exact receipts from legacy receipt-less tools.

Human channel sends use `--ignore-budget`: configured automated-dispatch budgets do not prevent a person from steering the organization. That is a deliberate control policy. It must not be interpreted as a hard total-spend ceiling.

### 3. Busy messages and durability boundary

If the conductor is running/starting, the bridge enqueues the message. Its `_message_queue` is explicitly in memory and capped at 20 entries per session; overflow drops the oldest item and attempts to notify its callback. A drain task later sends retained input and calls the stored reply callback. This queue is distinct from the filesystem-backed generic sendqueue and from durable worker inboxes.

Evidence: [conductor_bridge.py](../repo/internal/session/conductor_bridge.py), lines 1120–1151 and 1245–1293. The main Telegram handler checks busy state and captures the callback/chat routing at lines 2912–2935.

For Wingman, losing an important product clarification while a bridge process restarts is different from losing a cosmetic notification. Persist original inbound Telegram message ID, project/question correlation and delivery state if the product requires durable intake. The existing receipt discipline is useful, but it does not make the in-memory queue durable.

### 4. Conductor judgment and worker launch

Current generated conductor instructions separate shared infrastructure knowledge, per-conductor identity, policy, state and learnings. The conductor is told how to inspect sessions, launch a new child, send instructions, handle approvals, drain the inbox and report urgent/info outcomes. These instructions run in Claude, Codex, Hermes or Pi. The coordinator is a real persistent harness conversation.

Evidence: [conductor_templates.go](../repo/internal/session/conductor_templates.go), lines 243–325, 343–407 and 529–560; [conductor.go](../repo/internal/session/conductor.go), lines 38–74.

`launch` resolves the project path/group/parent, prepares optional worktrees and tool configuration, registers the session, assigns metadata/annotations, starts it and delivers the initial prompt. `--assert-done` appends an instruction to emit an explicit completion sentinel. The worker is not a nested persona in the conductor's response. It becomes an independent managed session and external process.

Evidence: [launch_cmd.go](../repo/cmd/agent-deck/launch_cmd.go), lines 18–65, 499–575, 771–789 and 869–959.

What is missing is an authoritative task transaction connecting this launch to a product ticket, dependencies, specification version and acceptance criteria. A ticket annotation is a string hint, not a ticket record. A conductor can use an external tracker through tools, but that is integration work.

### 5. Execution evidence and activity status

`Instance.Start` serializes same-instance spawns, validates account selection, refuses to start over an owned old process tree, builds the correct fresh/resume/fork command, applies tool loadouts, wraps location and starts tmux. It records process ownership at spawn and watches fast death so startup failures do not become silent empty rows.

Evidence: [instance.go](../repo/internal/session/instance.go), lines 1487–1546 and 1686–1755.

Status is not simply “process exists.” Hook records, live pane classification and native transcript facts contribute. Foreground Stop can coexist with background workflows/subagents/shells. [background_work.go](../repo/internal/session/background_work.go), lines 15–74 and 428–506, defines the merge boundary. Finite work can retain running state. Completed transcript evidence can veto stale pane rows. Shell holds default to three minutes, so a dev server does not keep an agent busy indefinitely. The configured zero-hold compatibility mode allows the shell counter alone to retain running state (lines 82–110 and 434–441), so this protection is configurable rather than universal.

This is operationally important for Wingman. ProjectMaster must not restart a worker whose foreground prompt is idle while useful work continues. Conversely, a green running light is still not proof that a product task is progressing.

### 6. Child completion to durable parent inbox

The transition daemon loads the profile, refreshes status, observes native turn boundaries and persists communication. It records completed turns even when a fast transition was not seen as a prior running sample. Inboxes route results to the assigned parent or tagged sender; eligible parentless results are retained in a drainable unowned ledger. Deliberately suppressed notifications and results for a removed child remain terminal drops, so retention is not universal.

Evidence: [transition_daemon.go](../repo/internal/session/transition_daemon.go), lines 521–555 and 672–755; [inbox_outbox.go](../repo/internal/session/inbox_outbox.go), lines 611–750 and 830–894.

The important inbox contract is **at-least-once delivery with deduplication**. A drain stages records in a durable in-flight WAL before removing the inbox; consumed-turn fingerprints are persisted before the staged WAL is dropped. A crash can redeliver rather than lose a completion. The old raw read/truncate path remains at-most-once and is explicitly distinguished from the guaranteed drain path.

Evidence: [inbox.go](../repo/internal/session/inbox.go), lines 17–35 and 73–111. The controlled crash regression is [issue1225_durability_test.go](../repo/internal/session/issue1225_durability_test.go), lines 22–69, read but not run.

“Deduplicated delivery” should not be inflated into exactly-once business effects. If a model receives a completion and starts a deployment before recording its own state, the inbox cannot by itself make that downstream action transactional. Wingman still needs idempotent task transitions and durable decision records.

### 7. How a manager receives the result

Claude-compatible prompt/Stop hooks can inject pending records at safe turn boundaries. Heartbeat/manual drain is the fallback for other conductor harnesses. The current communication-ledger delivery canary applies only to enrolled Claude parents: Codex children can produce text records, but Codex parents remain on inbox delivery because the required prompt hook is not installed in this phase.

Evidence: [comms_deliver.go](../repo/internal/session/comms_deliver.go), lines 18–34, 79–98. The generated instructions describe the fallback in [conductor_templates.go](../repo/internal/session/conductor_templates.go), lines 303–325.

This matters directly to a Codex-only Wingman. Do not infer Claude injection/Stop-block behavior from a generic “supports Codex” statement. The Codex path can still supervise through explicit drains and heartbeats, but its latency and interruption behavior need their own integration test.

### 8. Escalation and human delivery

Records have urgent/info/noise tiers. A real completion sentinel, error or explicit question can wake the manager. Routine progress can wait for a digest. Conductor output outside a heartbeat is not automatically a human notification; current templates tell the conductor to use `conductor notify --tier urgent|info` when appropriate. Heartbeat `NEED:`/urgent lines and direct replies have channel delivery paths.

Evidence: [conductor_templates.go](../repo/internal/session/conductor_templates.go), lines 165–170 and 319–323; [record.go](../repo/internal/comms/record.go), lines 25–55, 95–129.

The mechanism is meaningful escalation infrastructure. It does not encode Room2→Room1→Butler membership or persist a business decision with its alternatives, owning project and acceptance consequences. Those semantics remain model policy and external records.

## Durable transport is not a permanent conversation archive

The ledger clips text to 600 bytes by default and never exceeds 2,048 bytes per capped field; ingestion applies the cap to both turn text and completion summaries. Evidence: [record.go](../repo/internal/comms/record.go), lines 62–67 and 205–225; [comms_ingest.go](../repo/internal/session/comms_ingest.go), lines 301–305. The ledger defaults to 90-day retention, 1,024 sealed segments and a 2 GiB per-profile quota. Unacknowledged segments are protected for recently active consumers; quota exhaustion refuses commits, leaving bounded spool/overload handling rather than silently erasing records. Evidence: [ledger.go](../repo/internal/comms/ledger.go), lines 21–36 and 211–215. Consumers inactive longer than the retention window lose compaction protection. A returning reader receives an explicit gap if history was compacted. Evidence: [consumer.go](../repo/internal/comms/consumer.go), lines 43–47 and 433–446.

Wingman needs a separate long-term room/project archive and links to full source content. Durable message delivery does not establish complete permanent discussion history, and gap/quota events need visible handling in the organization.

## Actual multi-host execution and coordination

There are two important remote paths. A local session can run its command through SSH in a remote working directory. Separately, configured remotes can run their own Agent Deck registry/runtime while the local TUI communicates with `agent-deck remote-agent` through one persistent SSH JSON-line channel. The remote pushes changes; requests are correlated by ID, and a dropped/unsupported channel falls back to individual SSH command execution.

Evidence: [instance_sandbox_ssh.go](../repo/internal/session/instance_sandbox_ssh.go), lines 89–123; [remote_channel.go](../repo/internal/session/remote_channel.go), lines 22–79 and 102–157.

Remote child records can cross back to a local parent. The communication cursor includes store/epoch/position; fetched records are spooled durably before advancing the position, then imported idempotently. Stable store identity rather than a mutable host alias namespaces duplicates. This is actual shared coordination over hosts, not a remote terminal merely displayed next to local sessions.

Evidence: [comms_remote.go](../repo/internal/session/comms_remote.go), lines 19–38, 47–65, 81–160, 225–245 and 271–317; [record.go](../repo/internal/comms/record.go), lines 80–94 and 131–142.

Limits for Wingman:

- No product workspace replication or automatic host scheduler is established by this transport.
- Each host must have the necessary binary/harness, authentication, repository files and runtime processes.
- Remote transport/profile/version compatibility affects features. A fallback SSH call is not identical to a healthy persistent channel.
- Parent result delivery is useful, but shared multi-party rooms and product tracker transactions remain absent.

## Executive visibility: useful and narrower than Wingman

The web Command Center synthesizes a snapshot from the live menu, optional conductor `status.json` headlines and annotation hints. Conductor rows are grouped by the convention that a conductor name matches the managed group. Fleet summaries can come from a `summary` annotation or a conductor's `note`. Child rows expose current prompt, headline, status hint and ticket string. This is meaningful human-readable context beyond a terminal grid.

Evidence: [handlers_command_center.go](../repo/internal/web/handlers_command_center.go), lines 46–145, 303–357 and 402–458.

Three product-significant limits are visible in the code:

1. **Error/stopped children are excluded** from this panel. Wingman explicitly wants blockers and agents needing attention, so errors should become a first-class executive concern rather than disappear here.
2. **Recent completion is a status diff**, running→waiting/idle since the previous snapshot. It is transient and does not prove an assignment was completed or accepted. There is no persistent per-agent accomplishment timeline generated by this field.
3. **Decisions are maintainer-specific**: the parser reads `conductor/agent-deck/OPEN-ITEMS.md`, section D, and routes items to `conductor-agent-deck`. It is not a general product decision registry.

Evidence: [handlers_command_center.go](../repo/internal/web/handlers_command_center.go), lines 360–384, 432–445 and 537–584. [handlers_command_center_test.go](../repo/internal/web/handlers_command_center_test.go), lines 41–136, explicitly tests these semantics.

Wingman can retain the web workbench's session drill-down and the panel's input controls while replacing the summary model with stable agent/project/task identities, current/recent/next/blocker fields, evidence-linked timeline entries and a generic decision source.

## Completion signals versus accepted delivery

The code deliberately introduces a sentinel because a normal Stop hook only ends a turn. The sentinel is still the worker's claim. A test runner, integrated acceptance evaluator or human acceptance record is not consulted by the parser. It should trigger a review/verification step, not directly close the product.

Evidence: [done_sentinel.go](../repo/internal/session/done_sentinel.go), lines 5–25 and 56–68.

Similarly, fleet recovery verifies boot rather than accepting that a restart returned successfully, and cross-harness handoff verifies native target identity while keeping semantic acceptance pending. Evidence: [fleet/verify.go](../repo/internal/fleet/verify.go), lines 10–26 and 63–108; [cross_harness_switch.go](../repo/internal/session/cross_harness_switch.go), lines 472–489. These are useful distinctions to preserve in Wingman's own model: **transport delivered**, **agent executing**, **worker asserted done**, **tests verified**, and **product accepted** are separate facts.
