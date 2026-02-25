# WSL Migration Guide

**Purpose:** Step-by-step guide for migrating Python/data science projects from Windows to WSL2.
**Audience:** Any DSM-tracked project needing environment standardization.
**Created:** 2026-02-04
**Date Completed:** 2026-02-24
**Outcome Reference:** Consumed at Session 16 start

---

## Why WSL?

| Benefit | Description |
|---------|-------------|
| **Environment consistency** | Same as CI/CD and production (Linux) |
| **Path simplicity** | No more `D:\` vs `/mnt/d/` issues |
| **Native tooling** | Git, Python, shell tools work as expected |
| **Container-ready** | Easy path to Docker when needed |
| **IDE support** | VSCode Remote-WSL, PyCharm, etc. |

---

## Prerequisites

### On Windows
- Windows 10 (build 19041+) or Windows 11
- WSL2 installed (`wsl --install` in PowerShell as admin)
- Ubuntu or preferred Linux distro installed
- VSCode with Remote-WSL extension (optional but recommended)

### In WSL
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.12+ (if not present)
sudo apt install python3.12 python3.12-venv python3-pip -y

# Install git (usually pre-installed)
sudo apt install git -y

# Verify
python3 --version  # Should show 3.12+
git --version
```

---

## Migration Steps

### Step 1: Backup on Windows

Before anything, ensure your work is safely backed up:

```powershell
# In Windows terminal, navigate to project
cd D:\data-science\your-project

# Verify clean git state
git status

# Push all changes
git add -A
git commit -m "Pre-WSL migration checkpoint"
git push origin master
```

### Step 2: Choose WSL Directory Structure

Projects can be placed either at home root (`~/project-name`) or in a subdirectory (`~/data-science/project-name`). The DSM ecosystem uses home root for primary projects:

```bash
# In WSL terminal
# Projects at home root (recommended for DSM ecosystem)
cd ~

# Or create subdirectory if preferred
mkdir -p ~/data-science
```

### Step 3: Copy Projects

**Option A: Copy from Windows mount (preserves local changes)**
```bash
# Copy entire project folder to home root
cp -r /mnt/d/data-science/your-project ~/your-project

# Or to subdirectory
cp -r /mnt/d/data-science/your-project ~/data-science/your-project
```

**Option B: Fresh clone (clean start)**
```bash
# Clone from remote
git clone https://github.com/your-org/your-project.git ~/your-project
```

### Step 4: Set Up Python Environment

```bash
cd ~/your-project

# Remove Windows venv if copied
rm -rf .venv venv __pycache__

# Create fresh venv
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -e ".[dev]"  # or: pip install -r requirements.txt
```

### Step 5: Verify Tests Pass

```bash
# Run test suite
pytest tests/

# Should see same results as on Windows
```

### Step 6: Update Project Configuration

Update any hardcoded paths in your project:

**CLAUDE.md (if using Claude Code)**
```markdown
# Before
- Project path: D:\data-science\your-project\

# After
- Project path: ~/data-science/your-project/
```

**Config files**
Most config files should work as-is if they use relative paths or forward slashes.

### Step 7: Configure Git (if needed)

```bash
# Set identity (one-time)
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Set default branch name
git config --global init.defaultBranch master

# Verify remote
git remote -v
```

### Step 8: Set Up VSCode (Optional)

```bash
# Open project in VSCode from WSL
code ~/data-science/your-project
```

Or from Windows: `File > Open Folder > \\wsl$\Ubuntu\home\<username>\data-science\your-project`

---

## Project-Specific Notes

### DSM Graph Explorer
```bash
cd ~/dsm-graph-explorer

# Dependencies
pip install -e ".[dev]"

# Verify
pytest tests/  # Expect 202 tests
dsm-validate ~/dsm-agentic-ai-data-science-methodology
```

### DSM Methodology Repository
```bash
cd ~/dsm-agentic-ai-data-science-methodology

# No Python dependencies, just markdown files
# Verify git status
git status
```

### Other Python Projects
```bash
# Generic pattern
pip install -e ".[dev]"  # or pip install -r requirements.txt
pytest  # or your test command
```

---

## Troubleshooting

### Permission denied errors
```bash
# Fix ownership
sudo chown -R $USER:$USER ~/data-science/your-project
```

### Python command not found
```bash
# Check available versions
ls /usr/bin/python*

# Use specific version
python3.12 -m venv .venv
```

### Git credential issues
```bash
# Use credential helper
git config --global credential.helper store
# Next push will prompt and save credentials
```

### WSL slow with Windows files
Always work in the WSL filesystem (`~/`), not in `/mnt/d/`. File operations are much faster in native WSL paths.

---

## Post-Migration Checklist

- [ ] All projects copied to WSL home directory (`~/project-name` or `~/data-science/project-name`)
- [ ] Virtual environments recreated (not copied)
- [ ] Tests pass for each project
- [ ] Git remotes configured
- [ ] CLAUDE.md updated with new paths
- [ ] VSCode connects via Remote-WSL
- [ ] Claude Code sessions work in WSL terminal
- [ ] Windows copies retained as backup (optional)

### DSM Ecosystem Path Mappings

| Project | WSL Path |
|---------|----------|
| DSM Methodology | `~/dsm-agentic-ai-data-science-methodology` |
| DSM Graph Explorer | `~/dsm-graph-explorer` |
| sql-query-agent | `~/sql-query-agent-ollama` (or as preferred) |

---

## Rollback Plan

If migration fails, your Windows copies remain intact:
1. Continue working on Windows as before
2. Debug WSL issues separately
3. Try migration again when resolved

---

## References

- [Microsoft WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [VSCode Remote-WSL](https://code.visualstudio.com/docs/remote/wsl)
- DEC-004: WSL Migration Decision (dsm-graph-explorer)

---

**Guide version:** 1.1
**Last updated:** 2026-02-05
**Author:** Alberto Diaz Durana (with AI assistance)
