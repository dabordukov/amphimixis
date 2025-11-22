# pylint: skip-file
import os
import subprocess

import pytest

import amphimixis


class TestShell:
    local_machine = amphimixis.general.MachineInfo(
        amphimixis.general.Arch.X86, None, None
    )

    @pytest.mark.parametrize("machine", [local_machine])
    def test_copy_to_remote(
        self,
        machine: amphimixis.general.MachineInfo,
        tmp_path_factory,
    ):
        original_file = tmp_path_factory.mktemp("data0") / "original.txt"
        os.system(f"dd if=/dev/random of={original_file} bs=1 count=1234")

        shell = amphimixis.Shell(machine).connect()
        error, stdout, stderr = shell.run("echo $(mktemp -d)")
        assert error == 0
        remote_tmpdir = stdout[0][0].strip()
        remote_tmpfile = os.path.join(remote_tmpdir, "copy_file")

        assert shell.copy_to_remote(original_file, destination=remote_tmpfile)

        error, stdout, stderr = shell.run(f"md5sum {remote_tmpfile}")
        assert error == 0
        md5digest_remote = stdout[0][0].split()[0]

        with subprocess.Popen(
            ["md5sum", original_file],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as cmd:
            assert cmd.wait() == 0
            assert cmd.stdout is not None
            out = cmd.stdout.readline()
            md5digest_local = out.decode("utf-8").split()[0]

        assert md5digest_local == md5digest_remote

    @pytest.mark.parametrize("machine", [local_machine])
    def test_copy_to_host(
        self,
        machine: amphimixis.general.MachineInfo,
        tmp_path_factory,
    ):
        shell = amphimixis.Shell(machine).connect()

        error, stdout, stderr = shell.run("echo $(mktemp -d)")
        assert error == 0
        remote_tmpdir = stdout[0][0].strip()
        remote_tmpfile = os.path.join(remote_tmpdir, "original.txt")
        shell.run(f"dd if=/dev/random of={remote_tmpfile} bs=1 count=1234")

        local_tmpfile = tmp_path_factory.mktemp("data1") / "original.txt"
        assert shell.copy_to_host(remote_tmpfile, destination=local_tmpfile)

        error, stdout, stderr = shell.run(f"md5sum {remote_tmpfile}")
        assert error == 0
        md5digest_remote = stdout[0][0].split()[0]

        with subprocess.Popen(
            ["md5sum", local_tmpfile],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as cmd:
            assert cmd.wait() == 0
            assert cmd.stdout is not None
            out = cmd.stdout.readline()
            md5digest_local = out.decode("utf-8").split()[0]

        assert md5digest_local == md5digest_remote
