# Retained Orca experiment evidence

## Scope

The older research tested selected orchestration contracts at commit `0e25b0e22bf331fda82e470585df58eeef848d6b`.
It used source-derived exports, retained bundles, and isolated SQLite state.
It did not operate a deployed desktop team.
The current [technical assessment](ASSESSMENT.md) governs the Wingman fit verdict.

## Useful findings

A Run is a durable coordination namespace. A Dispatch identifies one execution attempt.
Mail uses those identities for ownership and routing.
Completion must come from the worker that owns the attempt.
A successful task can unlock dependent work. A failed task cannot satisfy a success dependency.

The main snapshot consumes a normal mailbox check with a mutation receipt.
The older inspected release required explicit acknowledgment.
Do not apply one release's acknowledgment behavior to every release.
Consumption still does not prove that the model understood a message.

Remote workers route control mail to the Run's home coordinator.
This differs from unrestricted remote peer messaging.
Generation checks and receipts limit stale reports and repeated mutations.
They do not guarantee exactly-once effects in external tools.

## Retained records

- [Initial six checks](evidence/orca-assessment.mjs).
- [Initial implementation bundle](evidence/orca-orchestration-audit.mjs).
- [Fifteen communication and lifecycle checks](evidence/orca-communication-tests.mjs).
- [Communication implementation bundle](evidence/orca-communication-audit.mjs).
- [Combined relocation result](evidence/relocated-assessment-tests.log): 21 passes.

These are historical runs. This reorganization did not rerun them.
Inspect imports and runtime requirements before using a retained script.
The source-derived bundles cover selected paths. They are not the full installed application.
