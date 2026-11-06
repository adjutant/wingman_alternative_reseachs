# Retained CAR research findings

## Scope

The older research used commit `3bedfe817e6fc70eb16650f216eca93cd37fa411`.
Its narrative reports 237 focused passes in groups of 102, 99, 20, and 16.
No separate raw test log was retained.
Treat that count as a historical narrative claim.
The current [technical assessment](ASSESSMENT.md) governs the Wingman fit verdict.

## Findings that remain useful

CAR has two separate execution models.
An ordered ticket flow selects unfinished work and evaluates its outcome.
A managed thread retains a conversation binding and execution records.
PMA can direct several managed threads independently.
Do not describe the whole product as one serial ticket loop.

The message contract has queue, reject, and interrupt policies.
Queue admits later work. Reject refuses work while the target is busy.
Interrupt stops the current execution before it prepares another execution.
This path does not establish native in-flight `turn/steer` behavior.

A done ticket can encounter a commit barrier when the working tree remains dirty.
Persisted retry and pause state supports recovery.
A stale-worker cleanup observation cannot replace the user's requested lifecycle state.
Completion delivery and autonomous PMA follow-up also have separate conditions.

## Source evidence

- [Runner invariants](../repo/tests/tickets/test_runner_invariants.py).
- [Runner state transitions](../repo/tests/tickets/test_runner_state_transitions.py).
- [Ticket recovery](../repo/tests/core/test_ticket_flow_recovery.py).
- [Managed thread store](../repo/tests/test_managed_thread_store.py).
- [Managed delivery recovery](../repo/tests/core/orchestration/test_managed_thread_delivery_recovery.py).
- [Flow supervisor tests](../repo/tests/core/flows/test_flow_supervisor.py).

These source files explain the asserted contracts.
Their presence does not prove a new test run or the historical total.
The reorganization did not execute them.
