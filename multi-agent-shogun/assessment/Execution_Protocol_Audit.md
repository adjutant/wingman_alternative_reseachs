# multi-agent-shogun: execution and protocol audit

This chapter supports the [main assessment](ASSESSMENT.md). It concerns checkout commit `aff8dc8495da26a2aad582257457655fa953b57e`, inspected November 5, 2026. Findings below come from reading source and test fixtures. No live CLI, watcher, Android app, dependency installation or source test execution was involved.

## Creation is a shell process plus durable files

The execution path is more specific than “agents configured in YAML.” [The launcher](../repo/shutsujin_departure.sh), lines 335–454, first removes the named old tmux sessions. It preserves coordination queues by default and resets them only under `--clean`. It then creates the Shogun session, constructs the subordinate terminal grid and stamps `@agent_id`, `@model_name` and `@current_task` before launching each CLI (lines 552–672, 700–800). Its watchers are separate background processes (lines 892–939). A worker is therefore an actual independently running process, while an assignment is a record read by that process.

```text
config/settings.yaml
   ├── agent IDs/models ──> launcher ──> named tmux panes ──> interactive coding CLIs
   ├── model tiers ──────> CLI adapter helpers <─────────── Karo's reasoning
   └── ntfy topic ───────> input listener

role + common + CLI instruction parts ──> generated instruction text

command/task/report YAML <──────────────> agent reads/edits shared files
inbox YAML ──> watcher ──> inboxN terminal nudge ──> agent reads actual message
dashboard.md <────────────────────────── Karo/Gunshi summary
```

Native coding tools, shell execution, provider credentials and transcript persistence belong to the selected CLI. Shogun's shell scripts do not implement a provider conversation engine or a server-side agent actor. Replacing a CLI preserves a slot ID and assignment records. It does not migrate its provider conversation. [switch_cli.sh](../repo/scripts/switch_cli.sh), lines 322–396, sends an exit sequence and detects shell output before relaunching. It proceeds after a shell-detection timeout, so switching is best understood as operational process replacement with recovery, not a proven seamless handoff.

## Formation extensibility has three different boundaries

[agent_registry.sh](../repo/lib/agent_registry.sh), lines 25–125, parses ordered `cli.agents` entries. It treats them as a full formation only if Karo is present, otherwise retaining the historical ten-agent set for backward-compatible partial overrides. It maps subordinate IDs to panes by list position. That makes the supervisor configurable, but does not create agent processes itself.

[cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 1445–1467, separately extracts IDs whose names start with `ashigaru`. The launcher reads that list and count (lines 65–71), labels panes with the listed IDs (lines 621–632), but launches workers and watchers with `ashigaru${i}` for `i=1..count` (lines 750–783, 924–928). Sparse IDs such as `ashigaru2` and `ashigaru5` therefore cannot be assumed to retain a consistent identity across these paths. More than seven workers also encounter the fixed nine-pane subordinate grid (lines 602–619) and Gunshi's offset `count+1` (line 787). Fewer workers leave extra panes; arbitrary additional role names are not incorporated into the launch arrays.

The third boundary is role definition. [get_instruction_file](../repo/lib/cli_adapter.sh), lines 347–373, recognizes Shogun, Karo, Gunshi and `ashigaru*`; other IDs return failure. [build_instructions.sh](../repo/scripts/build_instructions.sh), lines 122–161, explicitly enumerates those four roles for each CLI. A new `ProductMaster` profile consequently needs coordinated changes to instruction generation, role dispatch, launch, permissions, report routing and archival treatment. A new inbox filename alone is not a new fully managed agent profile.

This is why F02/F24 are partial matches. The useful abstraction is a configurable fleet of known roles. The desired Wingman abstraction is an extensible directory of profiles and project-scoped instances whose tools, tracker and dashboards grow together.

## Model routing is executable assistance to management

[cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 649–883, reads configured Bloom capability ceilings, cost groups and preferred models, filters candidates and recommends a model. Unconfigured capability defaults to level 6. This maximizes compatibility but does not validate competence. [find_agent_for_model](../repo/lib/cli_adapter.sh), lines 1291–1442, searches matching workers, then any idle worker, and returns `QUEUE` when none is available. It returns an ID, not a task lease or a launched agent. Missing panes can still return configured candidates, a convenience explicitly described for test environments in lines 1372–1375 and 1424–1427.

The command to switch a worker remains an instruction-driven Karo decision. That is a meaningful division of responsibility, but it also limits claims that routing is a self-contained automatic scheduler. [The original Karo instructions](../repo/instructions/karo.md), lines 55–106, prescribe Bloom labeling and Step 6.5 dynamic routing. [The generated Codex Karo file](../repo/instructions/generated/codex-karo.md), lines 1–86, starts with the prose role and task examples, without that original front-matter workflow. The source builder intends to extract front matter using exact delimiter matching (lines 62–65). The checked-out generated artifact should be assessed as it exists rather than assuming every source workflow instruction arrived in every variant.

The adapter has another concrete compatibility issue: its allowed CLI string is assigned twice (lines 21–23), with the latter omitting Cursor even though the Python parser and launch case include it (lines 183, 317–324). `get_cli_type` validates against that shell list (lines 220–228). Thus the presence of a launch case does not establish that normal configuration reaches it. These inconsistencies are reasons to establish one authoritative provider/role capability description before adopting the whole adapter.

## Communication persistence and acknowledgment are different operations

[inbox_write.sh](../repo/scripts/inbox_write.sh), lines 40–145, generates IDs, serializes cooperating writers with a directory lock plus optional flock, appends an unread message and replaces the file atomically. Retries are bounded. It keeps all unread messages when pruning older read entries. The strong design idea is storing payloads in YAML while sending only a count through the TUI. The recipient can recover the payload after a missed nudge.

There are practical limits to the “guaranteed” wording in the instructions:

- Message content is interpolated into a Python triple-quoted literal inside `python -c` (lines 80–101), with no data serialization step. Payloads containing that delimiter or Python escape sequences are not handled as arbitrary opaque text. The special-character test [test_inbox_write.bats](../repo/tests/test_inbox_write.bats), lines 382–405, covers ordinary quotes/newlines/YAML syntax, not all Python literal delimiters. By contrast, [ntfy_listener.sh](../repo/scripts/ntfy_listener.sh), lines 61–81, passes mobile message text through an environment variable to Python. This is a source-level reliability and boundary finding, not a live injection experiment.
- The writer serializes its own writes, while [the common protocol](../repo/instructions/common/protocol.md), lines 67–74, tells the agent to acknowledge by directly editing the YAML. That generic operation has no shared locking contract enforced by this script. OpenCode supplies a stronger specific path: [mark-as-read.ts](../repo/.opencode/tools/mark-as-read.ts), lines 129–208 and 233–255, performs atomic replacement under the same directory lock, verifies the target equals `OPENCODE_AGENT_ID` and treats an already-read message idempotently. That is useful implementation work, though not a universal CLI acknowledgment path.
- [slim_yaml.py](../repo/scripts/slim_yaml.py), lines 40–48 and 298–349, loads an inbox, archives read entries and rewrites the inbox through ordinary file writes. [Its wrapper](../repo/scripts/slim_yaml.sh), lines 15–16 and 32–54, takes a separate `.slim_yaml.lock`, not the per-inbox writer lock. An arrival concurrent with that read-modify-write may be overwritten. The mailbox's atomic append is therefore not an end-to-end transaction spanning archive and acknowledgment.
- Inbox success, `read: true`, task `done`, report publication and command acceptance are separate updates. There is no broker acknowledgment, lease, transactional outbox or exactly-once work execution protocol joining them. An agent must reconstruct state carefully after interruption.

These limits do not negate the useful durable-payload design. Wingman can retain it while making all mutations use a single append/ack/archive API, passing payloads as data and explicitly deduplicating task execution by ID. Locks also need an operational recovery policy after abrupt process loss. A temporary pathname or lock directory by itself is not a distributed coordination protocol.

## Recovery is substantial, but schema-sensitive

[The session hook](../repo/scripts/session_start_hook.sh), lines 22–89, reads identity from tmux and injects role recovery instructions. Its headers identify it as a Claude hook (lines 15–18), and [.claude/settings.json](../repo/.claude/settings.json), lines 3–25, wires SessionStart and Stop commands. Codex instead receives a startup prompt from [cli_adapter.sh](../repo/lib/cli_adapter.sh), lines 594–641, and `/clear` is translated into `/new` by [the watcher](../repo/scripts/inbox_watcher.sh), lines 549–575. Role recovery and continuity are thus CLI-dependent mechanisms.

The watcher deduplicates unread auto-recovery hints (lines 353–362), checks for cancellation/idle (lines 364–380), then enqueues another task-assigned hint (lines 382–409). The guard reads only `task_data.get('status')`. The launcher clean template (lines 398–406) and Karo task example (role lines 63–84) put that state in `task.status`. The archival utility already accommodates both schemas through `get_item_status` (lines 63–72), but this guard does not. [test_send_wakeup.bats](../repo/tests/unit/test_send_wakeup.bats), lines 859–915, uses flat status fixtures, so its cancellation/idle intent does not establish the guard for nested clean-start/role records. This does not prove that a cancelled task will execute: the receiving agent is still instructed to reread and obey its task. It means one layer of the claimed prevention may fail to suppress an unnecessary recovery hint.

Busy detection is also not a provider event stream. [agent_status.sh](../repo/lib/agent_status.sh), lines 33–128, reads terminal text and matches idle prompts, interrupt hints, animation rows and spinner phrases. Unknown text defaults toward idle. The watcher adds flags, throttling, clear deferral and CLI-specific key sequences. These mechanisms directly address operational failure modes; their effectiveness depends on the CLI's rendered interface and version. They should not be mistaken for a structured cancellation acknowledgment or a committed task boundary.

Finally, [watcher_supervisor.sh](../repo/scripts/watcher_supervisor.sh), lines 34–92, is an optional standalone program that periodically restarts watchers for existing panes when separately run. A checkout-wide search found test references and changelog documentation, but no non-test invocation. The [standard launcher](../repo/shutsujin_departure.sh), lines 893–939, starts individual watchers directly without wiring this supervisor. Its five-second restart loop should therefore not be credited as standard-launcher behavior. Even with the supervisor enabled, a pane can contain a shell after its CLI crashes. A live pane does not prove that a coding agent works or its conversation resumed. It also does not prove that an agent interpreted a product blocker. Wingman needs semantic supervision in addition to process supervision.

## Instruction variants leave several coordination choices unresolved

The role/common files are operational prompts, not schemas validated by a task server. Their inconsistencies matter because agents are expected to act on them:

| Concern | Concrete source tension | Assessment consequence |
|---|---|---|
| Dependency ownership | [Common task flow](../repo/instructions/common/task_flow.md), lines 80–101, supports a blocked worker slot while also requiring blocked prerequisites to remain unassigned in `pending.yaml`; [Karo role](../repo/instructions/roles/karo_role.md), lines 74–84, shows a blocked assignment. | Credit dependency-aware agent coordination, not a single enforced scheduler. |
| Report recipient | [Ashigaru role](../repo/instructions/roles/ashigaru_role.md), lines 65–70, routes completion to Gunshi; [common protocol](../repo/instructions/common/protocol.md), lines 16–17, 97–104 and 120–125, still routes reports to Karo. | The main trace follows the newer role/AGENTS intent; common examples may wake a different manager. |
| Supplemental completion notification | [Stop hook](../repo/scripts/stop_hook_inbox.sh), lines 95–114, can notify Karo after matching natural-language completion/error phrases. | Completion signals can also arrive outside the worker→Gunshi review route. They are notifications, not review certificates. |
| Command statuses | [Task flow](../repo/instructions/common/task_flow.md), lines 13–19, omits `paused`; lines 46–65 then include it in the exhaustive command set. | Pause/resume is a management convention with archival behavior, not a uniformly enforced state machine. |
| Human input protection | [Common protocol](../repo/instructions/common/protocol.md), lines 37–39, prohibits keystrokes when the Shogun pane is active; [watcher wake-up](../repo/scripts/inbox_watcher.sh), lines 895–917, explicitly delivers Shogun nudges even while busy. | Protection against destructive resets is stronger than a blanket guarantee that human input is never touched. |

## What a traced request does and does not prove

An ntfy request has a concrete entry: stream JSON, filter outbound messages, persist `pending` input and notify Shogun ([listener](../repo/scripts/ntfy_listener.sh), lines 142–179). After that, the human intent interpretation, project matching, decomposition and acceptance are LLM actions instructed by files. The script does not itself understand “add this API endpoint” or decide which existing project is meant. That is the proper boundary for assessing this as an autonomous organization.

The most relevant end-to-end test [e2e_basic_flow.bats](../repo/tests/e2e/e2e_basic_flow.bats), lines 5–12 and 120–155, uses mock CLIs and explicitly sends nudges. It verifies the protocol-shaped integration scenario as test intent, with worker completion going directly to Karo. [e2e_blocked_by.bats](../repo/tests/e2e/e2e_blocked_by.bats), lines 74–89, simulates Karo unblocking via direct fixture editing. Neither demonstrates a live model obeying the latest quality-review chain, a daemon interpreting dependencies, or the complete human request→delivered product lifecycle.

The adoption implication is practical: borrow the inspectable task/command contracts, purpose validation, role recovery and separation of durable payload from wake-up. Establish authoritative schemas, mutation APIs and role generation before treating this as Wingman's organization runtime. Product discovery, Telegram conversation correlation, project leadership instances, collaboration rooms and connected executive/project/agent views remain application work beyond this shell formation.
