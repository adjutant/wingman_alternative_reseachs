# Agent task management source assessments

Status: in progress.

The baseline is [AGENT_TASK_MANAGEMENT.md](../AGENT_TASK_MANAGEMENT.md).
It defines the desired shared work system for leaders, agents, subagents, reviewers and the human owner.
The 24 requirements cover project records, work allocation, dependencies, delegation, recovery, verification, inspection and operation.

This study replaces the earlier targeted screening with full source checkouts and per-codebase assessments.
The earlier screening remains at [task coordination](../generic/task-coordination.html), with its original evidence limits.
It does not prove completion of this deeper study.

## Source scope

The [checkout manifest](checkouts.json) covers all repositories in the previous study, GitLab, the historical Python communication companion and the Taiga frontend.
Paperclip and Agent Swarm reuse their preserved local checkouts.
New source worktrees are at `<project>/repo/` under this folder.
They are independent repositories ignored by the research Git repository.
There are no compatibility symlinks or new submodules in the research repository.

The checkout tool materializes the full tracked tree at a recorded commit.
It does not use sparse checkout.
Git LFS payloads and nested submodules are recorded separately when present; a pointer file is not described as its external payload.
The source manifest records clean status, tracked-path counts and hashes, commits and checkout completion state.

## Completed source assessments

Seventeen of 25 assessments are complete at this checkpoint.
The [progress record](progress.json) lists all pending codebases.
HTML publication and the cross-project comparison remain pending.

| Codebase | Assessment | Evidence ledger |
|---|---|---|
| Agent HQ | [Source assessment](agent-hq/assessment/ASSESSMENT.md) | [Review ledger](agent-hq/assessment/review.json) |
| agent-kanban-rs | [Source assessment](agent-kanban-rs/assessment/ASSESSMENT.md) | [Review ledger](agent-kanban-rs/assessment/review.json) |
| Python Agent Mail | [Source assessment](agent-mail-python/assessment/ASSESSMENT.md) | [Review ledger](agent-mail-python/assessment/review.json) |
| Rust Agent Mail | [Source assessment](agent-mail-rust/assessment/ASSESSMENT.md) | [Review ledger](agent-mail-rust/assessment/review.json) |
| Backlog.md | [Source assessment](backlog-md/assessment/ASSESSMENT.md) | [Review ledger](backlog-md/assessment/review.json) |
| Beads | [Source assessment](beads/assessment/ASSESSMENT.md) | [Review ledger](beads/assessment/review.json) |
| beads_rust | [Source assessment](beads-rust/assessment/ASSESSMENT.md) | [Review ledger](beads-rust/assessment/review.json) |
| beads-viewer | [Source assessment](beads-viewer/assessment/ASSESSMENT.md) | [Review ledger](beads-viewer/assessment/review.json) |
| DevBoard | [Source assessment](devboard/assessment/ASSESSMENT.md) | [Review ledger](devboard/assessment/review.json) |
| Gemba | [Source assessment](gemba/assessment/ASSESSMENT.md) | [Review ledger](gemba/assessment/review.json) |
| Kanboard | [Source assessment](kanboard/assessment/ASSESSMENT.md) | [Review ledger](kanboard/assessment/review.json) |
| Muster | [Source assessment](muster/assessment/ASSESSMENT.md) | [Review ledger](muster/assessment/review.json) |
| Plane MCP adapter | [Source assessment](plane-mcp/assessment/ASSESSMENT.md) | [Review ledger](plane-mcp/assessment/review.json) |
| Planka | [Source assessment](planka/assessment/ASSESSMENT.md) | [Review ledger](planka/assessment/review.json) |
| Rhizome MCP | [Source assessment](rhizome-mcp/assessment/ASSESSMENT.md) | [Review ledger](rhizome-mcp/assessment/review.json) |
| Vibe Kanban | [Source assessment](vibe-kanban/assessment/ASSESSMENT.md) | [Review ledger](vibe-kanban/assessment/review.json) |
| Vikunja | [Source assessment](vikunja/assessment/ASSESSMENT.md) | [Review ledger](vikunja/assessment/review.json) |

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

The study remains in progress until every checkout is verified, every required assessment is complete, cross-project findings and reports are published, and a requirement-by-requirement completion audit passes.
The original 75-project Wingman matrix retains its separate baseline and source-preservation checks.
