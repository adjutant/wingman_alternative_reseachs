# Assessment guide

Assess the active checkouts in [the source manifest](../../checkouts.json).
Use [Wingman's purpose](../../WINGMAN_PURPOSE.md) as the product baseline.
Describe the pinned local commit. Keep each checkout unchanged.

## Report structure

Each project has `assessment/ASSESSMENT.md` and `index.html`.
Place supporting Markdown chapters in the same `assessment/` folder.
Keep the verdict and all 24 feature rows in the main assessment.
Use the HTML decision brief to explain the highest-impact use and adoption boundary.

## Required technical coverage

1. Record identity, bare repository URL, local checkout, full commit, date, and fit verdict.
2. Trace architecture from the executable entry point to persistence and actual execution.
3. Compare every feature below. Cite implementation evidence and explain the difference from Wingman.
4. Explain the complete agent lifecycle. Cover definition, creation, identity, execution, tools, and permissions.
5. Continue the lifecycle review through routing, concurrency, persistence, resume, scheduling, interruption, and cancellation.
6. Explain failure, retry, recovery, completion, acceptance, retirement, and cleanup.
7. Trace one request through tickets, messages, dependencies, events, shared state, and human decisions.
8. Describe substantial extra capabilities. Explain their value and integration consequences.
9. Describe distinctive mechanisms and their limits. Do not claim industry-wide novelty without evidence.
10. State what Wingman can reuse, adapt, and still needs to build.
11. Separate source findings, tests inspected, tests executed, and unverified runtime behavior.

Distinguish a session, task, process, durable agent, and role prompt.
Do not treat a model persona as an independently running agent.
Do not treat a terminal grid as a complete project dashboard.
An approval prompt does not establish product discovery.
An event log does not establish an executive briefing.
A local subprocess does not establish multi-host execution.

Use targeted implementation searches for missing features.
State the paths searched and any external source boundary.
Do not use README silence as proof of absence.
State default-off settings and prompt-dependent procedures.

Use local relative links for implementation evidence.
State source line numbers beside the links.
Use bare complete external URLs.
Read applicable checkout instructions before operating inside a repository.
Do not install dependencies or launch candidate services merely to write a report.
Do not expose secrets, generated bundles, or vendored dependencies.

## Writing

Use ASD-STE100 principles: short sentences, active voice, one topic per sentence, and consistent terms.
Keep the technical details needed to explain contracts, failure conditions, and adoption costs.
Use lists for parallel requirements and tables for comparisons.
Do not replace mechanisms and evidence with a checklist of product names.
Do not claim formal controlled-language certification from automated checks alone.

## Feature matrix

Use these stable IDs and cover each individually:

| ID | WINGMAN capability |
|---|---|
| F01 | Real independent coding agents and specialist instances |
| F02 | Extensible agent profiles, roles and team composition |
| F03 | Agent directory and visible working relationships |
| F04 | Telegram as the main human channel and Butler-style routing |
| F05 | Cross-project registry, intake and existing/new project routing |
| F06 | Per-project product and technical leadership |
| F07 | Proportionate research, discovery and iterative human clarification |
| F08 | Product scope, specifications, acceptance scenarios and definition of done |
| F09 | Technical decomposition, assignment and shared task tracking |
| F10 | Human-facing portfolio/project management dashboard |
| F11 | Agent chat application, rooms and direct collaboration |
| F12 | Management escalation and human decisions/approvals |
| F13 | Durable project knowledge and reusable directives |
| F14 | Persistent identity, conversation and work continuity |
| F15 | Proactive supervision, periodic wake and blocker follow-up |
| F16 | Parallel products and concurrent specialists |
| F17 | Real multi-host execution with shared coordination |
| F18 | Executive agent overview: current/recent/next work and blockers |
| F19 | Individual agent summary timeline linked to underlying work |
| F20 | Drill-down into detailed per-agent coding workspace |
| F21 | Live activity, lifecycle controls, steering and execution visibility |
| F22 | Testing, integrated verification and product acceptance/delivery |
| F23 | Autonomous operation with human direction through the organization |
| F24 | Chat, tracker and dashboards accommodate newly added agent profiles |

## Feature verdicts

- **Exact:** Implemented behavior meets the feature within the stated boundary.
- **Similar:** A substantial equivalent exists. Its scope, workflow, interface, or persistence differs.
- **Resembles:** A related mechanism exists. It does not supply the complete feature.
- **Absent:** Targeted source searches found no corresponding capability. State the search scope.
- **Unclear:** Missing source or an external dependency prevents a reliable finding.

Explain each boundary beside its verdict.
Do not sum verdicts into a product ranking.
