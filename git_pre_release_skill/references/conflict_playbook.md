# Conflict Resolution Playbook (Advanced)

## 1) Identify conflicts quickly
- `git status`
- `git diff --name-only --diff-filter=U`
- `git diff --check` (leftover conflict markers)

## 2) Inspect base/ours/theirs
- `git show :1:<path>` (base)
- `git show :2:<path>` (ours)
- `git show :3:<path>` (theirs)
- `git checkout --conflict=merge <path>` to reintroduce conflict markers if needed.

## 3) Choose a resolution strategy per file
- **Manual merge**: edit `<<<<<<<` blocks, keep intent from both sides.
- **Prefer ours/theirs** (only if safe):
  - `git checkout --ours <path>`
  - `git checkout --theirs <path>`
  - Then `git add <path>`.
- **Regenerate**: for lockfiles or generated outputs, re-run generator and `git add`.

## 4) Handle tricky conflict types
- **Rename/rename**: pick final path, `git mv` to the chosen name, then `git add -A`.
- **Delete/modify**: confirm whether file should exist; if kept, restore and edit; if removed, `git rm`.
- **Binary conflicts**: cannot merge; pick one side after business confirmation.
- **Directory/file conflicts**: choose structure, move files, `git add -A`.

## 5) Large or multi-file conflicts
- Resolve in dependency order (shared types/config first, call sites after).
- Use `git mergetool` if configured; otherwise do staged, small commits.
- Consider enabling `git rerere` for repeated conflicts:
  - `git config rerere.enabled true`

## 6) Validate before commit
- `git status` shows no unmerged paths.
- `git diff` is clean of conflict markers.
- Run minimal tests or lint if available.

## 7) Commit
- `git add <paths>` (avoid `git add .` unless confirmed).
- `git commit -m "Resolve merge conflicts"`

## 8) Abort safely (if needed)
- Merge: `git merge --abort`
- Rebase: `git rebase --abort`
