"""The most common steps in the release of a Python package."""

import requests

from bag.check_rst import check_rst_file
from bag.console import bool_input
from bag.pathlib_complement import Path

from . import ReleaseStep, StopRelease, CommandStep
from .regex import version_in_python_source_file

__all__ = (
    "Shell",
    "CheckRstFiles",
    "InteractivelyApproveDistribution",
    "InteractivelyApproveWheel",
    "PypiUploadWheel",
    "InteractivelyEnsureChangesDocumented",
    "CheckTravis",
    "SetVersionNumberInteractively",
    "PypiUpload",
    "SetFutureVersion",
    "ErrorStep",
    "Warn",
)


class Shell(ReleaseStep):
    """Run some shell command."""

    ERROR_CODE = 2

    def __init__(self, command, stop_on_failure=True):  # noqa
        self.COMMAND = command
        self.stop_on_failure = stop_on_failure
        self.no_rollback = "Unable to roll back the step {0}".format(self)

    def __call__(self):  # noqa
        self._execute_or_complain(self.COMMAND)  # sets self.success

    def __str__(self):
        return "[" + self.COMMAND + "]"


class CheckRstFiles(ReleaseStep):
    """Helps keep documentation correct by verifying .rst files.

    If files are not provided to the constructor, recursively finds
    *.rst files in the current directory and subdirectories.
    """

    ERROR_CODE = 4

    def __init__(self, *files):  # noqa
        self.paths = files

    def __call__(self):  # noqa
        paths = self.paths or Path(".").walk(
            filter=lambda p: p.suffix == ".rst"
        )
        for path in paths:
            self.log.info(f"Checking {path}")
            warnings = check_rst_file(str(path))
            if warnings:
                raise StopRelease(
                    "There are errors in {0}:\n{1}".format(
                        path, "\n".join([str(w) for w in warnings])
                    )
                )


class InteractivelyApproveDistribution(ReleaseStep):
    """Generate a source distribution and let the user verify it."""

    ERROR_CODE = 5

    def __call__(self):  # noqa
        self._execute_or_complain("python setup.py sdist")
        # TODO: Optionally xdg-open the archive for convenience
        # Create the sdist with "-d <output_dir>"  on a temp dir.
        # Delete it at the end.
        print("The source distribution has been generated. Since it is just")
        print("a zip file, you should now open it (in the 'dist' directory)")
        print("and check that all files are in there.")
        if not bool_input("Do you approve the archive contents?"):
            raise StopRelease(
                "Source distribution content not approved.\n"
                "If the distribution is missing some files,\n"
                "try correcting your MANIFEST.in file."
            )


class InteractivelyApproveWheel(ReleaseStep):
    """Generate wheel and let user verify it before proceeding."""

    COMMAND = "python setup.py bdist_wheel"
    ERROR_CODE = 10

    def __call__(self):  # noqa
        self._execute_or_complain(self.COMMAND)  # sets self.success
        # TODO: Optionally xdg-open the wheel for convenience
        print(
            "The wheel has been generated. Since it is just a\n"
            "zip file, you should now open it (from the 'dist' directory)"
            "\nand check that all files are in there."
        )
        if not bool_input("Do you approve the wheel contents?"):
            raise StopRelease("Wheel content not approved.")


class InteractivelyEnsureChangesDocumented(ReleaseStep):
    """Step that just bugs the user to verify the CHANGES file."""

    ERROR_CODE = 3

    def __call__(self):  # noqa
        if bool_input("Did you remember to update the CHANGES file?"):
            self.log.debug("User says CHANGES file is up to date.")
        else:
            raise StopRelease("One more joeshlabotniked release is avoided.")


class CheckTravis(ReleaseStep):
    """Check the status, on travis-ci.org, of the latest build."""

    ERROR_CODE = 91
    URL = (
        "https://api.travis-ci.org/repos/"
        "{github_user}/{github_repository}/builds"
    )

    def __call__(self):  # noqa
        branch = self.config.get("branch", "master")
        resp = requests.get(self.URL.format(**self.config))
        builds = resp.json()
        onbranch = filter(lambda x: x["branch"] == branch, builds)
        finished = list(filter(lambda x: x["state"] == "finished", onbranch))
        if len(finished) == 0:
            raise StopRelease(
                'Travis has not built branch "{0}" yet.'.format(branch)
            )
        latest = finished[0]
        if latest["result"] == 0:
            self.log.info(
                'No problem in latest Travis build: "{0}"'.format(
                    latest.get("message")
                )
            )
            self._succeed()
        else:
            raise StopRelease(
                'Last Travis build on branch "{0}" failed.'.format(branch)
            )


class SetVersionNumberInteractively(ReleaseStep):
    """Ask user for the new version number and write it on the source code."""

    ERROR_CODE = 6

    def __call__(self):  # noqa
        releaser = self.releaser
        path = releaser.config["version_file"]
        keyword = releaser.config.get("version_keyword", "version")
        releaser.old_version = version_in_python_source_file(
            path, keyword=keyword
        )
        print("Current version: {0}".format(releaser.old_version))
        releaser.the_version = input("What is the new version number? ")
        # Write the new version onto the source code
        version_in_python_source_file(
            path, keyword=keyword, replace=releaser.the_version
        )
        self._succeed()


class PypiUpload(CommandStep):
    """Use *twine* to upload a source distribution to pypi."""

    ERROR_CODE = 8
    no_rollback = "Cannot roll back the sdist upload to http://pypi.python.org"

    def __call__(self):  # noqa
        name = self.config["github_repository"]
        version = self.releaser.the_version
        self._execute_expect_zero(f"twine upload dist/{name}-{version}.tar.gz")

    def _validate_command_output(self, command_output):
        return "Server response (200): OK" in command_output


class PypiUploadWheel(CommandStep):
    """Use *twine* to upload a wheel to pypi."""

    ERROR_CODE = 11
    no_rollback = "Cannot roll back the wheel upload to http://pypi.python.org"

    def __call__(self):  # noqa
        name = self.config["github_repository"]
        version = self.releaser.the_version
        self._execute_expect_zero(
            f"twine upload dist/{name}-{version}-py3-none-any.whl"
        )

    def _validate_command_output(self, command_output):
        return "Server response (200): OK" in command_output


class SetFutureVersion(ReleaseStep):
    """Set the development version number in source code after release."""

    ERROR_CODE = 9

    def __call__(self):  # noqa
        releaser = self.releaser
        path = releaser.config["version_file"]
        keyword = releaser.config.get("version_keyword", "version")
        # If the SetVersionNumberInteractively step is disabled for debugging,
        # we can still execute the current step, by populating the_version:
        if releaser.the_version is None:
            releaser._the_version = version_in_python_source_file(
                path, keyword=keyword
            )
        self.log.info(
            "Ready for the next development cycle! Setting version "
            + releaser.future_version
        )
        version_in_python_source_file(
            path, keyword=keyword, replace=releaser.future_version
        )
        self._succeed()


class ErrorStep(CommandStep):
    """Raise an exception to force a rollback. Good for testing."""

    COMMAND = "thisCommandDontExist"
    ERROR_CODE = 255


class Warn(ReleaseStep):
    """Just print a warning on the screen and on the log file."""

    def __init__(self, msg: str):  # noqa
        self.msg = msg

    def __call__(self):  # noqa
        self.log.warn(self.msg)
        self.success = True
