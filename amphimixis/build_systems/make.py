"Make IBuildSystem implementation"

from amphimixis.general import Build, IBuildSystem, Printer, Project
from amphimixis.shell import Shell


class Make(IBuildSystem):
    """The Make implementation of IBuildSystem"""

    @staticmethod
    def get_build_system_prompt(project: Project, build: Build) -> str:
        """Generate build system prompt with all specified flags"""

        raise NotImplementedError

    # pylint: disable=unused-argument
    @staticmethod
    def get_runner_prompt(project: Project, build: Build, printer: Printer) -> str:
        """Generate runner prompt"""
        shell = Shell(build.build_machine, printer, build.build_id).connect()
        err, stdout, _ = shell.run("nproc")
        nproc = int(stdout[0][0])

        prompt = "make"
        if err == 0:
            if nproc > 1:
                nproc -= 1  # to prevent OM
            prompt += " -j" + str(nproc)

        return prompt
