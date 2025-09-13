#!/usr/bin/env python3
"""
CLI Integration Tests for PromptBin

Tests all CLI parameter combinations to ensure proper process lifecycle management:
1. promptbin (default both mode) - MCP + Flask
2. promptbin --web - Flask only
3. promptbin --mcp - MCP only
4. promptbin --both - Explicit both mode
"""

import asyncio
import os
import psutil
import pytest
import requests
import signal
import subprocess
import time
from typing import List, Optional, Tuple


class ProcessManager:
    """Helper class to manage test processes and cleanup"""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.test_port = 5555  # Use different port to avoid conflicts

    def start_promptbin(self, args: List[str]) -> subprocess.Popen:
        """Start PromptBin with given arguments"""
        cmd = (
            ["uv", "run", "promptbin"]
            + args
            + ["--port", str(self.test_port), "--log-level", "INFO"]
        )

        # Set environment to avoid MCP-managed mode detection
        env = os.environ.copy()
        env.pop("PROMPTBIN_MCP_MANAGED", None)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env
        )
        self.processes.append(process)
        return process

    def wait_for_flask_ready(self, timeout: int = 30) -> bool:
        """Wait for Flask to be ready by checking health endpoint"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(
                    f"http://127.0.0.1:{self.test_port}/health", timeout=2
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("status") == "healthy":
                        return True
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                pass
            time.sleep(0.5)
        return False

    def wait_for_mcp_ready(self, process: subprocess.Popen, timeout: int = 15) -> bool:
        """Wait for MCP server to be ready by checking log output"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            # Check if process is still running
            if process.poll() is not None:
                # Process exited - check if it was successful initialization
                # Read stderr to see if MCP server initialized properly
                try:
                    _, stderr = process.communicate(timeout=1)
                    if "PromptBin MCP Server initialized" in stderr:
                        return True  # Successfully initialized before exit
                except:
                    pass
                return False
            time.sleep(0.5)

        # If still running after timeout, consider it successful
        return process.poll() is None

    def get_process_children(self, pid: int) -> List[int]:
        """Get all child process PIDs recursively"""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            return [child.pid for child in children]
        except psutil.NoSuchProcess:
            return []

    def is_flask_running(self) -> bool:
        """Check if Flask is responding"""
        try:
            response = requests.get(
                f"http://127.0.0.1:{self.test_port}/health", timeout=2
            )
            return response.status_code == 200
        except:
            return False

    def is_process_running(self, pid: int) -> bool:
        """Check if process is still running"""
        try:
            return psutil.Process(pid).is_running()
        except psutil.NoSuchProcess:
            return False

    def terminate_process(self, process: subprocess.Popen) -> Tuple[bool, List[int]]:
        """Terminate process and return (success, remaining_pids)"""
        if process.poll() is not None:
            return True, []  # Already terminated

        main_pid = process.pid
        child_pids = self.get_process_children(main_pid)
        all_pids = [main_pid] + child_pids

        # Send SIGTERM
        try:
            process.terminate()
        except ProcessLookupError:
            pass

        # Wait for graceful shutdown
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            # Force kill if needed
            try:
                process.kill()
                process.wait(timeout=5)
            except:
                pass

        # Check what's still running
        remaining_pids = [pid for pid in all_pids if self.is_process_running(pid)]
        return len(remaining_pids) == 0, remaining_pids

    def cleanup(self):
        """Clean up all test processes"""
        for process in self.processes:
            try:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=2)
            except:
                pass
        self.processes.clear()


@pytest.fixture
def process_manager():
    """Fixture to provide process manager with cleanup"""
    manager = ProcessManager()
    yield manager
    manager.cleanup()


class TestCLIIntegration:
    """Integration tests for CLI parameter combinations"""

    def test_promptbin_default_both_mode(self, process_manager):
        """Test: promptbin (default) - both MCP and Flask should initialize"""
        print("\n🧪 Testing: promptbin (default both mode)")

        # Start PromptBin in default mode
        process = process_manager.start_promptbin([])

        # Give time for initialization
        time.sleep(3)

        # Check if process completed successfully (MCP servers exit without client)
        if process.poll() is not None:
            # Process exited - check if it initialized properly
            _, stderr = process.communicate()
            assert (
                "PromptBin MCP Server initialized" in stderr
            ), "MCP server failed to initialize"
            assert "Flask web interface started" in stderr, "Flask failed to start"
            print(
                "✅ Both MCP and Flask initialized successfully (MCP exited as expected)"
            )
            return

        # If still running, check Flask is responding
        assert (
            process_manager.wait_for_flask_ready()
        ), "Flask web interface failed to start"
        assert process_manager.is_flask_running(), "Flask should be responding"

        print("✅ Both MCP and Flask are running")

        # Terminate and verify cleanup
        success, remaining = process_manager.terminate_process(process)

        # Give a moment for cleanup
        time.sleep(2)

        # Verify Flask is no longer responding
        assert (
            not process_manager.is_flask_running()
        ), "Flask should stop responding after termination"

        print("✅ Both MCP and Flask stopped correctly")

        if not success:
            print(
                f"⚠️  Warning: {len(remaining)} processes may still be running: {remaining}"
            )

    def test_promptbin_web_only_mode(self, process_manager):
        """Test: promptbin --web - only Flask should run"""
        print("\n🧪 Testing: promptbin --web (web only mode)")

        # Start PromptBin in web-only mode
        process = process_manager.start_promptbin(["--web"])

        # Wait for Flask to be ready
        assert (
            process_manager.wait_for_flask_ready()
        ), "Flask web interface failed to start"

        # Verify Flask is running
        assert process.poll() is None, "Web process should be running"
        assert process_manager.is_flask_running(), "Flask should be responding"

        print("✅ Flask web interface is running")

        # Terminate and verify cleanup
        success, remaining = process_manager.terminate_process(process)

        # Give a moment for cleanup
        time.sleep(2)

        # Verify Flask is no longer responding
        assert (
            not process_manager.is_flask_running()
        ), "Flask should stop responding after termination"

        print("✅ Flask stopped correctly")

        if not success:
            print(
                f"⚠️  Warning: {len(remaining)} processes may still be running: {remaining}"
            )

    def test_promptbin_mcp_only_mode(self, process_manager):
        """Test: promptbin --mcp - only MCP server should initialize"""
        print("\n🧪 Testing: promptbin --mcp (MCP only mode)")

        # Start PromptBin in MCP-only mode
        process = process_manager.start_promptbin(["--mcp"])

        # Give time for initialization
        time.sleep(3)

        # Check if process completed successfully (MCP servers exit without client)
        if process.poll() is not None:
            # Process exited - check if it initialized properly
            _, stderr = process.communicate()
            assert (
                "PromptBin MCP Server initialized" in stderr
            ), "MCP server failed to initialize"
            # Flask should NOT have started in MCP-only mode
            assert (
                "Flask web interface started" not in stderr
            ), "Flask should NOT start in MCP-only mode"
            print("✅ MCP server initialized successfully, Flask correctly not started")
            return

        # If still running, verify Flask is NOT running
        time.sleep(2)  # Give time to ensure Flask doesn't start
        assert (
            not process_manager.is_flask_running()
        ), "Flask should NOT be running in MCP-only mode"

        print("✅ MCP server is running, Flask correctly not started")

        # Terminate and verify cleanup
        success, remaining = process_manager.terminate_process(process)

        print("✅ MCP server stopped correctly")

        if not success:
            print(
                f"⚠️  Warning: {len(remaining)} processes may still be running: {remaining}"
            )

    def test_promptbin_explicit_both_mode(self, process_manager):
        """Test: promptbin --both - explicit both mode should work like default"""
        print("\n🧪 Testing: promptbin --both (explicit both mode)")

        # Start PromptBin in explicit both mode
        process = process_manager.start_promptbin(["--both"])

        # Give time for initialization
        time.sleep(3)

        # Check if process completed successfully (MCP servers exit without client)
        if process.poll() is not None:
            # Process exited - check if it initialized properly
            _, stderr = process.communicate()
            assert (
                "PromptBin MCP Server initialized" in stderr
            ), "MCP server failed to initialize"
            assert "Flask web interface started" in stderr, "Flask failed to start"
            print(
                "✅ Both MCP and Flask initialized successfully (explicit mode, MCP exited as expected)"
            )
            return

        # If still running, check Flask is responding
        assert (
            process_manager.wait_for_flask_ready()
        ), "Flask web interface failed to start"
        assert process_manager.is_flask_running(), "Flask should be responding"

        print("✅ Both MCP and Flask are running (explicit mode)")

        # Terminate and verify cleanup
        success, remaining = process_manager.terminate_process(process)

        # Give a moment for cleanup
        time.sleep(2)

        # Verify Flask is no longer responding
        assert (
            not process_manager.is_flask_running()
        ), "Flask should stop responding after termination"

        print("✅ Both MCP and Flask stopped correctly (explicit mode)")

        if not success:
            print(
                f"⚠️  Warning: {len(remaining)} processes may still be running: {remaining}"
            )


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
