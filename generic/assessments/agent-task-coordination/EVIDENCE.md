# Agent task coordination evidence

Review date: November 8, 2026. Return to the [study](../AGENT_TASK_COORDINATION.md).

The 22 pinned repositories include the Plane adapter and five restricted alternatives or companions. GitLab is a separate documentation-only entry. The candidate count is 17 open-source systems plus three restricted alternatives and two restricted companions. Source retrieval and test-file inspection do not establish a runtime result.

The source manifest records hashes for retrieved files. Raw candidate files stay in ignored local research scratch storage; no additional source checkout was added to the original 75-checkout collection. Reproduce a file read from its immutable upstream URL.

## Pinned revisions

| Project | Full commit | Evidence scope |
|---|---|---|
| tools-for-agents/agent-hq | `785cd8c9a55b2b517eb8eb8f680cd65985992282` | implementation |
| fxeqxmulfx/agent-kanban-rs | `3ab1218eac51edca8556e6dfbeea322477e7a444` | implementation |
| Dicklesworthstone/mcp_agent_mail_rust | `49866939b1f52af5741bd3c87145d01846b93a38` | license and README; no adoption review |
| desplega-ai/agent-swarm | `6aff700f53755cb71bd6a1aa2e2fa1da9586b892` | existing pinned implementation |
| MrLesk/Backlog.md | `3a296c0f6f949b31e458b849b9617702c56c1023` | implementation |
| gastownhall/beads | `2edea9ced8c6f6124b6c157896ae53a0e09ff7be` | implementation |
| Dicklesworthstone/beads_rust | `117f81de0d5dae007d972a9ff7f1d73c392d8822` | license and README; no adoption review |
| Dicklesworthstone/beads_viewer | `516e96aa1ac78d6f634b0d394f5102bf430de016` | license and README; no adoption review |
| RapidWebs-Enterprise/DevBoard | `cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b` | implementation |
| GembaCore/gemba-core | `64c266f889c6d6a579904c5e336676fa1c49b216` | implementation |
| kanboard/kanboard | `2ddb31bf72d355727d0639fc3423630f3bae1a9c` | targeted API procedure source |
| musterai/muster | `bb98b21a6ac0ed4cb095f948e55ae8a644e10c40` | implementation |
| opf/openproject | `05d9afe72a3c9198e26c0284c213f733c4863ca2` | official API/edition docs plus license |
| paperclipai/paperclip | `46fb933b0155d183ce64a8bdc4950d1b58c926f6` | existing pinned implementation |
| makeplane/plane | `618d0eb74658329a6f6e92434ac54231422c5b96` | targeted model/API and adapter source |
| makeplane/plane-mcp-server | `5c3467adb36fe15a2ef8f9df6fb9f5dc24b6d881` | Official integration source |
| plankanban/planka | `2cf423824a09f84df7dc3acf0ded9a700292d882` | license and README |
| Odrin/rhizome-mcp | `03fffd7d1410ddccadf7c199f5d6e796a497b1f0` | implementation |
| taigaio/taiga-back | `8ab6a4e3b5f6fbbfcbf108a6449011f07b7308aa` | official API docs plus license |
| eyaltoledano/claude-task-master | `c0c98d367c55296bfe69e65680625b6db437af02` | license and planning documentation |
| BloopAI/vibe-kanban | `08064e043c2d78ad123b473257ed867e7ce74768` | implementation and deployment documentation |
| go-vikunja/vikunja | `d2c9aee4f8894edc02611a8b40becbd5dfc95e33` | official docs plus license |

## Implementation references

Line ranges identify the inspected mechanism at the pinned revision. License-only and documentation-only classifications are identified separately. Upstream test links describe test intent, not an execution result from this study.


### Beads

- `internal/storage/issueops/claim.go`, lines 35–160: https://github.com/gastownhall/beads/blob/2edea9ced8c6f6124b6c157896ae53a0e09ff7be/internal/storage/issueops/claim.go#L35-L160
- `internal/storage/issueops/claim_next.go`, lines 45–79: https://github.com/gastownhall/beads/blob/2edea9ced8c6f6124b6c157896ae53a0e09ff7be/internal/storage/issueops/claim_next.go#L45-L79
- `internal/storage/issueops/lease.go`, lines 20–68: https://github.com/gastownhall/beads/blob/2edea9ced8c6f6124b6c157896ae53a0e09ff7be/internal/storage/issueops/lease.go#L20-L68
- `README.md`, lines 151–165: https://github.com/gastownhall/beads/blob/2edea9ced8c6f6124b6c157896ae53a0e09ff7be/README.md#L151-L165

### Rhizome MCP

- `internal/adapters/sqlite/attempts.go`, lines 38–87: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/internal/adapters/sqlite/attempts.go#L38-L87
- `internal/adapters/sqlite/attempts.go`, lines 222–365: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/internal/adapters/sqlite/attempts.go#L222-L365
- `integration/claim_race_test.go`, lines 20–85: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/integration/claim_race_test.go#L20-L85
- `docs/08-local-http-transport.md`, lines 72–112: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/docs/08-local-http-transport.md#L72-L112
- `docs/09-review-workflow.md`, lines 1–45: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/docs/09-review-workflow.md#L1-L45
- `docs/13-status-board.md`, lines 1–31: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/docs/13-status-board.md#L1-L31

### agent-kanban-rs

- `src/commands/lifecycle.rs`, lines 31–99: https://github.com/fxeqxmulfx/agent-kanban-rs/blob/3ab1218eac51edca8556e6dfbeea322477e7a444/src/commands/lifecycle.rs#L31-L99
- `src/commands/lifecycle.rs`, lines 149–177: https://github.com/fxeqxmulfx/agent-kanban-rs/blob/3ab1218eac51edca8556e6dfbeea322477e7a444/src/commands/lifecycle.rs#L149-L177
- `src/commands/lifecycle.rs`, lines 474–525: https://github.com/fxeqxmulfx/agent-kanban-rs/blob/3ab1218eac51edca8556e6dfbeea322477e7a444/src/commands/lifecycle.rs#L474-L525

### Backlog.md

- `src/core/backlog.ts`, lines 3070–3095: https://github.com/MrLesk/Backlog.md/blob/3a296c0f6f949b31e458b849b9617702c56c1023/src/core/backlog.ts#L3070-L3095
- `src/file-system/operations.ts`, lines 716–759: https://github.com/MrLesk/Backlog.md/blob/3a296c0f6f949b31e458b849b9617702c56c1023/src/file-system/operations.ts#L716-L759
- `README.md`, lines 235–242: https://github.com/MrLesk/Backlog.md/blob/3a296c0f6f949b31e458b849b9617702c56c1023/README.md#L235-L242

### Muster

- `src/services/card-assignment.operations.ts`, lines 93–193: https://github.com/musterai/muster/blob/bb98b21a6ac0ed4cb095f948e55ae8a644e10c40/src/services/card-assignment.operations.ts#L93-L193
- `src/db/sqlite-adapter.ts`, lines 61–76: https://github.com/musterai/muster/blob/bb98b21a6ac0ed4cb095f948e55ae8a644e10c40/src/db/sqlite-adapter.ts#L61-L76
- `tests/card-claim.test.ts`, lines 108–147: https://github.com/musterai/muster/blob/bb98b21a6ac0ed4cb095f948e55ae8a644e10c40/tests/card-claim.test.ts#L108-L147
- `docs/deployment.md`, lines 8–46: https://github.com/musterai/muster/blob/bb98b21a6ac0ed4cb095f948e55ae8a644e10c40/docs/deployment.md#L8-L46

### Agent HQ

- `src/services.js`, lines 630–705: https://github.com/tools-for-agents/agent-hq/blob/785cd8c9a55b2b517eb8eb8f680cd65985992282/src/services.js#L630-L705
- `src/server.js`, lines 128–178: https://github.com/tools-for-agents/agent-hq/blob/785cd8c9a55b2b517eb8eb8f680cd65985992282/src/server.js#L128-L178
- `test/concurrency.test.js`, lines 1–67: https://github.com/tools-for-agents/agent-hq/blob/785cd8c9a55b2b517eb8eb8f680cd65985992282/test/concurrency.test.js#L1-L67

### DevBoard

- `src/devboard/__init__.py`, lines 419–479: https://github.com/RapidWebs-Enterprise/DevBoard/blob/cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b/src/devboard/__init__.py#L419-L479
- `docs/adrs/0003-atomic-claims.md`, lines 1–26: https://github.com/RapidWebs-Enterprise/DevBoard/blob/cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b/docs/adrs/0003-atomic-claims.md#L1-L26

### Vibe Kanban

- `crates/mcp/src/task_server/tools/task_attempts.rs`, lines 19–113: https://github.com/BloopAI/vibe-kanban/blob/08064e043c2d78ad123b473257ed867e7ce74768/crates/mcp/src/task_server/tools/task_attempts.rs#L19-L113
- `docs/self-hosting/deploy-docker.mdx`, lines 1–20: https://github.com/BloopAI/vibe-kanban/blob/08064e043c2d78ad123b473257ed867e7ce74768/docs/self-hosting/deploy-docker.mdx#L1-L20

### Gemba

- `internal/adapter/bd/workplane.go`, lines 47–111: https://github.com/GembaCore/gemba-core/blob/64c266f889c6d6a579904c5e336676fa1c49b216/internal/adapter/bd/workplane.go#L47-L111
- `docs/adaptors/beads.md`, lines 1–70: https://github.com/GembaCore/gemba-core/blob/64c266f889c6d6a579904c5e336676fa1c49b216/docs/adaptors/beads.md#L1-L70

### Plane

- `apps/api/plane/db/models/issue.py`, lines 1–90: https://github.com/makeplane/plane/blob/618d0eb74658329a6f6e92434ac54231422c5b96/apps/api/plane/db/models/issue.py#L1-L90

### plane-mcp

- `plane_mcp/client.py`, lines 45–73: https://github.com/makeplane/plane-mcp-server/blob/5c3467adb36fe15a2ef8f9df6fb9f5dc24b6d881/plane_mcp/client.py#L45-L73
- `plane_mcp/tools/workitem.py`, lines 1–68: https://github.com/makeplane/plane-mcp-server/blob/5c3467adb36fe15a2ef8f9df6fb9f5dc24b6d881/plane_mcp/tools/workitem.py#L1-L68

### Kanboard

- `app/Api/Procedure/TaskProcedure.php`, lines 1–75: https://github.com/kanboard/kanboard/blob/2ddb31bf72d355727d0639fc3423630f3bae1a9c/app/Api/Procedure/TaskProcedure.php#L1-L75
- `app/Api/Procedure/SubtaskProcedure.php`, lines 1–60: https://github.com/kanboard/kanboard/blob/2ddb31bf72d355727d0639fc3423630f3bae1a9c/app/Api/Procedure/SubtaskProcedure.php#L1-L60

### Paperclip

- `server/src/services/issues.ts`, lines 12168–12303: https://github.com/paperclipai/paperclip/blob/46fb933b0155d183ce64a8bdc4950d1b58c926f6/server/src/services/issues.ts#L12168-L12303

### Agent Swarm

- `src/be/db.ts`, lines 3107–3159: https://github.com/desplega-ai/agent-swarm/blob/6aff700f53755cb71bd6a1aa2e2fa1da9586b892/src/be/db.ts#L3107-L3159
- `src/be/db/runtime.ts`, lines 73–136: https://github.com/desplega-ai/agent-swarm/blob/6aff700f53755cb71bd6a1aa2e2fa1da9586b892/src/be/db/runtime.ts#L73-L136

## License evidence

The inspected license is a screening input. This is not a dependency-wide licensing assessment.

- tools-for-agents/agent-hq: https://github.com/tools-for-agents/agent-hq/blob/785cd8c9a55b2b517eb8eb8f680cd65985992282/LICENSE
- fxeqxmulfx/agent-kanban-rs: https://github.com/fxeqxmulfx/agent-kanban-rs/blob/3ab1218eac51edca8556e6dfbeea322477e7a444/LICENSE
- Dicklesworthstone/mcp_agent_mail_rust: https://github.com/Dicklesworthstone/mcp_agent_mail_rust/blob/49866939b1f52af5741bd3c87145d01846b93a38/LICENSE
- desplega-ai/agent-swarm: https://github.com/desplega-ai/agent-swarm/blob/6aff700f53755cb71bd6a1aa2e2fa1da9586b892/LICENSE
- MrLesk/Backlog.md: https://github.com/MrLesk/Backlog.md/blob/3a296c0f6f949b31e458b849b9617702c56c1023/LICENSE
- gastownhall/beads: https://github.com/gastownhall/beads/blob/2edea9ced8c6f6124b6c157896ae53a0e09ff7be/LICENSE
- Dicklesworthstone/beads_rust: https://github.com/Dicklesworthstone/beads_rust/blob/117f81de0d5dae007d972a9ff7f1d73c392d8822/LICENSE
- Dicklesworthstone/beads_viewer: https://github.com/Dicklesworthstone/beads_viewer/blob/516e96aa1ac78d6f634b0d394f5102bf430de016/LICENSE
- RapidWebs-Enterprise/DevBoard: https://github.com/RapidWebs-Enterprise/DevBoard/blob/cbe017a445fd4f9dee2de73f729c65b7fe0f9b9b/LICENSE
- GembaCore/gemba-core: https://github.com/GembaCore/gemba-core/blob/64c266f889c6d6a579904c5e336676fa1c49b216/LICENSE
- kanboard/kanboard: https://github.com/kanboard/kanboard/blob/2ddb31bf72d355727d0639fc3423630f3bae1a9c/LICENSE
- musterai/muster: https://github.com/musterai/muster/blob/bb98b21a6ac0ed4cb095f948e55ae8a644e10c40/LICENSE
- opf/openproject: https://github.com/opf/openproject/blob/05d9afe72a3c9198e26c0284c213f733c4863ca2/LICENSE
- paperclipai/paperclip: https://github.com/paperclipai/paperclip/blob/46fb933b0155d183ce64a8bdc4950d1b58c926f6/LICENSE
- makeplane/plane: https://github.com/makeplane/plane/blob/618d0eb74658329a6f6e92434ac54231422c5b96/LICENSE.txt
- makeplane/plane-mcp-server: https://github.com/makeplane/plane-mcp-server/blob/5c3467adb36fe15a2ef8f9df6fb9f5dc24b6d881/LICENSE
- plankanban/planka: https://github.com/plankanban/planka/blob/2cf423824a09f84df7dc3acf0ded9a700292d882/LICENSE.md
- Odrin/rhizome-mcp: https://github.com/Odrin/rhizome-mcp/blob/03fffd7d1410ddccadf7c199f5d6e796a497b1f0/LICENSE
- taigaio/taiga-back: https://github.com/taigaio/taiga-back/blob/8ab6a4e3b5f6fbbfcbf108a6449011f07b7308aa/LICENSE
- eyaltoledano/claude-task-master: https://github.com/eyaltoledano/claude-task-master/blob/c0c98d367c55296bfe69e65680625b6db437af02/LICENSE
- BloopAI/vibe-kanban: https://github.com/BloopAI/vibe-kanban/blob/08064e043c2d78ad123b473257ed867e7ce74768/LICENSE
- go-vikunja/vikunja: https://github.com/go-vikunja/vikunja/blob/d2c9aee4f8894edc02611a8b40becbd5dfc95e33/LICENSE

## Official documentation

These references were checked on November 8, 2026. They are not immutable snapshots.

- Issue boards and Free/paid tier boundaries: https://docs.gitlab.com/user/project/issue_board/
- Issue lifecycle and authenticated API access: https://docs.gitlab.com/api/issues/
- Board and list API: https://docs.gitlab.com/api/boards/
- Community license; no GitLab source implementation claim: https://gitlab.com/gitlab-org/gitlab/-/blob/master/LICENSE
- lockVersion optimistic locking: https://www.openproject.org/docs/api/endpoints/work-packages/
- Action boards available in Community since 17.3: https://www.openproject.org/blog/openproject-17-3-release/
- MCP write operations and Enterprise plan boundary: https://www.openproject.org/blog/openproject-17-8-release/
- Projects, subtasks, collaboration and task views: https://vikunja.io/features/
- Task relation API discovery; no lease guarantee established: https://try.vikunja.io/api/v2/docs
- Task/story/milestone API and optimistic concurrency: https://docs.taiga.io/api.html
- Protocol tasks differ from a shared project tracker: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2025-11-25/basic/utilities/tasks.mdx
- Python implementation is superseded by Rust rewrite: https://github.com/Dicklesworthstone/mcp_agent_mail

## Machine-readable records

- [Candidate screening](candidates.json)
- [Source revisions and file hashes](sources.json)
