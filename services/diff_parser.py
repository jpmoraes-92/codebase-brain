import re

HUNK_HEADER = re.compile(r"@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@")

class ChangedFile:
    def __init__(self, path: str, added_lines: list, removed_lines: list):
        self.path = path
        self.added_lines = added_lines
        self.removed_lines = removed_lines
        self.changed_lines = sorted(list(set(added_lines + removed_lines)))

def parse_git_diff(raw_diff: str) -> list:
    """Parse determinístico de Git Unified Diff."""
    changed_files = []
    current_file = None
    old_line = None
    new_line = None
    added = []
    removed = []

    lines = raw_diff.splitlines()

    for line in lines:
        if line.startswith("+++ b/"):
            if current_file:
                changed_files.append(ChangedFile(current_file, added, removed))
            current_file = line[6:]
            added = []
            removed = []
            old_line = None
            new_line = None
            continue
            
        elif line.startswith("+++ /dev/null"):
            if current_file:
                changed_files.append(ChangedFile(current_file, added, removed))
                current_file = None
            added = []
            removed = []
            old_line = None
            new_line = None
            continue

        match = HUNK_HEADER.search(line)
        if match:
            old_line = int(match.group(1))
            new_line = int(match.group(3))
            continue

        if old_line is not None and new_line is not None:
            if line.startswith("+") and not line.startswith("+++"):
                added.append(new_line)
                new_line += 1
            elif line.startswith("-") and not line.startswith("---"):
                removed.append(old_line)
                old_line += 1
            elif line.startswith(" ") or line == "":
                old_line += 1
                new_line += 1

    if current_file and (added or removed):
        changed_files.append(ChangedFile(current_file, added, removed))

    return changed_files