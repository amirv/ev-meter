#!/usr/bin/env python3
"""
EV-Meter Release Automation Script

This script automates the process of creating new releases for both:
1. evmeter-client (PyPI package)
2. ev-meter (HACS integration)

Usage:
    python release.py --help
    python release.py --type minor --component client
    python release.py --type major --component integration
    python release.py --type patch --component both

Supports:
- Semantic versioning (major.minor.patch)
- Automatic changelog updates
- Git tagging and pushing
- PyPI publishing
- Dry-run mode for testing
"""

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple


class ReleaseManager:
    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.client_path = Path("/home/amirv/git/evmeter-client")
        self.integration_path = Path("/home/amirv/git/ev-meter")

    def log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp and level."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prefix = "[DRY RUN] " if self.dry_run else ""
        print(f"{prefix}[{timestamp}] {level}: {message}")

    def run_command(
        self, command: List[str], cwd: Optional[Path] = None
    ) -> Tuple[bool, str]:
        """Run a shell command and return success status and output."""
        if self.dry_run and any(
            cmd in command for cmd in ["git push", "twine upload", "git tag"]
        ):
            self.log(f"Would run: {' '.join(command)}", "DRY_RUN")
            return True, "Dry run - command not executed"

        try:
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, check=True
            )
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            self.log(f"Command failed: {' '.join(command)}", "ERROR")
            self.log(f"Error: {e.stderr}", "ERROR")
            return False, e.stderr

    def get_current_version(self, component: str) -> str:
        """Get the current version of a component."""
        if component == "client":
            pyproject_path = self.client_path / "pyproject.toml"
            with open(pyproject_path, "r") as f:
                content = f.read()
                match = re.search(r'version = "([^"]+)"', content)
                return match.group(1) if match else "0.0.0"
        elif component == "integration":
            manifest_path = (
                self.integration_path / "custom_components/evmeter/manifest.json"
            )
            with open(manifest_path, "r") as f:
                data = json.load(f)
                return str(data["version"])
        else:
            raise ValueError(f"Unknown component: {component}")

    def bump_version(self, current_version: str, bump_type: str) -> str:
        """Bump version according to semantic versioning."""
        parts = list(map(int, current_version.split(".")))

        if bump_type == "major":
            parts[0] += 1
            parts[1] = 0
            parts[2] = 0
        elif bump_type == "minor":
            parts[1] += 1
            parts[2] = 0
        elif bump_type == "patch":
            parts[2] += 1
        else:
            raise ValueError(f"Invalid bump type: {bump_type}")

        return ".".join(map(str, parts))

    def update_client_version(self, new_version: str) -> bool:
        """Update the evmeter-client version in pyproject.toml."""
        pyproject_path = self.client_path / "pyproject.toml"

        with open(pyproject_path, "r") as f:
            content = f.read()

        # Update version
        new_content = re.sub(
            r'version = "[^"]+"', f'version = "{new_version}"', content
        )

        if not self.dry_run:
            with open(pyproject_path, "w") as f:
                f.write(new_content)

        self.log(f"Updated client version to {new_version}")
        return True

    def update_integration_version(
        self, new_version: str, client_version: Optional[str] = None
    ) -> bool:
        """Update the HACS integration version and client requirement."""
        manifest_path = (
            self.integration_path / "custom_components/evmeter/manifest.json"
        )

        with open(manifest_path, "r") as f:
            data = json.load(f)

        # Update integration version
        data["version"] = new_version

        # Update client requirement if provided
        if client_version:
            data["requirements"] = [f"evmeter-client>={client_version}"]

        if not self.dry_run:
            with open(manifest_path, "w") as f:
                json.dump(data, f, indent=2)
                f.write("\n")  # Add trailing newline

        self.log(f"Updated integration version to {new_version}")
        if client_version:
            self.log(f"Updated client requirement to >={client_version}")
        return True

    def update_changelog(self, component: str, version: str, bump_type: str) -> bool:
        """Update the changelog with new version entry."""
        if component == "client":
            changelog_path = self.client_path / "CHANGELOG.md"
        else:
            # Integration doesn't have a separate changelog currently
            return True

        if not changelog_path.exists():
            self.log(f"Changelog not found: {changelog_path}", "WARNING")
            return True

        with open(changelog_path, "r") as f:
            content = f.read()

        # Create new changelog entry
        date_str = datetime.now().strftime("%Y-%m-%d")
        new_entry = f"""## [{version}] - {date_str}

### {bump_type.title()}
- Version {bump_type} release
- TODO: Add specific changes for this release

"""

        # Insert after the header
        lines = content.split("\n")
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith("## ["):
                insert_pos = i
                break

        if insert_pos > 0:
            lines.insert(insert_pos, new_entry.rstrip())
            new_content = "\n".join(lines)
        else:
            new_content = content.replace(
                "# Changelog\n\n", f"# Changelog\n\n{new_entry}"
            )

        if not self.dry_run:
            with open(changelog_path, "w") as f:
                f.write(new_content)

        self.log(f"Updated changelog for {component}")
        return True

    def git_commit_and_tag(self, component: str, version: str, bump_type: str) -> bool:
        """Commit changes and create git tag."""
        if component == "client":
            repo_path = self.client_path
            repo_name = "evmeter-client"
        else:
            repo_path = self.integration_path
            repo_name = "HACS integration"

        # In dry-run mode, just log what would happen
        if self.dry_run:
            commit_msg = f"Release v{version}: {bump_type} version bump for {repo_name}"
            tag_msg = f"Release v{version}: {bump_type} version bump"
            self.log(f"Would commit: {commit_msg}", "DRY_RUN")
            self.log(f"Would create tag: v{version} with message: {tag_msg}", "DRY_RUN")
            return True

        # Stage changes
        success, _ = self.run_command(["git", "add", "-A"], cwd=repo_path)
        if not success:
            return False

        # Check if there are changes to commit
        success, output = self.run_command(
            ["git", "status", "--porcelain"], cwd=repo_path
        )
        if not success:
            return False

        if not output.strip():
            self.log(f"No changes to commit for {component}", "WARNING")
            return True

        # Commit
        commit_msg = f"Release v{version}: {bump_type} version bump for {repo_name}"
        success, _ = self.run_command(
            ["git", "commit", "-m", commit_msg], cwd=repo_path
        )
        if not success:
            return False

        # Tag
        tag_msg = f"Release v{version}: {bump_type} version bump"
        success, _ = self.run_command(
            ["git", "tag", "-a", f"v{version}", "-m", tag_msg], cwd=repo_path
        )
        if not success:
            return False

        self.log(f"Created commit and tag v{version} for {component}")
        return True

    def push_changes(self, component: str, version: str) -> bool:
        """Push commits and tags to remote repository."""
        if component == "client":
            repo_path = self.client_path
        else:
            repo_path = self.integration_path

        # Check if remote exists
        success, output = self.run_command(["git", "remote", "-v"], cwd=repo_path)
        if not success or not output.strip():
            self.log(
                f"No git remote configured for {component}, skipping push", "WARNING"
            )
            return True

        # In dry-run mode, the tag doesn't exist yet, so skip the push
        if self.dry_run:
            self.log(
                f"Would push changes and tag v{version} for {component}", "DRY_RUN"
            )
            return True

        # Push main branch
        success, _ = self.run_command(["git", "push", "origin", "main"], cwd=repo_path)
        if not success:
            return False

        # Push tags
        success, _ = self.run_command(
            ["git", "push", "origin", f"v{version}"], cwd=repo_path
        )
        if not success:
            return False

        self.log(f"Pushed changes and tags for {component}")
        return True

    def build_and_publish_client(self, version: str) -> bool:
        """Build and publish the client package to PyPI."""
        if self.dry_run:
            self.log(
                f"Would build and publish evmeter-client v{version} to PyPI", "DRY_RUN"
            )
            return True

        # Clean previous builds
        success, _ = self.run_command(
            ["rm", "-rf", "dist/", "build/", "*.egg-info/"], cwd=self.client_path
        )

        # Activate virtual environment and build
        venv_python = self.client_path / "test_env/bin/python"
        if not venv_python.exists():
            self.log("Virtual environment not found, using system python", "WARNING")
            python_cmd = "python"
        else:
            python_cmd = str(venv_python)

        # Build package
        success, output = self.run_command(
            [python_cmd, "-m", "build"], cwd=self.client_path
        )
        if not success:
            self.log("Failed to build package", "ERROR")
            return False

        # Upload to PyPI
        success, output = self.run_command(
            [python_cmd, "-m", "twine", "upload", "dist/*"], cwd=self.client_path
        )
        if not success:
            self.log("Failed to upload to PyPI", "ERROR")
            return False

        self.log(f"Successfully published evmeter-client v{version} to PyPI")
        return True

    def release_client(self, bump_type: str) -> bool:
        """Release new version of evmeter-client."""
        self.log(f"Starting {bump_type} release for evmeter-client")

        current_version = self.get_current_version("client")
        new_version = self.bump_version(current_version, bump_type)

        self.log(f"Bumping client version: {current_version} -> {new_version}")

        # Update version
        if not self.update_client_version(new_version):
            return False

        # Update changelog
        if not self.update_changelog("client", new_version, bump_type):
            return False

        # Commit and tag
        if not self.git_commit_and_tag("client", new_version, bump_type):
            return False

        # Build and publish
        if not self.build_and_publish_client(new_version):
            return False

        # Push to git
        if not self.push_changes("client", new_version):
            return False

        self.log(f"Successfully released evmeter-client v{new_version}")
        return True

    def release_integration(
        self, bump_type: str, client_version: Optional[str] = None
    ) -> bool:
        """Release new version of HACS integration."""
        self.log(f"Starting {bump_type} release for HACS integration")

        current_version = self.get_current_version("integration")
        new_version = self.bump_version(current_version, bump_type)

        self.log(f"Bumping integration version: {current_version} -> {new_version}")

        # Update version and client requirement
        if not self.update_integration_version(new_version, client_version):
            return False

        # Commit and tag
        if not self.git_commit_and_tag("integration", new_version, bump_type):
            return False

        # Push to git
        if not self.push_changes("integration", new_version):
            return False

        self.log(f"Successfully released HACS integration v{new_version}")
        return True

    def release_both(self, bump_type: str) -> bool:
        """Release both client and integration."""
        self.log(f"Starting {bump_type} release for both components")

        # Calculate new client version first
        current_client_version = self.get_current_version("client")
        new_client_version = self.bump_version(current_client_version, bump_type)

        # Release client first
        if not self.release_client(bump_type):
            return False

        # Release integration with updated client requirement
        if not self.release_integration(bump_type, new_client_version):
            return False

        self.log(f"Successfully released both components with {bump_type} version bump")
        return True


def main():
    parser = argparse.ArgumentParser(description="EV-Meter Release Automation")
    parser.add_argument(
        "--type",
        choices=["major", "minor", "patch"],
        required=True,
        help="Type of version bump",
    )
    parser.add_argument(
        "--component",
        choices=["client", "integration", "both"],
        required=True,
        help="Component to release",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()

    release_manager = ReleaseManager(dry_run=args.dry_run)

    try:
        if args.component == "client":
            success = release_manager.release_client(args.type)
        elif args.component == "integration":
            success = release_manager.release_integration(args.type)
        elif args.component == "both":
            success = release_manager.release_both(args.type)
        else:
            print(f"Unknown component: {args.component}")
            return 1

        if success:
            print("\n🎉 Release completed successfully!")
            return 0
        else:
            print("\n❌ Release failed!")
            return 1

    except KeyboardInterrupt:
        print("\n⚠️  Release cancelled by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
