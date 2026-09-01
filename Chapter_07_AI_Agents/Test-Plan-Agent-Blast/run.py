#!/usr/bin/env python3
"""Test Plan Agent - CLI.

Usage:
    python run.py VWO-49                    # generate a plan
    python run.py "make a plan for VWO-49"  # same, natural language
    python run.py --health                  # test both connections
    python run.py --dry-run VWO-49          # fetch + normalize, no LLM call
    python run.py --force VWO-49            # plan even if the ticket is thin

Exit codes: 0 ok · 2 bad input · 3 auth · 4 not found · 5 rate limited ·
6 schema violation · 7 LLM failure
"""

import argparse
import sys
from pathlib import Path

import config_store
import jira_client
import llm_client
import navigation
from navigation import PipelineError, run_pipeline


def _print_health(cfg: dict) -> int:
    """Test Jira + Groq connectivity (BLAST Phase 2 Link)."""
    ok = True
    print("Testing connections...")

    jira_url = jira_client.normalize_base_url(cfg.get("jira_url", ""))
    if not jira_url or not cfg.get("jira_email") or not cfg.get("jira_token"):
        print("[FAIL] Jira: URL/email/token not configured. Add them on the Settings screen or in .env.")
        ok = False
    else:
        try:
            # Probe the Jira API (no ticket lookup) - a 200/401 tells us reachability.
            import requests
            resp = requests.get(
                f"{jira_url}/rest/api/3/myself",
                auth=(cfg["jira_email"], cfg["jira_token"]),
                timeout=15,
            )
            if resp.status_code == 200:
                print(f"[ OK ] Jira: authenticated at {jira_url}")
            elif resp.status_code == 401:
                print("[FAIL] Jira: credentials rejected (401).")
                ok = False
            else:
                print(f"[FAIL] Jira: HTTP {resp.status_code}.")
                ok = False
        except Exception as exc:
            print(f"[FAIL] Jira: {exc}")
            ok = False

    if not cfg.get("groq_key"):
        print("[FAIL] Groq: API key not configured.")
        ok = False
    else:
        try:
            import requests
            resp = requests.post(
                llm_client.GROQ_URL,
                json={"model": llm_client.GROQ_MODEL, "messages": [{"role": "user", "content": "ping"}], "max_tokens": 1},
                headers={"Authorization": f"Bearer {cfg['groq_key']}"},
                timeout=30,
            )
            if resp.status_code == 200:
                print(f"[ OK ] Groq: {llm_client.GROQ_MODEL} reachable")
            else:
                print(f"[FAIL] Groq: HTTP {resp.status_code} - {resp.text[:200]}")
                ok = False
        except Exception as exc:
            print(f"[FAIL] Groq: {exc}")
            ok = False

    return 0 if ok else 3


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Test Plan Agent - Jira ticket in, formal Test Plan out.")
    ap.add_argument("prompt", nargs="?", help="A Jira key (VWO-49) or a sentence containing one")
    ap.add_argument("--health", action="store_true", help="Test both connections and exit")
    ap.add_argument("--dry-run", action="store_true", help="Fetch + normalize only, no LLM call")
    ap.add_argument("--force", action="store_true", help="Generate even if the ticket is thin")
    args = ap.parse_args(argv)

    cfg = config_store.load_config()

    if args.health:
        return _print_health(cfg)

    if not args.prompt:
        ap.print_help()
        return navigation.BAD_INPUT

    try:
        result = run_pipeline(
            args.prompt,
            cfg,
            force=args.force,
            dry_run=args.dry_run,
            out_dir=Path(__file__).parent / "out",
        )
    except PipelineError as exc:
        print(f"ERROR: {exc.message}", file=sys.stderr)
        return exc.code

    ticket = result["ticket"]
    if args.dry_run:
        print(f"[dry-run] Fetched {ticket['key']} - {ticket['summary']}")
        print(f"[dry-run] Readiness: {navigation.readiness_score(ticket)[0]}/{navigation.readiness_score(ticket)[1]}")
        print(f"[dry-run] Description: {len(ticket['description'])} chars, AC: {len(ticket['acceptance_criteria'])} chars")
        print("[dry-run] No LLM call made.")
        return navigation.OK

    print(f"Generated plan for {ticket['key']}: {result['out_path']}")
    print(f"Trace: {result['trace_path']}")
    return navigation.OK


if __name__ == "__main__":
    sys.exit(main())
