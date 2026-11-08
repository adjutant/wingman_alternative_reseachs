# Plane MCP adapter task management assessment

Repository: https://github.com/makeplane/plane-mcp-server

Commit: `5c3467adb36fe15a2ef8f9df6fb9f5dc24b6d881`.
Baseline: [Shared task management for an agent organization](../../../AGENT_TASK_MANAGEMENT.md).
Review: November 9, 2026. Full local checkout; static implementation and selected test-source review.
Candidate code, dependencies, tests and services were not installed or run.

## Fit decision and assessment boundary

This repository is an agent interface to Plane, not an independent task-management authority.
It makes substantial project-management operations available through MCP: projects, work items, relations, cycles, milestones, comments, pages, attachments and other resources.
It is useful when Plane is already the shared record and agents need structured access to it.

It does not add exclusive task claims, execution attempts, worker leases, delegation supervision, task acceptance or recovery scheduling.
Its normal assignment helper is a retrieve-then-update operation, without a conditional version or transaction spanning both API calls.
Installing this adapter therefore does not establish safe concurrent allocation among independent workers.

The adapter is MIT licensed.
That license does not establish the availability or licensing of every resource in a particular Plane deployment.
The code explicitly handles plan restrictions and workspace/project governance differences.
The separate Plane codebase assessment remains necessary for persistence, permissions, lifecycle enforcement and human usability supplied by the product.

Verdicts below distinguish an exposed API operation from behavior implemented here.
An adapter verdict does not assert that the upstream product lacks a feature.
No live Plane service, MCP client or browser was used to validate these findings.

## Architecture and source scope

The package declares Python `>=3.10` and pins FastMCP 3.2.0, MCP 1.28.1 and `plane-sdk` 0.3.1.
Server factories configure authentication, common middleware and tool registration.
The middleware logs calls, repairs string-encoded arguments and checks arguments against the selected action.
Resource functions build SDK request models and call a credential-bound Plane client.
See [package metadata](../repo/pyproject.toml), [server factories](../repo/plane_mcp/server.py) and [middleware](../repo/plane_mcp/middleware.py).

There are 30 declared resource tools and 207 action declarations at this commit.
The [static catalogue inventory](catalogue.json) records their names, source hashes and declaration ranges.
It was produced by parsing Python syntax, without importing candidate modules.
It establishes the declared surface, not successful runtime registration or correct implementation of every action.

The explicit registry fixes catalogue order and builds action and legacy-name maps.
Resource modules describe their actions through a shared declaration type; descriptions and conservative annotations are generated from it.
Registration also strips output schemas and installs optional retired-name transforms.
This reduces advertised tool count while retaining a broad API surface.
See [registry](../repo/plane_mcp/tools/registry.py), [registration](../repo/plane_mcp/tools/__init__.py) and [specification helpers](../repo/plane_mcp/toolkit/spec.py).

Task data is not stored by this process.
Its persistence is an OAuth token store: configured Redis variants or an in-memory fallback.
Projects, work items, comments, relations and history remain in Plane.
The MCP process does not execute a worker, own the backlog database or keep a durable task-operation journal.
See [client construction](../repo/plane_mcp/client.py), lines 47–99, and [token storage](../repo/plane_mcp/storage.py), lines 146–263.

The review traces the core work-item lifecycle, assignments, dependencies, comments/mentions, activity, project operations, planning helpers, selected attachment paths, authentication/context and server configuration.
Other resources received declaration inventory and targeted interface review.
The SDK and upstream Plane implementation were not audited as part of this adapter report.

## Requirement verdicts

These verdicts assess the adapter in its stated role.
They do not convert advertised SDK operations into proof of upstream invariants.

| Requirement | Verdict | Mechanism and boundary |
|---|---|---|
| T01 | Similar | Project operations expose identifier, description, project lead, default assignee, features and workspace-scoped listing. Stable records and access are delegated to Plane; this process adds no project registry or portfolio authority. [Project surface](../repo/plane_mcp/tools/project.py), lines 29–107 and 194–300. |
| T02 | Similar | Work-item requests expose name, description, parent, state, priority, dates, estimate, assignees, labels and external IDs. Records are stored and validated upstream; no local task or execution schema exists. [Fields/actions](../repo/plane_mcp/tools/workitem.py), lines 53–125; [writes](../repo/plane_mcp/tools/workitem.py), lines 254–283 and 351–383. |
| T03 | Similar | The adapter passes a parent ID and supplies an epic/child query recipe. It does not validate parent aggregation, hierarchy cycles or child acceptance before closure. [Instructions](../repo/plane_mcp/instructions.py); [parent payload](../repo/plane_mcp/tools/workitem.py), lines 254–283. |
| T04 | Resembles | Built-in dependencies and custom relation definitions have list/create/remove operations. The adapter has no ready-work predicate, claim-time blocker guard or dependency-cycle validator; upstream enforcement is outside this report. [Relations](../repo/plane_mcp/tools/workitem_relation.py), lines 47–85 and 177–239. |
| T05 | Resembles | Credentials identify Plane users, and member reads can filter bots and inspect roles. The adapter creates no permanent agent roster, agent-session record or task-attempt identity. Shared credentials make workers appear under the same upstream account. [Client context](../repo/plane_mcp/client.py); [member surface](../repo/plane_mcp/tools/member.py), lines 15–78. |
| T06 | Similar | A broad structured MCP surface, literal action sets, parameter declarations, coercion, corrected PQL errors and pagination aid agents. Errors can be returned as strings/dictionaries, and one resource schema contains fields for several actions. No task CLI is supplied beyond launching transports. [Middleware](../repo/plane_mcp/middleware.py), lines 19–109; [paging](../repo/plane_mcp/toolkit/paging.py), lines 44–135. |
| T07 | Absent | There is no exclusive claim action or local ownership authority. `manage_assignee` retrieves a set and replaces it; competing changes can overwrite each other. Generic update also accepts complete assignee/state values. [Assignment path](../repo/plane_mcp/tools/workitem.py), lines 385–410; [update](../repo/plane_mcp/tools/workitem.py), lines 367–374. |
| T08 | Resembles | Counts/grouping, cycles and estimates expose planning information. The declared catalogue has no worker queue, WIP admission, capability dispatch or per-agent capacity enforcement. [Work-item count](../repo/plane_mcp/tools/workitem.py), lines 311–327; [catalogue](catalogue.json). |
| T09 | Resembles | An agent can create children, assign members and link records through Plane. There is no parent-agent execution relationship, delegation acknowledgement, child-result join or coordinator recovery protocol. [Work-item create/parent](../repo/plane_mcp/tools/workitem.py), lines 254–283 and 351–360; [catalogue](catalogue.json). |
| T10 | Similar | Comments, external links, linked pages and attachment reads/uploads carry context. Immutable revision selection is the caller's responsibility, and the adapter provides no task-context snapshot or verified artifact bundle. [Links](../repo/plane_mcp/tools/workitem_link.py); [pages](../repo/plane_mcp/tools/page.py), lines 24–69; [attachment helpers](../repo/plane_mcp/tools/workitem_attachment.py), lines 65–162. |
| T11 | Resembles | Agents can post/edit comments and work logs, and attach results. No structured attempt checkpoint, handoff, verification or terminal result is required. [Comment writes](../repo/plane_mcp/tools/workitem_comment.py), lines 106–158; [catalogue](catalogue.json). |
| T12 | Resembles | Mention tokens are validated against active project members and rendered into Plane mention elements. Activity/comments support polling. Notification delivery, acknowledgement and missed-message recovery are not implemented here; transport SSE is not a task event subscription. [Mention check](../repo/plane_mcp/toolkit/mentions.py), lines 158–180; [activity](../repo/plane_mcp/tools/workitem_activity.py). |
| T13 | Resembles | Relations, comments, pages and states can represent obstacles and decisions. There is no structured open-question, escalation recipient, response lifecycle or blocker owner in this adapter's operation set. [Relations](../repo/plane_mcp/tools/workitem_relation.py); [catalogue](catalogue.json). |
| T14 | Absent | The adapter has no worker heartbeat, execution lease, stale-task sweep or allocation expiry. OAuth access-token expiration is an access mechanism, not task recovery. [Catalogue](catalogue.json); [OAuth verifier](../repo/plane_mcp/auth/plane_oauth_provider.py), lines 135–215. |
| T15 | Absent | Task writes carry no attempt credential, expected task version or idempotency key. External IDs are forwarded metadata; this code does not establish deduplication or reject stale workers. [Write payload/update](../repo/plane_mcp/tools/workitem.py), lines 254–283 and 367–410; [annotations](../repo/plane_mcp/toolkit/spec.py), lines 49–70. |
| T16 | Resembles | CRUD/archive calls and retained upstream comments permit manual reconciliation. Multi-call helpers have no rollback journal; there is no failed/interrupted execution model or worker cancellation. OAuth state can be durable in Redis, but that does not recover work attempts. [Cycle helper](../repo/plane_mcp/tools/cycle.py), lines 235–293; [token fallback](../repo/plane_mcp/storage.py), lines 250–263. |
| T17 | Similar | Remote streamable HTTP and local stdio can access one Plane authority from different hosts. HTTP binds all interfaces on port 8211. TLS, proxy operation, upstream availability and cross-process token configuration still need deployment work; no distributed task authority is added. [HTTP host](../repo/plane_mcp/__main__.py), lines 145–200; [client](../repo/plane_mcp/client.py), lines 66–99. |
| T18 | Resembles | Work-item activity reads expose upstream history, and structured logs label tool/resource/action plus available identity context. Logs are not an atomic task audit ledger and credential identity does not distinguish workers sharing a key. [Activity](../repo/plane_mcp/tools/workitem_activity.py); [logging](../repo/plane_mcp/middleware.py), lines 112–155; [log identity](../repo/plane_mcp/__main__.py), lines 22–51. |
| T19 | Resembles | List/retrieve/search/count and preserved cursors support inspection through an MCP client. This repository has no human board UI or independent project dashboard; Plane's browser usability requires its own assessment. [Work-item reads](../repo/plane_mcp/tools/workitem.py), lines 284–349; [registry](../repo/plane_mcp/tools/registry.py). |
| T20 | Similar | The interface exposes cycles, milestones, modules, releases, estimates and due dates. Those planning records and their business rules belong to Plane; local cycle completion merely updates an end date. [Cycle operations](../repo/plane_mcp/tools/cycle.py), lines 38–81 and 265–293; [milestones](../repo/plane_mcp/tools/milestone.py), lines 29–56; [catalogue](catalogue.json). |
| T21 | Absent | There is no task submission/acceptance operation that binds criteria, evidence, reviewer and delivered revision. Completion can be requested by updating a state ID. Upstream workflows may add rules, but this adapter establishes none. [Update](../repo/plane_mcp/tools/workitem.py), lines 367–374; [catalogue](catalogue.json). |
| T22 | Similar | PAT/OAuth validation and credential-bound workspace context are real interface boundaries; Plane remains responsible for resource permissions. Providers construct read/write scope claims, and all tools are registered. There is no per-agent local policy or review-only catalogue. OAuth selects the first returned installation. [Header validation](../repo/plane_mcp/auth/plane_header_auth_provider.py); [OAuth selection](../repo/plane_mcp/auth/plane_oauth_provider.py), lines 167–209; [factories](../repo/plane_mcp/server.py), lines 58–104. |
| T23 | Similar | Explicit resource modules, action declarations, custom relation definitions and custom-property/type operations provide extension points. There is no configurable agent-role or execution-workflow engine; new adapter behavior needs code and compatible API support. [Spec](../repo/plane_mcp/toolkit/spec.py); [relation definitions](../repo/plane_mcp/tools/workitem_relation.py), lines 109–175; [catalogue](catalogue.json). |
| T24 | Similar | Small Python adapter, pinned core dependencies, shared factories, optional durable OAuth storage and substantial contract-test source reduce integration work. It still requires Plane and credentials; HTTP also builds OAuth configuration. The standalone SSE mode has no startup branch at this revision. No install/runtime compatibility was tested. [Package](../repo/pyproject.toml); [entry point](../repo/plane_mcp/__main__.py), lines 116–204; [storage](../repo/plane_mcp/storage.py), lines 146–263. |

## Lifecycle and alternate mutation paths

A connection resolves a Plane client and workspace slug from its authenticated token, or from environment variables in stdio mode.
Projects and work items can then be listed, retrieved and created through SDK calls.
There is no independent local task copy to reconcile with the service.
The successful result and durable record are supplied by Plane, rather than by a local database transaction.
See [client binding](../repo/plane_mcp/client.py), lines 20–99, and [work-item dispatch](../repo/plane_mcp/tools/workitem.py), lines 284–383.

A worker can search by PQL, resolve members/types/states and update an item's assignees or parent.
That operation is not a claim.
`manage_assignee` reads the current IDs, removes requested IDs, adds requested IDs and writes a whole list.
Two callers reading the same old list can lose one another's additions.
No lock, expected revision or conditional API parameter is passed by this helper.
The same issue applies to its label-set merge.
The adapter does not establish whether upstream facilities could provide a stronger alternative.
See [set merge](../repo/plane_mcp/tools/workitem.py), lines 385–410.

Progress can be posted as comments or linked pages/files.
The mention helper checks project membership before writing a mention, then the comment function sends generated HTML through the SDK.
This improves addressing, but a rendered chip is not proof of notification delivery or recipient action.
Comments and links can be edited or deleted; none is an immutable execution checkpoint.
See [comment dispatch](../repo/plane_mcp/tools/workitem_comment.py), lines 83–158, and [mention validation](../repo/plane_mcp/toolkit/mentions.py), lines 158–180.

Completion is an ordinary state update.
The adapter does not fetch criteria, require verification, check child results or bind approval to a commit before making that request.
Deleting or archiving records is also an ordinary API operation, without an adapter-level worker stop/acknowledgement protocol.
The baseline needs this lifecycle implemented by another authority or a coordination service above the adapter.
See [state/delete/archive](../repo/plane_mcp/tools/workitem.py), lines 367–383.

## Concurrency, retry and recovery conditions

### One tool call can contain several writes

Cycle membership management can add several items and then remove others one by one.
A later failure does not undo successful earlier requests.
Archive retrieves the cycle, may first set its end date, then calls archive.
An archive failure can leave the changed end date behind.
There is no adapter transaction, compensation log or restartable operation ID for either sequence.
See [cycle helpers](../repo/plane_mcp/tools/cycle.py), lines 235–293.

The same caution applies to composing a task workflow across several tools.
Creating a child, assigning it, posting a comment and changing the parent state are separate service requests.
An interrupted agent must inspect upstream state before continuing.
The adapter has no durable record of which steps its prior conversation intended or completed.

### Payload omission is deliberate but not universal patch expressiveness

Work-item writes omit sentinel empty strings and zero values.
Explicit empty assignee/label lists are retained, and explicit null dates clear dates.
Other fields such as description and parent are normalized through `opt`, so the same interface does not expose every conceivable clearing operation.
A request that omitted a field is different from one that successfully cleared it.
See [payload construction](../repo/plane_mcp/tools/workitem.py), lines 254–283, and [sentinel helper](../repo/plane_mcp/toolkit/runtime.py), lines 64–66.

`external_id` and `external_source` are sent to the API but do not become idempotency keys in adapter code.
The annotations conservatively mark consolidated tools non-idempotent.
When a response is lost, the caller cannot infer that a create/comment/upload failed merely because the MCP call did not return.
It needs a read-back/reconciliation strategy and upstream guarantees appropriate to that operation.
See [work-item writes](../repo/plane_mcp/tools/workitem.py), lines 254–283 and 351–360, and [annotations](../repo/plane_mcp/toolkit/spec.py), lines 49–70.

### Credential durability is separate from work durability

HTTP token storage supports Redis, including URL, password and optional AWS credential-provider paths.
Configured Redis is checked at startup.
If no backing store is configured, the fallback is process memory and its tokens are lost on restart.
Task records remain in Plane, but clients may need to authenticate again.
There is no task lease or abandoned-work reaper associated with this token cache.
See [storage construction](../repo/plane_mcp/storage.py), lines 146–263.

HTTP mode creates OAuth and API-key applications and also mounts legacy SSE.
It creates the OAuth factory even if an operator only intends to use the API-key endpoint.
The OAuth provider validates its required client settings at construction.
Remote deployment therefore needs the actual factory/configuration graph, not just a PAT endpoint copied into a client.
See [HTTP construction](../repo/plane_mcp/__main__.py), lines 145–173, and [OAuth required settings](../repo/plane_mcp/auth/plane_oauth_provider.py), lines 326–332.

The entry-point enum includes `sse`, but `main` has startup branches only for stdio and HTTP.
Selecting standalone SSE reaches the end without starting a server.
Legacy SSE remains available through the HTTP assembly.
This is a static control-flow finding; no candidate command was executed.
See [entry point](../repo/plane_mcp/__main__.py), lines 116–204.

## Identity, access and artifact boundaries

Header/PAT validation calls Plane's current-user endpoint and requires a workspace header.
That verifies the key, not membership of the supplied workspace inside the adapter; resource authorization remains with Plane's API.
The returned access token carries read/write scopes set by the provider.
The adapter does not derive an independent least-privilege agent policy from those scope labels.
See [PAT verifier](../repo/plane_mcp/auth/plane_header_auth_provider.py), lines 19–73.

OAuth verification reads the user and application installations, selects the first installation and records its workspace in token claims.
This creates a connection binding rather than a per-tool arbitrary workspace argument.
The client context uses those claims even when the slug is empty, avoiding silent fallback to a different environment workspace.
Several projects can be addressed within that bound workspace.
A multi-workspace operator needs to verify which installation was selected.
See [OAuth binding](../repo/plane_mcp/auth/plane_oauth_provider.py), lines 167–209, and [context](../repo/plane_mcp/client.py), lines 20–99.

All server factories register the common catalogue.
Read/destructive/idempotency annotations are hints derived across every action of a resource, not permission enforcement for individual operations.
The shared governance helpers explain upstream plan/scope refusals; they are not an agent authorization system.
See [configuration](../repo/plane_mcp/server.py), lines 58–104; [annotations](../repo/plane_mcp/toolkit/spec.py), lines 49–70; and [governance](../repo/plane_mcp/toolkit/governance.py), lines 48–132.

Attachment handling adds actual outbound I/O beyond basic API wrapping.
URL upload uses bounded fetching, redirect checks and direct-connection DNS pinning.
In proxy mode, hostname network safety is delegated to the proxy; private literal IPs are still rejected locally.
This is an explicit deployment boundary, not proof that every supplied URL is safe in every proxy configuration.
See [upload](../repo/plane_mcp/tools/workitem_attachment.py), lines 128–162, and [fetch path](../repo/plane_mcp/attachments.py), lines 211–274 and 308–320.

The attachment read helper fetches a returned download URL with `requests.get`, then checks the buffered payload against image/text limits.
Those limits bound what is returned to the model, but do not bound the network read before buffering.
It also uses a different path from the DNS-pinned URL-upload helper.
This review did not certify all attachment, OAuth, proxy or SDK internals.
See [read helper](../repo/plane_mcp/tools/workitem_attachment.py), lines 91–125.

## Agent and human usability

The adapter makes several deliberate agent-facing improvements.
Its generated action descriptions name required/optional fields.
Middleware can repair JSON values encoded as strings and reject valued arguments that the selected action does not accept.
PQL errors include the failed query and reference material.
Paged work-item reads preserve counts and cursor fields, avoiding a first page that looks like a complete result.
See [middleware](../repo/plane_mcp/middleware.py), lines 19–109, and [paging](../repo/plane_mcp/toolkit/paging.py), lines 44–135.

These improvements do not eliminate interface cost.
An agent must discover UUIDs for states, types and members, choose an action from a large shared schema, and perform multi-step work through separate calls.
Several validation refusals are strings or error dictionaries rather than an explicitly marked MCP execution error in adapter code.
A consuming agent should inspect returned content as well as protocol failure status.
See [validation return](../repo/plane_mcp/middleware.py), lines 36–45; [required-field helper](../repo/plane_mcp/toolkit/runtime.py), lines 19–35; and [PQL failure](../repo/plane_mcp/toolkit/paging.py), lines 107–124.

One documentation inconsistency is visible at the pinned revision.
The README uses `state__group` in list-filter examples, while the work-item footer explicitly says that it is a grouping key and filtering on it is rejected.
Agents copying the example can spend a round trip repairing a query the tool description already warns against.
See [README examples](../repo/README.md), lines 106–130, and [work-item guidance](../repo/plane_mcp/tools/workitem.py), lines 143–157.

For the human owner, this repository supplies no board, task-detail browser, review interface or portfolio view.
Those experiences belong to Plane or the MCP client.
The ability to query a count is useful for reporting but does not establish that the complete project is understandable or manageable in a particular UI.
No candidate user interface was rendered or tested.

## Completeness, design quality and test-source evidence

As an API adapter, the design is cohesive.
The registry, declarations, common factories, typed SDK models and response helpers reduce repeated plumbing.
Conservative annotations avoid advertising destructive resources as read-only.
Credential-bound workspace selection is separated from resource arguments.
The scope is broad, but breadth must not be mistaken for an implemented autonomous-work lifecycle.

The source includes useful contract tests:

- Catalogue tests pin resource order, require matching declarations/signatures and check action/parameter consistency. [Conformance source](../repo/tests/tools/test_conformance.py), lines 34–143.
- Dispatch tests parameterize declared actions against a spy that binds the genuine SDK signature and validates argument types. They also require missing-argument calls to return before hitting the SDK. The spy's default response is deliberately permissive and does not model real backend constraints. [Dispatch assertions](../repo/tests/tools/test_dispatch.py), lines 119–153; [spy](../repo/tests/tools/_spyclient.py), lines 24–55 and 106–207.
- Pagination tests check cursor preservation and refuse a response that lacks the promised pagination fields. [Paging source](../repo/tests/toolkit/test_paging.py), lines 50–78.
- Argument tests check wrong-action parameters, accepted count scope, absent actions and literal-action behavior. [Validation source](../repo/tests/test_argument_validation.py), lines 50–125.
- Client tests check that OAuth/header/stdio report the same workspace they use and that a missing token slug does not borrow the environment's slug. [Context source](../repo/tests/test_client.py), lines 45–92.

These are inspected source assertions, not test results from this assessment.
The live integration test explicitly requires credentials and writes/deletes real project data; it was not run.
Its existence does not establish success against the user's Plane edition or configured server.
No backend concurrency, stale-worker, task-acceptance or recovery guarantees were demonstrated by this review.
See [integration scope](../repo/tests/test_integration.py), lines 1–95.

## Adoption work and useful components

Use this adapter when Plane is the chosen management system and agents need a coherent MCP bridge.
Keep the explicit catalogue, typed payloads, pagination envelopes, parameter correction and mention handling.
Verify the target Plane version/edition and required API resources before relying on the full advertised surface.

For autonomous task coordination, put authoritative claim/attempt state, ownership transfer, stale-worker fencing, recovery and acceptance in Plane extensions or a separate service.
Do not implement exclusive allocation by reading assignees and writing a replacement list.
Add explicit retry/reconciliation contracts for multi-step operations and distinguish the Plane user's identity from each worker and execution attempt.
Provide a typed handoff/result operation if completion must include evidence and reviewer approval.

The [review ledger](review.json) records the inspected ranges, source hashes and all 24 verdicts.
The catalogue inventory covers declarations across all resources; the detailed lifecycle findings cover the named paths, not an every-line or every-endpoint audit.
