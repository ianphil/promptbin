# Prompt 03a: Enhance Share Link Functionality

Improve the current basic share functionality to create a robust sharing system with proper public URLs and security.

## Current Issues
- Share buttons only copy local URLs (localhost:5000) - not useful for actual sharing
- No backend API to generate shareable links
- No public access mechanism for shared prompts
- Poor error handling and user feedback

## Requirements

### 1. Backend Share API
- **Share generation endpoint**: `POST /api/share/<prompt_id>`
  - Generate cryptographically secure share tokens
  - Return full shareable URLs with proper domain
  - Handle error cases (prompt not found, server errors)
  - Optional expiration time parameter

- **Public share access**: `GET /share/<token>/<prompt_id>`
  - Validate share tokens against stored data
  - Serve prompts in clean, public-friendly format
  - Handle invalid/expired tokens gracefully
  - Rate limiting to prevent abuse

### 2. Share Token Management
- **Secure token generation**
  - Use cryptographically secure random tokens (32+ chars)
  - Store tokens with associated prompt IDs and metadata
  - Simple in-memory or file-based storage (no database needed)
  - Optional expiration timestamps

- **Token validation**
  - Verify token exists and is valid
  - Check expiration if set
  - Clean up expired tokens periodically

### 3. Enhanced Frontend Integration
- **Improved sharePrompt() function**
  - Call `/api/share/<prompt_id>` to get proper shareable URL
  - Show loading state while generating share link
  - Handle API errors gracefully with user feedback
  - Fallback for clipboard API failures (show URL in modal)

- **Better UX**
  - Loading indicators during share link generation
  - Success notifications with copy confirmation
  - Error messages for failed share attempts
  - Option to regenerate share links

### 4. Public Share Template
- **Clean public interface**: `templates/share.html`
  - Minimal UI focused on prompt content
  - No edit controls or sensitive information
  - Clear PromptBin branding and attribution
  - Responsive design for sharing on social/mobile
  - Optional "View More Prompts" link back to main site

### 5. Security & Edge Cases
- **Robust error handling**
  - Invalid share tokens → 404 with helpful message
  - Deleted prompts → Handle gracefully
  - Expired tokens → Clear error messaging
  - Network/API failures → Fallback behavior

- **Security considerations**
  - Rate limiting on share generation
  - Token entropy to prevent guessing
  - No sensitive data in public shares
  - Optional share expiration

## Implementation Notes
- Keep share tokens in simple data structure (JSON file or in-memory)
- Ensure share URLs work with full domain (not just localhost)
- Make sharing URLs look professional: `yoursite.com/share/abc123/prompt-title`
- Consider future Microsoft Dev Tunnels integration for external sharing