import random
import socket
import string
import subprocess
import time
from contextlib import closing, contextmanager
from typing import List, Optional


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def wait_for_port(host, port, timeout=60):
    start = time.time()
    while True:
        try:
            if time.time() - start > timeout:
                raise Exception(f"Something is wrong. Timeout waiting for port {port}")
            with socket.create_connection((host, port), timeout=5):
                return
        except socket.error:
            pass
        except socket.timeout:
            raise


def random_string(length):
    return "".join(random.choice(string.ascii_lowercase) for i in range(length))


@contextmanager
def docker_run(
    image,
    name=None,
    detach=False,
    interactive=False,
    publish: Optional[List[dict]] = None,
    command: Optional[List[str]] = None,
    env: Optional[dict] = None,
):
    if name is None:
        name = random_string(10)

    cmd = ["docker", "run", "--name", name]
    if publish is not None:
        for port_binding in publish:
            host_port = port_binding["host"]
            container_port = port_binding["container"]
            cmd += ["--publish", f"{host_port}:{container_port}"]
    if env is not None:
        for key, value in env.items():
            cmd += ["-e", f"{key}={value}"]
    if detach:
        cmd += ["--detach"]
    if interactive:
        cmd += ["-i"]
    cmd += [image]
    if command:
        cmd += command
    try:
        subprocess.Popen(cmd)
        yield
    finally:
        subprocess.Popen(["docker", "rm", "--force", name]).wait()


def get_local_ip():
    return socket.gethostbyname(socket.gethostname())


def get_bridge_ip():
    """Return the IP address of the docker bridge network"""
    cmd = [
        "docker",
        "network",
        "inspect",
        "bridge",
        "--format='{{ json (index .IPAM.Config 0).Gateway }}'",
    ]
    out, _ = subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()

    return out.decode().strip().replace('"', "").replace("'", "")
