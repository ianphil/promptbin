# Prompt 5: Add Installation and Setup Instructions

Create installation documentation and setup utilities:

## Documentation Updates

1. **Update README.md** with Dev Tunnels section:
   - Installation instructions for devtunnel CLI
   - Platform-specific installation (Linux, macOS, Windows)
   - Authentication setup requirements
   - Usage examples and screenshots

2. **Create TUNNELS.md** with detailed guide:
   - What are Microsoft Dev Tunnels
   - Security implications and best practices
   - Troubleshooting common issues
   - Rate limiting explanation

## Installation Scripts

Create `scripts/install_devtunnel.py`:
- Auto-detect platform (Linux/macOS/Windows)
- Download and install devtunnel CLI using correct methods:
  - Linux: `curl -sL https://aka.ms/TunnelsCliDownload/linux-x64` or install script
  - macOS: `brew install --cask devtunnel` or curl download
  - Windows: `winget install Microsoft.devtunnel` or PowerShell download
- Verify installation success with `devtunnel --version`
- Setup PATH if needed (e.g., ~/.local/bin for Linux)

## Setup Checker

Add `setup_checker.py` module:
- Check devtunnel CLI availability with `devtunnel --version`
- Verify authentication status with `devtunnel user show`
- Test tunnel creation capability (if authenticated)
- Generate setup report with specific issues
- Provide fix suggestions for common problems

## Requirements Updates

Update project dependencies:
- Add any new Python requirements
- Document system requirements
- Add optional dependencies for enhanced features
- Update pyproject.toml if needed

## Environment Configuration

Add environment variables support:
- DEVTUNNEL_ENABLED (true/false)
- DEVTUNNEL_RATE_LIMIT (default: 5)
- DEVTUNNEL_AUTO_START (true/false)
- DEVTUNNEL_LOG_LEVEL (debug/info/warning)

## Platform Compatibility

Ensure cross-platform support:
- Linux: curl-based installation
- macOS: Homebrew or curl installation  
- Windows: winget or PowerShell installation
- Handle platform-specific path differences
- Test on different architectures (x64, arm64)