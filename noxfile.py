import nox


@nox.session
def check(session: nox.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("ruff", "check", ".")


@nox.session
def format(session: nox.Session) -> None:  # noqa: A001
    session.install("-r", "requirements.txt")
    session.run("ruff", "format", ".")


@nox.session
def deps(session: nox.Session) -> None:
    session.install("-r", "requirements.txt")
    session.run("fawltydeps", "--detailed")
