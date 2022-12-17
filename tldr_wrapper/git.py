import subprocess
import logging

logger = logging.getLogger(__name__)

def _exec_git(cmds) -> str:
    logger.info("Run: %s", " ".join(cmds))
    p = subprocess.run(cmds, encoding="utf-8", capture_output=True)
    if p.stderr == "":
        errs = None
    else:
        errs = p.stderr
    if p.returncode != 0:
        format_cli_line = " ".join(cmds)
        raise RuntimeError(
            "git ended with state %s %s: %s"
            % (p.returncode, format_cli_line, errs)
        )
    output = str(p.stdout)
    return output


def git_clone(repo: str, local_dir: str) -> str:
    args = ["git", "clone", repo, local_dir]
    return _exec_git(args)


def git_pull(local_dir: str) -> str:
    args = ["git", "-C", local_dir, "pull"]
    return _exec_git(args)
