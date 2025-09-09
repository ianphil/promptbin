#!/bin/bash
# Kill PromptBin processes script for Linux/macOS
# This script kills any running PromptBin processes and processes using port 5001

set -e

echo "🔍 Searching for PromptBin processes..."

# Function to kill processes by name pattern
kill_by_name() {
    local pattern="$1"
    local description="$2"
    
    if command -v pgrep >/dev/null 2>&1; then
        # Use pgrep for more reliable process finding
        pids=$(pgrep -f "$pattern" 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "📍 Found $description processes: $pids"
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            # Force kill if still running
            remaining_pids=$(pgrep -f "$pattern" 2>/dev/null || true)
            if [ -n "$remaining_pids" ]; then
                echo "🔨 Force killing remaining $description processes: $remaining_pids"
                echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
            fi
            echo "✅ Killed $description processes"
        else
            echo "✅ No $description processes found"
        fi
    else
        # Fallback to ps + grep
        pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}' || true)
        if [ -n "$pids" ]; then
            echo "📍 Found $description processes: $pids"
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            # Force kill if still running
            remaining_pids=$(ps aux | grep -E "$pattern" | grep -v grep | awk '{print $2}' || true)
            if [ -n "$remaining_pids" ]; then
                echo "🔨 Force killing remaining $description processes: $remaining_pids"
                echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
            fi
            echo "✅ Killed $description processes"
        else
            echo "✅ No $description processes found"
        fi
    fi
}

# Function to kill processes using specific port
kill_by_port() {
    local port="$1"
    local description="processes using port $port"
    
    if command -v lsof >/dev/null 2>&1; then
        # Use lsof to find processes using the port
        pids=$(lsof -ti tcp:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            echo "📍 Found $description: $pids"
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            # Force kill if still running
            remaining_pids=$(lsof -ti tcp:$port 2>/dev/null || true)
            if [ -n "$remaining_pids" ]; then
                echo "🔨 Force killing remaining $description: $remaining_pids"
                echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
            fi
            echo "✅ Killed $description"
        else
            echo "✅ No $description found"
        fi
    elif command -v netstat >/dev/null 2>&1; then
        # Fallback to netstat
        pids=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d/ -f1 | grep -v '-' || true)
        if [ -n "$pids" ]; then
            echo "📍 Found $description: $pids"
            echo "$pids" | xargs kill -TERM 2>/dev/null || true
            sleep 2
            # Force kill if still running
            remaining_pids=$(netstat -tlnp 2>/dev/null | grep ":$port " | awk '{print $7}' | cut -d/ -f1 | grep -v '-' || true)
            if [ -n "$remaining_pids" ]; then
                echo "🔨 Force killing remaining $description: $remaining_pids"
                echo "$remaining_pids" | xargs kill -KILL 2>/dev/null || true
            fi
            echo "✅ Killed $description"
        else
            echo "✅ No $description found"
        fi
    else
        echo "⚠️  Neither lsof nor netstat available - cannot kill processes by port"
    fi
}

# Kill PromptBin processes by name patterns
kill_by_name "promptbin" "PromptBin"
kill_by_name "python.*app\.py" "Flask app.py"
kill_by_name "python.*mcp.*server\.py" "MCP server"
kill_by_name "python.*src/promptbin" "PromptBin Python"
kill_by_name "devtunnel" "Dev Tunnel"

# Kill processes using port 5001
kill_by_port "5001"

# Also check common alternative ports
kill_by_port "5000"

echo ""
echo "🎉 PromptBin cleanup complete!"
echo ""
echo "ℹ️  If you were running PromptBin in MCP mode, you may also need to restart your AI client"
echo "   (Claude Desktop, ChatGPT, etc.) to reconnect to a fresh MCP server instance."