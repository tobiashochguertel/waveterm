#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Generate .github/UPSTREAM-PRS.md from open upstream pull requests.

Fetches all open PRs via `gh pr list`, categorizes them by risk level,
detects file overlaps, and writes a markdown document.

Usage:
    uv run --script .github/scripts/generate_upstream_prs.py

Requires: gh CLI authenticated with access to wavetermdev/waveterm.
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

UPSTREAM_REPO = "wavetermdev/waveterm"
OUTPUT_FILE = Path(".github/UPSTREAM-PRS.md")

# Files we already patch in this fork — PRs touching these get elevated risk
PATCHED_FILES = {
    "frontend/app/view/term/term.tsx",
    "frontend/app/view/webview/webview.tsx",
    "frontend/app/block/block.tsx",
}

# Files that are conflict-prone in upstream (frequently changed, config schemas)
CONFLICT_PRONE_FILES = {
    "pkg/wconfig/settingsconfig.go",
    "pkg/wconfig/metaconsts.go",
    "pkg/waveobj/metaconsts.go",
    "pkg/waveobj/wtypemeta.go",
    "frontend/types/gotypes.d.ts",
    "schema/settings.json",
    "schema/connections.json",
    "schema/widgets.json",
}

# PRs already integrated in this fork
ALREADY_INTEGRATED = {
    3429: ("fix: stop a de-focusing block from re-grabbing focus", "dev.patch", "003-focus-fix.patch"),
    3420: ("Fix bookmark typeahead not rendering suggestions", "dev.patch", "002-bookmark-typeahead-fix.patch"),
}

# PRs to exclude (dependabot, docs-only, etc.)
DEPENDABOT_AUTHOR = "app/dependabot"


@dataclass
class PR:
    number: int
    title: str
    author: str
    additions: int
    deletions: int
    files: list[str]
    created_at: str

    @property
    def size(self) -> str:
        return f"+{self.additions}/-{self.deletions}"

    @property
    def file_count(self) -> int:
        return len(self.files)

    @property
    def total_changes(self) -> int:
        return self.additions + self.deletions

    @property
    def is_dependabot(self) -> bool:
        return self.author == DEPENDABOT_AUTHOR

    @property
    def is_docs_only(self) -> bool:
        return all(f.startswith("docs/") or f.endswith(".mdx") or f.endswith(".md") for f in self.files)

    @property
    def touches_patched_files(self) -> bool:
        return bool(set(self.files) & PATCHED_FILES)

    @property
    def touches_conflict_prone(self) -> bool:
        return bool(set(self.files) & CONFLICT_PRONE_FILES)

    @property
    def risk(self) -> str:
        if self.is_dependabot or self.is_docs_only:
            return "N/A"
        if self.file_count == 1 and self.total_changes < 10 and not self.touches_conflict_prone:
            return "Zero"
        if self.file_count <= 2 and self.total_changes < 60 and not self.touches_patched_files and not self.touches_conflict_prone:
            return "Low"
        if self.touches_patched_files or self.touches_conflict_prone or self.file_count <= 7:
            return "Medium"
        return "High"

    @property
    def patch_fit(self) -> str:
        if self.is_dependabot:
            return "N/A"
        if self.is_docs_only:
            return "N/A"
        if self.risk == "Zero":
            return "Excellent"
        if self.risk == "Low":
            return "Great" if self.file_count <= 2 else "Good"
        if self.risk == "Medium":
            if self.touches_patched_files:
                return "Caution — overlaps existing patch"
            return "Caution — config schema changes" if self.touches_conflict_prone else "Caution"
        return "Risky"


def fetch_prs() -> list[PR]:
    """Fetch all open PRs with file lists via gh CLI."""
    result = subprocess.run(
        [
            "gh", "pr", "list",
            "--repo", UPSTREAM_REPO,
            "--state", "open",
            "--limit", "100",
            "--json", "number,title,author,additions,deletions,files,createdAt",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    raw = json.loads(result.stdout)
    prs = []
    for item in raw:
        files = [f["path"] for f in item.get("files", [])]
        prs.append(PR(
            number=item["number"],
            title=item["title"],
            author=item["author"]["login"],
            additions=item["additions"],
            deletions=item["deletions"],
            files=files,
            created_at=item["createdAt"],
        ))
    return prs


def compute_file_overlaps(prs: list[PR]) -> dict[str, list[int]]:
    """Find files that appear in multiple PRs."""
    file_to_prs: dict[str, list[int]] = defaultdict(list)
    for pr in prs:
        if pr.is_dependabot or pr.is_docs_only:
            continue
        for f in pr.files:
            file_to_prs[f].append(pr.number)
    return {f: sorted(nums) for f, nums in file_to_prs.items() if len(nums) > 1}


def fmt_files(files: list[str], max_show: int = 2) -> str:
    """Format file list for table cell."""
    if len(files) == 0:
        return "—"
    if len(files) <= max_show:
        return ", ".join(f"`{f}`" for f in files)
    return f"{len(files)} files (`{files[0]}`, ...)"


def generate_markdown(prs: list[PR]) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        "# WaveTerm Upstream Pull Requests",
        "",
        f"Catalog of open pull requests from [{UPSTREAM_REPO}](https://github.com/{UPSTREAM_REPO}/pulls)",
        "evaluated for integration into the fork via the `.patch` strategy.",
        "",
        f"**Last updated:** {now}",
        f"**Total open PRs:** {len(prs)}",
        "",
        "## Legend",
        "",
        "- **Risk** — conflict risk if integrated as a `.patch` file:",
        "  - **Zero** — 1 file, <10 lines, no config/schema changes",
        "  - **Low** — 1-2 files, isolated, no overlap with `PATCHED_FILES`",
        "  - **Medium** — touches files we already patch, or touches conflict-prone files (`settingsconfig.go`, `metaconsts.go`, `gotypes.d.ts`)",
        "  - **High** — large, multi-file, touches core files or config schemas",
        "- **.patch fit** — suitability for the revert-then-repatch strategy",
        "",
        "## Already integrated",
        "",
        "| PR | Title | Size | Files | Branch | Patch file |",
        "|----|-------|------|-------|--------|------------|",
    ]

    for num, (title, branch, patch_file) in sorted(ALREADY_INTEGRATED.items()):
        pr = next((p for p in prs if p.number == num), None)
        if pr:
            lines.append(f"| #{num} | {title} | {pr.size} | {fmt_files(pr.files)} | `{branch}` | `{patch_file}` |")
        else:
            # PR may be closed/merged — use stored info
            lines.append(f"| #{num} | {title} | — | — | `{branch}` | `{patch_file}` |")

    # Filter out already-integrated and dependabot/docs for the main tables
    active = [p for p in prs if p.number not in ALREADY_INTEGRATED and not p.is_dependabot and not p.is_docs_only]
    dependabot = [p for p in prs if p.is_dependabot]
    docs_only = [p for p in prs if p.is_docs_only and p.number not in ALREADY_INTEGRATED]

    # Group by risk
    tiers = [
        ("Tier 1 — Zero risk (pure bugfixes, tiny, single-file)", "Zero"),
        ("Tier 2 — Low risk (small, isolated)", "Low"),
        ("Tier 3 — Medium risk (overlaps or touches conflict-prone files)", "Medium"),
        ("Tier 4 — High risk (large, multi-file, features)", "High"),
    ]

    for heading, risk_level in tiers:
        tier_prs = sorted([p for p in active if p.risk == risk_level], key=lambda p: p.total_changes)
        if not tier_prs:
            continue
        lines.extend(["", f"### {heading}", "", "| PR | Title | Size | Files | Risk | .patch fit |", "|----|-------|------|-------|------|------------|"])
        for pr in tier_prs:
            lines.append(f"| #{pr.number} | {pr.title} | {pr.size} | {fmt_files(pr.files)} | {pr.risk} | {pr.patch_fit} |")

    # Not applicable
    if docs_only:
        lines.extend(["", "## Not applicable", "", "### Documentation only", "", "| PR | Title | Size | Files |", "|----|-------|------|-------|"])
        for pr in sorted(docs_only, key=lambda p: p.number, reverse=True):
            lines.append(f"| #{pr.number} | {pr.title} | {pr.size} | {fmt_files(pr.files)} |")

    if dependabot:
        lines.extend(["", "### Dependabot (auto-managed by upstream)", "", "| PR | Title | Size |", "|----|-------|------|"])
        for pr in sorted(dependabot, key=lambda p: p.number, reverse=True):
            lines.append(f"| #{pr.number} | {pr.title} | {pr.size} |")

    # File overlap matrix
    overlaps = compute_file_overlaps(prs)
    if overlaps:
        lines.extend(["", "## File overlap matrix", "", "Files that appear in multiple PRs — integrating one may complicate integrating another:", "", "| File | PRs |", "|------|-----|"])
        for f, nums in sorted(overlaps.items(), key=lambda x: (-len(x[1]), x[0])):
            pr_links = ", ".join(f"#{n}" for n in nums)
            marker = " **(patched)**" if f in PATCHED_FILES else ""
            lines.append(f"| `{f}`{marker} | {pr_links} |")

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    print(f"Fetching open PRs from {UPSTREAM_REPO}...")
    prs = fetch_prs()
    print(f"  Found {len(prs)} open PRs")

    dependabot_count = sum(1 for p in prs if p.is_dependabot)
    docs_count = sum(1 for p in prs if p.is_docs_only and not p.is_dependabot)
    active_count = len(prs) - dependabot_count - docs_count
    print(f"  Active: {active_count}, Dependabot: {dependabot_count}, Docs-only: {docs_count}")

    print(f"Generating {OUTPUT_FILE}...")
    markdown = generate_markdown(prs)
    OUTPUT_FILE.write_text(markdown)
    print(f"  Wrote {len(markdown)} bytes to {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
