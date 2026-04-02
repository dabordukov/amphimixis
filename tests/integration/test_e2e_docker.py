"""Tests for the full launch of the application on a specific project"""

import os
import subprocess
import time

import docker
import pytest


@pytest.mark.integration
def test_e2e_remote_machine_between_containers(
    clone_repo, create_working_space, _docker_compose
):
    """End-to-end test for remote build between Docker containers.
    Validates that the pipeline can successfully run across separate
    containers (build-client and build-server).
    Waits for containers to be ready, extracts server IP, updates configuration,
    copies repository to client container, and executes the process.
    """

    docker_client = docker.from_env()

    client_container = docker_client.containers.get("build-client")
    server_container = docker_client.containers.get("build-server")

    check_env_is_ready_cmd = ["bash", "-c", "ls secret_ishtar"]

    while (
        client_container.exec_run(check_env_is_ready_cmd)[0]
        or server_container.exec_run(check_env_is_ready_cmd)[0]
    ):
        time.sleep(5)

    get_ip_cmd = [
        "docker",
        "inspect",
        "-f",
        "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
        "build-server",
    ]
    ip_build_server = subprocess.run(
        get_ip_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True
    )

    ip_address = ip_build_server.stdout.decode().strip()

    add_ip_cmd = [
        "bash",
        "-c",
        f"sed 's/address:/address: {ip_address}/' "
        f"/workspace/input_remote.yml > /workspace/input.yml.tmp",
    ]
    exit_code = client_container.exec_run(add_ip_cmd)[0]
    assert exit_code == 0

    add_jobs_cmd = [
        "bash",
        "-c",
        f"sed 's/jobs:/jobs: {os.cpu_count() or 8}/' "
        f"/workspace/input.yml.tmp > /workspace/input.yml",
    ]
    exit_code = client_container.exec_run(add_jobs_cmd)[0]
    assert exit_code == 0

    repo_path = clone_repo("https://github.com/leethomason/tinyxml2")
    copy_cmd = ["docker", "cp", repo_path, "build-client:/workspace/tinyxml2"]
    subprocess.run(copy_cmd, check=True)

    build_cmd = [
        "bash",
        "-c",
        "/root/.local/bin/uv --project /app run coverage run -a /app/amixis.py /workspace/tinyxml2 --events cycles",
    ]
    exit_code = client_container.exec_run(build_cmd, workdir="/workspace")[0]

    if os.getenv("CI"):
        artifacts_dir = create_working_space()
        copy_artifacts_cmd = ["docker", "cp", "build-client:/workspace", artifacts_dir]
        subprocess.run(copy_artifacts_cmd, check=False)

    assert exit_code == 0
