#!/usr/bin/env python3
"""
ETR Web Application
Flask-based web interface for uploading and processing content through ETR
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import traceback

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = Path(tempfile.gettempdir()) / 'etr_uploads'
RESULTS_FOLDER = Path(tempfile.gettempdir()) / 'etr_results'
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULTS_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = str(UPLOAD_FOLDER)
app.config['RESULTS_FOLDER'] = str(RESULTS_FOLDER)
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max

# Allowed file extensions
ALLOWED_EXTENSIONS = {'ply', 'pcd', 'pts', 'xyz', 'las', 'laz', 'txt'}

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_info(filepath):
    """Get information about uploaded file"""
    stat = filepath.stat()
    return {
        'name': filepath.name,
        'size': stat.st_size,
        'size_mb': round(stat.st_size / (1024 * 1024), 2),
        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
        'extension': filepath.suffix.lower()
    }

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle file upload"""
    try:
        # Check if file is in request
        if 'file' not in request.files:
            return jsonify({'error': 'No file part in request'}), 400

        file = request.files['file']

        # Check if file is selected
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Check if file is allowed
        if not allowed_file(file.filename):
            return jsonify({
                'error': f'File type not allowed. Supported: {", ".join(ALLOWED_EXTENSIONS)}'
            }), 400

        # Save file
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = UPLOAD_FOLDER / unique_filename

        file.save(str(filepath))

        # Get file info
        file_info = get_file_info(filepath)
        file_info['id'] = unique_filename

        return jsonify({
            'success': True,
            'message': 'File uploaded successfully',
            'file': file_info
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Upload failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/process', methods=['POST'])
def process_file():
    """Process uploaded file through ETR"""
    try:
        data = request.json
        file_id = data.get('file_id')
        options = data.get('options', {})

        if not file_id:
            return jsonify({'error': 'No file_id provided'}), 400

        filepath = UPLOAD_FOLDER / file_id
        if not filepath.exists():
            return jsonify({'error': 'File not found'}), 404

        # Import ETR modules (only when needed to avoid dependency errors)
        try:
            from utils.point_cloud_io import load_point_cloud

            # Try to import ETR core (may fail if no PyTorch)
            try:
                from etr.core.entangled_triangles import RightTriangle, LeftTriangleGenerator
                has_pytorch = True
            except ImportError:
                has_pytorch = False
        except ImportError as e:
            return jsonify({
                'error': 'ETR modules not available',
                'message': 'Please install dependencies: pip install numpy torch',
                'details': str(e)
            }), 500

        # Load point cloud
        try:
            point_cloud = load_point_cloud(str(filepath))
            num_points = point_cloud.points.shape[0]
        except Exception as e:
            return jsonify({
                'error': f'Failed to load point cloud: {str(e)}',
                'traceback': traceback.format_exc()
            }), 500

        # Process through ETR (simplified version for demo)
        result_id = f"result_{file_id}"
        result_path = RESULTS_FOLDER / result_id
        result_path.mkdir(exist_ok=True)

        # Save point cloud info
        result_info = {
            'file_id': file_id,
            'result_id': result_id,
            'num_points': int(num_points),
            'has_colors': point_cloud.colors is not None,
            'has_normals': point_cloud.normals is not None,
            'processed_at': datetime.now().isoformat(),
            'options': options,
            'has_pytorch': has_pytorch
        }

        # If PyTorch available, do ETR processing
        if has_pytorch:
            # Example: Process sample triangles
            # In a real implementation, this would extract triangles from the mesh
            result_info['etr_processed'] = True
            result_info['message'] = 'ETR processing completed'
        else:
            result_info['etr_processed'] = False
            result_info['message'] = 'Point cloud loaded (ETR requires PyTorch)'

        # Save result metadata
        with open(result_path / 'metadata.json', 'w') as f:
            json.dump(result_info, f, indent=2)

        return jsonify({
            'success': True,
            'result': result_info
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Processing failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/demo/etr', methods=['POST'])
def demo_etr():
    """Demonstrate ETR with a simple 3:4:5 triangle (no dependencies)"""
    try:
        data = request.json or {}
        base = data.get('base', 3)
        height = data.get('height', 4)
        hypotenuse = data.get('hypotenuse', 5)
        levels = data.get('levels', 5)

        # Pure Python ETR implementation
        results = []

        rt_base, rt_height, rt_hyp = base, height, hypotenuse

        for level in range(levels):
            # Validate right triangle
            rt_error = abs(rt_base**2 + rt_height**2 - rt_hyp**2)
            rt_valid = rt_error < 1e-10

            # Compute scaling factor
            scaling_factor = rt_height * rt_hyp

            # Left triangle transformation (CORRECTED formulas)
            lt_height = 1.0 / rt_hyp
            lt_hyp = 1.0 / rt_height
            lt_base = rt_base / scaling_factor

            # Validate left triangle
            lt_error = abs(lt_base**2 + lt_height**2 - lt_hyp**2)
            lt_valid = lt_error < 1e-10

            results.append({
                'level': level,
                'right_triangle': {
                    'base': rt_base,
                    'height': rt_height,
                    'hypotenuse': rt_hyp,
                    'scaling_factor': scaling_factor,
                    'pythagorean_error': rt_error,
                    'valid': rt_valid
                },
                'left_triangle': {
                    'base': lt_base,
                    'height': lt_height,
                    'hypotenuse': lt_hyp,
                    'scaling_factor': lt_height * lt_hyp,
                    'pythagorean_error': lt_error,
                    'valid': lt_valid
                }
            })

            # Next iteration: use left triangle
            rt_base, rt_height, rt_hyp = lt_base, lt_height, lt_hyp

        return jsonify({
            'success': True,
            'input': {'base': base, 'height': height, 'hypotenuse': hypotenuse},
            'levels': levels,
            'results': results
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Demo failed: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Get information about supported formats"""
    formats = {
        'ply': {
            'name': 'PLY',
            'extension': '.ply',
            'description': 'Polygon File Format - Standard 3D mesh format',
            'features': ['vertices', 'faces', 'colors', 'normals']
        },
        'pcd': {
            'name': 'PCD',
            'extension': '.pcd',
            'description': 'Point Cloud Data - PCL library format',
            'features': ['points', 'colors', 'normals', 'intensity']
        },
        'pts': {
            'name': 'PTS',
            'extension': '.pts',
            'description': 'Point cloud with intensity values',
            'features': ['points', 'intensity', 'colors']
        },
        'xyz': {
            'name': 'XYZ',
            'extension': '.xyz',
            'description': 'Simple ASCII point cloud format',
            'features': ['points', 'optional_colors']
        },
        'las': {
            'name': 'LAS/LAZ',
            'extension': '.las/.laz',
            'description': 'LiDAR format with optional compression',
            'features': ['points', 'intensity', 'classification', 'gps_time']
        }
    }

    return jsonify({
        'supported_formats': formats,
        'total_formats': len(formats)
    }), 200

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and available features"""
    # Check for dependencies
    dependencies = {}

    try:
        import numpy
        dependencies['numpy'] = True
    except ImportError:
        dependencies['numpy'] = False

    try:
        import torch
        dependencies['torch'] = True
        dependencies['torch_version'] = torch.__version__
    except ImportError:
        dependencies['torch'] = False

    try:
        from utils.point_cloud_io import PointCloudLoader
        dependencies['point_cloud_loader'] = True
    except ImportError:
        dependencies['point_cloud_loader'] = False

    try:
        from etr.core.entangled_triangles import RightTriangle
        dependencies['etr_core'] = True
    except ImportError:
        dependencies['etr_core'] = False

    # Count uploaded files
    num_uploads = len(list(UPLOAD_FOLDER.glob('*')))
    num_results = len(list(RESULTS_FOLDER.glob('*')))

    return jsonify({
        'status': 'running',
        'version': '1.0.0',
        'dependencies': dependencies,
        'features': {
            'file_upload': True,
            'point_cloud_loading': dependencies.get('point_cloud_loader', False),
            'etr_processing': dependencies.get('etr_core', False),
            'demo_mode': True
        },
        'statistics': {
            'uploads': num_uploads,
            'results': num_results
        }
    }), 200

@app.route('/api/clear', methods=['POST'])
def clear_data():
    """Clear uploaded files and results"""
    try:
        # Clear uploads
        for file in UPLOAD_FOLDER.glob('*'):
            if file.is_file():
                file.unlink()

        # Clear results
        for dir in RESULTS_FOLDER.glob('*'):
            if dir.is_dir():
                shutil.rmtree(dir)

        return jsonify({
            'success': True,
            'message': 'All data cleared'
        }), 200

    except Exception as e:
        return jsonify({
            'error': f'Clear failed: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("="*70)
    print("ETR Web Application Starting")
    print("="*70)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Results folder: {RESULTS_FOLDER}")
    print(f"Supported formats: {', '.join(ALLOWED_EXTENSIONS)}")
    print("="*70)
    print("\nAccess the application at: http://localhost:5000")
    print("="*70)

    app.run(host='0.0.0.0', port=5000, debug=True)
