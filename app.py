from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import re
import time
import argparse
import logging
from dotenv import load_dotenv
from prompt_manager import PromptManager
from share_manager import ShareManager
from tunnel_manager import TunnelManager
import markdown
try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:  # pragma: no cover
    tomllib = None

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['START_TIME'] = time.time()
app.config['MODE'] = 'standalone'

# Initialize managers with defaults (may be updated when app starts)
share_manager = None  # Will be initialized after parsing args
prompt_manager = PromptManager()  # Default initialization
tunnel_manager = None  # Will be initialized with flask port

# Helper function to get share_manager
def get_share_manager():
    global share_manager
    if share_manager is None:
        share_manager = ShareManager()  # Use default path as fallback
    return share_manager

# Helper function to get tunnel_manager  
def get_tunnel_manager():
    global tunnel_manager
    if tunnel_manager is None:
        # Use the same port that Flask is running on
        flask_port = int(os.environ.get('FLASK_RUN_PORT', 5001))
        tunnel_manager = TunnelManager(flask_port=flask_port)
    return tunnel_manager

# Add custom Jinja2 filter for regex operations
@app.template_filter('regex_findall')
def regex_findall_filter(text, pattern):
    """Custom Jinja2 filter to find all regex matches"""
    try:
        return re.findall(pattern, text)
    except (re.error, TypeError):
        return []

# Add secure highlight filter to prevent XSS
@app.template_filter('safe_highlight')
def safe_highlight_filter(text):
    """Custom Jinja2 filter that only allows specific highlight markup"""
    import html
    from markupsafe import Markup
    
    if not text:
        return text
    
    # First escape all HTML to prevent XSS
    escaped_text = html.escape(str(text))
    
    # Only allow our specific highlight markup through
    # Replace escaped mark tags back to HTML (handle both quote styles)
    safe_text = escaped_text.replace(
        '&lt;mark class=&quot;search-highlight&quot;&gt;', '<mark class="search-highlight">'
    ).replace(
        '&lt;/mark&gt;', '</mark>'
    )
    
    # Return as safe markup since we've sanitized it
    return Markup(safe_text)

@app.route('/')
def index():
    """Main page showing all prompts"""
    category = request.args.get('category')
    prompts = prompt_manager.list_prompts(category)
    stats = prompt_manager.get_stats()
    return render_template('index.html', prompts=prompts, stats=stats, selected_category=category)

@app.route('/create')
def create():
    """Create new prompt page"""
    return render_template('create.html')

@app.route('/view/<prompt_id>')
def view(prompt_id):
    """View single prompt"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        return render_template('404.html'), 404
    return render_template('view.html', prompt=prompt)

@app.route('/edit/<prompt_id>')
def edit(prompt_id):
    """Edit existing prompt"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        return render_template('404.html'), 404
    return render_template('edit.html', prompt=prompt)

@app.route('/htmx/view/<prompt_id>')
def htmx_view(prompt_id):
    """HTMX endpoint for viewing a prompt - returns only main content"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        return '<div class="error-container"><div class="error-content"><h1>Prompt not found</h1></div></div>', 404
    return render_template('partials/view_content.html', prompt=prompt)

@app.route('/htmx/edit/<prompt_id>')
def htmx_edit(prompt_id):
    """HTMX endpoint for editing a prompt - returns only main content"""
    prompt = prompt_manager.get_prompt(prompt_id)
    if not prompt:
        return '<div class="error-container"><div class="error-content"><h1>Prompt not found</h1></div></div>', 404
    return render_template('partials/edit_content.html', prompt=prompt)

@app.route('/htmx/create')
def htmx_create():
    """HTMX endpoint for create page - returns only main content"""
    return render_template('partials/create_content.html')

@app.route('/htmx/index')
def htmx_index():
    """HTMX endpoint for index page - returns only main content"""
    category = request.args.get('category')
    prompts = prompt_manager.list_prompts(category)
    stats = prompt_manager.get_stats()
    return render_template('partials/index_content.html', prompts=prompts, stats=stats, selected_category=category)

@app.route('/htmx/navigation')
def htmx_navigation():
    """HTMX endpoint for navigation sidebar"""
    category = request.args.get('category')
    stats = prompt_manager.get_stats()
    return render_template('partials/navigation.html', stats=stats, selected_category=category)

@app.route('/health')
def health():
    """Health check endpoint for subprocess monitoring"""
    try:
        uptime = int(time.time() - app.config.get('START_TIME', time.time()))
        mode = app.config.get('MODE', 'standalone')

        # Derive version from pyproject if possible
        version = "0.1.0"
        try:
            pyproject_path = os.path.join(os.path.dirname(__file__), 'pyproject.toml')
            if tomllib and os.path.exists(pyproject_path):
                with open(pyproject_path, 'rb') as f:
                    data = tomllib.load(f)
                    version = data.get('project', {}).get('version', version)
        except Exception:
            pass

        try:
            stats = prompt_manager.get_stats()
            prompts_count = stats.get('total_prompts', 0) if stats else 0
        except Exception as e:
            logging.warning(f"Error calculating prompt stats: {e}")
            prompts_count = 0
        
        # Get tunnel status
        try:
            tunnel_status = get_tunnel_manager().get_status()
        except Exception as e:
            logging.warning(f"Error getting tunnel status: {e}")
            tunnel_status = {'active': False}
            
        return jsonify({
            'status': 'healthy',
            'uptime': uptime,
            'mode': mode,
            'version': version,
            'prompts_count': prompts_count,
            'tunnel_active': tunnel_status.get('active', False),
            'tunnel_url': tunnel_status.get('tunnel_url')
        })
    except Exception:
        return jsonify({'status': 'unhealthy'}), 500

@app.route('/mcp-status')
def mcp_status():
    """Status endpoint indicating MCP integration mode"""
    return jsonify({'mode': app.config.get('MODE', 'standalone')})

@app.route('/api/prompts', methods=['POST'])
def create_prompt():
    """API endpoint to create a new prompt"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        prompt_id = prompt_manager.save_prompt(data)
        return jsonify({
            'status': 'success', 
            'message': 'Prompt created successfully',
            'prompt_id': prompt_id
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/prompts/<prompt_id>', methods=['PUT'])
def update_prompt(prompt_id):
    """API endpoint to update a prompt"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400
        
        # Check if prompt exists
        if not prompt_manager.get_prompt(prompt_id):
            return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
        
        prompt_manager.save_prompt(data, prompt_id)
        return jsonify({
            'status': 'success', 
            'message': 'Prompt updated successfully'
        })
    except ValueError as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def delete_prompt(prompt_id):
    """API endpoint to delete a prompt"""
    try:
        if prompt_manager.delete_prompt(prompt_id):
            return jsonify({
                'status': 'success', 
                'message': 'Prompt deleted successfully'
            })
        else:
            return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/api/search')
def search_prompts():
    """API endpoint for searching prompts - returns HTML for HTMX"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        
        prompts = prompt_manager.search_prompts(query, category)
        
        return render_template('partials/search_results.html', 
                             prompts=prompts, 
                             query=query, 
                             count=len(prompts))
    except Exception as e:
        return '<div class="error">Search failed</div>', 500

@app.route('/api/search/json')
def search_prompts_json():
    """JSON API endpoint for searching prompts"""
    try:
        query = request.args.get('q', '')
        category = request.args.get('category')
        
        prompts = prompt_manager.search_prompts(query, category)
        
        return jsonify({
            'prompts': prompts,
            'query': query,
            'count': len(prompts)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Search failed'}), 500

@app.route('/api/preview', methods=['POST'])
def preview_content():
    """API endpoint to preview prompt content with syntax highlighting - handles both JSON and form data"""
    try:
        # Handle both JSON (for fetch requests) and form data (for HTMX)
        if request.is_json:
            data = request.get_json()
            if not data or 'content' not in data:
                return jsonify({'status': 'error', 'message': 'No content provided'}), 400
            content = data['content']
            return_json = True
        else:
            # Handle form data from HTMX
            content = request.form.get('content', '')
            return_json = False
        
        if not content.strip():
            if return_json:
                return jsonify({'status': 'success', 'html': '<div class="preview-placeholder"><div class="placeholder-icon">👁️</div><p>Start typing to see a live preview...</p></div>'})
            else:
                return '<div class="preview-placeholder"><div class="placeholder-icon">👁️</div><p>Start typing to see a live preview...</p></div>'
        
        # Convert markdown to HTML
        html_content = markdown.markdown(
            content, 
            extensions=['codehilite', 'fenced_code', 'tables']
        )
        
        # Highlight template variables
        import re
        html_content = re.sub(
            r'\{\{([^}]+)\}\}',
            r'<span class="template-var">{{\1}}</span>',
            html_content
        )
        
        if return_json:
            return jsonify({
                'status': 'success',
                'html': html_content
            })
        else:
            # Return HTML directly for HTMX
            return html_content
            
    except Exception as e:
        if return_json:
            return jsonify({'status': 'error', 'message': 'Preview generation failed'}), 500
        else:
            return '<div class="preview-error">Preview generation failed</div>', 500

@app.route('/api/share/<prompt_id>', methods=['POST'])
def create_share_link(prompt_id):
    """API endpoint to create a shareable link for a prompt"""
    try:
        # Verify prompt exists
        prompt = prompt_manager.get_prompt(prompt_id)
        if not prompt:
            return jsonify({'status': 'error', 'message': 'Prompt not found'}), 404
        
        # Get optional expiration from request
        data = request.get_json() or {}
        expires_in_hours = data.get('expires_in_hours')
        
        # Create share token
        token = get_share_manager().create_share_token(prompt_id, expires_in_hours)
        
        # Generate full shareable URL - use tunnel URL if available
        tunnel_url = get_tunnel_manager().get_tunnel_url()
        if tunnel_url:
            base_url = tunnel_url
        else:
            base_url = request.url_root.rstrip('/')
        share_url = f"{base_url}/share/{token}/{prompt_id}"
        
        return jsonify({
            'status': 'success',
            'share_url': share_url,
            'token': token,
            'expires_in_hours': expires_in_hours
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Failed to create share link'}), 500

@app.route('/api/tunnel/start', methods=['POST'])
def start_tunnel():
    """API endpoint to start devtunnel"""
    try:
        client_ip = request.environ.get('REMOTE_ADDR', '127.0.0.1')
        result = get_tunnel_manager().start_tunnel(client_ip)
        
        if result['status'] == 'success':
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logging.error(f"Error starting tunnel: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/tunnel/stop', methods=['POST'])
def stop_tunnel():
    """API endpoint to stop devtunnel"""
    try:
        result = get_tunnel_manager().stop_tunnel()
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error stopping tunnel: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/tunnel/status')
def get_tunnel_status():
    """API endpoint to get current tunnel status"""
    try:
        status = get_tunnel_manager().get_status()
        return jsonify({
            'status': 'success',
            'data': status
        })
        
    except Exception as e:
        logging.error(f"Error getting tunnel status: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/api/tunnel/url')
def get_tunnel_url():
    """API endpoint to get active tunnel URL"""
    try:
        tunnel_url = get_tunnel_manager().get_tunnel_url()
        return jsonify({
            'status': 'success',
            'tunnel_url': tunnel_url
        })
        
    except Exception as e:
        logging.error(f"Error getting tunnel URL: {e}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

@app.route('/share/<token>/<prompt_id>')
def view_shared_prompt(token, prompt_id):
    """Public view for shared prompts"""
    try:
        # Validate share token
        validated_prompt_id = get_share_manager().validate_share_token(token)
        
        if not validated_prompt_id or validated_prompt_id != prompt_id:
            return render_template('404.html'), 404
        
        # Get the prompt
        prompt = prompt_manager.get_prompt(prompt_id)
        if not prompt:
            return render_template('404.html'), 404
        
        # Get share info for analytics
        share_info = get_share_manager().get_share_info(token)
        
        return render_template('share.html', 
                             prompt=prompt, 
                             share_info=share_info,
                             is_shared_view=True)
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error in view_shared_prompt: {e}")
        import traceback
        traceback.print_exc()
        return render_template('500.html'), 500

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

def parse_args():
    parser = argparse.ArgumentParser(description='Run PromptBin Flask app')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=5001)
    parser.add_argument('--mode', choices=['standalone', 'mcp-managed'], default='standalone')
    parser.add_argument('--log-level', default=os.environ.get('PROMPTBIN_LOG_LEVEL', 'INFO'))
    parser.add_argument('--data-dir', default=os.path.expanduser('~/promptbin-data'))
    return parser.parse_args()


def main():
    """Main entry point for the application"""
    args = parse_args()

    # Configure logging
    logging.basicConfig(level=getattr(logging, str(args.log_level).upper(), logging.INFO))

    # Reinitialize prompt manager with the parsed data directory
    global prompt_manager
    prompt_manager = PromptManager(data_dir=args.data_dir)
    
    # Reinitialize share manager with the parsed data directory
    global share_manager
    share_file = os.path.join(args.data_dir, 'shares.json')
    share_manager = ShareManager(share_file=share_file)
    
    # Initialize tunnel manager with the correct Flask port
    global tunnel_manager
    tunnel_manager = TunnelManager(flask_port=args.port)

    # Apply mode and start time
    app.config['MODE'] = args.mode
    app.config['START_TIME'] = time.time()

    # Debug mode only for standalone
    debug = args.mode != 'mcp-managed'

    app.run(host=args.host, port=args.port, debug=debug)


if __name__ == '__main__':
    main()
