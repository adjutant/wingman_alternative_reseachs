# Planka: live shared cards without an agent ownership protocol

Source: https://github.com/plankanban/planka

Reviewed commit: `2cf423824a09f84df7dc3acf0ded9a700292d882`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).

## Fit decision

Planka is a useful human board and shared work-record foundation. It has projects, boards, lists, cards, checklists, card members, checklist assignees, comments, attachments, custom fields, activity, notifications and structured HTTP operations. Its client receives live socket updates and fetches fresh data after reconnecting. Agents can use user API keys to work with the same records that people see.

The reviewed Community code does not supply a native autonomous-work ownership protocol. Card membership permits multiple participants. Checklist assignment is a mutable user field. Neither is an atomic exclusive claim with a renewable lease or execution-attempt token. General card and task writes lack expected-revision conditions. Two workers can overwrite assignment or continue writing after a coordinator has reassigned the work.

Planka implements meaningful consistency inside selected database operations. Closing a card can transactionally update checklist items linked to that card. Changing a list's type locks the list row and updates relevant cards and linked items in one transaction. These safeguards keep displayed state consistent. They do not require accepted child results, readiness or qualified review before closure.

Licensing is a separate adoption constraint. The pinned [Community license](../repo/LICENSE.md), lines 19–60, permits stated internal and other uses but restricts commercial hosting and shared use across organizations. This is source available under use restrictions, not an unqualified permissive open-source option. The [README](../repo/README.md), lines 19–66, advertises separate Pro capabilities. Those marketing claims are not credited as implementation in this checkout. In particular, Pro recurrence, SSO, additional views and mobile features were not reviewed as Community features.

## Scope and evidence level

The full checkout contains 1,648 tracked files. This review traces targeted source bodies for the card/task model, query-method layer, main mutation controllers and helpers, list-level alternate writers, authentication and board permissions, activity/notifications, webhooks, attachments, custom fields and client mutation/reconnect behavior. Selected test assertions and acceptance-step bodies were read. No candidate application, dependency install, build, migration or test was executed.

This is not an every-line audit. Full imports and duplication, every user/permission mutation, all migrations, complete file and HTTP security, notification-provider internals, full deployment scaling and all browser screens are outside certification. Pro features and external integrations do not receive credit from documentation alone. The ledger identifies inspected source ranges and test-source evidence rather than implying a passing runtime experiment.

## Architecture and shared records

The root [package manifest](../repo/package.json) identifies version 2.3.1. The [server manifest](../repo/server/package.json) requires Node 24 or later and uses Sails, Waterline/PostgreSQL, Knex, Socket.IO and supporting services. The [client manifest](../repo/client/package.json), lines 133–175, uses React 18, Redux, Redux ORM and Redux Saga. [Datastore configuration](../repo/server/config/datastores.js) selects PostgreSQL through shared connection configuration.

The [query-method hook](../repo/server/api/hooks/query-methods/index.js) attaches a `qm` implementation to each model. Controllers validate requests and access, helpers coordinate effects, and these query methods perform database operations. This separation is readable, but an invariant must cover all helper/query callers rather than only a browser action.

[Project](../repo/server/api/models/Project.js), lines 123–186, has a name, description and manager/owner relationships. [Board](../repo/server/api/models/Board.js), lines 113–196, belongs to a project and carries view and card-display settings. [Project creation](../repo/server/api/hooks/query-methods/models/Project.js) transactionally inserts the project and its first manager and sets the owner for a private project. Subsequent socket/webhook delivery happens in a separate [project helper](../repo/server/api/helpers/projects/create-one.js).

The [card model](../repo/server/api/models/Card.js), lines 143–264, has project/story presentation types, board/list, description, due date, due-completion flag, stopwatch, closed state and associations. These card types are not agent roles. A [task list](../repo/server/api/models/TaskList.js), lines 70–110, groups checklist tasks within a card. A [task](../repo/server/api/models/Task.js), lines 75–117, has name, position, completion, optional linked card and optional assignee.

The selected [schema](../repo/server/db/migrations/20250228000022_version_2.js), lines 310–449, stores multiple card members with a unique card/user pair. That prevents duplicate membership for the same user; it does not limit a card to one worker. Task assignment has no attempt, lease or expected-owner field. [Session](../repo/server/api/models/Session.js) stores login tokens and browser/client metadata, not execution attempts.

## Requirement assessment

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Projects, descriptions, managers, boards and membership provide shared scope. Agent leadership, specification continuity and portfolio decisions need conventions or integration. |
| T02 | Similar | SQL-backed cards and checklist tasks are accessible to clients. Main writes, history, notifications and files do not share one universal transaction. |
| T03 | Similar | Card/checklist grouping and linked-card tasks support decomposition and progress display. They are not a governed recursive assignment hierarchy. |
| T04 | Resembles | Linked cards and labels can express relationships. The reviewed core has no blocking dependency DAG, cycle gate or atomic ready-work acquisition. |
| T05 | Resembles | Persistent users/API keys can represent agents. Login sessions, card membership and stopwatch fields do not distinguish a logical worker from its current attempt. |
| T06 | Similar | Structured HTTP/socket CRUD and documented request shapes support agent clients. No native task MCP, claim-next or agent process-control surface was found in the reviewed core operation inventory. |
| T07 | Resembles | Card members and task assignees record participation. Membership is many-to-many, while assignment writes lack expected-owner/revision conditions or leases. |
| T08 | Resembles | Ordered lists, member filters, card counters and dates assist planning. The reviewed models and mutation paths have no enforced worker capacity, WIP reservation or automatic dispatch. |
| T09 | Resembles | Checklist assignment and linked cards permit parallel human work organization. No child worker launch, result join or accepted-child parent-finish barrier. |
| T10 | Similar | Descriptions, comments, attachments and custom fields retain context. Uploaded file identity is not an accepted-result digest or a pinned artifact/attempt/review tuple. |
| T11 | Similar | Card moves, checklist completion, comments, timestamps and stopwatch expose progress. Structured result submission and durable handoff are conventions. |
| T12 | Similar | Persistent user notifications, mentions, subscriptions, sockets and webhooks provide communication. Unread items are bounded, delivery is separate from mutation and no native agent acknowledgement/replay protocol is established. |
| T13 | Resembles | Comments and mentions can request help, with labels or lists for blockers. No typed pending decision with accountable resolution and guarded worker continuation. |
| T14 | Absent | Stopwatch, card age and authentication-session validity are not work leases. Reviewed task/card APIs and models expose no worker heartbeat, renewal or guarded stale-work reclaim. |
| T15 | Absent | Main task/card writes have no expected revision or attempt fence. Local client IDs and attachment request IDs do not durably deduplicate server effects. |
| T16 | Similar | SQL persistence, archive/trash movement, reopening and reconnect snapshots support board recovery. No native worker resume/cancel or compensation for external agent effects. |
| T17 | Similar | A central HTTP service, PostgreSQL and optional S3 can serve multiple machines. Cross-process socket delivery and deployment consistency require configuration; exclusive agent claims remain absent. |
| T18 | Similar | User-attributed actions and comments support investigation. Action types cover selected events, and deletes/history publication are not an immutable complete mutation audit. |
| T19 | Similar | Live board/card views, filters, checklists and reconnect refresh provide useful inspection. Optimistic update failure and multi-request snapshot boundaries remain; live usability was not tested. |
| T20 | Similar | Continuous-flow lists, dates, labels, custom fields and checklist/card types support planning. No reviewed native iteration, capacity or autonomous scheduling protocol; Pro recurrence is outside this checkout's assessed scope. |
| T21 | Resembles | Closed lists and linked-card completion reflect outcomes. Closure does not require checklist result acceptance, pinned evidence or a separate qualified reviewer. |
| T22 | Similar | Active-user keys, session validation, board editor/viewer rules and private-data filtering are implemented. They authorize account operations rather than fenced agent attempts or execution sandboxes. |
| T23 | Similar | Clear model/query/helper boundaries, HTTP API, webhooks and custom fields support integration. No sandboxed agent plugin contract or automatic enforcement for added policy fields. |
| T24 | Similar | Included Node/container builds, database scripts and storage backends provide a conventional service package. Python notifications, backups, origins, scaling and restricted licensing add operating/adoption work. |

## Creating, selecting and assigning work

The [card creation controller](../repo/server/api/controllers/cards/create.js), lines 110–221, checks board membership and editor role, validates fields and calls the creation helper. [The helper](../repo/server/api/helpers/cards/create-one.js) computes ordering, may reposition siblings, persists a card, broadcasts, sends webhooks, adds an optional creator subscription and appends a creation action. These steps are sequential effects, not one atomic create-plus-history operation. A later failure can leave a committed card behind an error response.

The [card query methods](../repo/server/api/hooks/query-methods/models/Card.js), lines 1–179, support list search, user filters, included/excluded labels and cursor-based ordering for archive/trash-style lists. Queries use a list-changed timestamp and ID as a cursor. This is useful discovery and pagination. No query reserves a returned task for an agent or checks a dependency-ready work graph.

[Card membership creation](../repo/server/api/controllers/card-memberships/create.js), lines 100–154, requires an editor and validates the target user's board membership. [Its helper](../repo/server/api/helpers/card-memberships/create-one.js), lines 1–129, inserts a unique card/user membership, adds an optional subscription and records an action. Several different users can join the same card. The [query model](../repo/server/api/hooks/query-methods/models/CardMembership.js) has no exclusive-card claim operation.

[Task update](../repo/server/api/controllers/tasks/update.js), lines 94–210, verifies board editor access and target-assignee membership. [The task helper](../repo/server/api/helpers/tasks/update-one.js) then calls `Task.qm.updateOne(record.id, values)`. [The query method](../repo/server/api/hooks/query-methods/models/Task.js) matches ordinary criteria and sets values without an expected assignee, revision or attempt condition. Two workers can both write their own assignee successfully. No operation here stops the earlier worker when ownership changes.

The [card update controller](../repo/server/api/controllers/cards/update.js), lines 130–353, restricts viewers to subscription changes and requires editor membership in a destination board. It validates destination list and cover-attachment scope. These are substantive permission and relationship checks. They occur before the helper's later writes and do not make the displayed snapshot a revision-protected edit.

## Decomposition and completion semantics

[Linked-task creation](../repo/server/api/controllers/tasks/create.js), lines 88–202, checks access to the linked card. [Its helper](../repo/server/api/helpers/tasks/create-one.js) copies that card's name and marks the task completed when the card is closed. The [link migration](../repo/server/db/migrations/20250709160208_add_ability_to_link_tasks_to_cards.js) adds an indexed card reference. The inspected path has no DAG traversal or cycle check. A link represents a checklist reference, not a prerequisite reservation.

For an existing linked task, the update controller permits only reordering or moving it within the parent card's task lists. It prevents direct edits of the mirrored completion through that route. This is a useful consistency rule. It does not require either card to wait for accepted child results.

The create helper forces completion to true for a closed linked card, but does not force it to false for an open linked card. The creation API also accepts an explicit completion flag. That combination can start a linked item with a completion value that differs from its target. The stricter update route does not establish a universal initial-state invariant.

[Card mutation](../repo/server/api/helpers/cards/update-one.js), lines 1–240, sets `isClosed` when moving between opened and closed list types. Archive and trash preserve closure unless another explicit opened/closed transition applies. Its [query method](../repo/server/api/hooks/query-methods/models/Card.js), lines 199–269, transactionally updates a card and the completion flags of tasks pointing to that card when closed state is supplied.

This direction matters: it updates references to the closing card. It does not check that the closing card's own checklist is finished or accepted. No evidence, reviewer or result-version check precedes that update. Ordinary unlinked checklist tasks can be completed directly by an editor.

An alternate [list query writer](../repo/server/api/hooks/query-methods/models/List.js), lines 55–136, uses `SELECT ... FOR UPDATE` on the list for board/type changes. In that transaction it can update contained card board IDs, propagate opened/closed state to cards and synchronize tasks linked to those cards. This is stronger than a series of unrelated writes, but the locked entity is a list, not an agent attempt or accepted-result set.

The wider [list helper](../repo/server/api/helpers/lists/update-one.js), lines 1–264, performs membership/subscription cleanup, assignment clearing and label/custom-field work outside that central transaction. Card transfer has similar surrounding effects. [Bulk move](../repo/server/api/helpers/lists/move-cards.js) separately updates cards, creates movement actions and publishes sockets/webhooks; its notification creation remains a TODO. A new coordination rule must cover these alternate writers too.

## Context, results and communication

[Comment creation](../repo/server/api/helpers/comments/create-one.js), lines 65–188, persists text, broadcasts and calculates mention/subscriber recipients. Mention IDs are intersected with board members and exclude the author. [Comment update](../repo/server/api/controllers/comments/update.js), lines 80–138, requires the author and comment-capable membership. This supports retained discussion. A comment saying blocked or approved is not a typed decision record that gates execution.

[Custom-field writes](../repo/server/api/helpers/custom-field-values/create-or-update-one.js) persist content, broadcast and send a webhook. The [query implementation](../repo/server/api/hooks/query-methods/models/CustomFieldValue.js), lines 1–75, uses an SQL upsert on the card/group/field tuple. It gives one value per field, without a comparison against the old content. Adding an attempt or lease field here would not make other mutation paths enforce it.

[Attachment upload](../repo/server/api/controllers/attachments/create.js), lines 140–230, requires editor access. The [file processor](../repo/server/api/helpers/attachments/process-uploaded-file.js) creates an uploaded-file record, moves bytes to a generated per-upload location, optionally generates thumbnails and returns metadata. [Attachment creation](../repo/server/api/helpers/attachments/create-one.js) persists a separate attachment and may set the card cover afterward. These steps span storage and database writes, with no single result-acceptance transaction.

The attachment `requestId` is echoed in a socket event; this path does not use it as a durable uniqueness key. A generated upload ID identifies storage, not a content digest reviewed at a particular task revision. No inspected completion operation requires an attachment or source reference at all.

[Actions](../repo/server/api/models/Action.js), lines 70–90, cover creation, movement, membership and task completion/reopening. [Action creation](../repo/server/api/helpers/actions/create-one.js), lines 117–220, persists an attributed event and then triggers sockets, webhooks and selected notification types. General card name/description edits do not become complete before/after audit records merely because the action model exists. Card transfer also contains an explicit missing-transfer-action note in the [card helper](../repo/server/api/helpers/cards/update-one.js), lines 241–428.

The [notification model](../repo/server/api/models/Notification.js), lines 99–159, has a recipient, creator, card, action/comment reference and read flag. [Notification query methods](../repo/server/api/hooks/query-methods/models/Notification.js) transactionally insert notifications and mark older unread items read beyond a limit of 100 per user. They do not wait for the user to acknowledge the older items. [The index endpoint](../repo/server/api/controllers/notifications/index.js) lists unread items only.

This is a bounded attention queue. It cannot serve as the authoritative pending-decision backlog for agents. The [creation helper](../repo/server/api/helpers/notifications/create-many.js), lines 236–300, persists notification rows before broadcasting and invoking webhooks, separately from the originating card/task write. [Update](../repo/server/api/controllers/notifications/update.js), lines 65–107, scopes read-state changes to the recipient, but read state is not proof that a question was answered or a result accepted.

[Webhook delivery](../repo/server/api/helpers/utils/send-webhooks.js), lines 1–212, filters events and user/project/board scope, includes current/previous data where supplied, and starts asynchronous POSTs. Failed responses and network exceptions are logged. There is no durable delivery record, acknowledgement cursor, retry schedule or dead-letter queue in this implementation. Several derived changes, including linked-task synchronization and sibling reordering, carry explicit missing-webhook notes. Receivers cannot reconstruct an exactly-once task event stream from this transport.

## Concurrency, failure and recovery

The main [card helper](../repo/server/api/helpers/cards/update-one.js) does sibling reordering and cross-board cleanup before the card update. It can remove membership, subscriptions, labels and checklist assignees before a later operation fails. Label copying, actions, notifications and transport occur afterward. No overall transaction or compensating operation joins all these effects.

The card and task query writers accept criteria, but normal controller/helper calls pass the ID alone. Timestamp fields are maintained by [model hooks](../repo/server/config/models.js), lines 65–93; they are not read as conditional-update requirements. A stale worker is not rejected for writing from an old task attempt.

[Delete-card](../repo/server/api/helpers/cards/delete-one.js) removes related data before deleting the card. [Related cleanup](../repo/server/api/helpers/cards/delete-related.js) separately removes memberships, checklist records, comments and actions, and unlinks other tasks. [List cleanup](../repo/server/api/helpers/lists/delete-related.js) deletes cards before their related data. Failures between these steps can leave partial cleanup; exact deployed database outcomes were not exercised.

[List clear](../repo/server/api/controllers/lists/clear.js), lines 75–114, restricts the operation to a trash list and a project manager or board editor. Its [helper](../repo/server/api/helpers/lists/clear-one.js) performs that cleanup and then publishes. [Unreferenced-file cleanup](../repo/server/api/helpers/utils/remove-unreferenced-uploaded-files.js) starts asynchronous removals from a synchronous helper without awaiting all of them. A returned deletion response is not proof that every file removal completed.

There is no native agent process to resume, terminate or reconcile. Moving a card back to an active list or reassigning a task repairs the record, while any external worker can continue running. Safe retry after an uncertain create/update response requires a protocol beyond these CRUD methods. A unique membership pair prevents one duplicate relation, but does not make the whole membership-plus-subscription-plus-history operation retry-atomic.

## Access and human usability

[Current-user resolution](../repo/server/api/hooks/current-user/index.js) accepts bearer sessions or hashed user API keys. [Token validation](../repo/server/api/helpers/utils/resolve-access-token.js) verifies JWT data, an undeleted session, a paired cookie when required, an active user and password-change time. [Session queries](../repo/server/api/hooks/query-methods/models/Session.js) retain revocation state. These are real account controls, separate from work ownership.

[Policies](../repo/server/config/policies.js) require authentication and reject the special internal principal from ordinary external operations. API-key creation is admin-gated, and [the key controller](../repo/server/api/controllers/users/create-api-key.js), lines 65–103, stores a hash and returns the generated key once. [Board membership](../repo/server/api/models/BoardMembership.js), lines 70–136, distinguishes editors from viewers and viewer comment permission. Main mutation controllers enforce those permissions. They do not enforce specialist capability, current assignment or qualified reviewer separation.

The [socket client](../repo/client/src/api/socket.js) enables reconnection. [Reconnect handling](../repo/client/src/sagas/core/services/socket.js) fetches bootstrap and [core records](../repo/client/src/sagas/core/requests/core.js), including the current board/card and notifications. The [card reducer](../repo/client/src/models/Card.js), lines 95–137, replaces its card snapshot on this action. This is useful missed-event recovery for the current view. It is a collection of API reads, not a transactionally consistent snapshot or durable event replay.

[Card creation/update sagas](../repo/client/src/sagas/core/services/cards.js), lines 127–189 and 248–299, optimistically change local state. A failed create removes the temporary card, but the [card reducer](../repo/client/src/models/Card.js), lines 280–365, has no update-failure rollback branch; the client source inventory finds the failure constant, action and dispatch without a corresponding rollback handler. An unsuccessful edit can therefore leave optimistic state until refresh/reconnect or a later event. This is a source-based usability concern, not an observed live failure.

[Request sequencing](../repo/client/src/sagas/core/request.js) queues requests within one browser's saga layer and logs out on unauthorized responses. It is not a server lock between different clients. [Core fetching](../repo/client/src/sagas/core/requests/core.js), lines 80–140, also marks notifications for an opened card read. Opening context is not acknowledgement of an unresolved decision.

The [Dockerfile](../repo/Dockerfile) builds with Node 24 and includes Python. The [setup script](../repo/server/setup-python.js) creates a virtual environment and installs [notification dependencies](../repo/server/requirements.txt). No installer was run. [File-manager selection](../repo/server/api/hooks/file-manager/index.js) chooses local or S3 storage. [Production sockets](../repo/server/config/env/production.js), lines 254–294, configure accepted origins and leave the shared Redis adapter as an optional commented configuration. Multiple application processes need deliberate broadcast/storage/session planning; the presence of PostgreSQL alone does not certify clustered live updates.

## Test-source evidence and adoption work

Selected assertions were inspected, not run:

- [Card label query tests](../repo/server/test/integration/models/CardLabelFilters.test.js) stub native SQL responses and inspect included/excluded label predicates. They do not execute those queries against production PostgreSQL or prove ready-work allocation.
- [Notification endpoint tests](../repo/server/test/integration/controllers/notifications/show.test.js), lines 1–100 and 150–206, check recipient isolation, unauthenticated rejection and removal of private/credential fields. The [test environment](../repo/server/config/env/test.js) uses an in-memory Sails disk adapter, not production PostgreSQL transaction semantics.
- [Static-route tests](../repo/server/test/utils/static-routes.test.js) check path resolution and narrower local-file roots. This does not certify the complete upload or HTTP security surface.
- [Client label-filter tests](../repo/client/src/utils/filter-card-labels.test.js) and [local-ID tests](../repo/client/src/utils/local-id.test.js) check presentation helpers. They do not establish server idempotency.
- The [IME scenario](../repo/client/tests/acceptance/features/ime-composition.feature) and [step implementation](../repo/client/tests/acceptance/steps/ime-composition.step.js) assert that composing text with Enter does not accidentally submit a task. These are meaningful usability intentions, but no browser acceptance run was performed. The checked-in [User model test](../repo/server/test/integration/models/User.test.js) is commented out.

The inspected test inventory does not establish exclusive claims, stale-attempt rejection, review gates, cross-process allocation, complete deletion recovery or webhook replay. Application test coverage and source implementation are separate forms of evidence.

Adoption should add one durable ownership/attempt authority shared by every mutation surface. Acquire a task conditionally before execution, enforce capacity and readiness at acquisition, renew leases and reject progress from obsolete attempts. Persist outcomes under idempotency keys so uncertain responses can be resolved without repeating effects.

Introduce explicit submitted results, pinned artifacts, qualified review and accepted-child integration. Cover list retyping, bulk movement, transfer, direct task edits and deletion as well as normal card changes. Keep pending questions in durable decision records independent of the bounded unread queue. A transactional outbox, replay cursor and delivery acknowledgements would make communication suitable for unattended agents.

Planka's useful components are the shared board, permission-aware API, linked completion consistency and reconnect refresh. Its main gap for this baseline is the authoritative coordination protocol around those records, with licensing limits assessed separately from implementation quality.
