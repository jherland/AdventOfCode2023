import nox


def patch_binaries_if_needed(session: nox.Session, venv_dir: str) -> None:
    import os  # noqa: I001
    from pathlib import Path
    import shlex

    build_inputs = os.environ.get("buildInputs", "")  # noqa: SIM112
    if "auto-patchelf-hook" not in build_inputs:
        return

    auto_patchelf_hook_dir = next(
        dir for dir in shlex.split(build_inputs) if "auto-patchelf-hook" in dir
    )
    with open(f"{auto_patchelf_hook_dir}/nix-support/setup-hook") as f:
        for line in f:
            if "auto-patchelf.py" in line:
                argv = shlex.split(line.rstrip("\n\\"))
                break
    lib_dirs = [
        str(Path(path).with_name("lib"))
        for path in os.environ["PATH"].split(":")
        if path.startswith("/nix/store/")
    ]
    argv += ["--paths", venv_dir, "--libs", *lib_dirs]
    # auto-patchelf.py fails unless these are given (although empty)
    argv += ["--runtime-dependencies", "--append-rpaths", "--extra-args"]
    print(f"Running: {argv}")
    session.run(*argv, silent=True, external=True)


def install(
    session: nox.Session, *deps: str, include_self: bool = False
) -> None:
    """Install session dependencies, constrained by requirements.txt.

    If running on NixOS, ensure that any installed dependencies that contain
    binaries are appropriately patched with patchElf.
    """
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn("Running outside a Nox virtualenv! Installation skipped!")
        return

    session.install(*deps, "--constraint", "requirements.txt")
    if include_self:
        session.install("-e", ".")
    if not session.virtualenv._reused:  # noqa: SLF001
        patch_binaries_if_needed(session, session.virtualenv.location)


@nox.session
def check(session: nox.Session) -> None:
    install(session, "ruff")
    session.run("ruff", "check", ".")


@nox.session
def format(session: nox.Session) -> None:
    install(session, "ruff")
    session.run("ruff", "format", ".")


@nox.session
def deps(session: nox.Session) -> None:
    install(session, "fawltydeps")
    session.run("fawltydeps", "--detailed")


@nox.session
def typing(session: nox.Session) -> None:
    install(session, "mypy", "nox")
    session.run("mypy")
