# EV-Meter Release Automation

This directory contains automation scripts for releasing new versions of the EV-Meter ecosystem.

## Quick Start

```bash
# Test what a minor release would do (dry run)
python release.py --type minor --component both --dry-run

# Release a patch version for just the client
python release.py --type patch --component client

# Release a minor version for both components
python release.py --type minor --component both

# Release a major version for the integration only
python release.py --type major --component integration
```

## Release Script (`release.py`)

Automates the complete release process for:
- `evmeter-client` (PyPI package)
- `ev-meter` (HACS integration)

### Features

- ✅ **Semantic Versioning** - Automatic version bumping (major.minor.patch)
- ✅ **Changelog Updates** - Automatic changelog entry creation (client CHANGELOG.md + integration README.md)
- ✅ **Git Operations** - Commit, tag, and push automation
- ✅ **GitHub Releases** - Automatic GitHub release creation with release notes
- ✅ **PyPI Publishing** - Build and upload packages automatically
- ✅ **Dependency Updates** - Sync integration requirements with client versions
- ✅ **Dry Run Mode** - Test releases without making changes
- ✅ **Error Handling** - Comprehensive error checking and rollback

### Usage Examples

#### Component Options
- `client` - Release only evmeter-client PyPI package
- `integration` - Release only HACS integration
- `both` - Release both components (recommended)

#### Version Bump Types
- `patch` - Bug fixes (1.0.0 → 1.0.1)
- `minor` - New features (1.0.1 → 1.1.0)
- `major` - Breaking changes (1.1.0 → 2.0.0)

#### Common Workflows

**Bug Fix Release:**
```bash
# Fix critical bugs in both components
python release.py --type patch --component both
```

**Feature Release:**
```bash
# Add new features to client and update integration
python release.py --type minor --component both
```

**Breaking Change Release:**
```bash
# Major API changes or breaking modifications
python release.py --type major --component both
```

**Client-Only Update:**
```bash
# Update just the PyPI package (e.g., performance improvements)
python release.py --type minor --component client
```

**Integration-Only Update:**
```bash
# Update just the HACS integration (e.g., Home Assistant compatibility)
python release.py --type patch --component integration
```

### What the Script Does

#### For Client Releases (`evmeter-client`):
1. Bumps version in `pyproject.toml`
2. Updates `CHANGELOG.md` with new version entry
3. Commits changes with descriptive message
4. Creates git tag (`v1.2.3`)
5. Builds package using `python -m build`
6. Publishes to PyPI using `twine upload`
7. Pushes commits and tags to GitHub
8. Creates GitHub release with auto-generated release notes

#### For Integration Releases (`ev-meter`):
1. Bumps version in `manifest.json`
2. Updates `README.md` changelog section with new version entry
3. Updates client requirement to latest version (if releasing both)
4. Commits changes with descriptive message
5. Creates git tag (`v2.1.0`)
6. Pushes commits and tags to GitHub
7. Creates GitHub release with auto-generated release notes
8. HACS automatically detects the new release

#### For Both Components:
1. Releases client first
2. Updates integration with new client requirement
3. Ensures version synchronization

### Prerequisites

**For Client Releases:**
- Virtual environment at `/home/amirv/git/evmeter-client/test_env/`
- `build` and `twine` packages installed in venv
- PyPI credentials configured for `twine`

**For GitHub Releases:**
- GitHub CLI (`gh`) installed and authenticated
- Install: `brew install gh` (macOS) or `apt install gh` (Ubuntu)
- Authenticate: `gh auth login`

**For All Releases:**
- Git repositories with clean working directories
- Proper git remotes configured (for pushing)
- Write access to GitHub repositories

### Safety Features

- **Dry Run Mode**: Test releases with `--dry-run` flag
- **Version Validation**: Ensures proper semantic versioning
- **Git Status Check**: Verifies clean working directory
- **Build Validation**: Tests package building before publishing
- **Error Handling**: Stops on errors to prevent partial releases

### Example Output

```
[2025-11-08 14:30:15] INFO: Starting minor release for both components
[2025-11-08 14:30:15] INFO: Bumping client version: 1.1.1 -> 1.2.0
[2025-11-08 14:30:16] INFO: Updated client version to 1.2.0
[2025-11-08 14:30:16] INFO: Updated changelog for client
[2025-11-08 14:30:17] INFO: Created commit and tag v1.2.0 for client
[2025-11-08 14:30:25] INFO: Successfully published evmeter-client v1.2.0 to PyPI
[2025-11-08 14:30:26] INFO: Pushed changes and tags for client
[2025-11-08 14:30:26] INFO: Successfully released evmeter-client v1.2.0
[2025-11-08 14:30:26] INFO: Starting minor release for HACS integration
[2025-11-08 14:30:26] INFO: Bumping integration version: 2.0.2 -> 2.1.0
[2025-11-08 14:30:26] INFO: Updated integration version to 2.1.0
[2025-11-08 14:30:26] INFO: Updated client requirement to >=1.2.0
[2025-11-08 14:30:27] INFO: Created commit and tag v2.1.0 for integration
[2025-11-08 14:30:28] INFO: Pushed changes and tags for integration
[2025-11-08 14:30:28] INFO: Successfully released HACS integration v2.1.0
[2025-11-08 14:30:28] INFO: Successfully released both components with minor version bump

🎉 Release completed successfully!
```

### Troubleshooting

**PyPI Upload Fails:**
- Check PyPI credentials: `twine configure`
- Verify package builds: `python -m build`
- Check network connectivity

**Git Push Fails:**
- Verify remote repository access
- Check SSH keys or authentication
- Ensure working directory is clean

**Version Conflicts:**
- Use `--dry-run` to test first
- Check current versions manually
- Verify no uncommitted changes

### Time & Token Savings

This script replaces manual processes that previously required:
- ~20-30 terminal commands per release
- Multiple file edits across repositories
- Manual version number calculations
- Copy-paste of changelog entries
- Manual PyPI uploads and git pushes

**Estimated savings per release:**
- ⏰ **Time**: 15-20 minutes → 2-3 minutes
- 🤖 **Tokens**: 500-800 tokens → 50-100 tokens
- 🎯 **Accuracy**: Manual errors → Automated consistency
