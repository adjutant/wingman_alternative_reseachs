# Taiga frontend: a human planning interface over a separate task authority

Source: https://github.com/taigaio/taiga-front.git

Reviewed commit: `da8afa50b2a59c3aaec78854c0ae8145a16e6cd8`.
Assessment date: November 9, 2026.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Evidence ledger: [review.json](review.json).
Companion: [Taiga backend assessment](../../taiga/assessment/ASSESSMENT.md).

## Fit decision

This repository supplies the human-facing half of Taiga: project navigation, backlog, Kanban, sprint taskboard, story/task detail, search, assignment, blockers, attachments, custom fields, activity and notification views. It provides useful inspection and manual coordination over shared server records. It is not an independent task database, agent scheduler or execution runtime.

The distinction is visible in ordinary actions. “Assign to me” changes the assignee through the normal save path. Changing task status sends a record edit. Board movement mutates local models and calls the backend. None acquires an execution lease or stops an earlier worker. The browser's generated session identifier and WebSocket heartbeat identify a client connection, not a task attempt or worker reservation.

The client sends record versions and reports version conflicts. Some detail edits use a clone and replace the visible model only after success. Other paths, including board movement, update local state before the response and lack equivalent local failure reconciliation. The event service reconnects its transport, but the inspected reconnect path does not replay missed changes, refetch the board or explicitly resend existing project subscriptions.

Use this frontend as the human inspection and planning interface for the backend, with an additional agent coordination layer. Its practical risks concern stale views, inconsistent failed-save handling, a substantial legacy build chain and the operation of separately configured API/event services. The backend report establishes server-side behavior; those mechanisms are not credited as native frontend enforcement.

## Scope, architecture and license

The full checkout contains 2,879 tracked files. This targeted static review covers application and resource registration; project loading; task detail/create/assign/status/delete/block flows; ordinary model/repository/HTTP saves; selected taskboard and Kanban writers; WIP display; socket lifecycle; notifications/history/search; authentication and client permission checks; container/build configuration; and selected mocked test assertions. Relevant task/resource/event operation inventories were also searched for lease, attempt, claim and dependency alternatives.

No application, dependency installation, build, candidate test suite or browser session was run. Every-line coverage, all screens/importers/plugins, full HTTP/file security, performance, accessibility, mobile layout, real event-gateway behavior and production recovery are not certified. This is a source assessment; the report website's later browser checks will not count as testing Taiga.

The [package manifest](../repo/package.json) identifies frontend version 6.10.3 and `AGPL-3.0-or-later`. It declares Angular 1.5.10, CoffeeScript, Gulp, Jade, Immutable, jQuery and supporting libraries. The [license](../repo/LICENSE), lines 1–15, is AGPL version 3; the [README's contribution statement](../repo/README.md), lines 46–50, states AGPL 3.0. This is separate from the backend's MPL declaration. This review does not establish obligations for a particular redistribution or deployment.

[Application module registration](../repo/app/coffee/app.coffee), lines 1045–1141, loads both the older `taigaResources` and newer `taigaResources2` modules alongside the actual task, story, Kanban, taskboard, history and notification modules. [Build inputs and ordering](../repo/gulpfile.js), lines 133–165, and [CoffeeScript compilation](../repo/gulpfile.js), lines 510–525, include both directory families in the generated application. The old task mutation service is therefore not dismissed merely because a newer resource file exists.

[Route definitions](../repo/app/coffee/app.coffee), lines 226–287, connect backlog, Kanban, sprint taskboard, story, task and wiki views. [Task detail markup](../repo/app/partials/task/task-detail.jade), lines 10–158, binds the controller, related story, generated stories, description, custom fields, attachments, history, status, assignee, watchers, due date, blocker and delete controls. [URL resolution](../repo/app/coffee/modules/base/urls.coffee), lines 15–49, targets the configured API. Browser storage is preferences/credentials, not the shared task authority.

## Requirement assessment

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Project routes, loaded project context, memberships and permission data support distinct workspaces. Durable project authority is supplied by the backend. |
| T02 | Similar | Views and model/resource services create and edit stable server records. Browser models/local storage alone are not durable task persistence or an offline conflict-resolution store. |
| T03 | Similar | Story detail includes related tasks; task detail links its story, epics and generated stories. Client decomposition does not establish arbitrary governed assignment trees. |
| T04 | Resembles | Blocker notes, links and filtering expose some planning constraints. No native prerequisite graph, runnable selection or cycle gate in the reviewed client paths. |
| T05 | Resembles | User identity, assignee and generated browser session ID are distinct client concepts. No task-execution identity, attempt registry or durable subagent profile. |
| T06 | Resembles | Resource services consume structured backend HTTP APIs. This UI repository does not expose a native task CLI/MCP or agent scheduler; automated clients should target the backend. |
| T07 | Resembles | Self-assignment is a normal versioned assignee edit. No exclusive reservation, expected-unowned claim or lease capability; server enforcement must come from the backend or an added coordinator. |
| T08 | Resembles | WIP selectors and markers display near/reached/exceeded limits; backlog/taskboard views organize work. The inspected move handler does not reject overflow or reserve worker capacity. |
| T09 | Resembles | Related tasks can be created and assigned in parallel. No native worker spawning, child-result collection or accepted-child completion barrier. |
| T10 | Similar | Detail views connect descriptions, files, custom fields, story/epic links and history. They do not bind an approval to an artifact version and execution attempt. |
| T11 | Similar | Task status, discussion, activity and related-task views expose progress retained by the server. Required result/handoff envelopes and execution checkpoints remain absent. |
| T12 | Similar | Paginated persistent notifications/history supplement live events and desktop notifications. Socket reconnection is not guaranteed missed-event recovery or recipient acknowledgement. |
| T13 | Resembles | Block/unblock dialogs and notes offer visible escalation context. No typed decision request with accountable resolution and guarded worker continuation. |
| T14 | Absent | Ping/pong checks socket liveness. Reviewed task/resource/event paths contain no worker lease renewal, stale-claim expiry or fenced reclaim. |
| T15 | Resembles | Ordinary patches include record versions and a global conflict notice. Bulk board requests omit per-record versions; local queues and session IDs are not attempt fences or idempotency keys. |
| T16 | Resembles | Server refetch, manual reassignment/reopen and record deletion support manual record recovery. No native agent stop/resume, offline mutation recovery or process reconciliation. |
| T17 | Resembles | Browsers on different hosts can point at the same backend. The client supplies no independent shared claim authority, disconnected coordination or host-side execution fencing. |
| T18 | Similar | Paginated activity and comments expose server-attributed history. They do not constitute a local immutable attempt journal or proof that an external worker performed an action. |
| T19 | Similar | Connected planning/detail/search/notification views provide substantial human inspection. Static templates reveal some keyboard support and labeling defects; responsive/accessibility/runtime acceptance remain untested. |
| T20 | Similar | Backlog, Kanban, sprint taskboard, filtering, counts, estimates and planning links support continuous or iteration workflows. Capacity enforcement is not established. |
| T21 | Resembles | Status controls display server state and submit ordinary edits. No native reviewer/artifact-version approval or required verification-result gate; parent calculation belongs to the backend. |
| T22 | Similar | Login, bearer headers, refresh/logout and permission-aware controls consume server identities/roles. Hidden controls are not authorization; backend access checks remain necessary. |
| T23 | Similar | Module/plugin registration, themes/locales and resource services support presentation extensions. Durable schema/workflow invariants require server changes or integration. |
| T24 | Resembles | Gulp development scripts and an Nginx container exist. The container downloads a separate compiled distribution; plugin archive/glob version mismatch and old toolchain inputs need verification. |

## Creation, context and ordinary mutations

[Project loading](../repo/app/coffee/app.coffee), lines 41–69, resolves project context before a route. [The project service](../repo/app/modules/services/project.service.coffee), lines 78–109, switches by slug, retains an immutable project snapshot and exposes permissions. [Task loading](../repo/app/coffee/modules/tasks/detail.coffee), lines 105–161, resolves a task by project/ref, loads attachments, story and sprint and creates neighbor links. A replacement coordinator can inspect server context without recovering an old browser process.

[Related-task creation](../repo/app/coffee/modules/related-tasks.coffee), lines 115–194, supplies project/story IDs, subject, default status and optional assignee, then calls ordinary task creation. It reports success or error and resets the form. This is decomposition into server records, not delegation to a subagent runtime. [Task resource operations](../repo/app/coffee/modules/resources/tasks.coffee), lines 19–106, also provide lists, bulk creation, watcher operations, reorder and milestone moves. Filter preferences are stored with project-derived keys.

[The browser model](../repo/app/coffee/modules/base/model.coffee), lines 18–101, tracks changed attributes and includes a record's version in patches. [Repository save](../repo/app/coffee/modules/base/repository.coffee), lines 24–85, sends create/PATCH/PUT operations, merges the server response and clears dirty state on success. Failure rejects the caller's promise. [Refresh](../repo/app/coffee/modules/base/repository.coffee), lines 118–148, can replace a model from the server. None supplies an execution-attempt precondition.

[Detail transformation](../repo/app/coffee/modules/common.coffee), lines 232–308, queues saves in the browser, clones the target, applies edits and replaces the visible model on success. [Status editing](../repo/app/coffee/modules/tasks/detail.coffee), lines 257–310, uses that service and reports success/error. [Assignee editing](../repo/app/modules/components/ticket-assigned/assigned-to.directive.coffee), lines 14–82, sets `assigned_to`; self-assignment calls the same save with the current user ID. An authorized user can choose another assignee or remove the current one. No “one winner” ownership protocol is added by the UI.

The queue has a narrower asynchronous boundary: it stores a mutable scope/property target on a singleton service. The success callback uses the service's current target, rather than a captured task ID or view generation. Source-level inference: a response that arrives after navigation and a new `setObject` can replace the newer target with an older clone. This was not reproduced in a running browser. A local serial promise chain also does not serialize edits from another tab, machine or API client.

## Boards, failed saves and WIP semantics

[Taskboard movement](../repo/app/coffee/modules/taskboard/main.coffee), lines 628–659, updates its local task service, sends a versioned save with order headers, applies returned ordering and refreshes statistics. [The local move](../repo/app/coffee/modules/taskboard/taskboard-tasks.coffee), lines 76–113, changes status, story and order before the request succeeds. [Inline assignment](../repo/app/coffee/modules/taskboard/main.coffee), lines 362–378, likewise replaces a local model before saving. The inspected handlers have success callbacks but no corresponding error rollback/refetch; the moving-task flag is cleared only on success in that move path.

[Kanban movement](../repo/app/coffee/modules/kanban/main.coffee), lines 617–655, calls [the local story move](../repo/app/coffee/modules/kanban/kanban-usertories.coffee), lines 150–190, which changes status/swimlane/order before HTTP completion. [Its resource request](../repo/app/coffee/modules/resources/userstories.coffee), lines 112–129, sends IDs, destination and positioning, without each story's expected version. The move handler has no error branch restoring that local move. A global error/conflict notice does not restore authoritative state. Server-side differences between normal edits and bulk movement are traced in the companion backend assessment.

[Version-conflict handling](../repo/app/coffee/app.coffee), lines 738–756, detects a 400 response with a version field, shows a translated notice and rejects the response. It does not itself fetch the latest record or reconcile local changes. Detail clone-on-success and optimistic board movement therefore have different recovery behavior. The report does not claim every screen shares either approach.

[WIP configuration](../repo/app/modules/components/wip-limit-selector/wip-limit-selector.controller.coffee), lines 16–28, edits the selected status/swimlane limit and reloads project-related data. [WIP markers](../repo/app/coffee/modules/kanban/main.coffee), lines 809–847, count rendered cards and display `one-left`, `reached` or `exceeded`. The move path has no WIP admission condition. This is explicit advisory feedback; filtering/rendering also means a DOM card count should not be used as shared capacity authority.

## Live updates and missed-event recovery

[Event configuration and connection setup](../repo/app/coffee/modules/events.coffee), lines 20–68, can disable events when no URL is configured, supports relative WebSocket URLs and replaces an old connection. [Application initialization](../repo/app/coffee/app.coffee), lines 963–985, and [login success](../repo/app/coffee/modules/auth.coffee), lines 280–301, start that connection. [Transport authentication](../repo/app/coffee/modules/events.coffee), lines 235–250, sends a bearer token plus the generated session ID.

[Session generation and HTTP configuration](../repo/app/coffee/app.coffee), lines 20–26 and 590–606, create a browser identifier and attach it to requests/events. [Ping/pong](../repo/app/coffee/modules/events.coffee), lines 123–155, reconnects after missed socket heartbeats. These mechanisms can detect a lost browser connection. They cannot establish whether an agent is making progress, retain work ownership or reject a stale worker's completion.

[Subscription/send behavior](../repo/app/coffee/modules/events.coffee), lines 165–230, queues unsent messages in memory, retains one callback per routing key and clears the pending message list before sending it. [Connection handlers](../repo/app/coffee/modules/events.coffee), lines 235–284, reauthenticate and recreate notification subscriptions, with jittered retries and a maximum error count. They do not iterate existing project subscriptions to resend them, request a replay cursor or announce a board resnapshot. After transport interruption, this client does not itself establish recovery of those subscriptions or changes missed while disconnected. An external gateway might provide additional behavior; that gateway was not included in this frontend review.

[Kanban subscriptions and event application](../repo/app/coffee/modules/kanban/main.coffee), lines 259–277 and 458–488, refetch a list and reconcile affected/new stories when a relevant event arrives. [Taskboard subscriptions](../repo/app/coffee/modules/taskboard/main.coffee), lines 380–393, reload records/statistics on events. These are live invalidation paths, not a persisted event replay protocol.

[Project refresh](../repo/app/modules/services/project.service.coffee), lines 60–68, runs every ten minutes while active, pauses on inactivity and refetches on return. It fetches the project, not a universal task/board snapshot. [A backlog fallback](../repo/app/coffee/modules/backlog/main.coffee), lines 631–637, reloads sprint/statistic data after a move if events are disconnected. This useful local fallback should not be generalized into recovery for every screen.

## Discussion, blockers, acceptance and cancellation

[Notifications](../repo/app/modules/notifications/notifications.service.coffee), lines 20–101 and 111–142, map assignment, mention, watcher, membership and comment events into links and paginated queries. [The resource](../repo/app/modules/resources/users-resource.service.coffee), lines 142–175, requests unread items and sends individual/all read markers. This supplies later inspection of server records alongside ephemeral desktop notifications. Marking a notice read is not an agent result acknowledgement. The backend assessment separately records a permission defect in the individual read-marker route.

[Activity retrieval](../repo/app/modules/history/activity/activity.service.coffee), lines 22–60, loads and appends paginated entries through [the history resource](../repo/app/modules/resources/history-resource.service.coffee), lines 12–27. [Task detail](../repo/app/partials/task/task-detail.jade), lines 77–107, combines rich description, custom fields, attachments and history. [Story detail](../repo/app/partials/us/us-detail.jade), lines 116–163, adds related tasks, estimation and multiple assignees. This is useful durable context through the backend; no required handoff schema or accepted artifact/attempt tuple is introduced by these views.

[Blocking](../repo/app/coffee/modules/common/lightboxes.coffee), lines 209–278, writes an `is_blocked` flag and note through the same detail transformation. It supplies neither a decision owner nor a typed answer/resume protocol. [Related-task deletion](../repo/app/coffee/modules/related-tasks.coffee), lines 78–91, confirms and deletes a record. This cannot terminate an external agent. Ordinary status controls submit status changes without a native reviewer decision or verification-result envelope; the backend's task/story completion calculations remain a separate boundary.

## Access, human usability and operation

[HTTP requests](../repo/app/coffee/modules/base/http.coffee), lines 17–72, add a bearer token and language; GET caching deduplicates concurrent requests and is cleared afterward. [Auth storage/login/logout](../repo/app/coffee/modules/auth.coffee), lines 96–188, retains user/access/refresh data and removes credentials on logout. [Browser storage](../repo/app/coffee/modules/base/storage.coffee), lines 17–42, uses localStorage. [The refresh interceptor](../repo/app/coffee/app.coffee), lines 609–707, shares an in-progress refresh, replaces credentials and retries the original request, or redirects to login. These are client conveniences; the server must authenticate and authorize each replayed operation.

[Permission-aware presentation](../repo/app/modules/services/check-permissions.service.coffee), lines 18–23, uses the loaded project's `my_permissions`; task editing controls also check archive state. Hiding an action is not an authorization boundary. Permission snapshots can age between project fetches, and a direct API caller can bypass every visual control. Host and project isolation must be evaluated in the backend and deployment.

[Search](../repo/app/coffee/modules/search.coffee), lines 25–104, groups project resource results and aborts its previous request on a new query. [Backlog markup](../repo/app/partials/backlog/backlog.jade), lines 10–80, includes counts, filters, search and a burndown area. Detail neighbor links, story/epic context, translation keys and keyboard handling for related-task entry help normal human navigation. A concrete labeling defect appears in [WIP selector markup](../repo/app/modules/components/wip-limit-selector/wip-limit-selector.jade), lines 13–39: icon buttons use `arial-label` rather than `aria-label`. Static inspection does not establish keyboard, screen-reader, small-screen or visual acceptance of the complete product.

[Example configuration](../repo/conf/conf.example.json) requires an API and can leave events disabled. [The Nginx configuration](../repo/docker/default.conf) serves the built SPA and falls back to its index. [Environment substitution](../repo/docker/config_env_subst.sh) and [the template](../repo/docker/conf.json.template) configure API, event URL, subpath, registration and plugins. They do not start the backend, database, broker or event gateway.

[The Dockerfile](../repo/docker/Dockerfile), lines 7–47, downloads frontend-dist 6.10.3 rather than building this source commit. It also downloads plugin archives named 6.10.0 while its extraction globs name 6.10.1. That mismatch is a source-level packaging risk; archive contents and a successful build were not verified. The package's Gulp/CoffeeScript/Jade/Karma/Babel/node-sass inputs add compatibility work when selecting a modern development environment. A built distribution must not be assumed identical to this reviewed Git tree merely because its version label matches.

## Test-source evidence and adoption work

[Kanban assertions](../repo/app/coffee/modules/kanban/main.spec.coffee), lines 79–113 and 213–249, check archived filtering, removing a story hidden after an event, adding/replacing stories and refreshing counts using mocked resources. [Project tests](../repo/app/modules/services/project.service.spec.coffee), lines 80–104 and 172–202, assert slug switching, periodic refresh and inactivity/return behavior. [Permission tests](../repo/app/modules/services/check-permissions.service.spec.coffee), lines 36–52, check a supplied permission array. [Activity tests](../repo/app/modules/history/activity/activity.service.spec.coffee), lines 65–84, check loading and clearing entries. These are selected source assertions, not executed integration evidence for a server, socket gateway, failed optimistic mutation or concurrent assignment.

Retain the connected planning/detail/history experience. Add clear authoritative-save and connection status, consistent failed-save refetch/rollback, view-generation guards for late responses and an explicit reconnect reconciliation policy. Preserve advisory WIP labels unless the backend gains capacity enforcement. Agent claims, attempts, recovery and acceptance belong in a shared authority; the UI should display those records rather than infer them from assignees, columns or socket liveness. Verify a reproducible build/distribution path and representative desktop/mobile/keyboard behavior before adopting the combined product for daily operations.
