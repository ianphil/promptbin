# Prompt 9: Implement Share Token System

Create a secure sharing system with access tokens:

1. Generate cryptographically secure tokens for shared prompts
2. Share URLs format: /share/<token>/<prompt_id>
3. Token validation middleware that checks token before serving prompt
4. Store active tokens in memory (reset on app restart)
5. Public share view that shows prompt read-only with limited UI
6. Origin validation - only /share/ routes accessible via tunnel
7. Regular routes return 403 when accessed from tunnel URL

Include a "Generate Share Link" button that creates token and shows copyable URL.