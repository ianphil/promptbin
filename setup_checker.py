#!/usr/bin/env python3
"""
PromptBin DevTunnel Setup Checker

Validates system configuration and provides diagnostic information
for DevTunnel integration troubleshooting.
"""

import subprocess
import sys
import os
import platform
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path

class SetupChecker:
    def __init__(self):
        self.system = platform.system().lower()
        self.results: Dict[str, Dict] = {}
        self.issues: List[str] = []
        self.suggestions: List[str] = []
    
    def check_cli_availability(self) -> Tuple[bool, str, Optional[str]]:
        """Check if devtunnel CLI is installed and accessible"""
        try:
            result = subprocess.run(
                ['devtunnel', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                return True, version_info, None
            else:
                return False, "CLI returned error", result.stderr.strip()
        except FileNotFoundError:
            return False, "DevTunnel CLI not found in PATH", None
        except subprocess.TimeoutExpired:
            return False, "CLI check timed out (>10s)", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
    
    def check_cli_location(self) -> Optional[str]:
        """Find where devtunnel CLI is installed"""
        try:
            if self.system == 'windows':
                result = subprocess.run(['where', 'devtunnel'], capture_output=True, text=True)
            else:
                result = subprocess.run(['which', 'devtunnel'], capture_output=True, text=True)
            
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass
        return None
    
    def check_authentication(self) -> Tuple[bool, str, Optional[str]]:
        """Check if user is authenticated with devtunnel"""
        try:
            result = subprocess.run(
                ['devtunnel', 'user', 'show'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and 'Logged in as' in result.stdout:
                user_info = result.stdout.strip()
                return True, user_info, None
            else:
                return False, "Not authenticated or authentication expired", result.stderr.strip()
        except FileNotFoundError:
            return False, "DevTunnel CLI not available", None
        except subprocess.TimeoutExpired:
            return False, "Authentication check timed out", None
        except Exception as e:
            return False, f"Unexpected error: {str(e)}", None
    
    def test_tunnel_creation(self) -> Tuple[bool, str]:
        """Test tunnel creation capability (non-destructive)"""
        try:
            # Just test the help command for tunnel creation - doesn't create actual tunnel
            result = subprocess.run(
                ['devtunnel', 'host', '--help'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return True, "Tunnel creation command available"
            else:
                return False, "Tunnel creation command failed"
        except FileNotFoundError:
            return False, "DevTunnel CLI not available"
        except subprocess.TimeoutExpired:
            return False, "Tunnel command test timed out"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def check_python_environment(self) -> Dict[str, str]:
        """Check Python and dependency information"""
        info = {
            'python_version': sys.version,
            'python_executable': sys.executable,
            'platform': platform.platform(),
            'architecture': platform.machine()
        }
        
        # Check for required modules
        required_modules = ['flask', 'requests', 'psutil']
        missing_modules = []
        
        for module in required_modules:
            try:
                __import__(module)
                info[f'{module}_available'] = 'Yes'
            except ImportError:
                info[f'{module}_available'] = 'No'
                missing_modules.append(module)
        
        if missing_modules:
            self.issues.append(f"Missing Python modules: {', '.join(missing_modules)}")
            self.suggestions.append("Run: uv sync")
        
        return info
    
    def check_network_connectivity(self) -> Tuple[bool, str]:
        """Check internet connectivity to Microsoft services"""
        try:
            import urllib.request
            import urllib.error
            
            # Test connectivity to Dev Tunnels service
            test_urls = [
                'https://global.rel.tunnels.api.visualstudio.com/',
                'https://aka.ms/TunnelsCliDownload/linux-x64'
            ]
            
            for url in test_urls:
                try:
                    urllib.request.urlopen(url, timeout=10)
                    return True, "Internet connectivity OK"
                except urllib.error.URLError:
                    continue
            
            return False, "Cannot reach Microsoft Dev Tunnels services"
            
        except Exception as e:
            return False, f"Network check failed: {str(e)}"
    
    def check_path_configuration(self) -> Dict[str, any]:
        """Check PATH configuration and common installation locations"""
        path_info = {
            'current_path': os.environ.get('PATH', ''),
            'path_entries': os.environ.get('PATH', '').split(os.pathsep),
            'devtunnel_location': self.check_cli_location()
        }
        
        # Check common installation locations
        common_locations = []
        if self.system == 'windows':
            common_locations = [
                Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'DevTunnel',
                Path(os.environ.get('LOCALAPPDATA', '~')) / 'DevTunnel'
            ]
        else:
            common_locations = [
                Path('/usr/local/bin'),
                Path('/usr/bin'),
                Path.home() / '.local' / 'bin'
            ]
        
        found_locations = []
        for location in common_locations:
            devtunnel_path = location / ('devtunnel.exe' if self.system == 'windows' else 'devtunnel')
            if devtunnel_path.exists():
                found_locations.append(str(location))
        
        path_info['found_in_common_locations'] = found_locations
        
        return path_info
    
    def generate_suggestions(self) -> None:
        """Generate specific suggestions based on found issues"""
        cli_available, _, _ = self.check_cli_availability()
        auth_ok, _, _ = self.check_authentication()
        
        if not cli_available:
            self.suggestions.extend([
                "Install DevTunnel CLI:",
                "  Linux: curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel && chmod +x devtunnel && sudo mv devtunnel /usr/local/bin/",
                "  macOS: brew install --cask devtunnel",
                "  Windows: winget install Microsoft.devtunnel",
                "  Or run: python scripts/install_devtunnel.py"
            ])
        elif not auth_ok:
            self.suggestions.extend([
                "Authenticate with DevTunnel:",
                "  devtunnel user login -g (GitHub account)",
                "  devtunnel user login (Microsoft account)"
            ])
    
    def run_all_checks(self) -> Dict[str, any]:
        """Run all diagnostic checks and return comprehensive results"""
        print("PromptBin DevTunnel Setup Checker")
        print("=" * 40)
        
        # CLI Availability
        cli_available, cli_info, cli_error = self.check_cli_availability()
        self.results['cli'] = {
            'available': cli_available,
            'info': cli_info,
            'error': cli_error,
            'location': self.check_cli_location()
        }
        
        if not cli_available:
            self.issues.append("DevTunnel CLI not available")
        
        # Authentication
        if cli_available:
            auth_ok, auth_info, auth_error = self.check_authentication()
            self.results['authentication'] = {
                'authenticated': auth_ok,
                'info': auth_info,
                'error': auth_error
            }
            
            if not auth_ok:
                self.issues.append("DevTunnel authentication required")
            
            # Test tunnel capabilities
            tunnel_ok, tunnel_info = self.test_tunnel_creation()
            self.results['tunnel_capability'] = {
                'available': tunnel_ok,
                'info': tunnel_info
            }
        else:
            self.results['authentication'] = {'available': False}
            self.results['tunnel_capability'] = {'available': False}
        
        # Python Environment
        self.results['python'] = self.check_python_environment()
        
        # Network Connectivity
        network_ok, network_info = self.check_network_connectivity()
        self.results['network'] = {
            'connected': network_ok,
            'info': network_info
        }
        
        if not network_ok:
            self.issues.append("Network connectivity issues")
        
        # PATH Configuration
        self.results['path'] = self.check_path_configuration()
        
        # Generate suggestions
        self.generate_suggestions()
        
        self.results['summary'] = {
            'overall_status': len(self.issues) == 0,
            'issues_found': len(self.issues),
            'issues': self.issues,
            'suggestions': self.suggestions
        }
        
        return self.results
    
    def print_results(self) -> None:
        """Print formatted diagnostic results"""
        results = self.results
        
        def status_icon(ok: bool) -> str:
            return "✅" if ok else "❌"
        
        print(f"\n{status_icon(results['cli']['available'])} DevTunnel CLI: {results['cli']['info']}")
        if results['cli']['location']:
            print(f"   Location: {results['cli']['location']}")
        
        if results['cli']['available']:
            auth_ok = results['authentication']['authenticated']
            print(f"{status_icon(auth_ok)} Authentication: {results['authentication']['info']}")
            
            tunnel_ok = results['tunnel_capability']['available']
            print(f"{status_icon(tunnel_ok)} Tunnel Capability: {results['tunnel_capability']['info']}")
        
        network_ok = results['network']['connected']
        print(f"{status_icon(network_ok)} Network: {results['network']['info']}")
        
        python_info = results['python']
        print(f"ℹ️  Python: {python_info['python_version'].split()[0]} ({python_info['architecture']})")
        
        # Summary
        print(f"\n{'🎉' if results['summary']['overall_status'] else '⚠️ '} Overall Status: ", end="")
        if results['summary']['overall_status']:
            print("Ready for DevTunnel integration!")
        else:
            print(f"{results['summary']['issues_found']} issue(s) found")
        
        # Issues and suggestions
        if self.issues:
            print(f"\nIssues Found:")
            for i, issue in enumerate(self.issues, 1):
                print(f"  {i}. {issue}")
        
        if self.suggestions:
            print(f"\nSuggested Fixes:")
            for suggestion in self.suggestions:
                if suggestion.startswith("  "):
                    print(f"    {suggestion}")
                else:
                    print(f"  • {suggestion}")
        
        print()

def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print("""
PromptBin DevTunnel Setup Checker

This diagnostic tool checks your system configuration for DevTunnel integration.

Usage:
    python setup_checker.py [--json] [--verbose]

Options:
    --json      Output results in JSON format
    --verbose   Show detailed diagnostic information
    --help      Show this help message

The checker validates:
- DevTunnel CLI installation and availability
- Authentication status with Microsoft/GitHub
- Network connectivity to Microsoft services  
- Python environment and dependencies
- PATH configuration and common issues
            """)
            return 0
        
    checker = SetupChecker()
    results = checker.run_all_checks()
    
    if '--json' in sys.argv:
        print(json.dumps(results, indent=2))
    else:
        checker.print_results()
    
    # Return appropriate exit code
    return 0 if results['summary']['overall_status'] else 1

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nSetup check cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during setup check: {e}")
        sys.exit(1)