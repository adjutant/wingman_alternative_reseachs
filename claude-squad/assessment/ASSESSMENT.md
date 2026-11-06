# Claude Squad assessment for Wingman

Repository: https://github.com/smtg-ai/claude-squad

Local snapshot: `researchs/claude-squad/repo`  
Inspected commit: `ce1ffb4392b01f38e2c4599c7c84d2a93973b138`  
Assessment date: November 5, 2026  
Review basis: independently re-read implementation and relevant tests; earlier report text was treated as an unverified draft.  
Baseline: [Wingman purpose](../../WINGMAN_PURPOSE.md)

**Fit verdict:** Claude Squad is a useful local execution and review workbench for a human supervising several real coding agents. It does not implement Wingman's standing organization, product-discovery process, shared tracker, agent collaboration rooms, portfolio routing, or distributed execution control plane. Its strongest reusable ideas are isolated Git branches/worktrees, background terminal sessions, direct access to each agent's native interface, and review of each session's cumulative changes. Treating its session list as an agent organization would leave nearly all of Wingman's coordination product to build.

This is an assessment of checked-out source, not a live deployment. No dependencies were installed, services started, agent programs launched, or tests executed. Statements about external coding agents describe the boundary visible in Claude Squad's implementation rather than independently verified capabilities of those programs.

## Product and architecture

The executable is a Go/Cobra application with a Bubble Tea terminal UI. Startup checks that the current directory is a Git repository, resolves a configurable program command, stops an existing automatic-acceptance daemon, and starts the UI. The hidden daemon mode runs a different loop over saved sessions. See [main.go](../repo/main.go), lines 21–77 and 148–164. The `web/` tree is a product landing page: [page.tsx](../repo/web/src/app/page.tsx), lines 1–100, renders installation instructions and a demo. It is not a browser client connected to the session runtime.

The central entity is `session.Instance`: a title, repository path, branch, status, program command, timestamps, dimensions, optional initial prompt, and references to a Git worktree and tmux session. It has no organization ID, role, supervisor, task queue, project record, capability declaration, model configuration, conversation ID, or host. See [instance.go](../repo/session/instance.go), lines 18–69. It is best understood as a durable launcher record for a coding session, not a durable organizational worker.

Creation binds two concrete resources together:

1. A Git worktree on either an existing branch or a new branch derived from the session title.
2. A detached tmux session whose current directory is that worktree and whose launched command is the selected coding program.

[Instance.Start](../repo/session/instance.go), lines 203–284, performs this orchestration. [TmuxSession.Start](../repo/session/tmux/tmux.go), lines 93–157, invokes `tmux new-session -d -s … -c … <program>`, waits briefly for session existence, and opens a PTY connection. The actual reasoning, file operations, tools, model calls, and conversation implementation live in the launched CLI. Claude Squad has no model SDK or agent reasoning loop of its own. The CLI has only interactive launch flags plus reset/debug/version commands. There is no machine-oriented task submission or coordination API in [main.go](../repo/main.go), lines 80–175.

Claude Squad stores state in a user-global JSON file under `~/.claude-squad/`. It does not use a project/team database. [config/state.go](../repo/config/state.go), lines 12–47 and 58–126, defines and writes that state. [session/storage.go](../repo/session/storage.go), lines 10–42 and 56–94, serializes instance metadata, worktree metadata, and cached diff statistics. tmux retains terminal history. The external CLI owns native conversation storage. Each continuity layer has different survival conditions.

The important entity boundaries are:

| Concept | Actual representation and lifetime |
|---|---|
| Agent profile | A `name`/`program` launcher preset, not a role with duties or relationships. |
| Agent instance | A title-keyed local session record and paired process/worktree, not a worker registered in an organization. |
| Task | A human-supplied initial prompt and branch. There is no task object, durable objective or completion event. |
| Conversation | Native CLI state and tmux scrollback; no conversation ID/transcript belongs to Claude Squad's JSON record. |
| Project | A repository path retained by instances, with no separate product/project aggregate. |
| Shared state | One local user-global JSON file and Git repository storage, with no server, message bus or distributed scheduler. |

These distinctions matter for reuse: keeping an instance visible after a restart does not establish that its original objective, conversation or accepted outcome can be reconstructed.

## Feature-by-feature comparison

Verdicts follow the shared [assessment guide](../../generic/assessments/ASSESSMENT_GUIDE.md). “Absent” means no corresponding product mechanism was found in the implementation surfaces described in the verification section. An external CLI can be prompted to do additional work, but that does not make the mechanism part of Claude Squad.

| ID | Wingman capability | Verdict | Implemented behavior, evidence, and concrete gap |
|---|---|---|---|
| F01 | Real independent coding agents and specialist instances | **Similar** | Each instance launches a real separate coding CLI in its own tmux session/worktree. This is concurrent execution, not simulated personas. [instance.go](../repo/session/instance.go), lines 203–284; [tmux.go](../repo/session/tmux/tmux.go), lines 93–157. Specialist responsibilities and multiple instances of a named role are left to human prompts, not managed organizational entities. |
| F02 | Extensible agent profiles, roles and team composition | **Resembles** | Profiles are only `name` and `program` command, and the creation overlay can choose a program. [config.go](../repo/config/config.go), lines 29–86; [app.go](../repo/app/app.go), lines 503–533. No role responsibilities, team membership, hierarchy, or profile-bound knowledge/tools. |
| F03 | Agent directory and visible working relationships | **Resembles** | The list shows sessions with titles, status, branches, repository context, and diff counts. [ui/list.go](../repo/ui/list.go), lines 56–65 and 117–225. There is no supervisor/team relationship model or connected tasks and discussions. |
| F04 | Telegram and Butler-style routing | **Absent** | Intake consists of TUI creation and prompt entry, then PTY keystrokes. [app.go](../repo/app/app.go), lines 483–555 and 610–660; [instance.go](../repo/session/instance.go), lines 631–649. No Telegram transport, representative agent, or reply correlation. |
| F05 | Cross-project registry and existing/new project routing | **Resembles** | Saved sessions retain repository paths and the UI can show multiple repositories. [storage.go](../repo/session/storage.go), lines 10–35; [ui/list.go](../repo/ui/list.go), lines 63–65. New UI sessions use `Path: "."`. There is no project registry or intent-based routing. [app.go](../repo/app/app.go), lines 625–652. |
| F06 | Per-project product and technical leadership | **Absent** | `Instance` has no leadership or team fields, and the app only creates/selects/manages peer sessions. [instance.go](../repo/session/instance.go), lines 31–69; [app.go](../repo/app/app.go), lines 610–817. A human could name sessions ProductMaster and TechMaster, but no responsibilities or handoff behavior follow. |
| F07 | Proportionate research/discovery and iterative clarification | **Absent** | A free-text prompt goes to the chosen CLI; no research stage, uncertainty record, product clarification state, or context-aware question router exists. [app.go](../repo/app/app.go), lines 483–555. Interactive questioning by an underlying agent remains unstructured terminal conversation. |
| F08 | Product scope/specifications/acceptance scenarios/definition of done | **Absent** | Persisted data is session/worktree/diff metadata, not product definition. [storage.go](../repo/session/storage.go), lines 10–42. There is no scope artifact schema or completion rule tied to acceptance scenarios. |
| F09 | Technical decomposition, assignment and shared task tracking | **Resembles** | A human names a session and supplies work as a prompt. This resembles assigning a task but has no ticket ID, assignee record, dependencies, comments, or shared task status. [app.go](../repo/app/app.go), lines 387–555; [instance.go](../repo/session/instance.go), lines 18–54. |
| F10 | Portfolio/project management dashboard | **Absent** | The TUI is a session list plus Preview/Diff/Terminal tabs. [tabbed_window.go](../repo/ui/tabbed_window.go), lines 33–69. It has no projects, milestones, blockers, delivery view, or tracker links; `web/` is marketing content. |
| F11 | Agent chat application, rooms and direct collaboration | **Absent** | Prompt delivery addresses one selected PTY. There is no agent mailbox, room membership, message routing, or shared chat record. [instance.go](../repo/session/instance.go), lines 631–670. Parallel branches isolate work rather than establish collaboration. |
| F12 | Management escalation and human decisions/approvals | **Resembles** | Native agent prompts can be handled through terminal attachment. The UI confirms kill/push actions. [app.go](../repo/app/app.go), lines 677–738 and 779–813. There is no escalation chain, project-scoped question entity, or decision delivery to a responsible leadership agent. |
| F13 | Durable project knowledge and reusable directives | **Resembles** | Git worktrees carry committed repository content, which can include instructions/specifications prepared elsewhere. [worktree_ops.go](../repo/session/git/worktree_ops.go), lines 82–112. Claude Squad does not create/manage a `DIRECTIVES` equivalent, shared knowledge taxonomy, or synchronization of independently updated project records. |
| F14 | Persistent identity, conversation and work continuity | **Similar** | Title, program, branch, path, and status survive in JSON; live tmux sessions can reconnect; code survives on branches. [storage.go](../repo/session/storage.go), lines 10–35 and 75–94; [instance.go](../repo/session/instance.go), lines 110–146 and 509–571. Native conversation identity is neither stored nor explicitly resumed after process loss. |
| F15 | Proactive supervision, periodic wake and blocker follow-up | **Resembles** | A 500ms metadata loop captures output/diffs, and an optional daemon presses Enter on recognized confirmation text. [app.go](../repo/app/app.go), lines 238–260 and 942–982; [daemon.go](../repo/daemon/daemon.go), lines 20–111. No supervisor reasons about progress, detects semantic blockers, follows up, or escalates. |
| F16 | Parallel products and concurrent specialists | **Similar** | Multiple local sessions run concurrently, including records associated with different repositories; UI creation is capped at 10 instances. [app.go](../repo/app/app.go), line 24 and lines 610–652; [ui/list.go](../repo/ui/list.go), lines 63–65. Parallel product teams and workload-driven scaling remain absent. |
| F17 | Real multi-host execution with shared coordination | **Absent** | tmux and Git commands are local subprocesses; instances contain no host/routing field. [tmux.go](../repo/session/tmux/tmux.go), lines 95–102; [instance.go](../repo/session/instance.go), lines 31–69. A custom program could itself run SSH, but Claude Squad would not coordinate remote identities, workspaces, or hosts. |
| F18 | Executive overview of current/recent/next work and blockers | **Resembles** | Titles, activity indicators and diff counts give coarse monitoring. [ui/list.go](../repo/ui/list.go), lines 117–190. Activity is inferred from changed pane text; no accomplishments, next assignments, semantic blocker summaries, or evidence links. |
| F19 | Individual agent summary timeline linked to underlying work | **Absent** | Full tmux scrollback is accessible, but it is raw terminal history rather than meaningful summary entries connected to tickets/tests/discussions. [instance.go](../repo/session/instance.go), lines 652–657. Timestamps in instance storage do not form a timeline. |
| F20 | Detailed per-agent coding workspace drill-down | **Similar** | Select a session to inspect output, cumulative Git diff, attach to the native agent, or open a separate shell in its worktree. [tabbed_window.go](../repo/ui/tabbed_window.go), lines 59–69 and 106–126; [terminal.go](../repo/ui/terminal.go), lines 125–182. This is valuable direct access, but lacks structured tool-call/artifact/test entities and organization links. |
| F21 | Live activity, lifecycle controls, steering and execution visibility | **Similar** | Creation, attachment, direct reprompting, pause/resume, kill, output, diff inspection, and background sessions exist. [app.go](../repo/app/app.go), lines 677–813; [instance.go](../repo/session/instance.go), lines 422–571 and 631–670. No structured budgets, goals, fork/compact/archive API, usage accounting, or durable steering queue; pause is not a reliable execution suspension. |
| F22 | Testing, integrated verification and product acceptance/delivery | **Resembles** | Humans can use the per-worktree shell to run tests and review diffs, then commit/push a branch. [terminal.go](../repo/ui/terminal.go), lines 146–182; [worktree_git.go](../repo/session/git/worktree_git.go), lines 70–126. No TestMaster, integrated acceptance pipeline, test-result record, or definition-of-done gate. Commit helpers use `--no-verify`. |
| F23 | Autonomous operation with human direction through organization | **Resembles** | A launched CLI can work in the background, and automatic confirmation can continue while the TUI is closed. [main.go](../repo/main.go), lines 62–76; [daemon.go](../repo/daemon/daemon.go), lines 20–111. Humans still decompose, assign, coordinate, review, and decide delivery; no autonomous organization exists. |
| F24 | New profiles participate across chat/tracker/dashboards | **Resembles** | Additional program profiles can launch through the same generic session UI. [config.go](../repo/config/config.go), lines 29–86. Chat, tracker and organizational dashboards do not exist, and program-specific prompt recognition is hard-coded rather than extended by profiles. [tmux.go](../repo/session/tmux/tmux.go), lines 244–266. |

## Agent definition and lifecycle in depth

### Definition, identity and creation

A profile is a launch preset, not an agent specification. It does not contain an instruction body, model, tools, permission policy, memory location, duties, or reports-to relationship. A user can place arguments in its program string or rely on repository configuration consumed by the CLI, but Claude Squad neither understands nor enforces them. `GetProgram` resolves the default profile name to its command; `GetProfiles` returns the configured presets with the default first. See [config.go](../repo/config/config.go), lines 29–86.

The user initiates creation with `n` or `N`. Both create an unstarted `Instance` pointed at the current directory. The `N` path gathers a prompt and optionally an existing branch and program; then the app starts resources asynchronously and sends the initial prompt to the CLI. See [app.go](../repo/app/app.go), lines 387–555 and 610–660. This is a human-defined task boundary. There is no autonomous decision to hire a worker, allocate a role, or create a team.

The session title supplies identity to tmux and Git naming. Tmux removes whitespace and replaces dots, while Git branch names use a configured prefix and sanitization; worktree directory names also receive a nanosecond suffix. See [tmux.go](../repo/session/tmux/tmux.go), lines 60–90, and [worktree.go](../repo/session/git/worktree.go), lines 48–107. Distinct titles can sanitize to the same tmux name (for example, `api task` and `apitask`); startup rejects an already existing tmux session rather than allocating a separate stable ID. A running instance cannot be renamed through `SetTitle` ([instance.go](../repo/session/instance.go), lines 403–410). The title is not a globally unique agent ID suitable for distributed routing.

### Execution, permissions and concurrency

Independent tmux sessions execute real CLI programs concurrently. Their Git worktrees reduce simultaneous edits to the same checkout, but they are not OS sandboxes: the code adds no container, resource limits, credential isolation, or tool authorization layer. The external program executes with the local user's environment and permissions through the tmux command shown in [tmux.go](../repo/session/tmux/tmux.go), lines 95–104. A Wingman adapter would have to make that execution policy explicit. Tool availability, filesystem approvals and model credentials belong to that CLI or its environment. The profile schema cannot express a wrapper-enforced capability policy.

The TUI enforces a global creation limit of 10 records, not a workload-aware scheduler. New sessions derive from the current repository; saved records can retain other repository paths. Worktree branches isolate changes, but interface coordination, shared artifact updates, integration order, and merge conflict resolution remain human or external-agent responsibilities. There is no task-dependency scheduler or shared work queue. The recurring timers refresh terminal/Git observations or send recognized confirmation keystrokes. They never wake an agent with a supervision objective or assign new work.

### Observation and steering

The UI periodically captures pane text and computes diffs. A changed SHA-256 hash of output means “Running”; unchanged output without a recognized confirmation means “Ready.” See [tmux.go](../repo/session/tmux/tmux.go), lines 204–266, and [app.go](../repo/app/app.go), lines 238–260. This is a heuristic: a long silent build can appear ready, and changing output is not proof of progress toward a task.

Steering is direct keyboard input. `SendPrompt` writes prompt bytes, waits 100ms, and writes Enter; interactive attachment forwards stdin to the PTY. See [instance.go](../repo/session/instance.go), lines 631–649, and [tmux.go](../repo/session/tmux/tmux.go), lines 269–343. The wrapper has no durable prompt queue or execution-safe interrupt protocol. The underlying CLI determines whether supplied text becomes steering, a new turn, or inappropriate input for its current screen.

The workbench also creates a separate shell tmux session per selected instance in the same worktree. This lets the human investigate files and run commands without entering the agent's conversation. Those shell sessions are cached and recovered by name where possible. They are additional terminals, not extra agents. See [terminal.go](../repo/ui/terminal.go), lines 22–40 and 125–182.

### Continuity and recovery

Saving serializes only started instances. It retains program/path/branch/status/worktree/base commit and diff data, but not the initial `Prompt`, native conversation ID, transcript, task objective, acceptance criteria, or tool history. On reload, `FromInstanceData` reconstructs references and restores the existing tmux session. A surviving tmux session can preserve the running CLI process and its live conversation state; that continuity depends on the external process remaining alive. See [storage.go](../repo/session/storage.go), lines 10–42 and 56–94; [instance.go](../repo/session/instance.go), lines 71–146. `AutoYes` is serialized but omitted from `FromInstanceData`. The TUI/daemon instead re-enable it from their current global mode ([app.go](../repo/app/app.go), lines 142–148; [daemon.go](../repo/daemon/daemon.go), lines 31–34). It is not a reliably restored per-agent permission preference.

If tmux has disappeared, restore returns the explicit `ErrSessionNotFound`. The instance becomes Paused rather than preventing the whole saved list from loading. Resume checks whether the worktree remains valid and preserves it if so, including uncommitted changes left by a dead session; otherwise it reconstructs the worktree. It then reconnects a surviving tmux session or launches the configured program afresh. See [instance.go](../repo/session/instance.go), lines 248–263 and 509–571. There is no explicit `codex resume` or Claude session-ID recovery. Any conversation resurrection after CLI loss depends on configuration/behavior outside this wrapper.

New tmux startup retries existence checks with bounded exponential backoff for about two seconds and attempts cleanup on failure. Startup cleanup is not fully transactional: `Start` defers `Kill`, but `Kill` immediately returns for an instance whose `started` flag is still false ([instance.go](../repo/session/instance.go), lines 236–278 and 287–292). The explicit worktree cleanup on tmux-start failure remains present. The deferred handler should not be treated as a general guarantee that every partial startup is rolled back. This is resource startup recovery, not retry of a failed coding task. Errors are surfaced/logged, but the system does not autonomously reassign a failed task, revise its plan, or diagnose an agent crash.

### Pause, cancellation and retirement are materially different

The implementation's `Pause` is a checkout handoff operation. It checks for dirty files and commits them, detaches the terminal connection, removes the worktree, preserves the branch, and marks the instance Paused. It copies the branch name for the user to check out elsewhere. See [instance.go](../repo/session/instance.go), lines 422–507. Despite the method's introductory comment referring to stopping tmux, its operative path calls `DetachSafely`, not `Close`, `kill-session`, or a process suspension command. The tmux session can remain alive while its worktree is removed. Consequently Wingman must not interpret Paused here as proof that the agent has stopped executing or that it is safe to transfer an active assignment.

Resume likewise may reconnect the same still-running CLI, or create a new CLI after loss. It prevents resuming a branch checked out in the original repository, but does not restore a model conversation through an explicit harness API. Pause/resume is about Git/workspace availability and terminal connections, not a transactionally managed agent state machine.

Kill is the destructive retirement path: it closes the tmux session and cleans up the worktree. Cleanup force-removes the worktree and deletes branches created by Claude Squad; pre-existing branches are preserved. See [instance.go](../repo/session/instance.go), lines 287–311, and [worktree_ops.go](../repo/session/git/worktree_ops.go), lines 115–149. The UI requires confirmation and refuses deletion if the branch is currently checked out in the original repository ([app.go](../repo/app/app.go), lines 677–715). There is no soft archive retaining an organizational history. There are also no wrapper-level fork, compact, budget, or continuing-goal lifecycle controls.

### Background continuation and completion

Quitting saves records but does not kill agent tmux sessions. With automatic acceptance enabled, the app launches a detached daemon on exit; normal startup stops it to avoid simultaneous TUI and daemon management. The daemon loads the saved list, sets `AutoYes`, polls active sessions, recognizes confirmation strings, and presses Enter. See [main.go](../repo/main.go), lines 62–76, and [daemon.go](../repo/daemon/daemon.go), lines 20–111 and 115–158.

Recognition is narrow and program-dependent: exact `claude`, an `aider` prefix, and a `gemini` prefix receive separate strings. A custom profile or full executable path does not necessarily match the same heuristic; Codex has no dedicated prompt recognition here. Separate trust/MCP-dismiss helpers exist, but searches of all Go call sites found no caller of `Instance.CheckAndHandleTrustPrompt`. They are not part of the active startup/daemon path in this revision. See [instance.go](../repo/session/instance.go), lines 344–355, and [tmux.go](../repo/session/tmux/tmux.go), lines 159–183 and 244–266. This is opportunistic keystroke automation, not a protocol-aware permission/decision system or organizational supervisor.

There is no Completed or Accepted status: only Running, Ready, Loading and Paused. A quiescent terminal means Ready, not successful work. The human reviews changes and chooses whether to push a branch, keep working, pause, or delete. Both local-commit and push helpers use `git commit --no-verify`, so the wrapper does not enforce repository hooks as a quality gate. See [worktree_git.go](../repo/session/git/worktree_git.go), lines 70–150. An agent can run tests on its own, but the workbench records no structured verification or accepted product outcome.

## Coordination mechanics and a traced task

Claude Squad's coordination is **human-to-session**, combined with Git-based code isolation. There is no built-in agent-to-agent messaging or ticket coordination. Shared Git object storage/branches are the only structural connection between parallel coding sessions. The human decides which session should handle which task and how outputs fit together.

The following traces the implemented `N` → initial prompt → review → push path using an API-endpoint assignment as an illustrative input. It is a code trace, not a task executed during this assessment:

1. From the API repository, the human uses `N`, enters a title, picks a program/profile and optionally an existing branch, and enters the endpoint prompt. [app.go](../repo/app/app.go), lines 610–639 and 503–533.
2. The app constructs a worktree from HEAD or the selected branch. The branch picker searches local/remote branch names, with best-effort `git fetch --prune` started when entering creation ([worktree_git.go](../repo/session/git/worktree_git.go), lines 15–54; [app.go](../repo/app/app.go), lines 618–640). A fresh task does not inherit dirty edits from the original checkout. [worktree_ops.go](../repo/session/git/worktree_ops.go), lines 24–35 and 82–112.
3. The selected command launches in detached tmux, and the prompt is written through its PTY after the start event. [app.go](../repo/app/app.go), lines 304–336; [instance.go](../repo/session/instance.go), lines 631–649.
4. A second human-created instance can work concurrently on its own branch. No dependency, API contract message, or shared acceptance record is automatically established. The human must convey interface changes to the second agent.
5. The metadata loop samples output and line counts. Selecting a session brings its full diff; other sessions receive cheaper `--numstat` polling. [app.go](../repo/app/app.go), lines 942–982; [diff.go](../repo/session/git/diff.go), lines 25–74.
6. The human attaches to ask questions or steer work, or uses the independent worktree shell to run tests. These interactions are not linked to tickets or an executive summary.
7. The human confirms a push. The helper commits dirty changes, attempts GitHub synchronization, falls back to `git push -u origin <branch>` if needed, syncs again, and optionally opens the branch. [app.go](../repo/app/app.go), lines 716–738; [worktree_git.go](../repo/session/git/worktree_git.go), lines 70–125.
8. Integration, product acceptance and the decision to stop are outside the wrapper. “Push” does not merge the two agents' work, create a product acceptance result, or notify a Butler.

This is a good workflow for a developer directing several bounded coding efforts. It does not transfer the coordination burden to the agents in the way Wingman intends.

### Reliability boundaries affecting coordination

Several source-level details constrain reuse beyond the intended single-user TUI. These are inspection findings, not reproduced runtime failures:

- **Observation writes to the worktree index.** Both full-diff and numstat polling issue `git add -N .` before diffing ([diff.go](../repo/session/git/diff.go), lines 25–74). This includes untracked files in review, but monitoring is not read-only and can contend with an agent's own Git activity. The diff compares against a recorded base rather than only the latest uncommitted changes.
- **The diff baseline can move on resume.** Reconstructing a removed worktree calls `Setup`, which uses the now-existing branch and records its current HEAD as the base ([instance.go](../repo/session/instance.go), lines 526–539; [worktree_ops.go](../repo/session/git/worktree_ops.go), lines 24–79). Changes already committed during Pause can consequently disappear from the new cumulative diff. A Wingman review should retain an immutable assignment baseline separately.
- **Action errors are not consistently returned to the event loop.** `confirmAction` calls `_ = action()` synchronously ([app.go](../repo/app/app.go), lines 1020–1042), discarding the returned error/message from push or kill callbacks. The UI's generic error-message handling does not establish that those action failures become visible. Kill also deletes the saved record before resource cleanup, and `List.Kill` logs cleanup errors while still removing the list item ([app.go](../repo/app/app.go), lines 700–710; [ui/list.go](../repo/ui/list.go), lines 277–304). Recovery should not rely on a durable failure record here.
- **Persistence has a single-writer assumption.** JSON is written directly using `os.WriteFile`, with no atomic replacement or locking in the state layer ([state.go](../repo/config/state.go), lines 89–125). Startup attempts to kill the daemon to separate the viewer and background poller, but that is not coordination for multiple simultaneous TUI instances. `StopDaemon` uses `proc.Kill`, whereas graceful daemon saving handles SIGINT/SIGTERM ([daemon.go](../repo/daemon/daemon.go), lines 74–86 and 129–166). Do not credit startup's stop as a guaranteed graceful state flush.

## Major capabilities beyond Wingman's described organization

**A provider-neutral local CLI workbench.** Wingman specifies Codex agents; Claude Squad can launch arbitrary local commands and offers named program presets. That enables heterogeneous CLI/tool/model experiments through one workbench, without implementing an SDK adapter for every provider. The consequence is that the integration is terminal-level: structured events, permissions, cost accounting and reliable resume are unavailable unless separately implemented. Generic launch support should not be confused with equally capable lifecycle support for every program. The concrete preset and launch boundary is [config.go](../repo/config/config.go), lines 29–81, and [tmux.go](../repo/session/tmux/tmux.go), lines 93–157.

**Branch-isolated parallel implementation with a human review boundary.** Wingman describes detailed workspaces but does not prescribe a per-task Git worktree/branch policy. Claude Squad concretely implements this policy, keeps a base commit for cumulative review, can start from existing branches, and provides local handoff/push operations. This is substantial execution infrastructure worth borrowing. It still requires an integration strategy and a shared-artifact policy: separate branches can diverge on interfaces, specifications and coordination records as readily as source code. The branch/base mechanics are [worktree_ops.go](../repo/session/git/worktree_ops.go), lines 12–112, and review computation is [diff.go](../repo/session/git/diff.go), lines 25–74.

**UI-independent terminal execution with detached auto-confirmation.** The tmux process is independent of the viewing application, and the daemon can maintain limited confirmation handling after UI exit. This gives a local developer a practical background execution model. Wingman could use that separation of viewer and executor, but should replace text heuristics with explicit harness events and task-aware decisions. The daemon does not make the organization autonomous. The implementation boundary is [main.go](../repo/main.go), lines 64–76, and [daemon.go](../repo/daemon/daemon.go), lines 19–87 and 90–126.

These are major execution capabilities, not evidence of another full product such as chat-based or ticket-based coordination. No separate chat/team-management/ticket product was found in this repository.

## Distinctive mechanisms and innovations

The most useful design is the **pairing of one native agent terminal with one isolated code branch**, exposing both output and the resulting delta without taking over the CLI's reasoning loop. This makes the workbench thin and adaptable while giving the human a tangible unit of work to compare. The tradeoff is precisely its shallow semantic understanding: it sees terminal bytes and Git changes, not tasks, decisions or accepted outcomes.

Its **layered continuity** is also instructive. JSON remembers launcher records; Git remembers code; tmux preserves running processes and scrollback. Missing tmux sessions are explicitly downgraded to a recoverable Paused state, and valid worktrees are protected from needless recreation on resume. Those mechanisms are grounded in [instance.go](../repo/session/instance.go), lines 248–263 and 526–568. Wingman should preserve this distinction between a recoverable workspace and a recoverable conversation, rather than representing both with one “agent resumed” flag.

The **bounded monitoring loop** avoids overlapping ticks, performs per-instance I/O in parallel, and loads full diff content only for the selected session. [app.go](../repo/app/app.go), lines 942–982. This is a useful scaling detail for a local session observer, but not a major autonomous-coordination invention. Similarly, prompt recognition through terminal strings is an economical compatibility mechanism with clear fragility, not protocol-level intelligence.

No claim is made that these ideas are historically novel or unique across other products. Their value here is the coherent, inspectable execution workbench they produce. The repository contains no new organizational coordination model comparable to Wingman's Butler/portfolio/product/technical leadership arrangement.

## Practical use for Wingman

Use the worktree/base-commit diff pattern and the separation of background executor from viewer as implementation references. The raw terminal drill-down and adjacent worktree shell are sensible fallbacks when structured Codex views are unavailable. Direct use is most plausible as a human-operated local tool alongside Wingman, rather than as an immediately callable backend: no agent-control API is exposed. The repository declares AGPL-3.0 in [README.md](../repo/README.md), in its License section, and includes [LICENSE.md](../repo/LICENSE.md); that is a concrete distribution/integration consideration for taking its implementation into another product.

Adapt the runtime boundary before making it a Wingman execution backend: introduce stable agent/project/task/host IDs, explicit native conversation handles, task outcome events, robust cancellation, permission policy, and a genuine stopped state. Preserve recoverable code after process loss and model conversation restoration separately. The existing Paused semantics need particular care because detaching and deleting a worktree is not execution suspension. The error propagation, immutable review baseline, index-mutating observation and single-writer persistence issues above also need adaptation before unattended organizational use.

Wingman still needs these organization capabilities:

- Telegram Butler, contextual routing, and a portfolio registry.
- ProductMaster and TechMaster for each project.
- Proportionate discovery, clarification, specifications, and acceptance criteria.
- Assigned tickets, dependencies, and durable agent chat.
- Supervision, escalation, and two-host coordination.
- Executive summaries, timelines, integrated acceptance, and delivery.

Claude Squad's workbench does not implement those product workflows.

## Verification scope and limits

The inspection covered the actual commit, CLI startup, configuration/profile resolution, app creation/steering/control paths, instance serialization/reload, tmux launch/restore/prompt recognition/attachment/kill, worktree creation/cleanup/diffs/commit/push, session list, detailed tabs, adjacent shell, daemon loop and `web/` page. No `AGENTS.md` was found within this checkout. Source files were not modified.

Absence findings were checked against the `Instance`/`InstanceData` models, complete Go package inventory and the likely `app`, `config`, `session`, `daemon`, `ui`, `main` and `web` implementation surfaces. Searches for Telegram, tickets, leaders, schedule/budget/archive/fork/compact, SSH/hosts, messaging and approval-related implementation found terminal/UI mechanisms rather than an organization system. External CLI configuration and arbitrary user-supplied launch commands are outside that conclusion.

Relevant tests were read, not run. Their presence is evidence of the intended regression boundary, not evidence that this checkout passes:

- [session/instance_test.go](../repo/session/instance_test.go), lines 36–76: missing tmux sessions become recoverable Paused instances; surviving sessions restore. These tests use mocked commands/PTYs and do not establish native conversation restoration.
- [session/tmux/tmux_test.go](../repo/session/tmux/tmux_test.go), lines 44–121: naming, launch command construction, missing-session errors and surviving-session attachment.
- [session/git/worktree_ops_test.go](../repo/session/git/worktree_ops_test.go), lines 11–127: Git-backed tests for orphan directory removal and recording the base commit on existing branches.
- [config/config_test.go](../repo/config/config_test.go), lines 205–269: profiles resolve to program commands and preserve default ordering.
- [ui/terminal_test.go](../repo/ui/terminal_test.go), tests beginning at lines 120, 153, 210 and 325: terminal content/fallbacks, caching and instance cleanup. [app/app_test.go](../repo/app/app_test.go), lines 34–107, covers confirmation state transitions rather than delivery correctness.

There was no runtime validation of installed CLI compatibility, terminal rendering, daemon behavior, pause while an agent actively writes, or GitHub push behavior. The assessment distinguishes implementation paths from tested deployment guarantees throughout.

Fresh review also inspected the full profile/state/storage types and searched every non-test Go/TSX source for organization, discovery, chat, tracker, scheduling, distributed-host and lifecycle terms. It separately checked call sites for the trust-prompt helpers rather than inferring live behavior from their existence. No network services or external product documentation were needed to establish this local-snapshot assessment.
