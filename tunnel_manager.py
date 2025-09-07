import subprocess
import time
import re
import logging
import atexit
import os
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class TunnelManager:
    """
    Comprehensive Microsoft Dev Tunnels management with subprocess handling,
    rate limiting, and security features.
    """
    
    def __init__(self, flask_port: int = 5001):
        self.flask_port = flask_port
        self.tunnel_process = None
        self.tunnel_url = None
        self.tunnel_id = None
        self._ip_attempts = defaultdict(list)  # IP -> list of attempt timestamps
        
        # Read configuration from environment variables
        self._enabled = os.environ.get('DEVTUNNEL_ENABLED', 'true').lower() == 'true'
        self._rate_limit = int(os.environ.get('DEVTUNNEL_RATE_LIMIT', '5'))
        self._auto_start = os.environ.get('DEVTUNNEL_AUTO_START', 'false').lower() == 'true'
        
        # Rate limit window in minutes
        rate_window_minutes = int(os.environ.get('DEVTUNNEL_RATE_WINDOW', '30'))
        self._rate_limit_window = timedelta(minutes=rate_window_minutes)
        
        # Configure logging level for tunnel operations
        log_level = os.environ.get('DEVTUNNEL_LOG_LEVEL', 'info').upper()
        if log_level in ['DEBUG', 'INFO', 'WARNING', 'ERROR']:
            logger.setLevel(getattr(logging, log_level))
        
        # Log configuration
        logger.info(f"TunnelManager initialized: enabled={self._enabled}, rate_limit={self._rate_limit}, auto_start={self._auto_start}")
        
        # Register cleanup on exit - let Flask handle signals
        atexit.register(self.cleanup)
    
    def cleanup(self):
        """Clean up tunnel process and resources"""
        if self.tunnel_process and self.tunnel_process.poll() is None:
            try:
                logger.info("Terminating tunnel process...")
                self.tunnel_process.terminate()
                # Wait up to 5 seconds for graceful shutdown
                try:
                    self.tunnel_process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logger.warning("Tunnel process didn't terminate gracefully, killing...")
                    self.tunnel_process.kill()
                    self.tunnel_process.wait()
            except Exception as e:
                logger.error(f"Error during tunnel cleanup: {e}")
        
        self.tunnel_process = None
        self.tunnel_url = None
        self.tunnel_id = None
    
    def check_cli_available(self) -> tuple[bool, str]:
        """
        Check if devtunnel CLI is installed and accessible.
        Returns (is_available, message)
        """
        try:
            result = subprocess.run(
                ['devtunnel', '--version'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return True, "DevTunnel CLI is available"
            else:
                return False, f"DevTunnel CLI returned error: {result.stderr}"
        except FileNotFoundError:
            return False, "DevTunnel CLI not installed. Please install from https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/"
        except subprocess.TimeoutExpired:
            return False, "DevTunnel CLI check timed out"
        except Exception as e:
            return False, f"Error checking DevTunnel CLI: {str(e)}"
    
    def check_authentication(self) -> tuple[bool, str]:
        """
        Check if user is authenticated with devtunnel.
        Returns (is_authenticated, message)
        """
        try:
            result = subprocess.run(
                ['devtunnel', 'user', 'show'],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and 'Logged in as' in result.stdout:
                return True, result.stdout.strip()
            else:
                return False, "Not authenticated. Please run 'devtunnel user login' or 'devtunnel user login -g' for GitHub"
        except FileNotFoundError:
            return False, "DevTunnel CLI not installed"
        except subprocess.TimeoutExpired:
            return False, "Authentication check timed out"
        except Exception as e:
            return False, f"Error checking authentication: {str(e)}"
    
    def _check_rate_limit(self, client_ip: str) -> tuple[bool, str]:
        """
        Check if IP has exceeded rate limit.
        Returns (is_allowed, message)
        """
        now = datetime.now()
        attempts = self._ip_attempts[client_ip]
        
        # Remove old attempts outside the window
        cutoff = now - self._rate_limit_window
        self._ip_attempts[client_ip] = [attempt for attempt in attempts if attempt > cutoff]
        
        if len(self._ip_attempts[client_ip]) >= self._rate_limit:
            return False, f"Rate limit exceeded. Maximum {self._rate_limit} attempts per {self._rate_limit_window.total_seconds()/60:.0f} minutes"
        
        return True, "Rate limit check passed"
    
    def _record_attempt(self, client_ip: str):
        """Record a tunnel access attempt for rate limiting"""
        self._ip_attempts[client_ip].append(datetime.now())
    
    def _parse_tunnel_url(self, output: str) -> Optional[str]:
        """
        Parse tunnel URL from devtunnel CLI output.
        Expected format: https://tunnel_id-port.region.devtunnels.ms/
        """
        # Look for the tunnel URL pattern in the output
        url_pattern = r'(https://[a-zA-Z0-9-]+-\d+\.[a-zA-Z0-9-]+\.devtunnels\.ms/?)'
        match = re.search(url_pattern, output)
        if match:
            return match.group(1).rstrip('/')
        
        # Fallback: look for any devtunnels.ms URL
        fallback_pattern = r'(https://[^\s]+\.devtunnels\.ms[^\s]*)'
        match = re.search(fallback_pattern, output)
        if match:
            return match.group(1).rstrip('/')
        
        return None
    
    def start_tunnel(self, client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """
        Start the devtunnel process.
        Returns dict with status, message, and tunnel_url if successful.
        """
        # Check if tunnels are enabled
        if not self._enabled:
            return {
                'status': 'error',
                'message': 'Dev Tunnels are disabled. Set DEVTUNNEL_ENABLED=true to enable.'
            }
            
        # Check if tunnel is already running
        if self.is_tunnel_active():
            return {
                'status': 'error',
                'message': 'Tunnel is already running',
                'tunnel_url': self.tunnel_url
            }
        
        # Check rate limiting
        allowed, limit_msg = self._check_rate_limit(client_ip)
        if not allowed:
            # Auto-shutdown any existing tunnel on rate limit breach
            self.stop_tunnel()
            return {
                'status': 'error',
                'message': limit_msg
            }
        
        # Check CLI availability
        cli_available, cli_msg = self.check_cli_available()
        if not cli_available:
            return {
                'status': 'error',
                'message': cli_msg
            }
        
        # Check authentication
        auth_ok, auth_msg = self.check_authentication()
        if not auth_ok:
            return {
                'status': 'error',
                'message': auth_msg
            }
        
        try:
            # Record the attempt
            self._record_attempt(client_ip)
            
            # Start tunnel process with anonymous access
            cmd = [
                'devtunnel', 'host',
                '--port-numbers', str(self.flask_port),
                '--allow-anonymous'
            ]
            
            logger.info(f"Starting tunnel with command: {' '.join(cmd)}")
            
            self.tunnel_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Wait for tunnel to start and capture output
            startup_output = ""
            tunnel_url = None
            timeout = 30  # 30 second timeout
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if self.tunnel_process.poll() is not None:
                    # Process has terminated
                    output = self.tunnel_process.stdout.read() if self.tunnel_process.stdout else ""
                    startup_output += output
                    return {
                        'status': 'error',
                        'message': f'Tunnel process terminated unexpectedly: {startup_output}'
                    }
                
                # Read available output
                try:
                    line = self.tunnel_process.stdout.readline()
                    if line:
                        startup_output += line
                        logger.debug(f"Tunnel output: {line.strip()}")
                        
                        # Try to parse URL from this line
                        parsed_url = self._parse_tunnel_url(line)
                        if parsed_url:
                            tunnel_url = parsed_url
                            break
                except Exception as e:
                    logger.warning(f"Error reading tunnel output: {e}")
                
                time.sleep(0.5)
            
            if tunnel_url:
                self.tunnel_url = tunnel_url
                # Extract tunnel ID from URL for cleanup purposes
                id_match = re.search(r'https://([^-]+)', tunnel_url)
                self.tunnel_id = id_match.group(1) if id_match else None
                
                logger.info(f"Tunnel started successfully: {tunnel_url}")
                return {
                    'status': 'success',
                    'message': 'Tunnel started successfully',
                    'tunnel_url': tunnel_url
                }
            else:
                # Timeout or no URL found
                self.stop_tunnel()
                return {
                    'status': 'error',
                    'message': f'Tunnel startup timed out or URL not found. Output: {startup_output}'
                }
                
        except Exception as e:
            logger.error(f"Error starting tunnel: {e}")
            self.cleanup()
            return {
                'status': 'error',
                'message': f'Failed to start tunnel: {str(e)}'
            }
    
    def stop_tunnel(self) -> Dict[str, Any]:
        """
        Stop the devtunnel process.
        Returns dict with status and message.
        """
        if not self.tunnel_process:
            return {
                'status': 'success',
                'message': 'No tunnel to stop'
            }
        
        try:
            logger.info("Stopping tunnel...")
            self.cleanup()
            return {
                'status': 'success',
                'message': 'Tunnel stopped successfully'
            }
        except Exception as e:
            logger.error(f"Error stopping tunnel: {e}")
            return {
                'status': 'error',
                'message': f'Error stopping tunnel: {str(e)}'
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get current tunnel status.
        Returns dict with status info.
        """
        is_active = self.is_tunnel_active()
        
        return {
            'active': is_active,
            'tunnel_url': self.tunnel_url if is_active else None,
            'process_id': self.tunnel_process.pid if self.tunnel_process and is_active else None,
            'cli_available': self.check_cli_available()[0],
            'authenticated': self.check_authentication()[0]
        }
    
    def get_tunnel_url(self) -> Optional[str]:
        """
        Get the current tunnel URL if active.
        Returns URL string or None.
        """
        if self.is_tunnel_active():
            return self.tunnel_url
        return None
    
    def is_tunnel_active(self) -> bool:
        """Check if tunnel process is running"""
        if not self.tunnel_process:
            return False
        
        # Check if process is still running
        poll_result = self.tunnel_process.poll()
        if poll_result is not None:
            # Process has terminated
            logger.info(f"Tunnel process terminated with code {poll_result}")
            self.cleanup()
            return False
        
        return True
    
    def reset_rate_limits(self):
        """Reset all rate limiting counters (for manual admin reset)"""
        self._ip_attempts.clear()
        logger.info("Rate limiting counters reset")
    
    @property
    def is_enabled(self) -> bool:
        """Check if Dev Tunnels are enabled"""
        return self._enabled
    
    @property
    def auto_start_enabled(self) -> bool:
        """Check if auto-start is enabled"""
        return self._auto_start
    
    @property
    def rate_limit(self) -> int:
        """Get current rate limit setting"""
        return self._rate_limit
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current tunnel configuration"""
        return {
            'enabled': self._enabled,
            'auto_start': self._auto_start,
            'rate_limit': self._rate_limit,
            'rate_window_minutes': self._rate_limit_window.total_seconds() / 60,
            'log_level': logger.getEffectiveLevel()
        }
