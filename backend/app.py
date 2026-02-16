"""
Access to MySQL Converter - Flask Backend
Production-ready API server for converting Access databases to MySQL
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import sys
import json
import logging
from datetime import datetime
import traceback
from pathlib import Path

# Import custom modules
from database_handler import DatabaseHandler
from config_manager import ConfigManager
from data_exporter import DataExporter
from job_manager import ExportJobManager

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Detect if running as PyInstaller bundle
is_bundled = getattr(sys, 'frozen', False)
if is_bundled:
    base_path = sys._MEIPASS  # PyInstaller temp directory
else:
    base_path = os.path.dirname(os.path.dirname(__file__))  # Project root

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 1000 * 1024 * 1024  # 100MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(base_path, 'data', 'uploads')
app.config['CONFIG_FOLDER'] = os.path.join(base_path, 'configs')
app.config['LOG_FOLDER'] = os.path.join(base_path, 'logs')
app.config['FRONTEND_FOLDER'] = os.path.join(base_path, 'frontend')
app.config['ALLOWED_EXTENSIONS'] = {'accdb', 'mdb'}

# Create necessary directories
for folder in [app.config['UPLOAD_FOLDER'], app.config['CONFIG_FOLDER'], app.config['LOG_FOLDER']]:
    os.makedirs(folder, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(app.config['LOG_FOLDER'], 'app.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Log startup info
logger.info(f"Starting Access to MySQL Converter")
logger.info(f"Running as bundle: {is_bundled}")
logger.info(f"Base path: {base_path}")
logger.info(f"Frontend folder: {app.config['FRONTEND_FOLDER']}")
if not os.path.exists(app.config['FRONTEND_FOLDER']):
    logger.warning(f"Frontend folder not found: {app.config['FRONTEND_FOLDER']}")


# Session storage for database connections
active_sessions = {}

# Initialize managers
db_handler = DatabaseHandler()
config_manager = ConfigManager(app.config['CONFIG_FOLDER'])
data_exporter = DataExporter()
job_manager = ExportJobManager(db_handler, data_exporter, active_sessions)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET'])
def index():
    """Serve the frontend index.html"""
    try:
        index_path = os.path.join(app.config['FRONTEND_FOLDER'], 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error serving index.html: {e}")
        return jsonify({'error': 'Frontend not found'}), 404


@app.route('/app.js', methods=['GET'])
def serve_app_js():
    """Serve the frontend app.js"""
    try:
        js_path = os.path.join(app.config['FRONTEND_FOLDER'], 'app.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'application/javascript'}
    except Exception as e:
        logger.error(f"Error serving app.js: {e}")
        return jsonify({'error': 'JavaScript not found'}), 404


@app.route('/styles.css', methods=['GET'])
def serve_styles():
    """Serve the frontend styles.css"""
    try:
        css_path = os.path.join(app.config['FRONTEND_FOLDER'], 'styles.css')
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read(), 200, {'Content-Type': 'text/css'}
        else:
            # styles are inline in index.html, return empty
            return '', 200, {'Content-Type': 'text/css'}
    except Exception as e:
        logger.error(f"Error serving styles.css: {e}")
        return '', 404



@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })


@app.route('/api/upload-access', methods=['POST'])
def upload_access_file():
    """Upload Access database file"""
    try:
        # Allow optional session_id in form data so we can clean previous uploads
        session_id = request.form.get('session_id') if request.form else None

        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Only .accdb and .mdb files are allowed'}), 400
        
        # If session provided and prior upload exists, remove it
        if session_id and session_id in active_sessions:
            prev_path = active_sessions[session_id].get('access_filepath')
            if prev_path and os.path.exists(prev_path):
                try:
                    os.remove(prev_path)
                    logger.info(f"Removed previous upload for session {session_id}: {prev_path}")
                except Exception as ex:
                    logger.warning(f"Failed to remove previous upload {prev_path}: {ex}")

        # Secure filename and save
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        file.save(filepath)
        
        logger.info(f"Access file uploaded: {unique_filename}")

        # Store the uploaded filepath in session if provided
        if session_id:
            if session_id not in active_sessions:
                active_sessions[session_id] = {}
            active_sessions[session_id]['access_filepath'] = filepath
        
        return jsonify({
            'success': True,
            'filename': unique_filename,
            'filepath': filepath,
            'original_name': file.filename,
            'size': os.path.getsize(filepath)
        })
        
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/connect-access', methods=['POST'])
def connect_access():
    """Connect to Access database and retrieve metadata"""
    try:
        data = request.json
        filename = data.get('filename')
        session_id = data.get('session_id', 'default')
        
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not filepath or not os.path.exists(filepath):
            return jsonify({'error': 'Invalid file path'}), 400
        
        # Connect to Access database
        connection = db_handler.connect_access(filepath)
        
        if not connection:
            return jsonify({'error': 'Failed to connect to Access database'}), 500
        
        # Get table list
        tables = db_handler.get_access_tables(connection)
        
        # Store connection in session
        if session_id not in active_sessions:
            active_sessions[session_id] = {}
        
        active_sessions[session_id]['access_connection'] = connection
        active_sessions[session_id]['access_filepath'] = filepath
        active_sessions[session_id]['access_tables'] = tables
        
        logger.info(f"Connected to Access database: {filepath}, found {len(tables)} tables")
        
        return jsonify({
            'success': True,
            'tables': tables,
            'table_count': len(tables),
            'filepath': filepath
        })
        
    except Exception as e:
        logger.error(f"Error connecting to Access: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/connect-mysql', methods=['POST'])
def connect_mysql():
    """Connect to MySQL database"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        mysql_config = {
            'host': data.get('host', 'localhost'),
            'port': int(data.get('port', 3306)),
            'user': data.get('user', 'root'),
            'password': data.get('password', ''),
            'database': data.get('database')
        }
        
        # Validate required fields
        if not mysql_config['database']:
            return jsonify({'error': 'Database name is required'}), 400
        
        # Connect to MySQL
        connection = db_handler.connect_mysql(mysql_config)
        
        if not connection:
            return jsonify({'error': 'Failed to connect to MySQL database'}), 500
        
        # Store connection in session
        if session_id not in active_sessions:
            active_sessions[session_id] = {}
        
        active_sessions[session_id]['mysql_connection'] = connection
        active_sessions[session_id]['mysql_config'] = mysql_config
        
        # Get existing tables in MySQL
        mysql_tables = db_handler.get_mysql_tables(connection)
        
        logger.info(f"Connected to MySQL database: {mysql_config['database']}")
        
        return jsonify({
            'success': True,
            'database': mysql_config['database'],
            'existing_tables': mysql_tables,
            'table_count': len(mysql_tables)
        })
        
    except Exception as e:
        logger.error(f"Error connecting to MySQL: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-table-info', methods=['POST'])
def get_table_info():
    """Get detailed information about a specific Access table"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        table_name = data.get('table_name')
        
        if session_id not in active_sessions or 'access_connection' not in active_sessions[session_id]:
            return jsonify({'error': 'No active Access connection'}), 400
        
        connection = active_sessions[session_id]['access_connection']
        
        # Get table schema and row count
        schema = db_handler.get_table_schema(connection, table_name)
        row_count = db_handler.get_table_row_count(connection, table_name)
        
        return jsonify({
            'success': True,
            'table_name': table_name,
            'schema': schema,
            'row_count': row_count
        })
        
    except Exception as e:
        logger.error(f"Error getting table info: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/preview-table', methods=['POST'])
def preview_table():
    """Preview data from a table"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        table_name = data.get('table_name')
        source = data.get('source', 'access')  # 'access' or 'mysql'
        limit = int(data.get('limit', 100))
        
        if session_id not in active_sessions:
            return jsonify({'error': 'No active session'}), 400
        
        if source == 'access':
            if 'access_connection' not in active_sessions[session_id]:
                return jsonify({'error': 'No active Access connection'}), 400
            connection = active_sessions[session_id]['access_connection']
        else:
            if 'mysql_connection' not in active_sessions[session_id]:
                return jsonify({'error': 'No active MySQL connection'}), 400
            connection = active_sessions[session_id]['mysql_connection']
        
        # Get preview data
        preview_data = db_handler.get_table_preview(connection, table_name, limit, source)
        
        return jsonify({
            'success': True,
            'table_name': table_name,
            'data': preview_data
        })
        
    except Exception as e:
        logger.error(f"Error previewing table: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export', methods=['POST'])
def export_data():
    """Export selected tables from Access to MySQL"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        tables = data.get('tables', [])
        options = data.get('options', {})
        
        if session_id not in active_sessions:
            return jsonify({'error': 'No active session'}), 400
        
        if 'access_connection' not in active_sessions[session_id]:
            return jsonify({'error': 'No active Access connection'}), 400
        
        if 'mysql_connection' not in active_sessions[session_id]:
            return jsonify({'error': 'No active MySQL connection'}), 400
        
        if not tables:
            return jsonify({'error': 'No tables selected for export'}), 400
        
        access_conn = active_sessions[session_id]['access_connection']
        mysql_conn = active_sessions[session_id]['mysql_connection']
        
        # Export options
        override_data = options.get('override_data', True)
        create_tables = options.get('create_tables', True)
        batch_size = options.get('batch_size', 1000)
        
        # Start export as background job (non-blocking)
        job_id = job_manager.start_export(session_id, tables, {
            'override_data': override_data,
            'create_tables': create_tables,
            'batch_size': batch_size
        })

        return jsonify({
            'success': True,
            'job_id': job_id,
            'message': 'Export started in background'
        })
        
    except Exception as e:
        logger.error(f"Error during export: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-status', methods=['GET'])
def export_status():
    """Get status of the current export job"""
    try:
        status = job_manager.get_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting export status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/export-cancel', methods=['POST'])
def export_cancel():
    """Request cancellation of the running export job"""
    try:
        job_manager.request_cancel()
        return jsonify({'success': True, 'message': 'Cancel requested'})
    except Exception as e:
        logger.error(f"Error requesting cancel: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/purge-uploads', methods=['POST'])
def purge_uploads():
    """Purge all uploaded files from the uploads folder"""
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        removed = []
        errors = []

        for fname in os.listdir(upload_folder):
            path = os.path.join(upload_folder, fname)
            if os.path.isfile(path):
                try:
                    os.remove(path)
                    removed.append(fname)
                except Exception as ex:
                    errors.append({'file': fname, 'error': str(ex)})

        logger.info(f"Purged {len(removed)} uploaded files")

        return jsonify({
            'success': True,
            'removed_count': len(removed),
            'removed': removed,
            'errors': errors
        })

    except Exception as e:
        logger.exception('Error purging uploads')
        return jsonify({'error': str(e)}), 500


@app.route('/api/save-config', methods=['POST'])
def save_config():
    """Save export configuration"""
    try:
        data = request.json
        config_name = data.get('config_name')
        config_data = data.get('config_data')
        
        if not config_name or not config_data:
            return jsonify({'error': 'Config name and data are required'}), 400
        
        # Add timestamp
        config_data['created_at'] = datetime.now().isoformat()
        config_data['updated_at'] = datetime.now().isoformat()
        
        # Save configuration
        config_id = config_manager.save_config(config_name, config_data)
        
        logger.info(f"Configuration saved: {config_name}")
        
        return jsonify({
            'success': True,
            'config_id': config_id,
            'config_name': config_name
        })
        
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/load-config/<config_id>', methods=['GET'])
def load_config(config_id):
    """Load a saved configuration"""
    try:
        config_data = config_manager.load_config(config_id)
        
        if not config_data:
            return jsonify({'error': 'Configuration not found'}), 404
        
        return jsonify({
            'success': True,
            'config': config_data
        })
        
    except Exception as e:
        logger.error(f"Error loading config: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/list-configs', methods=['GET'])
def list_configs():
    """List all saved configurations"""
    try:
        configs = config_manager.list_configs()
        
        return jsonify({
            'success': True,
            'configs': configs,
            'count': len(configs)
        })
        
    except Exception as e:
        logger.error(f"Error listing configs: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete-config/<config_id>', methods=['DELETE'])
def delete_config(config_id):
    """Delete a saved configuration"""
    try:
        success = config_manager.delete_config(config_id)
        
        if not success:
            return jsonify({'error': 'Configuration not found'}), 404
        
        logger.info(f"Configuration deleted: {config_id}")
        
        return jsonify({
            'success': True,
            'message': 'Configuration deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting config: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/get-mysql-tables', methods=['POST'])
def get_mysql_tables():
    """Get list of tables in MySQL database"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id not in active_sessions or 'mysql_connection' not in active_sessions[session_id]:
            return jsonify({'error': 'No active MySQL connection'}), 400
        
        connection = active_sessions[session_id]['mysql_connection']
        tables = db_handler.get_mysql_tables(connection)
        
        return jsonify({
            'success': True,
            'tables': tables,
            'count': len(tables)
        })
        
    except Exception as e:
        logger.error(f"Error getting MySQL tables: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/disconnect', methods=['POST'])
def disconnect():
    """Disconnect from databases"""
    try:
        data = request.json
        session_id = data.get('session_id', 'default')
        
        if session_id in active_sessions:
            # Close connections
            if 'access_connection' in active_sessions[session_id]:
                db_handler.close_connection(active_sessions[session_id]['access_connection'])
            
            if 'mysql_connection' in active_sessions[session_id]:
                db_handler.close_connection(active_sessions[session_id]['mysql_connection'])
            
            # Remove session
            del active_sessions[session_id]
        
        logger.info(f"Session disconnected: {session_id}")
        
        return jsonify({
            'success': True,
            'message': 'Disconnected successfully'
        })
        
    except Exception as e:
        logger.error(f"Error disconnecting: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 100MB'}), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
