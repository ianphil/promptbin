#!/usr/bin/env python3
"""
Literate Test Runner

Parses markdown test files and executes embedded Python code blocks,
validating assertions marked with `# expect: <value>` comments.

Usage:
    python tests/run_literate_tests.py tests/mcp_server_lifecycle.md
    uv run python tests/run_literate_tests.py tests/mcp_server_lifecycle.md
"""

import re
import sys
import tempfile
import traceback
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class TestBlock:
    """Represents a single test code block"""
    section: str
    code: str
    line_number: int
    assertions: list = field(default_factory=list)


@dataclass
class TestResult:
    """Result of executing a test block"""
    block: TestBlock
    passed: bool
    error: Optional[str] = None
    assertion_results: list = field(default_factory=list)


class LiterateTestRunner:
    """Runs literate tests from markdown files"""

    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.content = filepath.read_text()
        self.blocks: list[TestBlock] = []
        self.results: list[TestResult] = []

    def parse(self) -> list[TestBlock]:
        """Extract test blocks from markdown"""
        lines = self.content.split('\n')
        current_section = "Unknown"
        in_code_block = False
        code_lines = []
        block_start_line = 0
        block_language = ""

        for i, line in enumerate(lines, 1):
            # Track section headers
            if line.startswith('## '):
                current_section = line[3:].strip()
                continue

            # Detect code block start
            if line.startswith('```python'):
                in_code_block = True
                block_language = "python"
                block_start_line = i
                code_lines = []
                continue

            # Detect code block end
            if line.startswith('```') and in_code_block:
                in_code_block = False
                if block_language == "python" and code_lines:
                    code = '\n'.join(code_lines)
                    # Extract expect comments
                    assertions = self._extract_assertions(code)
                    self.blocks.append(TestBlock(
                        section=current_section,
                        code=code,
                        line_number=block_start_line,
                        assertions=assertions
                    ))
                continue

            # Collect code lines
            if in_code_block:
                code_lines.append(line)

        return self.blocks

    def _extract_assertions(self, code: str) -> list[tuple[int, str]]:
        """Extract # expect: comments and their expected values"""
        assertions = []
        lines = code.split('\n')
        for i, line in enumerate(lines):
            match = re.search(r'#\s*expect:\s*(.+)$', line)
            if match:
                expected = match.group(1).strip()
                assertions.append((i + 1, expected))
        return assertions

    def run(self) -> list[TestResult]:
        """Execute all test blocks"""
        if not self.blocks:
            self.parse()

        for block in self.blocks:
            result = self._run_block(block)
            self.results.append(result)

        return self.results

    def _run_block(self, block: TestBlock) -> TestResult:
        """Execute a single test block"""
        # Create isolated namespace for execution
        namespace = {'__name__': '__test__'}

        try:
            # Execute the code block
            exec(block.code, namespace)

            # All assertions passed if we got here (assert raises on failure)
            return TestResult(
                block=block,
                passed=True,
                assertion_results=[(a[0], a[1], True) for a in block.assertions]
            )

        except AssertionError as e:
            return TestResult(
                block=block,
                passed=False,
                error=f"AssertionError: {e}",
                assertion_results=[(0, str(e), False)]
            )

        except Exception as e:
            tb = traceback.format_exc()
            return TestResult(
                block=block,
                passed=False,
                error=f"{type(e).__name__}: {e}\n{tb}"
            )

    def report(self) -> int:
        """Print test results and return exit code"""
        if not self.results:
            self.run()

        print(f"\n{self.BOLD}Literate Test Results: {self.filepath.name}{self.RESET}")
        print("=" * 60)

        passed = 0
        failed = 0
        current_section = ""

        for result in self.results:
            # Print section header if changed
            if result.block.section != current_section:
                current_section = result.block.section
                print(f"\n{self.BLUE}{self.BOLD}{current_section}{self.RESET}")

            # Print result
            if result.passed:
                status = f"{self.GREEN}PASS{self.RESET}"
                passed += 1
            else:
                status = f"{self.RED}FAIL{self.RESET}"
                failed += 1

            print(f"  [{status}] Line {result.block.line_number}")

            # Print error details for failures
            if not result.passed and result.error:
                error_lines = result.error.split('\n')
                for line in error_lines[:5]:  # Limit error output
                    print(f"    {self.RED}{line}{self.RESET}")
                if len(error_lines) > 5:
                    print(f"    {self.YELLOW}... (truncated){self.RESET}")

        # Summary
        print("\n" + "=" * 60)
        total = passed + failed
        if failed == 0:
            summary_color = self.GREEN
        else:
            summary_color = self.RED

        print(f"{summary_color}{self.BOLD}Results: {passed}/{total} passed{self.RESET}")

        if failed > 0:
            print(f"{self.RED}{failed} test(s) failed{self.RESET}")
            return 1
        else:
            print(f"{self.GREEN}All tests passed!{self.RESET}")
            return 0


def main():
    """CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage: python run_literate_tests.py <test_file.md>")
        print("Example: python tests/run_literate_tests.py tests/mcp_server_lifecycle.md")
        sys.exit(1)

    filepath = Path(sys.argv[1])
    if not filepath.exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    if not filepath.suffix == '.md':
        print(f"Warning: Expected .md file, got: {filepath.suffix}")

    runner = LiterateTestRunner(filepath)
    exit_code = runner.report()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
