import asyncio
import logging
import os
import socket
import sys
from dataclasses import dataclass, field
from typing import Optional, Dict, Any

import psutil
import requests


def find_available_port(start_port: int = 5000, max_tries: int = 50) -> int:
    port = start_port
    for _ in range(max_tries):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1
    
    # Raise exception instead of returning potentially occupied port
    raise RuntimeError(f"No available ports found in range {start_port}-{start_port + max_tries - 1}")


@dataclass
class FlaskManager:
    host: str = "127.0.0.1"
    base_port: int = 5001
    log_level: str = "INFO"
    data_dir: str = os.path.expanduser("~/promptbin-data")
    health_check_interval: int = 30
    shutdown_timeout: int = 10
    restart_threshold: int = 3
    debug_mode: bool = False

    process: Optional[asyncio.subprocess.Process] = field(default=None, init=False)
    port: Optional[int] = field(default=None, init=False)
    _logger: logging.Logger = field(default_factory=lambda: logging.getLogger(__name__), init=False)
    _restart_count: int = field(default=0, init=False)
    _monitor_task: Optional[asyncio.Task] = field(default=None, init=False)

    async def start_flask(self) -> None:
        if self.process and self.process.returncode is None:
            self._logger.warning("Flask process already running")
            return

        self.port = find_available_port(self.base_port)
        # Get the directory where this script is located
        script_dir = os.path.dirname(os.path.abspath(__file__))
        app_path = os.path.join(script_dir, "app.py")
        
        cmd = [
            sys.executable,
            app_path,
            "--mode",
            "mcp-managed",
            "--host",
            self.host,
            "--port",
            str(self.port),
            "--log-level",
            self.log_level,
            "--data-dir",
            self.data_dir,
        ]

        self._logger.info(f"Starting Flask on {self.host}:{self.port} ...")
        
        if self.debug_mode:
            # In debug mode, capture output to log files
            log_dir = os.path.join(self.data_dir, 'logs')
            os.makedirs(log_dir, exist_ok=True)
            stdout_file = open(os.path.join(log_dir, 'flask_stdout.log'), 'w')
            stderr_file = open(os.path.join(log_dir, 'flask_stderr.log'), 'w')
            
            self.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=stdout_file,
                stderr=stderr_file
            )
        else:
            self.process = await asyncio.create_subprocess_exec(
                *cmd, 
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )

        # Give Flask a moment to start up before health checking
        await asyncio.sleep(2)
        
        # Wait for health
        ready = await self._wait_until_healthy(timeout=30)
        if not ready:
            self._logger.error("Flask failed to become healthy in time")
            raise RuntimeError("Flask did not become healthy")

        if not self._monitor_task or self._monitor_task.done():
            self._monitor_task = asyncio.create_task(self.monitor_loop())

    async def stop_flask(self) -> None:
        if not self.process:
            return
        try:
            self._logger.info("Stopping Flask process ...")
            self.process.terminate()
            try:
                await asyncio.wait_for(self.process.wait(), timeout=self.shutdown_timeout)
            except asyncio.TimeoutError:
                self._logger.warning("Flask did not exit on SIGTERM; killing...")
                self.process.kill()
                try:
                    await asyncio.wait_for(self.process.wait(), timeout=5)
                except asyncio.TimeoutError:
                    self._logger.error("Flask failed to terminate after SIGKILL")
        finally:
            self._cleanup_process_refs()

    async def restart_flask(self) -> None:
        await self.stop_flask()
        backoff = min(2 ** self._restart_count, 30)
        if self._restart_count:
            await asyncio.sleep(backoff)
        await self.start_flask()
        self._restart_count += 1

    async def monitor_loop(self) -> None:
        while self.process and self.process.returncode is None:
            healthy = await self.is_healthy()
            if not healthy:
                self._logger.warning("Health check failed; restarting Flask")
                try:
                    await self.restart_flask()
                except Exception as e:
                    self._logger.error(f"Failed to restart Flask: {e}")
            await asyncio.sleep(self.health_check_interval)

    async def is_healthy(self) -> bool:
        if not self.process:
            return False
        if self.process.returncode is not None:
            return False
        # Process exists
        try:
            proc = psutil.Process(self.process.pid)
            if not proc.is_running():
                return False
        except Exception:
            return False

        # HTTP health
        try:
            url = f"http://{self.host}:{self.port}/health"
            resp = await asyncio.to_thread(requests.get, url, timeout=3)
            json_data = resp.json() if resp.ok else {}
            is_healthy = resp.ok and json_data.get("status") == "healthy"
            if not is_healthy:
                self._logger.warning(f"Health check failed: status={resp.status_code}, data={json_data}")
            return is_healthy
        except Exception as e:
            self._logger.warning(f"Health check exception: {e}")
            return False

    async def _wait_until_healthy(self, timeout: int = 30) -> bool:
        start = asyncio.get_event_loop().time()
        while (asyncio.get_event_loop().time() - start) < timeout:
            if await self.is_healthy():
                return True
            await asyncio.sleep(0.5)
        return False

    def flask_status(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "pid": self.process.pid if self.process else None,
            "restarts": self._restart_count,
        }

    def _cleanup_process_refs(self):
        self.process = None
        self.port = None

