# Prompt 10: Add Security & Rate Limiting

Implement security features for shared prompts:

1. Rate limiting: Track failed access attempts per IP
2. After 5 failed attempts from an IP, automatically kill tunnel
3. Show security alerts in UI when suspicious activity detected
4. Log all external access attempts with timestamps and IPs
5. Implement CSRF protection for all state-changing operations
6. Add request origin validation to prevent unauthorized tunnel access
7. Security dashboard showing recent access attempts and blocked IPs

The rate limiter should reset counts after successful access or manual reset.