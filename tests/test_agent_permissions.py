"""The OpenCode reviewer's outside-the-worktree grants (the owner, 2026-10-11): /tmp and the
pinned DOSBox-X bundle are open; the owner-authorized timezone read is scoped by tool permissions.
OpenCode needs an /etc/* external-directory gate for /etc/timezone because it requests the parent
directory glob. Read rules allow only the timezone file, while path-insensitive grep/glob tools
stay denied. This is an OpenCode tool policy, not an OS sandbox. The reviewer is the one OpenCode
agent: the main session or a Claude agent implements (CLAUDE.md "Choosing models", 2026-10-11)."""
from fnmatch import fnmatchcase
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# the one grant outside /tmp: the DOSBox-X 2024.03.01 bundle (#117), the folder and what is in it
BUNDLE = ("~/tools/dosbox-x-2024.03.01", "~/tools/dosbox-x-2024.03.01/*")


def grants(agent):
    """The `external_directory` block of an agent's frontmatter, as {pattern: action}."""
    front = (ROOT / ".opencode" / "agents" / f"{agent}.md").read_text().split("---")[1]
    block = re.search(r"^  external_directory:\n((?:    .*\n)+)", front, re.M)
    assert block, f"{agent}: no external_directory block"
    return dict(re.findall(r'^    "([^"]+)": (\w+)$', block.group(1), re.M))


def permission_rules(agent, permission):
    """Return ordered pattern/action rules from one mapping-valued frontmatter permission."""
    front = (ROOT / ".opencode" / "agents" / f"{agent}.md").read_text().split("---")[1]
    block = re.search(rf"^  {re.escape(permission)}:\n((?:    .*\n)+)", front, re.M)
    assert block, f"{agent}: no {permission} permission block"
    return re.findall(r'^    "([^"]+)": (\w+)$', block.group(1), re.M)


def action_for(rules, requested):
    """OpenCode 1.18.32 evaluates permission rules with last-match-wins semantics."""
    action = None
    for pattern, value in rules:
        if fnmatchcase(requested, pattern):
            action = value
    return action


def under_tmp(pattern):
    """Whether a grant stays inside /tmp once `.` and `..` are resolved (a glob is a name)."""
    if not pattern.startswith("/"):
        return False
    parts = []
    for part in pattern.split("/")[1:]:
        if part in ("", "."):
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return bool(parts) and parts[0] == "tmp"


AGENTS = ("reviewer",)


class AgentTmpGrantTests(unittest.TestCase):
    def test_the_reviewer_is_the_one_opencode_agent(self):
        names = sorted(p.stem for p in (ROOT / ".opencode" / "agents").glob("*.md"))
        self.assertEqual(names, ["reviewer"])

    def test_tmp_is_open_to_the_reviewer(self):
        for agent in AGENTS:
            g = grants(agent)
            self.assertEqual(g.get("/tmp"), "allow", agent)
            self.assertEqual(g.get("/tmp/*"), "allow", agent)

    def test_the_dosbox_bundle_is_open_to_the_reviewer(self):
        # the pinned emulator every run executes (#117, setup/dosbox-x-2024.03.01.sh): a reviewer
        # reading its wrapper ended PR 120's re-check (the owner, 2026-10-11)
        for agent in AGENTS:
            g = grants(agent)
            for p in BUNDLE:
                self.assertEqual(g.get(p), "allow", (agent, p))

    def test_nothing_else_outside_the_worktree_is_granted(self):
        for agent in AGENTS:
            outside = {p for p, action in grants(agent).items()
                       if action == "allow" and not under_tmp(p) and p not in BUNDLE}
            # OpenCode 1.18.32 derives /etc/* from a read of /etc/timezone; direct read policy
            # below narrows that backend gate to the single owner-authorized file.
            self.assertEqual(outside, {"/etc/*"}, agent)

    def test_only_the_authorized_timezone_read_is_allowed(self):
        for agent in AGENTS:
            rules = permission_rules(agent, "read")
            self.assertEqual(action_for(rules, "/etc/timezone"), "allow", agent)
            self.assertEqual(action_for(rules, "/etc/hostname"), "deny", agent)
            self.assertEqual(action_for(rules, "/etc/shadow"), "deny", agent)
            self.assertEqual(action_for(rules, "/etc"), "deny", agent)
            self.assertLess(rules.index(("/etc/*", "deny")),
                            rules.index(("/etc/timezone", "allow")), agent)

    def test_writes_and_parsed_bash_paths_to_etc_are_denied(self):
        for agent in AGENTS:
            front = (ROOT / ".opencode" / "agents" / f"{agent}.md").read_text().split("---")[1]
            self.assertRegex(front, r"(?m)^  edit: deny$")
            rules = permission_rules(agent, "bash")
            self.assertEqual(action_for(rules, "cat /etc/timezone"), "allow", agent)
            self.assertEqual(action_for(rules, "cat /etc/hostname"), "deny", agent)
            self.assertEqual(action_for(rules, "tee /etc/timezone"), "deny", agent)
            self.assertEqual(action_for(rules, "tee /etc/hostname"), "deny", agent)
            self.assertEqual(action_for(rules, "printf x > /etc/timezone"), "deny", agent)
            self.assertEqual(action_for(rules, "printf x >> /etc/hostname"), "deny", agent)

    def test_path_insensitive_search_tools_stay_disabled(self):
        # These tools ask permission for the search expression, not the requested file path;
        # allowing them alongside the /etc/* backend gate would expose sibling files.
        for agent in AGENTS:
            self.assertEqual(action_for(permission_rules(agent, "grep"), "timezone"), "deny", agent)
            self.assertEqual(action_for(permission_rules(agent, "glob"), "*"), "deny", agent)

    def test_a_dotted_path_out_of_tmp_is_not_under_tmp(self):
        # Luna's R1 on PR 119: "/tmp/../home/*" starts with "/tmp/" but leaves /tmp
        for p in ("/tmp/../home/*", "/tmp/./../etc", "/tmpfoo/*", "tmp/*"):
            self.assertFalse(under_tmp(p), p)
        for p in ("/tmp", "/tmp/*", "/tmp/opencode/*", "/tmp/a/./b"):
            self.assertTrue(under_tmp(p), p)


if __name__ == "__main__":
    unittest.main()
