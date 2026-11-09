# Assessment portability audit

Date: November 10, 2026.

All assessment files, local assets, imports and metadata are contained within this research repository.
Source checkouts remain optional, ignored inputs at the pinned repository-relative locations in the two manifests.
No candidate installation, launch or probe rerun formed part of this correction.

## Corrections

- Replaced historical host paths and stale source imports with canonical repository-relative locations.
- Removed machine-specific paths, inode identities and temporary backup pointers from metadata.
- Repaired archived links. Excluded historical sources are plain provenance labels rather than broken links.
- Removed the obsolete cross-workspace reorganization tool. The archived validator now invokes the current local validator.
- Put maintained fixture and prose-edit scratch files under `.run/`.
- Replaced illustrative host workspace roots with symbolic product-location labels.

## Historical evidence

Path normalization changes presentation bytes, not the recorded observations.
The gstack log retains separate lexical and resolved temporary-root tokens because their difference caused an assertion failure.
Orca bundle edits affect provenance comments only; its fixture wrapper also uses local scratch space.
The source-derived implementation code remains unchanged.
Original and current evidence hashes are in [the evidence ledger](legacy-evidence-preservation.json).
The [change record](portability-changes.json) lists original and current hashes for changed retained artifacts.
Original document hashes identify historical bytes and are not claims about the normalized files.

## Boundary check

`tools/validate_portability.py` scans the entire Git file inventory, including archives, hidden tracked files and generated reports.
It resolves links, assets, imports, manifest locations and symlinks against the physical repository boundary.
It also checks parent traversal and generic absolute, home, Windows and file-URL literals without assuming an account name or directory prefix.
Candidate runtime routes, slash commands, OS paths, syntax fragments and product home directories are individually classified in [the reviewed literal table](portability-runtime-paths.json).
Those classifications do not authorize an external local link, import or manifest dependency.

[Machine-readable results](portability.json) record the latest complete file check.
The [relocation check](portability-relocation.json) copied the assessment inventory into a differently named isolated directory without Git metadata or source checkouts.
All 66 reports rebuilt byte-for-byte identically. Boundary and publication checks passed there.
The 11 boundary regression tests and four report-server tests also passed.
Both source validators passed for the 49 orchestration checkouts and nine task-study checkouts.
The source checkouts remained unchanged.
