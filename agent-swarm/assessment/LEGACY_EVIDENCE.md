# Retained Agent Swarm experiment evidence

## Scope

The older research used commit `6aff700f53755cb71bd6a1aa2e2fa1da9586b892`.
The selected upstream run recorded 363 passes across 14 files.
Five additional probes used in-memory state without model calls.
The current [technical assessment](ASSESSMENT.md) governs the Wingman fit verdict.

## Useful probe findings

| Probe | Recorded result | Engineering consequence |
|---|---|---|
| Read three unread messages with limit one | The read returned the newest message. The remaining unread count became zero. | A cursor can mark omitted messages as read. Retained storage does not ensure later unread retrieval. |
| Reply after the parent message was read | The reply stored no mentions. Normal unread mention retrieval found none. | Inherited notification intent needs an explicit persisted target. |
| Request live steering | The API reported `steered`. The database row remained `pending`. | Admission is not confirmed delivery or handling. |
| Complete work with unaccepted steering | A delivered row remained `delivered`. | Terminal completion does not acknowledge every instruction. |
| Create a channel through the tool | The success result contained an empty channel object. | A missing `await` returned a Promise-shaped value. |

These results concern specific paths at the pinned commit.
They do not prove that all discussion or steering paths fail.
Stored messages can still exist after an unread cursor advances.

## Retained records

- [Selected upstream test log](evidence/agent-swarm-assessment-tests.log).
- [Original probe script](evidence/agent-swarm-communication-probe.ts).
- [Original probe results](evidence/agent-swarm-communication-probe.log).
- [Relocated probe script](evidence/agent-swarm-communication-probe.relocated.ts).
- [Relocated probe results](evidence/relocated-probe.log).
- [Preflight refusal](evidence/relocated-probe-preflight.log).

The preflight refusal required an explicit encryption key for an in-memory database.
The later run used a temporary test key.
Both probe scripts now import from `agent-swarm/repo/` through paths relative to their own files.
Stack traces use canonical repository-relative source locations.
These are path-normalized historical records, not new runs.
The [portability audit](../../generic/assessments/PORTABILITY_AUDIT.md) records original and current hashes.
