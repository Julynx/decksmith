import os
import io
import shutil
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from typing import Dict, Any

import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
from ruamel.yaml import YAML

from decksmith.deck_builder import DeckBuilder
from decksmith.card_builder import CardBuilder
from decksmith.export import PdfExporter
from decksmith.logger import logger

app = Flask(__name__)

# Configuration
# Use the current working directory as the workspace
PROJECT_STATE = {
    'working_dir': None
}


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/project/current', methods=['GET'])
def get_current_project():
    wd = PROJECT_STATE['working_dir']
    return jsonify({'path': str(wd) if wd else None})


@app.route('/api/system/browse', methods=['POST'])
def browse_folder():
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        folder_path = filedialog.askdirectory()
        root.destroy()
        if folder_path:
            return jsonify({'path': folder_path})
        return jsonify({'path': None})
    except Exception as e:
        logger.error(f"Error browsing folder: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/project/select', methods=['POST'])
def select_project():
    path_str = request.json.get('path')
    if not path_str:
        return jsonify({'error': 'Path is required'}), 400
    
    path = Path(path_str)
    if not path.exists() or not path.is_dir():
        return jsonify({'error': 'Directory does not exist'}), 400
        
    PROJECT_STATE['working_dir'] = path
    return jsonify({'status': 'success', 'path': str(path)})


@app.route('/api/project/close', methods=['POST'])
def close_project():
    PROJECT_STATE['working_dir'] = None
    return jsonify({'status': 'success'})


@app.route('/api/project/create', methods=['POST'])
def create_project():
    path_str = request.json.get('path')
    if not path_str:
        return jsonify({'error': 'Path is required'}), 400
        
    path = Path(path_str)
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        
        # Copy templates
        template_dir = Path(__file__).parent.parent / 'templates'
        
        if not (path / 'deck.yaml').exists():
            shutil.copy(template_dir / 'deck.yaml', path / 'deck.yaml')
            
        if not (path / 'deck.csv').exists():
            shutil.copy(template_dir / 'deck.csv', path / 'deck.csv')
            
        PROJECT_STATE['working_dir'] = path
        return jsonify({'status': 'success', 'path': str(path)})
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/load', methods=['GET'])
def load_files():
    working_dir = PROJECT_STATE['working_dir']
    if working_dir is None:
        return jsonify({'yaml': '', 'csv': ''})

    yaml_path = working_dir / 'deck.yaml'
    csv_path = working_dir / 'deck.csv'
    
    # Define template paths
    template_dir = Path(__file__).parent.parent / 'templates'
    yaml_template = template_dir / 'deck.yaml'
    csv_template = template_dir / 'deck.csv'
    
    data = {}
    
    # Load YAML
    if yaml_path.exists() and yaml_path.stat().st_size > 0:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data['yaml'] = f.read()
    elif yaml_template.exists():
        with open(yaml_template, 'r', encoding='utf-8') as f:
            data['yaml'] = f.read()
    else:
        data['yaml'] = ''
        
    # Load CSV
    if csv_path.exists() and csv_path.stat().st_size > 0:
        with open(csv_path, 'r', encoding='utf-8') as f:
            data['csv'] = f.read()
    elif csv_template.exists():
        with open(csv_template, 'r', encoding='utf-8') as f:
            data['csv'] = f.read()
    else:
        data['csv'] = ''
        
    return jsonify(data)


@app.route('/api/save', methods=['POST'])
def save_files():
    working_dir = PROJECT_STATE['working_dir']
    if working_dir is None:
        return jsonify({'error': 'No project selected'}), 400

    data = request.json
    yaml_content = data.get('yaml')
    csv_content = data.get('csv')
    
    try:
        if yaml_content is not None:
            with open(working_dir / 'deck.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_content.replace('\r\n', '\n'))
                
        if csv_content is not None:
            with open(working_dir / 'deck.csv', 'w', encoding='utf-8') as f:
                f.write(csv_content.replace('\r\n', '\n'))
                
        return jsonify({'status': 'success'})
    except Exception as e:
        logger.error(f"Error saving files: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cards', methods=['GET'])
def list_cards():
    working_dir = PROJECT_STATE['working_dir']
    if working_dir is None:
        return jsonify([])

    csv_path = working_dir / 'deck.csv'
    if not csv_path.exists():
        return jsonify([])
        
    try:
        df = pd.read_csv(csv_path, sep=';')
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        logger.error(f"Error listing cards: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/api/preview/<int:index>', methods=['POST'])
def preview_card(index):
    working_dir = PROJECT_STATE['working_dir']
    # Allow preview even without project, but base_path will be None
    
    data = request.json
    yaml_content = data.get('yaml')
    csv_content = data.get('csv')
    
    try:
        yaml = YAML()
        spec = yaml.load(yaml_content)
    except Exception as e:
        return jsonify({'error': f"Invalid YAML: {e}"}), 400

    try:
        from io import StringIO
        df = pd.read_csv(StringIO(csv_content), sep=';')
        if index < 0 or index >= len(df):
             return jsonify({'error': "Index out of bounds"}), 400
        row = df.iloc[index]
    except Exception as e:
        return jsonify({'error': f"Invalid CSV: {e}"}), 400

    try:
        row_dict = row.to_dict()
        resolved_spec = DeckBuilder.resolve_macros(spec, row_dict)
        
        builder = CardBuilder(resolved_spec, base_path=working_dir)
        card_image = builder.render()
                
        img_io = io.BytesIO()
        card_image.save(img_io, 'PNG')
        img_io.seek(0)
        return send_file(img_io, mimetype='image/png')
        
    except Exception as e:
        logger.error(f"Error previewing card: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/build', methods=['POST'])
def build_deck():
    working_dir = PROJECT_STATE['working_dir']
    if working_dir is None:
        return jsonify({'error': 'No project selected'}), 400

    # Save current state first
    data = request.json
    # We can reuse the save_files logic but we need to extract it or call it
    # For simplicity, let's just save here
    yaml_content = data.get('yaml')
    csv_content = data.get('csv')
    
    try:
        if yaml_content is not None:
            with open(working_dir / 'deck.yaml', 'w', encoding='utf-8') as f:
                f.write(yaml_content.replace('\r\n', '\n'))
        if csv_content is not None:
            with open(working_dir / 'deck.csv', 'w', encoding='utf-8') as f:
                f.write(csv_content.replace('\r\n', '\n'))

        yaml_path = working_dir / 'deck.yaml'
        csv_path = working_dir / 'deck.csv'
        output_path = working_dir / 'output'
        output_path.mkdir(exist_ok=True)
        
        builder = DeckBuilder(yaml_path, csv_path)
        builder.build_deck(output_path)
        
        return jsonify({'status': 'success', 'message': f'Deck built in {output_path}'})
    except Exception as e:
        logger.error(f"Error building deck: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_pdf():
    working_dir = PROJECT_STATE['working_dir']
    if working_dir is None:
        return jsonify({'error': 'No project selected'}), 400

    try:
        image_folder = working_dir / 'output'
        output_pdf = working_dir / 'deck.pdf'
        
        if not image_folder.exists():
             return jsonify({'error': 'Output folder does not exist. Build deck first.'}), 400
             
        exporter = PdfExporter(image_folder, output_pdf)
        exporter.export()
        
        return jsonify({'status': 'success', 'message': f'PDF exported to {output_pdf}'})
    except Exception as e:
        logger.error(f"Error exporting PDF: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
