# Release Flow (feat -> pre)

## Variables
- `<main_branch>`: mainline branch name, typically `master` or `main`.
- `<feature_branch>`: user-specified feature branch; if not provided, use current branch.

## SOP Steps
1) **Branch baseline**
   - `git symbolic-ref --short refs/remotes/origin/HEAD` to detect mainline.
   - Switch to `<feature_branch>` if needed.

2) **Stash (if dirty)**
   - `git status`
   - `git stash push -u -m "Claude-Auto-Stash-<DATE>"`

3) **Sync mainline**
   - `git fetch --prune origin <main_branch>`
   - `git merge origin/<main_branch>`
   - If conflicts: resolve using the conflict playbook, then `git add` and `git commit`.

4) **Restore stash**
   - `git stash pop`
   - Resolve conflicts if any, then `git add` and `git commit`.

5) **Rebuild pre**
   - `git branch -D pre` (local only)
   - `git checkout -b pre origin/<main_branch>`

6) **Remote backup + delete pre**
   - Confirm remote pre exists.
   - `git fetch --prune origin`
   - `git push origin origin/pre:refs/heads/pre_$(date +%Y%m%d)`
   - Confirm backup succeeded, then `git push origin --delete pre`.

7) **Final merge + push**
   - `git merge <feature_branch>`
   - `git push origin pre`

## Guardrails
- Never delete remote `pre` without explicit user confirmation.
- If a step fails, stop and report the exact error before continuing.
