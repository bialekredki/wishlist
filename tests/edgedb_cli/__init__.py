import subprocess
import time
from datetime import datetime, timedelta


def retryable_command(
    command: str | list[str],
    success_pattern: bytes,
    *,
    timeout: int = 5_000,
    retries_limit: int = 256,
    sleep_time: float = 0.15,
):
    if isinstance(command, str):
        command = command.split(" ")
    start = datetime.now()
    attempts = 0
    is_ok = True
    while (
        timedelta(milliseconds=timeout) >= datetime.now() - start
        and attempts < retries_limit
    ):
        attempts += 1
        proc = subprocess.Popen(command, stderr=subprocess.PIPE)
        stderr = proc.communicate()[1]
        is_ok = success_pattern in stderr
        if is_ok:
            break
        time.sleep(sleep_time)
    assert is_ok, f"Command {command} timed out. Last fail was {stderr}."
