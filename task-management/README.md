# Agent task management source assessments

Status: complete for the recorded static source assessments and report publication.

Open [the comparison](index.html), [the task baseline](purpose.html) or [the full Markdown matrix](REQUIREMENT_MATRIX.md).

The baseline is [AGENT_TASK_MANAGEMENT.md](../AGENT_TASK_MANAGEMENT.md).
It defines the desired shared work system for leaders, agents, subagents, reviewers and the human owner.
The 24 requirements cover project records, work allocation, dependencies, delegation, recovery, verification, inspection and operation.

This study replaces the earlier targeted screening with full source checkouts and per-codebase assessments.
The earlier screening remains at [task coordination](../generic/task-coordination.html), with its original evidence limits.
It does not prove completion of this deeper study.

## Source scope

The [checkout manifest](checkouts.json) covers the retained repositories from the earlier screening, plus the historical Python communication companion. The current study excludes general-purpose planners and applies design, repository activity and GitHub star filters. The [design and implementation review](COMPARISON.md#design-and-implementation-review) records three further exclusions based on defects in their core workflows.
Paperclip and Agent Swarm reuse their preserved local checkouts.
New source worktrees are at `<project>/repo/` under this folder.
They are independent repositories ignored by the research Git repository.
There are no compatibility symlinks or new submodules in the research repository.

The checkout tool materializes the full tracked tree at a recorded commit.
It does not use sparse checkout.
Git LFS payloads and nested submodules are recorded separately when present; a pointer file is not described as its external payload.
The source manifest records clean status, tracked-path counts and hashes, commits and checkout completion state.

## Completed source assessments

All 9 source assessments are complete at this checkpoint.
The [progress record](progress.json) records source coverage and checkout integrity.
The [cross-project findings](COMPARISON.md) synthesize their fit and lifecycle boundaries.
All reports are published in the HTML collection. The matrix contains all 216 recorded verdicts, with links to their explanations.
The [publication check](publication.json), [historical browser evidence](../generic/assessments/_audits/task-management-browser.json) and [historical HTTP evidence](../generic/assessments/_audits/task-management-http.json) record verification of the research presentation.

| Codebase | Assessment | Evidence ledger |
|---|---|---|
| Python Agent Mail | [Source assessment](agent-mail-python/assessment/ASSESSMENT.md) | [Review ledger](agent-mail-python/assessment/review.json) |
| Rust Agent Mail | [Source assessment](agent-mail-rust/assessment/ASSESSMENT.md) | [Review ledger](agent-mail-rust/assessment/review.json) |
| Agent Swarm | [Source assessment](agent-swarm/assessment/ASSESSMENT.md) | [Review ledger](agent-swarm/assessment/review.json) |
| Backlog.md | [Source assessment](backlog-md/assessment/ASSESSMENT.md) | [Review ledger](backlog-md/assessment/review.json) |
| Beads | [Source assessment](beads/assessment/ASSESSMENT.md) | [Review ledger](beads/assessment/review.json) |
| beads_rust | [Source assessment](beads-rust/assessment/ASSESSMENT.md) | [Review ledger](beads-rust/assessment/review.json) |
| beads-viewer | [Source assessment](beads-viewer/assessment/ASSESSMENT.md) | [Review ledger](beads-viewer/assessment/review.json) |
| Paperclip | [Source assessment](paperclip/assessment/ASSESSMENT.md) | [Review ledger](paperclip/assessment/review.json) |
| Vibe Kanban | [Source assessment](vibe-kanban/assessment/ASSESSMENT.md) | [Review ledger](vibe-kanban/assessment/review.json) |

## Assessment method

Read a candidate's applicable source instructions before reviewing it.
Use its README to locate implementation, then follow the executable paths and storage invariants.
Review creation, planning, ready selection, claim, progress, handoff, review, completion, cancellation and recovery.
Inspect alternate mutation paths, background jobs, authentication and relevant client code.
Trace data across process and host boundaries.

Each assessment must include:

1. The immutable source revision and inspected scope.
2. A fit decision for this task-management baseline.
3. Architecture, entry points, domain model and persistence.
4. All 24 requirement verdicts with implementation evidence and boundaries.
5. An end-to-end lifecycle and the paths that can bypass its rules.
6. Concurrency, failure, recovery, permissions and multi-host limits.
7. Human and agent usability, installation and operating costs.
8. Implementation completeness, design quality, test-source coverage and unresolved uncertainty.
9. Adoption gaps and useful components.
10. A source review ledger identifying the files and ranges that support the findings.

Exact, Similar, Resembles, Absent and Unclear describe fit to the baseline.
They are not points in a reliability ranking.
An adapter or companion receives the same requirement review, with clear attribution of behavior supplied by another product.
Restricted licenses remain an adoption constraint; they do not remove a codebase from this technical review.

Candidate applications and test suites are not started as part of this source assessment.
Source and test inspection do not establish runtime usability, race-free operation, performance or product acceptance.
Report-site tests verify the research presentation only.

## Completion

The [completion audit](COMPLETION_AUDIT.md) records source coverage, comparison, publication and verification.
Run `tools/validate_task_management.py --write --require-complete` from the research root for source integrity, and `uv run --script tools/validate_task_publication.py --write` for publication fidelity.
The original 75-project Wingman matrix retains its separate baseline and source-preservation checks.
