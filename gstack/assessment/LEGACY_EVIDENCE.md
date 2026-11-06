# Retained gstack experiment evidence

## Scope

The older research used commit `f8085aa0e499085c411f712d6d5c00a81d1b104a`.
It tested selected local mechanics without paid model calls.
The current [technical assessment](ASSESSMENT.md) governs the Wingman fit verdict.

## Recorded results

| Run | Result | Interpretation |
|---|---|---|
| Initial nine-file run | 185 cases: 180 passes and five failures. | Preserve the failures as part of the record. |
| Canonical-path two-file rerun | 84 passes and zero failures. | The selected cases overlap the first run. Do not add them as distinct coverage. |

The selected areas included plan admission, recovery, checkpoints, gate artifacts, review lifecycle, and verdict classification.
They also included Captain briefs, merge locks, and train verification.
The rerun corrected the path context for affected cases.
It did not establish a complete release acceptance result.

## Useful process findings

Office-hours and specification procedures provide explicit discovery guidance.
The host model must still apply that guidance to the actual domain.
Captain assigns implementation lanes and records readiness evidence.
The host supplies much of the thread, machine, message, and scheduling behavior.
Procedure artifacts and runtime guarantees must remain separate in the assessment.

## Retained records

- [Initial test log](evidence/gstack-assessment-tests.log).
- [Canonical-path rerun log](evidence/gstack-assessment-canonical-path-tests.log).

This reorganization did not rerun these tests.
No complete free acceptance suite, paid evaluation, live browser workflow, or remote-host deployment is established by these logs.
