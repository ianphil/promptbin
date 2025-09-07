# Prompt 2: Add Backend API Endpoints

Add Dev Tunnels API endpoints to `app.py`:

## New API Endpoints

1. **POST /api/tunnel/start**
   - Start devtunnel process using TunnelManager
   - Return tunnel URL and status
   - Handle authentication requirements
   - Implement rate limiting middleware

2. **POST /api/tunnel/stop**
   - Stop active tunnel process
   - Clean up resources
   - Return confirmation status

3. **GET /api/tunnel/status**
   - Return current tunnel state (active/inactive)
   - Include tunnel URL if active
   - Return process health information

4. **GET /api/tunnel/url**
   - Get active tunnel URL
   - Return null if no active tunnel
   - Used by frontend for URL copying

## Integration Points

- Import and initialize TunnelManager
- Integrate with existing Flask app structure
- Update share URL generation in `create_share_link()` to use tunnel URL when active
- Add tunnel status to health endpoint
- Handle tunnel process cleanup on app shutdown

## Rate Limiting

- Track IP addresses accessing tunnel endpoints
- Implement 5-attempt limit per IP
- Auto-shutdown tunnel on rate limit breach
- Reset counters on tunnel restart

## Error Responses

- Handle devtunnel CLI not installed
- Authentication failure responses
- Process startup/shutdown errors
- Rate limit exceeded responses