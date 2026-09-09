#!/usr/bin/env python3
"""Record and verify a Git worktree's per-run starting commit."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


class GuardError(Exception):
    pass


def git(repo, *args, allowed=(0,)):
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode not in allowed:
        raise GuardError(result.stderr.strip() or "git command failed")
    return result


def commit(repo, ref):
    return git(repo, "rev-parse", "--verify", "--end-of-options", ref + "^{commit}").stdout.strip()


def snapshot(repo):
    paths = {}
    for name, flag in (
        ("worktree", "--show-toplevel"),
        ("git_dir", "--git-dir"),
        ("git_common_dir", "--git-common-dir"),
    ):
        paths[name] = str(Path(git(repo, "rev-parse", "--path-format=absolute", flag).stdout.strip()).resolve())
    branch = git(repo, "symbolic-ref", "--quiet", "HEAD", allowed=(0, 1))
    return {**paths, "branch": branch.stdout.strip() or None, "head": commit(repo, "HEAD")}


def is_ancestor(repo, ancestor, descendant):
    return git(repo, "merge-base", "--is-ancestor", ancestor, descendant, allowed=(0, 1)).returncode == 0


def read_record(path, run_id):
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise GuardError("run record is missing; start must run before any history changes")
    except (ValueError, OSError) as error:
        raise GuardError("cannot read run record: " + str(error))
    required = ("worktree", "git_dir", "git_common_dir", "run_start")
    if (
        not isinstance(record, dict)
        or record.get("version") != 1
        or record.get("run_id") != run_id
        or any(not isinstance(record.get(key), str) for key in required)
        or "branch" not in record
        or "task_base" not in record
    ):
        raise GuardError("invalid run record; preserve it for diagnosis")
    return record


def verify(repo, state, record, require_task_base):
    failures = []
    for key in ("worktree", "git_dir", "git_common_dir", "branch"):
        if state[key] != record[key]:
            failures.append(key + " changed since this run started")
    if not is_ancestor(repo, record["run_start"], state["head"]):
        failures.append("HEAD no longer contains run_start " + record["run_start"])
    if require_task_base and record["task_base"] and not is_ancestor(repo, record["task_base"], state["head"]):
        failures.append("HEAD does not contain task_base " + record["task_base"])
    return failures


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="task worktree path (default: current directory)")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("inspect", help="print worktree identity without writing anything")
    start = commands.add_parser("start", help="capture this run once; existing records are never replaced")
    start.add_argument("--run-id", required=True)
    start.add_argument("--task-base", help="task's required base commit, frozen separately from run_start")
    check = commands.add_parser("check", help="verify identity and ancestry; never repair history")
    check.add_argument("--run-id", required=True)
    args = parser.parse_args(argv)

    try:
        state = snapshot(args.repo)
        if args.command == "inspect":
            print(json.dumps(state, indent=2))
            return 0
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", args.run_id):
            raise GuardError("run-id must be 1-128 ASCII letters, digits, dots, underscores or hyphens; start with a letter or digit")
        # Each linked worktree has its own git_dir even though refs are shared.
        path = Path(state["git_dir"]) / "cooperation-skill" / "runs" / (args.run_id + ".json")
        if args.command == "start":
            task_base = commit(args.repo, args.task_base) if args.task_base else None
            candidate = {
                "version": 1,
                "run_id": args.run_id,
                **{key: value for key, value in state.items() if key != "head"},
                "run_start": state["head"],
                "task_base": task_base,
            }
            path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with path.open("x", encoding="utf-8") as handle:
                    json.dump(candidate, handle, indent=2)
                    handle.write("\n")
            except FileExistsError:
                pass
            record = read_record(path, args.run_id)
            if args.task_base and record["task_base"] != task_base:
                raise GuardError("task_base differs from the existing run record; it was not overwritten")
        else:
            record = read_record(path, args.run_id)
        failures = verify(args.repo, state, record, require_task_base=args.command == "check")
        print(json.dumps({
            "status": "failed" if failures else "ok",
            "record": str(path),
            "run_id": args.run_id,
            "run_start": record["run_start"],
            "task_base": record["task_base"],
            "head": state["head"],
            "branch": state["branch"],
            "failures": failures,
        }, indent=2))
        return 1 if failures else 0
    except (GuardError, OSError) as error:
        print(json.dumps({"status": "error", "error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
