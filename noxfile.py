import nox


def patch_binaries_if_needed(session: nox.Session, venv_dir: str) -> None:
    """If we are on Nix, auto-patch any binaries under `venv_dir`.

    Detect if we are running under Nix, and auto-patch any pre-built binaries
    that were just installed into the Nox virtualenv.
    """
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
    session.run(*argv, silent=True, external=True)


def install(session: nox.Session, *deps: str) -> None:
    """Install session dependencies, constrained by requirements.txt.

    If running on NixOS, ensure that any installed dependencies that contain
    binaries are appropriately patched with patchElf.
    """
    if isinstance(session.virtualenv, nox.virtualenv.PassthroughEnv):
        session.warn("Running outside a Nox virtualenv! Installation skipped!")
        return

    session.install(*deps)
    if not session.virtualenv._reused:  # noqa: SLF001
        patch_binaries_if_needed(session, session.virtualenv.location)


@nox.session
def check(session: nox.Session) -> None:
    install(session, f".[{session.name}]")  # TODO: How to avoid installing self
    session.run("ruff", "check", ".")


@nox.session
def format(session: nox.Session) -> None:
    install(session, f".[{session.name}]")
    session.run("ruff", "format", ".")


@nox.session
def deps(session: nox.Session) -> None:
    install(session, f".[{session.name}]")
    session.run("fawltydeps", "--detailed")


@nox.session
def typing(session: nox.Session) -> None:
    install(session, f".[{session.name}]")
    session.run("mypy")


@nox.session
def tests(session: nox.Session) -> None:
    install(session, f".[{session.name}]")
    session.run("./test.py")
