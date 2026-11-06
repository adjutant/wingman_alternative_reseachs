#!/usr/bin/env python3
"""Check research artifact coverage, evidence links and checkout integrity.

This checks document structure and provenance, not the truth of source claims.
Independent source audits are in _audits/. No dependencies or service required.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import pathlib
import re
import subprocess
import urllib.parse

ROOT = pathlib.Path(__file__).resolve().parent
WORKSPACE = ROOT.parent
VERDICTS = ("Exact", "Similar", "Resembles", "Absent", "Unclear")


def feature_rows(body):
    rows = {}
    duplicates = []
    for line in body.splitlines():
        if not line.startswith("|"):
            continue
        match = re.search(r"\bF(\d{2})\b", line)
        if not match:
            continue
        key = "F" + match.group(1)
        if key in rows:
            duplicates.append(key)
        # The first verdict is the assessment; later evidence may mention others.
        verdict = re.search(r"\b(Exact|Similar|Resembles|Absent|Unclear)\b", line)
        rows[key] = verdict.group(1) if verdict else None
    return rows, duplicates


def link_targets(body):
    # Inline links and reference definitions. Source filenames can contain [].
    targets = re.findall(r"(?<!!)\[[^\n]*?\]\(([^\n)]+)\)", body)
    targets += re.findall(r"^\[[^\]\n]+\]:\s*(\S+)", body, re.M)
    return targets


def check_links(path, body):
    missing = []
    external = []
    local_count = 0
    for raw in link_targets(body):
        target = raw.strip().strip("<>")
        if re.match(r"https?://", target):
            external.append(target)
            continue
        if target.startswith(("#", "mailto:", "data:", "plugin://")):
            continue
        target = urllib.parse.unquote(target.split("#", 1)[0])
        if not target:
            continue
        # Optional title follows a whitespace+quote; source paths themselves may
        # contain spaces and must otherwise be preserved.
        target = re.split(r'\s+["\']', target, maxsplit=1)[0]
        resolved = pathlib.Path(target) if target.startswith("/") else path.parent / target
        if not resolved.exists():
            missing.append(raw)
        local_count += 1
    return local_count, sorted(set(missing)), sorted(set(external))


def git_value(directory, args):
    result = subprocess.run(["git", "-C", str(directory), *args], text=True,
                            capture_output=True, check=False)
    return result.stdout.rstrip("\n") if result.returncode == 0 else None


def audit():
    manifest = json.loads((ROOT / "coverage.json").read_text())
    results = []
    for repo in manifest["repositories"]:
        path = ROOT / repo["report"]
        checkout = WORKSPACE / "alternatives" / repo["directory"]
        item = {"repository": repo["repository"], "directory": repo["directory"],
                "report": repo["report"], "exists": path.is_file(), "issues": []}
        item["head"] = git_value(checkout, ["rev-parse", "HEAD"])
        item["git_status"] = git_value(checkout, ["status", "--porcelain"])
        if item["head"] != repo["commit"]:
            item["issues"].append("checkout revision differs from baseline")
        if item["git_status"] != repo.get("initial_git_status", ""):
            item["issues"].append("checkout status differs from baseline")
        if path.is_file():
            body = path.read_text()
            item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
            rows, duplicates = feature_rows(body)
            item["features"] = rows
            item["word_count"] = len(body.split())
            item["local_links"], missing, external = check_links(path, body)
            item["missing_links"] = missing
            item["linked_external_urls"] = external
            expected = {f"F{i:02}" for i in range(1, 25)}
            if set(rows) != expected:
                item["issues"].append("missing/unexpected feature IDs: " + str(sorted(set(rows) ^ expected)))
            if duplicates:
                item["issues"].append("duplicate feature rows: " + str(duplicates))
            if any(value is None for value in rows.values()):
                item["issues"].append("feature row lacks standard verdict")
            if missing:
                item["issues"].append("broken local links")
            if external:
                item["issues"].append("external URLs must be bare")
            if repo["commit"] not in body:
                item["issues"].append("full pinned commit missing from report")
            if not re.search(r"2026-11-05|November 5, 2026|5 November 2026", body):
                item["issues"].append("assessment date missing")
        else:
            item["issues"].append("report missing")
        results.append(item)
    other_docs = []
    for path in sorted(ROOT.rglob("*.md")):
        if path.name.endswith("_Assessments.md"):
            continue
        count, missing, external = check_links(path, path.read_text())
        other_docs.append({"path": str(path.relative_to(ROOT)),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "local_links": count,
                           "missing_links": missing, "linked_external_urls": external})
    orphan_chapters = []
    for chapter in sorted(ROOT.glob("*_Extra_Info/*.md")):
        slug = chapter.parent.name.removesuffix("_Extra_Info")
        master = ROOT / f"{slug}_Assessments.md"
        relative = str(chapter.relative_to(ROOT))
        if not master.is_file() or relative not in master.read_text():
            orphan_chapters.append(relative)
    expected_directories = {repo["directory"] for repo in manifest["repositories"]}
    actual_directories = {str(path.parent.relative_to(WORKSPACE / "alternatives"))
                          for path in (WORKSPACE / "alternatives").glob("*/*/.git")}
    audit_paths = [ROOT / "_audits" / f"qa{i:02}.md" for i in range(1, 26)]
    return {"checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scope": "Structural/provenance validation; semantic source audits are separate.",
            "repository_count": len(results),
            "unlisted_checkouts": sorted(actual_directories - expected_directories),
            "missing_checkouts": sorted(expected_directories - actual_directories),
            "unlinked_supporting_chapters": orphan_chapters,
            "independent_audits_present": sum(path.is_file() for path in audit_paths),
            "reports_present": sum(item["exists"] for item in results),
            "reports_passing_structural_checks": sum(not item["issues"] for item in results),
            "reports": results, "supporting_documents": other_docs}


def write_matrix(result):
    guide = (ROOT / "ASSESSMENT_GUIDE.md").read_text()
    features = [(m.group(1), m.group(2)) for m in re.finditer(r"^\| (F\d{2}) \| ([^|]+)\|", guide, re.M)]
    lines = ["# WINGMAN feature comparison", "",
             "Generated from the 75 individual source assessments. Read each report for evidence, boundaries and verification limits; these verdicts are not runtime certification or a numerical product ranking.", "",
             "E = Exact; S = Similar; R = Resembles; A = Absent; U = Unclear. A complete feature can contain multiple requirements; partial implementations are explained in the linked report.", "",
             "| Alternative | " + " | ".join(key for key, _ in features) + " |",
             "|---|" + "---|" * len(features)]
    symbols = {"Exact": "E", "Similar": "S", "Resembles": "R", "Absent": "A", "Unclear": "U"}
    for repo in result["reports"]:
        slug = pathlib.Path(repo["directory"]).name
        row = [symbols.get(repo.get("features", {}).get(key), "?") for key, _ in features]
        lines.append(f"| [{slug}]({repo['report']}) | " + " | ".join(row) + " |")
    lines += ["", "## Feature definitions", "", "| ID | WINGMAN capability |", "|---|---|"]
    lines += [f"| {key} | {name.strip()} |" for key, name in features]
    lines += ["", "The [assessment guide](ASSESSMENT_GUIDE.md) defines each verdict. The [purpose document](../alternatives/WINGMAN_PURPOSE.md) is the baseline. Individual reports distinguish source inspection, test inspection, test execution and external dependencies.", ""]
    (ROOT / "FEATURE_MATRIX.md").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write validation.json and FEATURE_MATRIX.md")
    args = parser.parse_args()
    result = audit()
    if args.write:
        write_matrix(result)
        for doc in result["supporting_documents"]:
            if doc["path"] == "FEATURE_MATRIX.md":
                doc["sha256"] = hashlib.sha256((ROOT / doc["path"]).read_bytes()).hexdigest()
        (ROOT / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("repository_count", "reports_present", "reports_passing_structural_checks")}, indent=2))
    for repo in result["reports"]:
        if repo["issues"]:
            print(repo["report"], json.dumps(repo["issues"]), json.dumps(repo.get("missing_links", [])))
    for doc in result["supporting_documents"]:
        if doc["missing_links"] or doc["linked_external_urls"]:
            print(doc["path"], json.dumps(doc))
    if result["unlinked_supporting_chapters"]:
        print("unlinked supporting chapters", json.dumps(result["unlinked_supporting_chapters"]))
    failed = (any(repo["issues"] for repo in result["reports"])
              or any(doc["missing_links"] or doc["linked_external_urls"]
                     for doc in result["supporting_documents"])
              or result["unlisted_checkouts"] or result["missing_checkouts"]
              or result["unlinked_supporting_chapters"]
              or result["independent_audits_present"] != 25)
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
