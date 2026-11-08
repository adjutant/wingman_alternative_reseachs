# Kanboard: a shared backlog with human workflow conventions

Source: https://github.com/kanboard/kanboard

Reviewed commit: `2ddb31bf72d355727d0639fc3423630f3bae1a9c`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

Kanboard can provide the durable shared backlog and human board for an agent team. It has project permissions, task assignment, subtasks, task relationships, comments, attachments, notifications, automation and a substantial JSON-RPC API. Agents can use ordinary user accounts and API calls to participate in the same work records that people inspect.

It does not implement the baseline's execution coordination protocol. Assignment is an unconditional task-field update. There is no native execution-attempt registry, renewable task lease, atomic claim-next operation or stale-attempt fencing in the reviewed core models and API surface. A separate coordinator must establish those guarantees. Adding a client that reads an unassigned task and then sets its owner does not make the two operations atomic.

Completion also has different semantics from the baseline. Closing a task marks all its subtasks done; it does not wait for their results to be submitted and accepted. Dependency labels and review columns communicate workflow, but the inspected mutation paths do not turn them into universal execution or acceptance gates.

The [license](../repo/LICENSE) is ordinary MIT. The pinned [README](../repo/README.md) declares maintenance mode, with small fixes and community contributions rather than active development of major features. That is the repository's statement at this revision, not a forecast of its future. Kanboard is a plausible conventional task authority to extend, with substantial additional work needed for reliable autonomous allocation.

## Scope and evidence level

The checkout contains 2,792 tracked files. The review inspects selected source bodies for projects, tasks, assignment, status, position, relationships, subtasks, recurrence, metadata, files, API authentication and authorization, event jobs, activity and notification delivery, plugin loading and board interaction. It also reads selected test assertion bodies. No candidate application, dependency install, build, migration or test suite was executed.

This is not an every-line audit or runtime usability certification. SQLite schema excerpts support the model findings. Full migration histories, other database backends, every import/duplication path, all authentication providers, third-party plugins and the complete attachment/HTTP security implementation are outside certification. The ledger separates inspected ranges, manifests and test-source evidence. Method inventories and searches are used to locate operations, not as substitutes for reading their bodies.

## Architecture and data model

[composer.json](../repo/composer.json) requires PHP 8.1 or later and several PHP extensions. It combines Pimple services, Symfony components and vendored libraries for the database, validation, JSON-RPC and browser application. [DatabaseProvider](../repo/app/ServiceProvider/DatabaseProvider.php), lines 1–115, chooses the configured driver and can run schema migrations at initialization. SQLite, MySQL and PostgreSQL are among the switch branches. Backend-specific isolation and deployment behavior were not tested.

The current [SQLite task table rebuild](../repo/app/Schema/Sqlite.php), lines 1–150, retains project, column, swimlane, owner, creator, description, priority, estimates, dates, recurrence and external-provider fields. `owner_id` is the task assignee. It is not an exclusive runtime reservation. The separate browser `sessions` table in this schema is not an agent execution-attempt table.

[TaskModel](../repo/app/Model/TaskModel.php), lines 1–125, defines only open and closed as task activity states. Board columns supply the visible workflow. Thus a task in a column named Review or Done can still be open; moving to that column and closing the task are separate operations unless configured automation connects them.

[Project creation](../repo/app/Model/ProjectModel.php), lines 365–425, groups project insertion, initial board and swimlane creation in a database transaction. It records an owner, normalizes an identifier and can add the creator as project manager. [Project membership](../repo/app/Model/ProjectUserRoleModel.php), lines 1–97, combines direct and group-associated projects. These are real shared organizational records, but agent-specific leadership, capability and attempt identity remain conventions outside the model.

The [API provider](../repo/app/ServiceProvider/ApiProvider.php) registers procedure objects for projects, boards, tasks, subtasks, comments, files, metadata, permissions and related entities. [jsonrpc.php](../repo/jsonrpc.php) delegates requests to that server. The inspected core provides JSON-RPC rather than a native MCP task server or an agent process launcher.

## Requirement assessment

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Durable projects, ownership, membership, identifiers and boards provide shared scope. Agent leadership and retained organizational context need additional conventions. |
| T02 | Similar | Rich tasks persist in SQL and are available through UI and API. Task writes, tags, files and events are not one universal atomic operation. |
| T03 | Similar | Assigned subtasks and reciprocal child/parent, milestone and follow-up links support decomposition. Links do not enforce a recursive execution hierarchy or accepted-child join. |
| T04 | Resembles | Blocking labels and link searches expose relationships. The inspected assignment, move and close paths do not require dependency readiness or enforce graph acyclicity. |
| T05 | Resembles | Persistent user accounts can represent agents. Browser sessions and time records do not distinguish logical agent, running worker and fenced execution attempt. |
| T06 | Similar | JSON-RPC covers core task operations, searching, files and comments. Native agent task MCP, claim-next and execution control are absent from the reviewed registered core surface. |
| T07 | Resembles | Task owner and assign-to-me operations record responsibility. Updates match by task ID without an expected owner/revision, so concurrent claim clients can overwrite each other. |
| T08 | Resembles | Column, swimlane and project limits, assignment actions and subtask restriction UI assist planning. These do not establish atomic worker-capacity admission or automatic agent dispatch. |
| T09 | Resembles | Subtasks can have different assignees and become full linked tasks. No child process launch, parallel result collection or controlled parent finish is implemented by these records. |
| T10 | Similar | Description, metadata, comments, files and links preserve context. They do not pin an accepted artifact version to an execution attempt. |
| T11 | Similar | Updates, comments, dates, estimates and time tracking expose progress. Structured handoff and result submission remain conventions rather than required lifecycle records. |
| T12 | Similar | SQL-backed unread notifications, mentions, activity and webhooks help participants coordinate. Delivery is separate from mutation, and there is no inspected native agent inbox acknowledgement/replay protocol. |
| T13 | Resembles | Comments, blocking links and overdue notifications can represent questions and escalation. No typed pending decision with a required responsible answer controls worker resumption. |
| T14 | Absent | Due dates, inactivity and time tracking are not task leases. The reviewed task/subtask schema and API expose no authenticated heartbeat, renewal or guarded reclaim operation. |
| T15 | Absent | General task/subtask writes have no attempt or expected-revision condition. JSON-RPC request IDs correlate responses rather than durably deduplicating effects. |
| T16 | Resembles | Reopen, reassignment and persistent records support human recovery. There is no native agent resume/cancel, process reconciliation or compensation for external worker effects. |
| T17 | Similar | Many clients can use one HTTP service and shared database. Local file storage and sessions need deployment planning; offline replicas are not a common exclusive-claim authority. |
| T18 | Similar | Activity, event data, user attribution and metadata change fields aid investigation. Activity is conditional on a logged user and is not an immutable transactionally coupled audit log. |
| T19 | Similar | Board, detail, search, subtasks and notifications provide a coherent human interface. Polling and drag failure boundaries remain; live accessibility and usability were not tested. |
| T20 | Similar | Continuous-flow columns, priorities, swimlanes, estimates, recurrence and milestone links support planning. They do not supply a native agent capacity or iteration execution protocol. |
| T21 | Resembles | Review columns, descriptions and role rules can express review policy. Core close marks subtasks done without requiring accepted results or a separate qualified reviewer. |
| T22 | Similar | Per-user API credentials, application/project roles, membership checks, comment visibility and CSRF controls are implemented. Application-wide API credentials intentionally bypass user-scoped checks. |
| T23 | Similar | PHP plugins, hooks, actions, metadata and procedures provide substantial extension points. Plugins run as application code; added fields alone do not enforce ownership invariants. |
| T24 | Similar | PHP/SQL deployment and included container files are approachable for a conventional board. Cron, files, database backups, credentials and plugin compatibility remain operating responsibilities. |

## Creation, assignment and concurrent updates

[TaskProcedure](../repo/app/Api/Procedure/TaskProcedure.php), lines 1–222, authorizes the project or task, verifies assignability for nonzero task owners, validates fields and calls the corresponding model. Updates omit null fields so a caller can make a partial edit. These are useful API semantics. They do not accept a current-owner condition, expected revision or attempt token.

[TaskCreationModel](../repo/app/Model/TaskCreationModel.php) prepares default column, swimlane, color and timestamps, computes a position and persists the row. Tags and queued events follow the row write. It does not use a single enclosing transaction for all these effects. It returns an integer, including zero when the persistence result is false. A client must validate the returned ID rather than treating any completed HTTP response as task creation.

[TaskModificationModel](../repo/app/Model/TaskModificationModel.php) reads the current row, updates tags, prepares values and executes an update constrained only by ID. The prior read is used for event differences, not a compare-and-swap predicate. Two workers can both read an unassigned task, each set its own owner and both receive successful writes. The last stored owner wins; earlier external work is not stopped or fenced.

The browser [assign-to-me controller](../repo/app/Controller/TaskModificationController.php), lines 1–106, applies CSRF and role-helper checks before calling the same model. Those checks do not close the race between observation and save. The automatic action [assign current user if unassigned](../repo/app/Action/TaskAssignCurrentUserColumnIfNoUserAlreadySet.php) tests the owner in event data and then also calls the unconditional model update. Its name describes an intention, not an atomic storage precondition.

[Task position changes](../repo/app/Model/TaskPositionModel.php), lines 1–175 and 177–315, do use database transactions to renumber tasks and change column/swimlane. This protects a useful multi-row operation. They do not reserve agent work or compare the original task revision. The database wrapper's [transaction methods](../repo/libs/picodb/lib/PicoDb/Database.php), lines 282–341, delegate to PDO begin/commit/rollback. No cross-backend concurrency guarantee is inferred from the mere presence of a transaction.

The [task validator](../repo/app/Validator/TaskValidator.php), lines 1–140 and 150–230, checks field types, dates and required inputs. It does not turn an acceptance description, board label or arbitrary metadata field into a completion gate.

## Relationships and decomposition

The [link schema](../repo/app/Schema/Sqlite.php), lines 943–968, includes labels such as blocks, is blocked by, child/parent and milestone targeting. A unique index prevents duplicate link triples. [TaskLinkModel](../repo/app/Model/TaskLinkModel.php), lines 97–235 and 278–305, transactionally creates or updates the forward and opposite relationship records. This is useful consistency for the pair.

There is no graph traversal or cycle check in that create/update body. The [link validator](../repo/app/Validator/TaskLinkValidator.php) rejects a self-link and missing opposite task in the form validation path, but the [API link procedure](../repo/app/Api/Procedure/TaskLinkProcedure.php) calls the model directly after permissions. Form validation therefore must not be credited to every writer. Database constraints still apply; exact invalid-link outcomes were not exercised.

[Link search](../repo/app/Filter/TaskLinkFilter.php) selects tasks with a matching link label. It does not determine whether all upstream work is accepted or reserve a ready task. Moving, assigning and closing tasks do not call a dependency scheduler in the inspected bodies. A coordinator needs its own readiness policy and must enforce it at the ownership boundary.

[SubtaskModel](../repo/app/Model/SubtaskModel.php), lines 1–108 and 213–337, gives each subtask a parent task, assignee, estimate, elapsed time and todo/in-progress/done status. Subtask update saves by ID, without attempt fencing. The [API procedure](../repo/app/Api/Procedure/SubtaskProcedure.php) checks that an updated subtask belongs to the supplied parent, which prevents a simple parent-ID mismatch. It still permits direct status changes rather than requiring a delegated result envelope.

[Subtask conversion](../repo/app/Model/SubtaskTaskConversionModel.php) creates a full task, adds a child relationship if the label exists, copies tags and removes the old subtask. These steps are not one transaction. Its strict comparison against false also differs from TaskCreationModel's integer-zero failure return, so a failed creation can enter later conversion steps with an invalid ID. Subsequent database and helper failures determine the final outcome; no runtime data-loss result is claimed.

## Capacity, automation and completion

Task limits are visible in the [board task template](../repo/app/Template/board/table_tasks.php) and [container template](../repo/app/Template/board/table_container.php). They add a limit-warning class when counts exceed configured values. The reviewed creation and position bodies do not reject a write because the limit is reached. This is advisory WIP visibility rather than a shared capacity reservation.

[SubtaskStatusModel](../repo/app/Model/SubtaskStatusModel.php) can detect another in-progress subtask for a user when restriction is enabled. The [subtask helper](../repo/app/Helper/SubtaskHelper.php), lines 1–84, routes the UI to a restriction dialog. [That dialog's save](../repo/app/Controller/SubtaskRestrictionController.php) performs two separate status updates. Direct API status updates do not pass through that dialog, and toggle itself does not atomically test capacity. A one-at-a-time UI convention is not a general agent admission invariant.

[TaskStatusModel](../repo/app/Model/TaskStatusModel.php) closes all subtasks first, then changes the task's activity flag and completion timestamp. There is no prerequisite for submitted evidence, dependency completion or reviewer identity. The subtask update and task update are separate operations, and the close path does not condition the latter on the former succeeding. The [confirmation template](../repo/app/Template/task_status/close.php) explicitly tells the person that subtasks will also close.

The [status controller](../repo/app/Controller/TaskStatusController.php) checks a confirmation and CSRF token and invokes this model. [TaskCloseColumn](../repo/app/Action/TaskCloseColumn.php) invokes the same operation automatically after a configured column event. A Review or Done column can therefore drive closure without implementing qualified acceptance.

[Recurring-task creation](../repo/app/Model/TaskRecurrenceModel.php), lines 81–132, reads pending recurrence state, saves a new task, copies ancillary records and only afterward marks the parent processed. The parent check/update is not an atomic reservation in this body. Replayed or concurrent trigger processing can create a duplication risk. Recurrence is a planning convenience, not a retry-safe execution-attempt protocol.

## Progress, context and artifact evidence

Task descriptions and comments provide durable context. [CommentModel](../repo/app/Model/CommentModel.php), lines 148–222, persists text, timestamps and visibility, emits events and allows edits/deletion. [CommentProcedure](../repo/app/Api/Procedure/CommentProcedure.php) restricts per-user author impersonation and comment changes. These are useful communication records, but no required progress/result schema distinguishes implementation submitted, rejected and accepted.

[Metadata procedures](../repo/app/Api/Procedure/TaskMetadataProcedure.php) expose task key/value data. [MetadataModel](../repo/app/Model/MetadataModel.php), lines 1–127, records change time and user and groups a save in a transaction. It checks existence then writes, without an expected old value. Storing `attempt_id` or `lease_until` as metadata would not make other task mutation paths honor them.

[Task file procedures](../repo/app/Api/Procedure/TaskFileProcedure.php) check that the task belongs to the supplied project and provide upload/download. The [file model](../repo/app/Model/FileModel.php), lines 164–193, 278–288 and 350–390, writes an object before creating its SQL metadata row. A database failure can leave an orphan object. Generated keys hash filename plus wall-clock seconds, not content. Equal filenames uploaded for the same task within one second can target the same key in this path. The [storage writer](../repo/app/Core/ObjectStorage/FileStorage.php), lines 16–73, uses a normal file write.

This is attachment storage rather than an immutable reviewed artifact registry. The core does not bind a content digest, source revision, result, reviewer decision and current task attempt into one accepted record. Complete file-security and concurrent-upload behavior were not runtime tested.

## Communication, audit and failure recovery

[TaskEventJob](../repo/app/Job/TaskEventJob.php) builds current task details and dispatches event names. [TaskEventBuilder](../repo/app/EventBuilder/TaskEventBuilder.php), lines 1–154, rereads the task when building the event. A delayed job can therefore observe task data newer than the originating write. Some paths carry explicit changes or an original task snapshot, but this is not a transactionally captured event stream for every mutation.

[QueueManager](../repo/app/Core/Queue/QueueManager.php) executes synchronously when no queue driver is configured. With a driver, it publishes a serialized job separately from the task write. [JobHandler](../repo/app/Core/Queue/JobHandler.php) preserves the initiating user ID, prepares a worker session and catches execution exceptions for logging. The queue loop marks the job completed after this handler returns. A caught job failure is therefore not itself proof of a retry or dead-letter record. Driver-specific recovery is outside this review.

The [notification subscriber](../repo/app/Subscriber/NotificationSubscriber.php) feeds [NotificationJob](../repo/app/Job/NotificationJob.php). [Web notifications](../repo/app/Notification/WebNotification.php) persist to the [unread-notification table](../repo/app/Model/UserUnreadNotificationModel.php). Reads are user-scoped, and marking read removes the row. This supplies durable pending human notifications. It is not a complete addressed agent-message protocol with a delivery cursor, acknowledgement history and replay from the task transaction.

[WebhookNotification](../repo/app/Notification/WebhookNotification.php) makes one HTTP POST, with a token in the URL and private-network checks unless configured otherwise. It does not inspect an acknowledgement or maintain a delivery ledger in this body. The request uses the [HTTP client](../repo/app/Core/Http/Client.php), lines 65–82 and 150–182, with error raising disabled by the caller. A receiver should not assume every task mutation produces exactly one retrievable webhook.

[ActivityStreamNotification](../repo/app/Notification/ActivityStreamNotification.php) records activity only when the session has a logged-in user. Application-wide `jsonrpc` credentials do not initialize such a user. Those writes can therefore lack this normal activity record. [ProjectActivityModel](../repo/app/Model/ProjectActivityModel.php) stores event JSON and supports cleanup; the [archive command](../repo/app/Console/ProjectActivityArchiveCommand.php) removes entries older than one year. This is useful operational history, not an immutable compliance or attempt audit.

There is no native worker process for Kanboard to resume or stop. Reopen and reassignment change records; they do not cancel an old agent's external effects. [Task removal](../repo/app/Model/TaskModel.php), lines 90–107, attempts attachment removal before deleting the row. Those file and database operations do not form one reversible cancellation transaction.

The API's alternate [move-to-project writer](../repo/app/Model/TaskProjectMoveModel.php), lines 20–65, directly updates the task and prepares it as open. It can therefore reopen a closed task as part of relocation. Its method returns true even when the row update returns false. This path must be included in any added transition policy and in client reconciliation; a success boolean alone is not proof that relocation persisted.

The [JSON-RPC parser](../repo/libs/jsonrpc/src/JsonRPC/Request/RequestParser.php), lines 92–181, executes the procedure and then echoes the request ID into the response. It does not cache a durable outcome keyed by that ID. After an uncertain response, repeating create, comment or other side-effecting calls can repeat effects. The reviewed core task/API/schema operation inventory has no task lease or attempt-fencing alternative to those ordinary mutations.

## Access, deployment and human interaction

[API authentication](../repo/app/Api/Middleware/AuthenticationMiddleware.php) supports user authentication and a separate application credential named `jsonrpc`. The application credential is compared with the configured API token and does not initialize a user session. [Procedure authorization](../repo/app/Api/Authorization/ProcedureAuthorization.php) denies selected personal procedures to that mode. [User authorization](../repo/app/Api/Authorization/UserAuthorization.php), [project authorization](../repo/app/Api/Authorization/ProjectAuthorization.php) and [task authorization](../repo/app/Api/Authorization/TaskAuthorization.php) apply user/role checks when a user is logged in.

Consequently, the application token is a broad integration credential. Separate per-agent user credentials preserve more useful scope and attribution. [ApiAccessTokenAuth](../repo/app/Auth/ApiAccessTokenAuth.php), lines 1–105, checks active users and API-scoped access tokens. The middleware switches two-factor-enabled users to this token provider. The [API access maps](../repo/app/ServiceProvider/AuthenticationProvider.php), lines 180–239, distinguish application roles and project member/manager/viewer operations.

Browser operations also use [project authorization middleware](../repo/app/Middleware/ProjectAuthorizationMiddleware.php), which resolves the task's actual project. [Role helpers](../repo/app/Helper/ProjectRoleHelper.php), lines 1–162 and 183–292, add configured column and assignment restrictions to applicable UI paths. These helpers are not a universal storage policy: the status controller and JSON-RPC procedures must be assessed through their own checks. This review does not claim a complete authorization security audit or identical custom-role behavior across every interface.

[Board dragging](../repo/assets/js/src/BoardDragAndDrop.js), lines 1–116, sends a position mutation and refreshes returned markup on success. Its generic error path clears loading state without explicitly restoring the prior card position; a 403 reloads. [BoardAjaxController](../repo/app/Controller/BoardAjaxController.php), lines 1–116, checks project association and movement permission but does not use the supplied source column as an expected current-state predicate in storage.

[Polling](../repo/assets/js/src/BoardPolling.js) refreshes while the page is visible and not saving. It uses the project's last-modified check rather than a durable event cursor. [Project timestamps](../repo/app/Model/ProjectModel.php), lines 434–458, use integer seconds and a strict greater-than comparison. [Event-driven timestamp updates](../repo/app/Subscriber/ProjectModificationDateSubscriber.php) are separate from the task write. This can delay or miss a refresh around failed event processing or same-second changes. It is a presentation-freshness boundary, not ownership protection.

The included [Dockerfile](../repo/Dockerfile) uses Alpine and PHP 8.5 packages; the [SQLite compose example](../repo/docker-compose.sqlite.yml) persists data, plugins and certificate volumes. [ObjectStorageProvider](../repo/app/ServiceProvider/ObjectStorageProvider.php) binds uploaded files to local storage. Multiple web hosts need consistent database, files, session and plugin configuration. No clustered setup was trialed.

[Plugin loading](../repo/app/Core/Plugin/Loader.php), lines 1–137, checks declared version compatibility and initializes plugin PHP code, services and schema. [Reference hooks](../repo/app/Core/Plugin/Hook.php), lines 94–116, can modify values in place. This gives useful extension power with application-level trust. Cron-driven [task triggers](../repo/app/Console/TaskTriggerCommand.php) and [overdue notifications](../repo/app/Console/TaskOverdueNotificationCommand.php), lines 1–90, require operational scheduling; they do not supply agent heartbeats.

## Test-source evidence and adoption work

Selected assertions were read, not executed:

- [Task status tests](../repo/tests/units/Model/TaskStatusModelTest.php), lines 58–143, check close/reopen timestamps and explicitly expect all subtasks to become done after parent close.
- [Modification tests](../repo/tests/units/Model/TaskModificationModelTest.php), lines 46–109, check ordinary title/owner changes and event counts. They do not exercise competing claimers or expected-revision rejection.
- [Link tests](../repo/tests/units/Model/TaskLinkModelTest.php), lines 103–145, verify reciprocal labels and linked task data. They do not establish graph readiness or cycle prevention.
- [Unread notification tests](../repo/tests/units/Model/UserUnreadNotificationTest.php), lines 50–93, check user-scoped removal and stored notifications. They do not prove task-write/outbox atomicity.
- [Role-helper tests](../repo/tests/units/Helper/ProjectRoleHelperTest.php), lines 165–219, exercise custom assignee restrictions in the helper. That is not certification of every API and controller mutation.
- [JSON-RPC batch tests](../repo/tests/units/Api/BatchRequestTest.php) verify per-request access-denial responses and whole-batch authentication failure using registered closures. They do not prove application authorization for every procedure or transactional batches.

For adoption, retain Kanboard's project/task API and human board, but add a single authoritative claim and attempt service that every worker mutation must pass. It needs conditional ownership acquisition, renewal, expiry, fenced progress writes, retry-safe outcomes and restart reconciliation. Enforce capacity and readiness during acquisition rather than through a prior search or UI warning.

Add explicit submitted results and qualified acceptance, with pinned artifacts and child integration. Prevent ordinary close, automation and alternate writers from bypassing that policy. A transactional outbox and durable delivery/acknowledgement records would strengthen communication. Keep pending questions separate from notification read state, and expose unresolved ownership or delivery failures to the human owner.

Kanboard's strengths are conventional task records, familiar inspection and extension points. Its adoption cost for this baseline lies in the distributed coordination and acceptance invariants that the conventional board intentionally leaves to people and integrations.
