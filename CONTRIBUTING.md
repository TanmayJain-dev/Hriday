# Contributing to HRIDAY

## 1. First-time setup

```bash
git clone https://github.com/TanmayJain-dev/Hriday.git
cd Hriday
git checkout main
git pull --ff-only origin main
```

## 2. Create your branch

Use the prepared branch naming convention:

```bash
git checkout -b feature/member-X-<domain>
```

Examples:

```bash
git checkout -b feature/member-1-graph
git checkout -b feature/member-3-extraction
git checkout -b feature/member-4-topology
```

Replace `X` with the member number assigned by the team.

## 3. Before starting work each day

```bash
git checkout main
git pull --ff-only origin main
git checkout feature/member-X-<domain>
git rebase main
```

Only rebase your own feature branch. If you already have uncommitted work, inspect `git status` first.

## 4. During work

Keep changes within your ownership boundary.

```bash
git status
git diff
git diff --check
```

## 5. Commit

Stage only your files:

```bash
git add <your-files>
git diff --cached
git commit -m "feat(graph): add downstream traversal"
```

## 6. Push

```bash
git push -u origin feature/member-X-<domain>
```

Then open a pull request into `main`.

## Protected behavior

Never use these on shared work:

```text
git push --force
git reset --hard
git clean -fd
git checkout -- .
```

If local state is confusing, stop and ask rather than destroying work.
