#!/usr/bin/env python3
"""
Cross-platform DevTunnel CLI installer for PromptBin
Supports Linux, macOS, and Windows with automatic platform detection
"""

import os
import sys
import platform
import subprocess
import urllib.request
import shutil
import tempfile
from pathlib import Path

class DevTunnelInstaller:
    def __init__(self):
        self.system = platform.system().lower()
        self.machine = platform.machine().lower()
        self.is_admin = self._check_admin_privileges()
        
    def _check_admin_privileges(self) -> bool:
        """Check if running with admin/sudo privileges"""
        try:
            if self.system == 'windows':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def _get_architecture(self) -> str:
        """Detect system architecture"""
        arch_mapping = {
            'x86_64': 'x64',
            'amd64': 'x64', 
            'aarch64': 'arm64',
            'arm64': 'arm64'
        }
        return arch_mapping.get(self.machine, 'x64')  # Default to x64
    
    def _get_download_info(self) -> tuple[str, str]:
        """Get download URL and filename for current platform"""
        arch = self._get_architecture()
        
        if self.system == 'linux':
            return (
                f"https://aka.ms/TunnelsCliDownload/linux-{arch}",
                "devtunnel"
            )
        elif self.system == 'darwin':  # macOS
            return (
                f"https://aka.ms/TunnelsCliDownload/osx-{arch}",
                "devtunnel"
            )
        elif self.system == 'windows':
            return (
                f"https://aka.ms/TunnelsCliDownload/win-{arch}",
                "devtunnel.exe"
            )
        else:
            raise ValueError(f"Unsupported platform: {self.system}")
    
    def _check_existing_installation(self) -> tuple[bool, str]:
        """Check if devtunnel is already installed"""
        try:
            result = subprocess.run(
                ['devtunnel', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                version_info = result.stdout.strip()
                return True, version_info
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        return False, ""
    
    def _try_package_manager_install(self) -> bool:
        """Try installing via system package manager"""
        print("Attempting installation via package manager...")
        
        try:
            if self.system == 'darwin':
                # Try Homebrew on macOS
                result = subprocess.run(['brew', '--version'], capture_output=True)
                if result.returncode == 0:
                    print("Installing via Homebrew...")
                    result = subprocess.run(
                        ['brew', 'install', '--cask', 'devtunnel'],
                        check=True
                    )
                    return True
            elif self.system == 'windows':
                # Try winget on Windows
                result = subprocess.run(['winget', '--version'], capture_output=True)
                if result.returncode == 0:
                    print("Installing via winget...")
                    result = subprocess.run(
                        ['winget', 'install', 'Microsoft.devtunnel'],
                        check=True
                    )
                    return True
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
            
        return False
    
    def _download_and_install(self) -> bool:
        """Download and install DevTunnel CLI directly"""
        url, filename = self._get_download_info()
        
        print(f"Downloading DevTunnel CLI from {url}...")
        
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_file = Path(temp_dir) / filename
                
                # Download the file
                urllib.request.urlretrieve(url, temp_file)
                
                # Make executable (Unix systems)
                if self.system != 'windows':
                    temp_file.chmod(0o755)
                
                # Determine installation directory
                install_dir = self._get_install_directory()
                install_path = install_dir / filename
                
                # Create install directory if it doesn't exist
                install_dir.mkdir(parents=True, exist_ok=True)
                
                # Copy to install directory
                shutil.copy2(temp_file, install_path)
                
                print(f"Installed DevTunnel CLI to: {install_path}")
                
                # Update PATH if needed
                self._update_path_if_needed(install_dir)
                
                return True
                
        except Exception as e:
            print(f"Download installation failed: {e}")
            return False
    
    def _get_install_directory(self) -> Path:
        """Get the appropriate installation directory"""
        if self.system == 'windows':
            # Windows: Use Program Files or user AppData
            if self.is_admin:
                return Path(os.environ.get('ProgramFiles', 'C:\\Program Files')) / 'DevTunnel'
            else:
                return Path(os.environ.get('LOCALAPPDATA', '~')) / 'DevTunnel'
        else:
            # Unix-like: Use /usr/local/bin if admin, ~/.local/bin if user
            if self.is_admin:
                return Path('/usr/local/bin')
            else:
                return Path.home() / '.local' / 'bin'
    
    def _update_path_if_needed(self, install_dir: Path) -> None:
        """Update PATH environment variable if needed"""
        install_dir_str = str(install_dir)
        
        # Check if already in PATH
        current_path = os.environ.get('PATH', '')
        if install_dir_str in current_path:
            return
            
        if self.system == 'windows':
            print(f"Add to PATH: {install_dir_str}")
            print("You may need to restart your terminal for PATH changes to take effect.")
        else:
            # Unix-like systems
            if not self.is_admin and install_dir == Path.home() / '.local' / 'bin':
                shell_configs = [
                    Path.home() / '.bashrc',
                    Path.home() / '.zshrc',
                    Path.home() / '.profile'
                ]
                
                path_export = f'export PATH="$HOME/.local/bin:$PATH"'
                
                for config_file in shell_configs:
                    if config_file.exists():
                        try:
                            content = config_file.read_text()
                            if path_export not in content:
                                with config_file.open('a') as f:
                                    f.write(f'\n# Added by PromptBin DevTunnel installer\n{path_export}\n')
                                print(f"Added PATH export to {config_file}")
                                break
                        except Exception:
                            continue
                            
                print(f"Run: source ~/.bashrc (or restart terminal)")
    
    def _verify_installation(self) -> bool:
        """Verify that the installation was successful"""
        print("Verifying installation...")
        
        # Try a few times as PATH updates might need a moment
        for attempt in range(3):
            installed, version_info = self._check_existing_installation()
            if installed:
                print(f"✅ DevTunnel CLI installed successfully!")
                print(f"Version: {version_info}")
                return True
            elif attempt < 2:  # Don't sleep on last attempt
                print("Waiting for PATH update...")
                import time
                time.sleep(2)
        
        print("❌ Installation verification failed")
        print("The CLI may be installed but not in your PATH.")
        print("Try running 'devtunnel --version' manually.")
        return False
    
    def install(self) -> bool:
        """Main installation method"""
        print("PromptBin DevTunnel CLI Installer")
        print("=" * 40)
        print(f"Platform: {self.system} ({self.machine})")
        print(f"Admin privileges: {'Yes' if self.is_admin else 'No'}")
        print()
        
        # Check if already installed
        installed, version_info = self._check_existing_installation()
        if installed:
            print("✅ DevTunnel CLI is already installed!")
            print(f"Version: {version_info}")
            
            response = input("Reinstall anyway? [y/N]: ").strip().lower()
            if response not in ['y', 'yes']:
                return True
        
        # Try package manager first, then direct download
        if self._try_package_manager_install():
            print("✅ Installed via package manager!")
        elif self._download_and_install():
            print("✅ Installed via direct download!")
        else:
            print("❌ Installation failed!")
            print("\nManual installation options:")
            print("- Linux: curl -sL https://aka.ms/TunnelsCliDownload/linux-x64 -o devtunnel")
            print("- macOS: brew install --cask devtunnel")  
            print("- Windows: winget install Microsoft.devtunnel")
            return False
        
        # Verify installation
        return self._verify_installation()

def main():
    """Main entry point"""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("""
PromptBin DevTunnel CLI Installer

This script automatically downloads and installs the Microsoft DevTunnel CLI
for your platform (Linux, macOS, or Windows).

Usage:
    python install_devtunnel.py

The installer will:
1. Detect your platform and architecture
2. Try package manager installation first (brew, winget)
3. Fall back to direct download if needed
4. Set up PATH configuration automatically
5. Verify the installation works

No arguments needed - the installer handles everything automatically.
        """)
        return 0
    
    try:
        installer = DevTunnelInstaller()
        success = installer.install()
        
        if success:
            print("\n🎉 Installation complete!")
            print("\nNext steps:")
            print("1. Restart your terminal (or run: source ~/.bashrc)")
            print("2. Authenticate: devtunnel user login -g")
            print("3. Start PromptBin: uv run python app.py")
            print("4. Click 'Start Tunnel' in the footer")
            return 0
        else:
            print("\n❌ Installation failed!")
            print("Please try manual installation - see TUNNELS.md for instructions.")
            return 1
            
    except KeyboardInterrupt:
        print("\nInstallation cancelled by user.")
        return 1
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        print("Please try manual installation - see TUNNELS.md for instructions.")
        return 1

if __name__ == '__main__':
    sys.exit(main())