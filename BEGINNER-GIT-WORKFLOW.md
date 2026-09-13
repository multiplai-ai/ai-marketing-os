# Working with Core using Git

Use one task branch and a reviewed pull request for each coherent change. Core
owns shared procedures; business context, credentials and operating data belong
in the consumer repository or its configured private storage.

## Start or resume a task

1. Open the correct repository in your coding app. Read its `AGENTS.md`.
2. Inspect the checkout before changing it:

   ```bash
   git status --short --branch
   git branch --show-current
   git diff
   ```

3. Preserve unfinished work. If the checkout is dirty or another task owns its
   branch, inspect the changes and resolve ownership before switching branches.
   Do not reset, stash or create another workspace simply to hide the conflict.
4. Fetch remote changes with `git fetch origin`. When starting from a clean
   checkout of `main`, update it with `git pull --ff-only origin main` and create
   a task branch such as `git switch -c codex/update-shared-procedure`.
5. In Codex, use an app-managed worktree or Handoff when isolation is needed.
   Do not create manual worktrees unless the owner explicitly requests one.

A branch names your proposed work. A commit records a local checkpoint. A push
uploads the branch. A pull request lets someone review it before it enters the
shared version of the repository.

## Make and validate a change

Edit canonical procedures only in `sops/<id>/SKILL.md`. Keep consumer values out
of shared source. Update the SOP version when its contract changes, regenerate
adapters using the repository's documented command, and run the validation in
[CONTRIBUTING.md](CONTRIBUTING.md).

Check the exact diff, including newly created files. Stage only files owned by
this task. Review `git diff --cached` before committing; it is the content Git
will record. Never stage credentials, source exports or unrelated work.

## Open a reviewed pull request

Commit a useful checkpoint, push the task branch, and open a pull request
explaining the problem, resulting behavior and validation performed. Address
review findings on that branch. Follow repository protections and required
checks; successful tests alone do not authorize a merge or release.

For changes across repositories, give each repository its own reviewed change.
A Core change may require a consumer binding update, but do not keep synchronized
copies of a shared SOP in both places.

## Finish

Report the pull request, validation results and any unresolved limitation. Leave
unmerged work on its branch. Clean up only branches or workspaces this task owns
and only when their work has been safely preserved. Archiving a Codex task lets
the app manage its associated worktree.

If a command fails, preserve the error and inspect state before retrying. Force
pushes, destructive resets and branch deletions are not routine fixes for a
confusing checkout.
