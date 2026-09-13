---
name: sync-repo
description: Keep the brand OS repository current before Hermes edits files, and push Hermes-authored changes with a clear commit prefix.
license: MIT
metadata:
  hermes:
    tags:
    - Git
    - GitHub
    - RepoSync
    - brand
  version: 1.0.0
  author: brand OS
  platforms:
  - linux
  - macos
---

# Sync Repo

Use this skill before changing files in the brand OS repo from a production Hermes profile, especially on the VPS production instance.

## Operating Branch

Read the branch from `config/hermes-profiles.yaml`:

```bash
BRANCH=$(python3 - <<'PY'
import yaml
with open('config/hermes-profiles.yaml') as f:
    print(yaml.safe_load(f)['operating_branch'])
PY
)
test "$BRANCH" = "main" || { echo "Unexpected operating_branch=$BRANCH"; exit 1; }
```

D1 rule: production agents pull and push only the registry branch. Do not discover or choose a different branch from local git state.

## Before Editing

1. Confirm you are in the brand OS repo and on the registry branch:

```bash
git rev-parse --show-toplevel
git remote -v
git branch --show-current
test "$(git branch --show-current)" = "$BRANCH"
```

2. Check for existing local work:

```bash
git status --short
```

If the working tree is dirty before you start, stop and report the changed files. Do not overwrite or auto-commit work that owner or another agent may have made.

3. Pull only when the tree is clean, using the D3 rebase protocol:

```bash
git fetch origin
git pull --rebase origin "$BRANCH"
```

If the pull/rebase fails, stop and report the failure. Do not merge, reset, clean, or force-push unless owner explicitly asks.

## After Editing

1. Review the diff:

```bash
git status --short
git diff --check
git diff --stat
```

2. Commit only the files you changed:

```bash
git add <files-you-changed>
git commit -m "[hermes] <specific summary>"
```

3. Push to the registry branch. If rejected because the remote moved, retry once with `pull --rebase`, then stop and report if it still fails:

```bash
git push origin "$BRANCH" || {
  git pull --rebase origin "$BRANCH" && git push origin "$BRANCH"
}
```

## Guardrails

- Never commit `.env`, logs, caches, key files, token files, or profile secrets.
- Never use `git reset --hard`, force push, or broad checkout commands without explicit approval.
- Use `[hermes]` for Hermes-authored repo changes.
- Use `[mac-sync]` only for local scheduled safety-net commits.
- Keep reusable workflow logic in `skills-core/`; keep Hermes-specific setup in `products/hermes-brand-agent/`.
