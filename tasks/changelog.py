# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "gitpython>=3.1.46",
#   "pygithub>=2.8.1",
#   "pyyaml>=6.0.2",
# ]
# ///
"""Generate the changelog on release."""

from __future__ import annotations

import os
import re
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import TYPE_CHECKING

import yaml
from git import Repo
from github import Github
from github.Auth import Token

if TYPE_CHECKING:
    from collections.abc import Iterator

    from github.Repository import Repository as GitHubRepository

ROOT = Path(__file__).parents[1]
REPO_SLUG = "tox-dev/platformdirs"


class Options(Namespace):
    bump: str
    pr: int | None
    base: str


def run() -> None:
    options = parse_cli()
    git_repo = Repo(ROOT)
    github = Github(auth=Token(os.environ["GITHUB_TOKEN"]))
    gh_repo = github.get_repo(REPO_SLUG)
    excluded_authors = _load_excluded_authors()

    last_version = latest_tag_version(git_repo)
    version = compute_next_version(last_version, options.bump)

    logs = []
    for title, pr_number, by in entries(gh_repo, git_repo, options.pr, options.base, excluded_authors):
        suffix = f" :pr:`{pr_number}`" if pr_number else ""
        by_suffix = f" - by :user:`{by}`" if by != "gaborbernat" else ""
        logs.append(f"- {title}{suffix}{by_suffix}")

    changelog_text = "\n".join(logs) if logs else "- No notable changes"

    if output := os.environ.get("GITHUB_OUTPUT"):
        with Path(output).open("at+", encoding="utf-8") as file_handler:
            file_handler.write(f"version={version}\n")
            file_handler.write(f"changelog<<EOF\n{changelog_text}\nEOF\n")


def _load_excluded_authors() -> set[str]:
    release_config = ROOT / ".github" / "release.yml"
    if release_config.exists():
        with release_config.open(encoding="utf-8") as file_handler:
            config = yaml.safe_load(file_handler)
        return set(config.get("changelog", {}).get("exclude", {}).get("authors", []))
    return set()


def parse_cli() -> Options:
    parser = ArgumentParser()
    parser.add_argument("bump", choices=["patch", "minor", "major"])
    parser.add_argument("pr", type=lambda value: int(value) if value else None, nargs="?", default=None)
    parser.add_argument("base", type=str, nargs="?", default="")
    options = Options()
    parser.parse_args(namespace=options)
    return options


def latest_tag_version(git_repo: Repo) -> str:
    tags = sorted(
        (tag for tag in git_repo.tags if re.match(r"^\d+\.\d+\.\d+$", tag.name)),
        key=lambda tag: tag.commit.committed_datetime,
    )
    if not tags:
        return "0.0.0"
    return tags[-1].name


def compute_next_version(current: str, bump: str) -> str:
    major, minor, patch = (int(part) for part in current.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def entries(
    gh_repo: GitHubRepository, git_repo: Repo, pr_number: int | None, base: str, excluded_authors: set[str]
) -> Iterator[tuple[str, str, str]]:
    if pr_number:
        pull = gh_repo.get_pull(pr_number)
        yield pull.title, str(pr_number), pull.user.login

    tags = {tag.commit.hexsha for tag in git_repo.tags if re.match(r"^\d+\.\d+\.\d+$", tag.name)}
    pr_re = re.compile(r"(?P<title>.*)[(]#(?P<pr>\d+)[)]")
    release_re = re.compile(r"^Release \d+\.\d+\.\d+")
    found_base = not base
    for change in git_repo.iter_commits():
        if change.hexsha in tags:
            break
        commit_title = str(change.message).split("\n")[0].strip()
        if release_re.match(commit_title):
            break
        found_base = found_base or change.hexsha == base
        if not found_base or change.author.name in excluded_authors:
            continue
        by = gh_repo.get_commit(change.hexsha).author.login
        if match := pr_re.match(commit_title):
            group = match.groupdict()
            yield group["title"].strip(), group["pr"], by
        else:
            yield commit_title, "", by


if __name__ == "__main__":
    run()
