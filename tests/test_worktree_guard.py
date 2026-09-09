import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "worktree_guard.py"


class WorktreeGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="cooperation-worktrees-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / "source repo"
        self.repo.mkdir()
        self.env = {
            key: value for key, value in os.environ.items()
            if not key.startswith("GIT_")
        }
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_AUTHOR_NAME": "Guard Test",
            "GIT_AUTHOR_EMAIL": "guard@example.invalid",
            "GIT_COMMITTER_NAME": "Guard Test",
            "GIT_COMMITTER_EMAIL": "guard@example.invalid",
            "GIT_TERMINAL_PROMPT": "0",
        })
        self.git(self.repo, "init", "-b", "main")
        self.base = self.save(self.repo, "base.txt", "base\n", "base")
        self.task = self.worktree("agent-one")
        self.start = self.save(self.task, "checkpoint.txt", "snapshot\n", "chore(agent): checkpoint")

    def git(self, repo, *args):
        result = subprocess.run(
            ["git", "-C", str(repo), *args], env=self.env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def save(self, repo, name, content, message):
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        self.git(repo, "add", "--", name)
        self.git(repo, "commit", "-m", message)
        return self.git(repo, "rev-parse", "HEAD")

    def worktree(self, branch):
        path = self.root / branch
        self.git(self.repo, "worktree", "add", "-b", branch, str(path), "main")
        return path

    def guard(self, repo, command, *args, code=0):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--repo", str(repo), command, *args],
            env=self.env, text=True, capture_output=True,
        )
        self.assertEqual(result.returncode, code, result.stdout + result.stderr)
        return json.loads(result.stdout if result.stdout else result.stderr)

    def begin(self, repo=None, run_id="turn-1", *args):
        return self.guard(repo or self.task, "start", "--run-id", run_id, *args)

    def check(self, repo=None, run_id="turn-1", code=0):
        return self.guard(repo or self.task, "check", "--run-id", run_id, code=code)

    def test_unchanged_and_descendant_pass_without_moving_start(self):
        initial = self.begin()
        self.check()
        tip = self.save(self.task, "feature.txt", "feature\n", "feature")
        repeated = self.begin()
        self.assertEqual(repeated["run_start"], self.start)
        self.assertEqual(repeated["record"], initial["record"])
        self.assertEqual(self.check()["head"], tip)

    def test_message_only_amend_reproduces_lost_start(self):
        initial = self.begin()
        before = Path(initial["record"]).read_bytes()
        tree = self.git(self.task, "rev-parse", "HEAD^{tree}")
        self.git(self.task, "commit", "--amend", "-m", "docs: rename checkpoint")
        self.assertEqual(self.git(self.task, "rev-parse", "HEAD^{tree}"), tree)
        self.assertIn("run_start", self.check(code=1)["failures"][0])
        self.guard(self.task, "start", "--run-id", "turn-1", code=1)
        self.assertEqual(Path(initial["record"]).read_bytes(), before)

    def test_reset_below_start_is_rejected(self):
        self.begin()
        self.git(self.task, "reset", "--hard", self.base)
        self.check(code=1)

    def test_rebase_that_replaces_start_is_rejected(self):
        self.begin()
        upstream = self.save(self.repo, "upstream.txt", "upstream\n", "upstream")
        self.git(self.task, "rebase", "--onto", upstream, self.base)
        self.check(code=1)

    def test_branch_switch_and_detach_are_rejected(self):
        self.begin()
        self.git(self.task, "switch", "-c", "replacement")
        self.assertIn("branch changed", self.check(code=1)["failures"][0])
        self.git(self.task, "checkout", "--detach", self.start)
        self.check(code=1)

    def test_initial_detached_head_can_advance_without_switching(self):
        self.git(self.task, "checkout", "--detach", self.start)
        self.begin()
        self.save(self.task, "detached.txt", "feature\n", "detached feature")
        self.assertIsNone(self.check()["branch"])

    def test_worktree_move_is_rejected(self):
        self.begin()
        moved = self.root / "moved task"
        self.git(self.repo, "worktree", "move", str(self.task), str(moved))
        result = self.check(moved, code=1)
        self.assertIn("worktree changed", result["failures"][0])

    def test_run_records_are_isolated_by_worktree_and_turn(self):
        other = self.worktree("agent-two")
        first = self.begin()
        second = self.begin(other)
        self.assertNotEqual(first["record"], second["record"])
        self.assertEqual(second["run_start"], self.base)
        tip = self.save(self.task, "next.txt", "next\n", "next")
        next_run = self.begin(run_id="turn-2")
        self.assertEqual(next_run["run_start"], tip)
        self.assertEqual(self.check()["run_start"], self.start)
        self.check(other)

    def test_authorized_dependency_merge_keeps_run_start(self):
        dependency = self.save(self.repo, "dependency.txt", "dependency\n", "dependency")
        record = self.begin(None, "turn-1", "--task-base", dependency)
        self.check(code=1)
        self.git(self.task, "merge", "--no-ff", dependency, "-m", "sync approved dependency")
        result = self.check()
        self.assertEqual(result["task_base"], dependency)
        self.assertEqual(result["run_start"], record["run_start"])
        self.guard(self.task, "start", "--run-id", "turn-1", "--task-base", self.base, code=2)
        self.assertEqual(self.check()["task_base"], dependency)

    def test_missing_record_fails_and_inspection_is_read_only(self):
        self.check(code=2)
        state = self.guard(self.task, "inspect")
        self.assertNotEqual(state["git_dir"], state["git_common_dir"])
        self.assertFalse((Path(state["git_dir"]) / "cooperation-skill").exists())

    def test_unique_messages_can_be_read_and_integrated_from_two_worktrees(self):
        other = self.worktree("agent-two")
        self.begin()
        self.begin(other)
        message_one = "docs/collab/messages/task-one/turn-1/001.md"
        message_two = "docs/collab/messages/task-two/turn-1/001.md"
        head_one = self.save(self.task, message_one, "id: task-one/turn-1/001\n", "send one")
        head_two = self.save(other, message_two, "id: task-two/turn-1/001\n", "send two")
        self.assertFalse((other / message_one).exists())
        self.assertEqual(self.git(other, "show", head_one + ":" + message_one), "id: task-one/turn-1/001")
        self.assertEqual(self.git(self.task, "show", head_two + ":" + message_two), "id: task-two/turn-1/001")
        self.check()
        self.check(other)
        self.begin(self.repo, "integrate-1")
        self.git(self.repo, "merge", "--no-ff", head_one, "-m", "integrate one")
        self.git(self.repo, "merge", "--no-ff", head_two, "-m", "integrate two")
        self.check(self.repo, "integrate-1")
        self.assertTrue((self.repo / message_one).is_file())
        self.assertTrue((self.repo / message_two).is_file())
        self.assertEqual(self.git(self.task, "rev-parse", "HEAD"), head_one)
        self.assertEqual(self.git(other, "rev-parse", "HEAD"), head_two)


if __name__ == "__main__":
    unittest.main()
