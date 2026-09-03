# Team Workflow

Each member works from their own feature branch. `main` remains the integration branch.

```bash
git checkout main
git pull --ff-only origin main
git checkout -b feature/member-X-<domain>
```

Then implement, test, inspect the diff, commit and push:

```bash
git status
git diff --check
git diff
git add <only-your-files>
git diff --cached
git commit -m "feat(domain): describe the change"
git push -u origin feature/member-X-<domain>
```

Open a PR into `main`. Never force-push shared branches or destroy work to resolve a conflict.
