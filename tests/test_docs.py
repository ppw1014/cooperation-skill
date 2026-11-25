"""母本文档一致性检查:拦住改名、加字段之后正文与模板不同步。

运行:python3 -m unittest discover -s tests
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = sorted(p for p in ROOT.rglob("*.md") if ".git" not in p.parts)
OLD_ROLE_NAMES = ("Conductor", "Coordinator", "指挥")
# 只有迁移说明可以出现旧名
MIGRATION_MARKERS = ("改名", "迁移", "旧名")


def read(path):
    return path.read_text(encoding="utf-8")


class DocConsistencyTests(unittest.TestCase):
    def test_relative_links_resolve(self):
        broken = []
        for doc in DOCS:
            for target in re.findall(r"\]\(([^)\s]+)\)", read(doc)):
                if re.match(r"[a-z]+:", target) or target.startswith("#"):
                    continue
                path = target.split("#", 1)[0]
                if path and not (doc.parent / path).exists():
                    broken.append(f"{doc.relative_to(ROOT)} -> {target}")
        self.assertEqual(broken, [])

    def test_old_role_names_only_in_migration_notes(self):
        leftovers = []
        for doc in DOCS:
            for no, line in enumerate(read(doc).splitlines(), 1):
                if any(n in line for n in OLD_ROLE_NAMES) and not any(m in line for m in MIGRATION_MARKERS):
                    leftovers.append(f"{doc.relative_to(ROOT)}:{no}")
        self.assertEqual(leftovers, [])

    def test_message_kinds_match_protocol_types(self):
        protocol = read(ROOT / "protocol.md")
        line = re.search(r"\*\*消息类型\*\*:(.+?)。", protocol).group(1)
        types = [re.sub(r"[((].*?[))]", "", t).strip() for t in re.split(r"\s*/\s*", line)]

        message = read(ROOT / "templates" / "message.md")
        enum = re.search(r'^kind: "<([^>]+)>"', message, re.M).group(1).split("|")
        mapping_text = " ".join(l.lstrip("# ") for l in message.splitlines() if l.startswith("# "))
        mapping = dict(re.findall(r"([a-z-]+) (\S+?)(?: /|。|$)", mapping_text))

        self.assertEqual(sorted(enum), sorted(mapping), "kind 枚举与注释里的对照表不一致")
        self.assertEqual(sorted(types), sorted(mapping.values()), "kind 对照表与 protocol §3.2 消息类型不一致")

    def test_channel_self_check_matches_heading_format(self):
        protocol = read(ROOT / "protocol.md")
        pattern = re.search(r"grep -c '([^']+)' <信道文件>", protocol).group(1).replace("<N>", "12")
        heading = re.search(r"^(## #N ｜.*)$", protocol, re.M).group(1).replace("#N", "#12")
        self.assertRegex(heading, pattern)
        template = read(ROOT / "templates" / "channel.md")
        self.assertIn("## #N ｜", template)

    def test_bootstraps_point_to_anti_patterns(self):
        for path in sorted((ROOT / "templates").glob("*-bootstrap.md")):
            self.assertIn("anti-patterns.md", read(path), path.name)

    def test_merge_condition_lists_high_consequence_everywhere(self):
        for rel in ("protocol.md", "reviewer.md", "architect.md", "templates/reviewer-bootstrap.md"):
            text = read(ROOT / rel)
            self.assertIn("高后果类别的错误", text, rel)


if __name__ == "__main__":
    unittest.main()
