# Kill PromptBin processes script for Windows PowerShell
# This script kills any running PromptBin processes and processes using port 5001

param(
    [switch]$Force,
    [switch]$Verbose
)

# Set error action preference
$ErrorActionPreference = "Continue"

Write-Host "🔍 Searching for PromptBin processes..." -ForegroundColor Cyan

# Function to kill processes by name pattern
function Kill-ProcessesByName {
    param(
        [string]$Pattern,
        [string]$Description
    )
    
    try {
        $processes = Get-Process | Where-Object { $_.ProcessName -match $Pattern -or $_.Path -match $Pattern }
        
        if ($processes) {
            Write-Host "📍 Found $Description processes:" -ForegroundColor Yellow
            foreach ($proc in $processes) {
                Write-Host "  - PID $($proc.Id): $($proc.ProcessName) $($proc.Path)" -ForegroundColor Gray
            }
            
            foreach ($proc in $processes) {
                try {
                    if ($Force) {
                        $proc.Kill()
                        Write-Host "🔨 Force killed PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Red
                    } else {
                        $proc.CloseMainWindow()
                        Start-Sleep -Seconds 2
                        if (!$proc.HasExited) {
                            $proc.Kill()
                            Write-Host "🔨 Killed PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Red
                        } else {
                            Write-Host "✅ Gracefully closed PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Green
                        }
                    }
                } catch {
                    Write-Host "⚠️  Could not kill PID $($proc.Id): $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
            Write-Host "✅ Processed $Description" -ForegroundColor Green
        } else {
            Write-Host "✅ No $Description processes found" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Error searching for $Description processes: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to kill processes using specific port
function Kill-ProcessesByPort {
    param(
        [int]$Port
    )
    
    try {
        # Use netstat to find processes using the port
        $netstatOutput = netstat -ano | Select-String ":$Port "
        
        if ($netstatOutput) {
            Write-Host "📍 Found processes using port $Port" -ForegroundColor Yellow
            
            $pids = @()
            foreach ($line in $netstatOutput) {
                if ($line -match '\s+(\d+)$') {
                    $pid = $matches[1]
                    if ($pid -and $pid -ne "0" -and $pids -notcontains $pid) {
                        $pids += $pid
                    }
                }
            }
            
            foreach ($pid in $pids) {
                try {
                    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                    if ($process) {
                        Write-Host "  - PID $pid: $($process.ProcessName) using port $Port" -ForegroundColor Gray
                        
                        if ($Force) {
                            Stop-Process -Id $pid -Force
                            Write-Host "🔨 Force killed PID $pid" -ForegroundColor Red
                        } else {
                            Stop-Process -Id $pid
                            Write-Host "✅ Killed PID $pid" -ForegroundColor Green
                        }
                    }
                } catch {
                    Write-Host "⚠️  Could not kill PID $pid: $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
            Write-Host "✅ Processed processes using port $Port" -ForegroundColor Green
        } else {
            Write-Host "✅ No processes found using port $Port" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Error searching for processes using port $Port`: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Function to kill processes by command line pattern
function Kill-ProcessesByCommandLine {
    param(
        [string]$Pattern,
        [string]$Description
    )
    
    try {
        $processes = Get-WmiObject Win32_Process | Where-Object { $_.CommandLine -match $Pattern }
        
        if ($processes) {
            Write-Host "📍 Found $Description processes:" -ForegroundColor Yellow
            foreach ($proc in $processes) {
                Write-Host "  - PID $($proc.ProcessId): $($proc.Name)" -ForegroundColor Gray
                if ($Verbose) {
                    Write-Host "    Command: $($proc.CommandLine)" -ForegroundColor DarkGray
                }
            }
            
            foreach ($proc in $processes) {
                try {
                    if ($Force) {
                        Stop-Process -Id $proc.ProcessId -Force
                        Write-Host "🔨 Force killed PID $($proc.ProcessId): $($proc.Name)" -ForegroundColor Red
                    } else {
                        Stop-Process -Id $proc.ProcessId
                        Write-Host "✅ Killed PID $($proc.ProcessId): $($proc.Name)" -ForegroundColor Green
                    }
                } catch {
                    Write-Host "⚠️  Could not kill PID $($proc.ProcessId): $($_.Exception.Message)" -ForegroundColor Yellow
                }
            }
            Write-Host "✅ Processed $Description" -ForegroundColor Green
        } else {
            Write-Host "✅ No $Description processes found" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Error searching for $Description processes: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# Kill PromptBin processes by name patterns
Kill-ProcessesByName "promptbin" "PromptBin"
Kill-ProcessesByName "python.*promptbin" "PromptBin Python"

# Kill processes by command line patterns
Kill-ProcessesByCommandLine "promptbin" "PromptBin command line"
Kill-ProcessesByCommandLine "app\.py" "Flask app.py"
Kill-ProcessesByCommandLine "mcp.*server\.py" "MCP server"
Kill-ProcessesByCommandLine "src[\\/]promptbin" "PromptBin source"
Kill-ProcessesByCommandLine "devtunnel" "Dev Tunnel"

# Kill processes using specific ports
Kill-ProcessesByPort 5001
Kill-ProcessesByPort 5000

Write-Host ""
Write-Host "🎉 PromptBin cleanup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "ℹ️  If you were running PromptBin in MCP mode, you may also need to restart your AI client" -ForegroundColor Cyan
Write-Host "   (Claude Desktop, ChatGPT, etc.) to reconnect to a fresh MCP server instance." -ForegroundColor Cyan
Write-Host ""
Write-Host "💡 Usage tips:" -ForegroundColor Yellow
Write-Host "   kill-promptbin.ps1 -Force    # Force kill all processes immediately" -ForegroundColor Gray
Write-Host "   kill-promptbin.ps1 -Verbose  # Show detailed command line info" -ForegroundColor Gray