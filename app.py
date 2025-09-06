from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
from dotenv import load_dotenv
from prompt_manager import PromptManager
import markdown

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize the prompt manager
prompt_manager = PromptManager()

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

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)