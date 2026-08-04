#!/usr/bin/env python3
"""Reproduce the DEC-012 counter-evidence 1 check: PageRank vs the shipped degree ranking.

DEC-012 (`dsm-docs/decisions/DEC-012-close-phase-2-clustering-vision-scope.md`)
§Counter-evidence 1 cites measured numbers for whether PageRank materially reorders the
hub list that `--knowledge-summary` already emits. Those numbers were originally produced
by an inline heredoc in Session 57 and no script survived, so the figures in an Accepted
decision could not be regenerated. This script is that missing artifact.

The check is **pre-registered**, and the threshold is reproduced here verbatim from the
session that ran it, so the verdict cannot be renegotiated after seeing the output:

    3 or more positions changed in the top 10, OR any new entrant
    => the reordering is material.

Session 57 recorded: Graph Explorer 9/10 positions changed; DSM Central 5/10 changed with
2 new entrants; global Pearson r = 0.92 between degree and PageRank. Both corpora cleared
the threshold, which refuted the agent's own prior claim that PageRank would collapse to
the degree ranking on a graph this sparse.

**A defect in the original S57 script is deliberately fixed here, and the fix changes
reported numbers.** That script looked up degree counts from a dictionary holding only the
top-10 rows, so any file that entered the PageRank top 10 from outside the degree top 10
printed "(degree refs: 0)", which reads as "no references at all". The true values in the
two observed cases were 29 refs at rank 12 and 25 at rank 15. This script ranks the full
file set and reports the real degree rank and count for every entrant.

Reproduction status as of 2026-08-04 (S58), stated in full because a partial match is
not a match:

  VALIDATED. The degree side reproduces the shipped ranking exactly. All 10 positions of
  this script's Graph Explorer degree top-10 are identical to the `## Hub Documents` table
  emitted by `dsm-validate . --knowledge-summary`, over the same 199-file scan.

  REPRODUCED. The verdict is unchanged on both corpora: MATERIAL REORDERING. DSM Central's
  Pearson r comes out at 0.9204 against the 0.92 recorded in DEC-012, with 2 new entrants,
  also as recorded.

  DIVERGENT. The positions-changed counts do not match. This script reports 7/10 for
  Graph Explorer and 8/10 for DSM Central; DEC-012 records 9/10 and 5/10. Two candidate
  causes, and they are not separable from here: the corpora moved (DSM Central released
  v1.19.0 between the S57 run and this one), and S57's exact projection could not be
  inspected because no script survived, which is the gap this file exists to close. The
  divergence does not touch DEC-012's conclusion, since that rests on the threshold being
  cleared rather than on the specific count, but it is recorded rather than smoothed over.

Usage:
    python scripts/check_pagerank_vs_degree.py
    python scripts/check_pagerank_vs_degree.py /path/to/repo [/path/to/other-repo]

Requires the optional graph extra: pip install -e '.[graph]'
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

try:
    import networkx as nx
except ImportError:  # pragma: no cover - environment guard
    sys.exit("networkx is required: pip install -e '.[graph]'")

from config.config_loader import DEFAULT_EXCLUDES  # noqa: E402
from filter.file_filter import filter_files  # noqa: E402
from graph.graph_builder import build_reference_graph  # noqa: E402
from parser.cross_ref_extractor import extract_cross_references  # noqa: E402
from parser.markdown_parser import parse_markdown_file  # noqa: E402
from validator.cross_ref_validator import build_section_lookup  # noqa: E402

TOP_N = 10
# Pre-registered before the S57 measurement. Do not adjust to fit an outcome.
THRESHOLD_POSITIONS_CHANGED = 3


def build_graph(repo: Path) -> nx.DiGraph:
    """Parse a repo's markdown and build the same reference graph the CLI builds."""
    md_files = sorted(repo.glob("**/*.md"))
    md_files = filter_files(md_files, DEFAULT_EXCLUDES, repo)

    documents = []
    references: dict[str, list] = {}
    for path in md_files:
        try:
            doc = parse_markdown_file(str(path))
        except Exception:
            continue
        documents.append(doc)
        refs = extract_cross_references(str(path))
        if refs:
            references[doc.file] = refs

    return build_reference_graph(documents, references, build_section_lookup(documents))


def degree_scores(G: nx.DiGraph) -> dict[str, int]:
    """Incoming REFERENCES aggregated to the file level.

    This mirrors ``_hub_rows`` in ``src/analysis/knowledge_summary.py`` exactly: for each
    FILE node, count REFERENCES edges arriving at any section the file CONTAINS. It is
    computed for **every** file, not just the top N, which is the bug fix described in the
    module docstring.
    """
    scores: dict[str, int] = {}
    for node, data in G.nodes(data=True):
        if data.get("type") != "FILE":
            continue
        count = 0
        for _, target, edge_data in G.out_edges(node, data=True):
            if edge_data.get("type") == "CONTAINS":
                count += sum(
                    1 for _, _, d in G.in_edges(target, data=True)
                    if d.get("type") == "REFERENCES"
                )
        scores[node] = count
    return scores


def file_reference_projection(G: nx.DiGraph) -> nx.DiGraph:
    """Project section-level REFERENCES edges onto a file-level digraph.

    Necessary because PageRank cannot be run on the raw graph and compared to the degree
    metric. In the raw graph, ``REFERENCES`` edges run section to section and ``FILE``
    nodes carry only outgoing ``CONTAINS`` edges, so a FILE node has no in-edges at all.
    Running PageRank on the raw graph (or its reverse) therefore scores files by how many
    sections they contain, not by how often they are referenced, and produces a top-10 of
    large documents with zero incoming references.

    The projection maps each ``REFERENCES`` edge (u, v) to an edge
    ``file(u) -> file(v)``, preserving the direction so that a referenced file accumulates
    in-edges. ``nx.pagerank`` on this graph is then the centrality analogue of the
    file-level incoming-reference count that ``_hub_rows`` ships.
    """
    P = nx.DiGraph()
    for node, data in G.nodes(data=True):
        if data.get("type") == "FILE":
            P.add_node(node)

    for u, v, data in G.edges(data=True):
        if data.get("type") != "REFERENCES":
            continue
        fu = G.nodes[u].get("file")
        fv = G.nodes[v].get("file")
        if not fu or not fv or fu == fv:
            continue  # self-references do not contribute to hub standing
        if P.has_edge(fu, fv):
            P[fu][fv]["weight"] += 1
        else:
            P.add_edge(fu, fv, weight=1)
    return P


def pearson(xs: list[float], ys: list[float]) -> float:
    """Pearson correlation without a numpy/scipy dependency."""
    n = len(xs)
    if n < 2:
        return float("nan")
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return float("nan")
    return cov / (vx * vy) ** 0.5


def analyse(repo: Path) -> dict:
    G = build_graph(repo)
    deg = degree_scores(G)
    if not deg:
        return {"repo": repo, "error": "no FILE nodes in graph"}

    # PageRank runs on the file-level REFERENCES projection, so that being *referenced*
    # raises the score. See file_reference_projection for why the raw graph cannot be used.
    P = file_reference_projection(G)
    pr_full = nx.pagerank(P, weight="weight")
    pr = {node: pr_full.get(node, 0.0) for node in deg}

    deg_ranked = sorted(deg.items(), key=lambda kv: (-kv[1], kv[0]))
    deg_ranked = [(f, c) for f, c in deg_ranked if c > 0]
    pr_ranked = sorted(pr.items(), key=lambda kv: (-kv[1], kv[0]))

    deg_top = [f for f, _ in deg_ranked[:TOP_N]]
    pr_top = [f for f, _ in pr_ranked[:TOP_N]]
    deg_rank_of = {f: i + 1 for i, (f, _) in enumerate(deg_ranked)}

    entrants = [f for f in pr_top if f not in deg_top]
    changed = sum(
        1 for i, f in enumerate(pr_top)
        if i >= len(deg_top) or deg_top[i] != f
    )

    common = [f for f in deg if deg[f] > 0]
    r = pearson([float(deg[f]) for f in common], [pr[f] for f in common])

    return {
        "repo": repo,
        "files_with_refs": len(deg_ranked),
        "files_total": len(deg),
        "deg_top": deg_top,
        "pr_top": pr_top,
        "deg_rank_of": deg_rank_of,
        "deg": deg,
        "changed": changed,
        "entrants": entrants,
        "pearson": r,
        "material": changed >= THRESHOLD_POSITIONS_CHANGED or bool(entrants),
    }


def report(res: dict) -> None:
    name = os.path.basename(str(res["repo"]).rstrip("/"))
    print(f"\n{'=' * 78}\n{name}  ({res['repo']})\n{'=' * 78}")
    if "error" in res:
        print(f"  SKIPPED: {res['error']}")
        return

    print(
        f"  {res['files_with_refs']} of {res['files_total']} files carry incoming "
        f"references ({100 * res['files_with_refs'] / res['files_total']:.1f}%)"
    )
    print(f"\n  {'#':<3} {'degree ranking':<44} {'PageRank ranking':<44}")
    print(f"  {'-' * 3} {'-' * 44} {'-' * 44}")
    for i in range(TOP_N):
        d = os.path.basename(res["deg_top"][i]) if i < len(res["deg_top"]) else ","
        p = os.path.basename(res["pr_top"][i]) if i < len(res["pr_top"]) else ","
        mark = " " if d == p else "*"
        print(f"  {i + 1:<3} {d:<44} {mark}{p:<43}")

    if res["entrants"]:
        print("\n  New entrants (in PageRank top 10, absent from degree top 10):")
        for f in res["entrants"]:
            rank = res["deg_rank_of"].get(f)
            # The S57 defect lived here: it printed 0 for these files.
            where = f"degree rank {rank}, {res['deg'][f]} refs" if rank else "no incoming refs"
            print(f"    - {os.path.basename(f)} ({where})")
    else:
        print("\n  New entrants: none")

    print(f"\n  Positions changed in top 10: {res['changed']}/{TOP_N}")
    print(f"  Pearson r (degree vs PageRank, files with refs): {res['pearson']:.4f}")
    verdict = "MATERIAL REORDERING" if res["material"] else "NOT MATERIAL"
    print(
        f"  Verdict against the pre-registered threshold "
        f"(>={THRESHOLD_POSITIONS_CHANGED} changed or any entrant): {verdict}"
    )


def main(argv: list[str]) -> int:
    if argv:
        repos = [Path(a).expanduser().resolve() for a in argv]
    else:
        repos = [REPO_ROOT, Path("~/dsm-agentic-ai-data-science-methodology").expanduser()]

    print("PageRank vs degree hub ranking, DEC-012 counter-evidence 1")
    print(f"Pre-registered threshold: >={THRESHOLD_POSITIONS_CHANGED} of top-{TOP_N} "
          "positions changed, or any new entrant.")

    missing = [r for r in repos if not r.exists()]
    for r in missing:
        print(f"\n  WARNING: {r} does not exist, skipping.")

    for repo in [r for r in repos if r.exists()]:
        report(analyse(repo))

    print(
        "\nNote: this compares the *ordering* produced by two centrality measures. It does "
        "not\nestablish that either ordering is more useful to a reader. See DEC-012 "
        "§Conditions 4:\noption A (a centrality upgrade) remains unresolved, not rejected."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
