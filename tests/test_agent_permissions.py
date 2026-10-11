"""The OpenCode agents' outside-the-worktree grants (the owner, 2026-10-11): all of /tmp is open to
the implementer and the reviewer, so a model's loose scratch file there no longer ends a run with
nothing posted (isle-wars-archaeology d30a137 hit it three times); every other path outside the
worktree stays rejected."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def grants(agent):
    """The `external_directory` block of an agent's frontmatter, as {pattern: action}."""
    front = (ROOT / ".opencode" / "agents" / f"{agent}.md").read_text().split("---")[1]
    block = re.search(r"^  external_directory:\n((?:    .*\n)+)", front, re.M)
    assert block, f"{agent}: no external_directory block"
    return dict(re.findall(r'^    "([^"]+)": (\w+)$', block.group(1), re.M))


class AgentTmpGrantTests(unittest.TestCase):
    def test_tmp_is_open_to_both_agents(self):
        for agent in ("implementer", "reviewer"):
            g = grants(agent)
            self.assertEqual(g.get("/tmp"), "allow", agent)
            self.assertEqual(g.get("/tmp/*"), "allow", agent)

    def test_nothing_else_outside_the_worktree_is_granted(self):
        for agent in ("implementer", "reviewer"):
            outside = {p for p, action in grants(agent).items()
                       if action == "allow" and not (p == "/tmp" or p.startswith("/tmp/"))}
            self.assertEqual(outside, set(), agent)


if __name__ == "__main__":
    unittest.main()
