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
    """API endpoint for searching prompts"""
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
    """API endpoint to preview prompt content with syntax highlighting"""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({'status': 'error', 'message': 'No content provided'}), 400
        
        content = data['content']
        
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
        
        return jsonify({
            'status': 'success',
            'html': html_content
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Preview generation failed'}), 500

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