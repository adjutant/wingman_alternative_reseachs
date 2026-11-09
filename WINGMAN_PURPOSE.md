# Wingman purpose

Wingman is a personal software-development organization of autonomous Codex agents.
One person directs the organization through conversation.
The agents research, clarify, define, plan, implement, test, and deliver products.
They maintain shared records and ask the human for decisions when needed.

Several products can progress at once.
Each product has its own context, leaders, assignments, specifications, and deliverables.
An organization-wide layer maintains the portfolio and the human conversation.
Telegram is the main human channel.
An agent directory, chat application, project dashboard, and executive dashboard provide connected views.
Each agent also has a detailed workspace. Web and mobile interfaces provide access to these views.

## 1. Human experience

The human talks to Butler through **@KraIOBot** on Telegram.
Requests use ordinary language. Examples include:

- “Build a mortgage loan origination system for new houses. Support conventional and Islamic lending.”
- “Create an analytics product similar to Redash.”
- “Make the CRM mockup usable by pilot customers.”
- “What blocks the mobile application?”
- “Continue yesterday's project. Change the onboarding flow.”

Wingman identifies the project and retrieves its context.
Butler returns questions, decisions, progress, and delivery information.
The human can continue the conversation over time.
The agents preserve the product context between requests.

The human controls goals, priorities, business decisions, and acceptance.
The organization handles routine research, planning, delegation, implementation, testing, and coordination.

## 2. Standing agents and roles

Each role is a separate Codex agent with its own identity and conversation.
Agents work independently. They communicate through shared records and rooms.

| Level | Roles | Responsibility |
|---|---|---|
| Organization | Butler and ProjectMaster | Human communication and portfolio coordination |
| Project leadership | ProductMaster and TechMaster | Product definition and technical coordination |
| Specialist execution | BackendCoder, FrontendCoder, MobileCoder, and TestMaster | Implementation and verification |

A project can have several instances of the same specialist profile.
Each instance has its own identity, assignment, and history.
Team size follows the workload.
A small mockup needs less process than a large integrated product.

Wingman can add profiles, responsibilities, and team structures.
New agents can receive work, join discussions, report progress, and appear in relevant views.
The directory, tracker, rooms, and dashboards must support those changes.

### Agent directory

The directory shows identity, profile, project, team, current activity, and working relationships.
It links each agent to tasks, conversations, a timeline, and a detailed workspace.
The human can view the organization or one project's team.

### Butler

Butler represents Wingman to the human.
It receives Telegram requests and passes them to ProjectMaster.
It carries questions and notifications from the organization to the human.
It returns answers to the responsible agent with the correct project and conversation context.
One Butler conversation can cover several projects.

### ProjectMaster

ProjectMaster maintains the shared project registry.
It decides whether a request continues an existing project or starts a new one.
It creates the required project leadership and tells Butler when a new project starts.

ProjectMaster also supervises ongoing work.
It checks progress, follows up with agents, helps resolve blockers, and escalates human decisions through Butler.
It maintains a view of active products, assignments, progress, and required attention.

### ProductMaster

Each project has a ProductMaster.
ProductMaster investigates the product and defines successful delivery.
It reads existing material, researches the domain, identifies uncertainty, and asks clarification questions.
The depth of discovery follows the size and consequences of the request.

ProductMaster writes scope, specifications, test scenarios, and the definition of done.
It remains available during implementation.
It answers product questions and discusses changes with TechMaster and specialists.

### TechMaster

Each project has a TechMaster.
TechMaster translates the product definition into technical work.
It reads the scope and specifications and resolves uncertainty with ProductMaster.
It creates tickets, selects specialists, and coordinates implementation and integration.
It can discuss decisions directly with ProductMaster.
Both leaders escalate decisions that require human judgment through Butler.

### Specialists

| Profile | Responsibility |
|---|---|
| BackendCoder | Services, APIs, data models, and databases. Use the language and database appropriate to the product. |
| FrontendCoder | Websites and web applications. TypeScript is the main language. |
| MobileCoder | Mobile applications. Flutter and React Native are the main frameworks. |
| TestMaster | Test cases, manual tests, automated tests, integration checks, and browser verification. Tools can include Playwright. |

Workers read their assignment and project context.
They update ProjectTracker and discuss progress or problems in the project room.
TestMaster verifies functional behavior and product acceptance.
Security and DevOps remain outside TestMaster's responsibilities.

## 3. Project intake and continuity

Every request uses the shared project registry.

| Request | Required action |
|---|---|
| New product idea | Establish a project and start discovery. |
| Explicit request to build a product | Create the project, inform the human, and organize its team. |
| Change to an existing product | Continue that project with its stored context. |
| Progress question | Consult the tracker and responsible agents. |
| Ambiguous reference | Ask which project or outcome the human means. |

ProductMaster reads the project's scope, specifications, directives, and notes before interpreting a follow-up.
Previous decisions and completed work remain part of the context.
Wingman reassesses major changes in direction.
A small CRM improvement and a transformation into a lending product need different discovery work.

## 4. Proportionate discovery

Discovery turns an initial request into a sufficiently clear product direction.

| Situation | Discovery work |
|---|---|
| Bounded mockup | Identify the audience, screens, demonstrated flows, and required fidelity. |
| Modest product change | Read existing context. Clarify affected behavior and acceptance criteria. |
| Substantial new product | Research users, domain, market, technology, workflows, and important tradeoffs. |
| Major transformation | Reassess product boundaries and previous assumptions. |

ProductMaster investigates facts independently when possible.
It presents meaningful choices to the human.
Research supports the questions. Answers become project knowledge.

### Clarification cycle

1. ProductMaster records its understanding, uncertainties, and questions.
2. Butler presents the questions through Telegram.
3. The human answers in the same conversation.
4. Butler routes the answers to the relevant ProductMaster.
5. ProductMaster updates the understanding and identifies any further questions.
6. ProductMaster writes scope and specifications when the direction is sufficiently clear.

Questions, answers, and context remain associated with the correct project.
This requirement also applies when several discovery conversations run at once.

A loan origination system needs discovery about users, jurisdiction, lending structures, workflows, responsibilities, and integrations.
It also needs acceptance criteria.
The initial mention of conventional and Islamic mortgages sets a direction.
It does not supply a complete product definition.

## 5. Product definition and technical work

ProductMaster maintains these records:

- Purpose and intended users.
- Scope and component boundaries.
- Functional behavior and important workflows.
- Decisions and constraints.
- Test cases and acceptance scenarios.
- Definition of done.

TechMaster creates technical tickets in ProjectTracker.
Each ticket identifies the responsible worker, product context, and expected result.
Workers can ask questions when implementation reveals new information.
ProductMaster and TechMaster remain involved throughout the work.

TestMaster verifies behavior against the agreed scenarios.
The team resolves defects and integration problems before it presents delivery for acceptance.
Completion depends on the definition of done.
The organization reviews implementation, test results, delivered behavior, and open work.
After accepted delivery, active development and testing stop until another request arrives.

## 6. Shared tracker and project dashboard

ProjectTracker is the common working record.
All agents can read it and update the parts relevant to their work.
It contains the project registry, tickets, assignees, status, progress, comments, blockers, and follow-up information.

ProjectMaster uses the tracker for portfolio supervision.
ProductMaster and TechMaster connect product direction to implementation.
Workers receive assignments and record progress.
The human can inspect the same records.

The project dashboard shows active products, goals, teams, tasks, assignees, and progress.
It distinguishes completed, active, and upcoming work.
It exposes blockers, open questions, and required decisions.
It links specifications, discussions, deliverables, and responsible agents.

The tracker must remain lightweight and inspectable.
Markdown tickets or a small database can provide the underlying records.
The dashboard presents those records as connected project and portfolio views.
Assignments and updates must remain available across conversations and sessions.
These views must support new profiles and evolving project workflows.

## 7. Chat, collaboration, and escalation

The chat application preserves participants, project context, history, and links to tasks and agents.
The human can browse discussions to understand the work.
Telegram remains the main channel for human requests and decisions through Butler.

| Room | Starting participants | Purpose |
|---|---|---|
| Room1 | Butler, ProjectMaster, ProductMaster, and TechMaster | Management coordination, cross-project issues, and human escalation |
| Room2 | ProductMaster, TechMaster, and specialists | Product clarification, technical discussion, implementation, and progress |

Workers discuss implementation and update ProjectTracker.
Backend and frontend agents can resolve integration questions directly.
TestMaster can discuss a failing scenario with the responsible developer.
ProductMaster and TechMaster can clarify intended behavior in the same room.

Unresolved issues follow this path:

1. Discuss the issue with relevant agents in Room2.
2. Escalate to Room1 when management coordination is needed.
3. Ask the human through Butler when a human decision is needed.

Room history preserves context and decisions.
Simple appended Markdown records can store conversations if the application makes them readable and navigable.
New profiles can join suitable rooms as the organization grows.
Direct collaboration also works across hosts.
An agent's host controls where it executes. Its project and responsibility determine its collaborators.

## 8. Durable product knowledge

Each product has a durable workspace with a `DIRECTIVES/` folder.

| Area | Content |
|---|---|
| SCOPES | Goals, boundaries, and agreed scope |
| SPECS | Product behavior, technical specifications, and decisions |
| HARNESS | Instructions for running, testing, and verifying the product |

Projects can also retain research, plans, questions, runbooks, and evaluation evidence.
Wingman preserves agent identity, conversation context, work state, and product knowledge together.
This continuity supports later improvements and resumed work.

### Workspace locations

| Location | Purpose |
|---|---|
| `Wingman workspace (this folder)` | Wingman's own source, scope, specifications, and supporting workspace |
| `<generated-products-root>/` | Generated products and shared coordination |
| `<temporary-work-root>/` | Temporary working material |

```text
<generated-products-root>/
├── ProjectTracker/
├── Communication/
│   ├── Room1/
│   └── Room2/
├── product-a/
│   ├── DIRECTIVES/
│   │   ├── SCOPES/
│   │   ├── SPECS/
│   │   └── HARNESS/
│   └── ...source and artifacts...
└── product-b/
    ├── DIRECTIVES/
    └── ...source and artifacts...
```

## 9. Active supervision

ProjectMaster periodically wakes to inspect ongoing work.
It reads the tracker and communication history and checks with project leaders and workers.

1. Review active products and worker progress.
2. Identify blockers, unresolved questions, and required follow-up.
3. Contact responsible agents and coordinate a resolution.
4. Escalate through Room1 and Butler when needed.
5. Record the resulting progress or decision.
6. Sleep between useful checks.

Agents can raise problems directly.
ProjectMaster can also discover stalled work during a review.
The human does not need to poll every agent.

## 10. Parallel products and teams

Several products can progress at once.
Each product can use several independent specialists.
Each retains its own leaders, scope, questions, tickets, source workspace, and artifacts.
The organization keeps these efforts visible without losing project context.

One team can build a mortgage product while another builds an analytics product.
Each ProductMaster conducts separate discovery.
Each TechMaster coordinates its backend, frontend, and testing work.
Butler carries questions and updates from both teams through the human's Telegram conversation.
Workers run concurrently where their assignments permit it.
They coordinate interfaces and integration through rooms and ProjectTracker.

## 11. Execution across hosts

Codex agents execute on the MacBook Pro and Endeavour, the Arch Linux host.
The Mac provides the central Telegram interface and organizational coordination.
Endeavour provides capacity for development, builds, automated tests, and browser work.

Existing projects retain their working location.
New work uses an appropriate host.
Agents on both hosts participate in the same organization.
Each agent can access the project context required for its assignment.
The same Butler conversation directs distributed work.
Shared tracking and communication connect the teams across hosts.

## 12. Executive visibility and detailed control

### Executive view

The executive dashboard gives a concise briefing for each agent.
It shows identity, role, project, current task, recent results, planned next work, and important blockers.
The human can scan the organization or focus on a project or agent.

### Agent timeline

Each agent has a chronological summary feed.
Entries describe meaningful work in plain language.
Examples include an assignment start, completed component, test result, question, or blocker.
Each summary links to its tasks, conversations, changes, or test evidence.
It shows when the information was updated.
Planned work remains distinct from completed work.

| Briefing part | BackendCoder example |
|---|---|
| Recent result | Completed the data model and migration tests. |
| Current work | Implementing the application submission API. |
| Next work | Connect the API to the frontend and support integration tests. |
| Required attention | Waiting for a decision about applicant documents. |

### Detailed agent workspace

The human can open a detailed workspace for any agent.
It provides a coding-session experience comparable to Codex, Claude Code, or Orca.
It connects conversations, live activity, task context, tools, commands, edits, tests, and artifacts.

| Capability | Required controls or information |
|---|---|
| Lifecycle | Start, resume, fork, rename, compact, and archive conversations. |
| Live activity | Show output, commands, tools, edits, plans, and execution state. |
| Usage | Show usage and ongoing work state. |
| Questions and approvals | Show requests for human attention and route responses. |
| Input | Steer ongoing work or queue instructions and attachments. |
| Execution | Stop work and manage continuing goals and budgets. Show interrupted state. |
| Review | Inspect files, changes, artifacts, browser observations, and review results. |
| Routing | Reach the correct conversation and execution host. |
| Background work | Continue agent execution independently of the viewing interface. |

### Connected views

| View | Main information |
|---|---|
| Agent directory | Members, roles, and working relationships |
| Executive dashboard | Recent results, current work, next work, and blockers |
| Project dashboard | Product progress and work ownership |
| Chat application | Discussions, decisions, and escalations |
| Agent workspace | Detailed execution and session history |

A timeline entry can lead to a task, discussion, and session.
New profiles participate in the same connected views.
Butler remains the main conversational representative.
The dashboards support review and detailed investigation.

## 13. Autonomy and human judgment

Wingman's own agents perform product development.
The human supplies intent, priorities, business decisions, answers, and acceptance.
Butler carries these conversations to the responsible agents.

The external agent that develops Wingman stays outside its product teams during operation.
Product direction enters through Telegram and Butler.
Infrastructure inspection and repair support the organization.
Wingman's agents remain accountable for product results.
Their records expose progress, decisions, testing, and deliverables.

## 14. Complete product journey

1. The human requests an idea or change through Telegram.
2. Butler passes the request to ProjectMaster.
3. ProjectMaster identifies or creates the project.
4. ProductMaster reads the context and performs proportionate discovery.
5. Butler routes clarification questions and answers.
6. ProductMaster records scope, specifications, scenarios, and the definition of done.
7. TechMaster creates technical tickets and assigns specialists.
8. Specialists implement work and collaborate directly.
9. ProjectMaster supervises progress and helps resolve blockers.
10. TestMaster and the team verify the integrated product.
11. The organization assesses completion and presents delivery through Butler.
12. Accepted delivery stops active work until a new request arrives.
13. The project retains context for fixes, improvements, and later requests.
