# Project Structure

```
access-to-mysql-converter/
├── backend/                          # Python Flask backend
│   ├── app.py                       # Main Flask application with API endpoints
│   ├── database_handler.py          # Database connection and operations handler
│   ├── data_exporter.py             # Data export logic and batch processing
│   ├── config_manager.py            # Configuration file management
│   ├── requirements.txt             # Python dependencies
│   ├── .env.example                 # Environment variables template
│   └── .env                         # Environment variables (not in git)
│
├── frontend/                         # Frontend web interface
│   ├── index.html                   # Main HTML interface
│   └── app.js                       # JavaScript application logic
│
├── data/                            # Data storage
│   └── uploads/                     # Uploaded Access database files
│       └── .gitkeep                 # Git placeholder
│
├── configs/                         # Saved export configurations
│   └── .gitkeep                     # Git placeholder
│
├── logs/                            # Application logs
│   └── app.log                      # Main application log (auto-generated)
│
├── Dockerfile                       # Docker container definition
├── docker-compose.yml               # Docker Compose configuration
├── nginx.conf                       # Nginx reverse proxy configuration
│
├── install.sh                       # Linux/Mac installation script
├── install.bat                      # Windows installation script
├── test_system.py                   # System test and verification script
│
├── README.md                        # Comprehensive documentation
├── QUICKSTART.md                    # Quick start guide
├── .gitignore                       # Git ignore rules
│
└── LICENSE                          # MIT License (optional)
```

## File Descriptions

### Backend Files

**app.py**
- Main Flask application
- Defines all API endpoints
- Handles HTTP requests and responses
- Manages sessions and connections
- Error handling and logging

**database_handler.py**
- Access database connectivity via PyODBC
- MySQL database connectivity via PyMySQL
- Table schema extraction
- Data preview functionality
- Connection management

**data_exporter.py**
- Table export orchestration
- Batch data processing
- Data type conversion (Access → MySQL)
- Table creation in MySQL
- Progress tracking and reporting

**config_manager.py**
- Save/load export configurations
- Configuration file management (JSON)
- Import/export configuration files
- Configuration listing and deletion

**requirements.txt**
- Flask and Flask-CORS
- PyODBC for Access
- PyMySQL for MySQL
- Pandas for data processing
- Additional dependencies

### Frontend Files

**index.html**
- Modern, responsive user interface
- Connection management sections
- Table selection interface
- Export configuration options
- Progress tracking display
- Data preview tables
- Configuration management UI

**app.js**
- API communication layer
- State management
- Event handlers
- UI updates and rendering
- Progress tracking
- Error handling

### Configuration Files

**Dockerfile**
- Container image definition
- System dependencies
- Python environment setup
- Application configuration

**docker-compose.yml**
- Multi-container orchestration
- Backend service
- MySQL service
- Nginx service (optional)
- Volume and network configuration

**nginx.conf**
- Reverse proxy configuration
- Static file serving
- API routing
- Upload size limits

### Installation Files

**install.sh** (Linux/Mac)
- Automated installation
- Dependency checking
- Directory creation
- Configuration setup

**install.bat** (Windows)
- Windows installation script
- Dependency verification
- Directory structure setup

**test_system.py**
- System verification
- Dependency testing
- Module import testing
- Directory structure validation

### Documentation Files

**README.md**
- Complete documentation
- Installation instructions
- Usage guide
- API documentation
- Troubleshooting
- Production deployment guide

**QUICKSTART.md**
- Quick start guide
- Essential steps only
- Common issues
- Basic troubleshooting

## Data Flow

```
User Interface (HTML/JS)
        ↓
    Frontend (app.js)
        ↓
    API Endpoints (Flask)
        ↓
    ┌─────────────┬──────────────┐
    ↓             ↓              ↓
Database     Data         Config
Handler      Exporter     Manager
    ↓             ↓              ↓
Access DB    MySQL DB     JSON Files
```

## API Flow

1. **Upload Access File**: POST /api/upload-access
2. **Connect to Access**: POST /api/connect-access
3. **Connect to MySQL**: POST /api/connect-mysql
4. **Load Tables**: Automatic after connection
5. **Preview Data**: POST /api/preview-table
6. **Export Data**: POST /api/export
7. **Save Config**: POST /api/save-config
8. **Load Config**: GET /api/load-config/<id>

## Database Schema

### Access Database
- Read-only connection
- Schema extraction
- Batch data reading
- No modifications

### MySQL Database
- Write connection
- Table creation (if needed)
- Data insertion
- Table truncation (if override)

## Security Considerations

1. **File Uploads**: 
   - Sanitized filenames
   - Type validation (.accdb, .mdb only)
   - Size limits (100MB default)

2. **Database Connections**:
   - Session-based isolation
   - No credential storage
   - Connection cleanup

3. **API Security**:
   - CORS configuration
   - Input validation
   - Error message sanitization

4. **File Storage**:
   - Timestamped unique filenames
   - Separate upload directory
   - Configurable cleanup

## Production Deployment

### Standalone
- Gunicorn WSGI server
- Nginx reverse proxy
- SSL/TLS certificates
- Systemd service

### Docker
- Multi-container setup
- Docker Compose orchestration
- Volume persistence
- Network isolation

### Cloud Deployment
- AWS/Azure/GCP compatible
- Environment variable configuration
- Scalable architecture
- Load balancer ready

## Maintenance

### Logs
- Application logs: `logs/app.log`
- Rotation recommended
- Error tracking
- Audit trail

### Backups
- Configuration files: `configs/`
- Upload cleanup policy
- Database backups separate

### Updates
- Backend: `pip install -r requirements.txt --upgrade`
- Frontend: Manual update
- Database drivers: OS-specific

## Performance Optimization

1. **Batch Size**: Adjust based on data volume (1000-5000)
2. **Connection Pooling**: For high-frequency exports
3. **Async Processing**: For large table exports
4. **Caching**: Configuration and schema caching
5. **Database Tuning**: MySQL buffer pool size

## Troubleshooting Paths

1. **Import Errors** → Check requirements.txt installation
2. **ODBC Errors** → Verify driver installation
3. **MySQL Errors** → Check credentials and permissions
4. **Upload Errors** → Check file size and permissions
5. **Export Errors** → Review logs/app.log
