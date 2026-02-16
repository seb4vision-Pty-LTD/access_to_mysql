# Access to MySQL Converter - Distribution Package

Professional-grade production application for migrating Microsoft Access databases to MySQL.

## Quick Start

### Windows
```powershell
.\run.bat
```

### Linux / macOS
```bash
chmod +x run.sh
./run.sh
```

Then open `http://localhost:5000` in your browser.

---

## Features

✨ **Complete Migration Workflow**
- Upload and connect to Access Database (.mdb, .accdb)
- Auto-detect tables and schema
- Connect to MySQL database
- Preview table structures and data
- Select specific tables for export
- Automatic MySQL table creation with type mapping
- Batch data export with configurable row sizing
- Real-time progress tracking

🎨 **Modern Interface**
- Beautiful, responsive design
- Real-time status updates and progress bar
- Live table preview
- Connection status indicators
- Material Design color scheme

⚙️ **Background Processing**
- Non-blocking background export jobs
- Single export lock (prevents concurrent exports)
- Pause/cancel export capability
- Detailed job status API

💾 **Configuration Management**
- Save/load export configurations
- Batch migration workflows
- Automatic duplicate file cleanup

📊 **Data Management**
- View/preview tables before and after export
- Automatic type conversion (Access → MySQL)
- Batch transaction processing
- Data validation and error reporting

---

## System Requirements

### Minimum
- 2GB RAM
- Windows 7 (64-bit) or Linux/macOS with Python 3.9+
- MySQL 5.7 or MySQL 8.0+
- 500MB disk space

### Recommended
- 4GB+ RAM
- Windows 10/11 or modern Linux/macOS
- MySQL 8.0+
- SSD (for faster file operations)

### Python Dependencies
- Python 3.9 or 3.10
- All packages in `backend/requirements.txt`

---

## Installation

### From Source

1. **Extract the package**
   ```bash
   unzip access-to-mysql-converter.zip
   cd access-to-mysql-converter
   ```

2. **Ensure Python 3.9+ is installed**
   ```bash
   python --version  # Should be 3.9 or higher
   ```

3. **Run startup script** (auto-installs dependencies)
   - **Windows:** `run.bat`
   - **Linux/macOS:** `./run.sh`

### Using Docker

1. **Ensure Docker is installed**

2. **Build and run**
   ```bash
   docker-compose up --build
   ```

3. **Access at:** `http://localhost:5000`

---

## Usage Guide

### 1. Access Database Upload

1. Click **Upload & Connect** button
2. Select your `.mdb` or `.accdb` file
3. App auto-detects and lists all tables
4. Preview table metadata (columns, row count)

### 2. MySQL Connection

1. Enter MySQL host (default: `localhost`)
2. Enter port (default: `3306`)
3. Enter username (default: `root`)
4. Optionally enter password
5. Enter target database name (auto-created if doesn't exist)
6. Click **Connect to MySQL**

### 3. Table Selection & Preview

- Select tables by clicking checkboxes
- Use **Select All** / **Deselect All** buttons
- Click table rows to preview schema and sample data
- Stats show total vs. selected tables

### 4. Export Configuration

- **Override existing data:** Check to truncate and reload tables
- **Create tables if missing:** Check to auto-create table schema
- **Batch size:** Rows per transaction (1000-10000 recommended)

### 5. Start Export

1. Click **🚀 Start Export**
2. Watch real-time progress:
   - Progress bar showing % complete
   - Current table being exported
   - Total rows exported
3. Use **⏸️ Cancel Export** to abort
4. Export status updates every 1 second

### 6. View Results

- After export, click **🔄 Refresh Tables** to see MySQL data
- Select tables from dropdown to preview
- View imported data side-by-side with source

### 7. Save Configuration

- Click **💾 Save Configuration** after selecting tables
- Name your migration profile
- Reuse later by clicking **Apply** on saved configs

---

## API Endpoints

### Health & Status
- `GET /api/health` — Server health check
- `GET /api/export-status` — Get current export job status

### Upload & Connection
- `POST /api/upload-access` — Upload Access database file
- `POST /api/connect-access` — Connect to uploaded Access DB
- `POST /api/connect-mysql` — Connect to MySQL database
- `POST /api/disconnect` — Close all connections

### Data Inspection
- `POST /api/get-table-info` — Get table schema
- `POST /api/preview-table` — Get table preview (first N rows)
- `POST /api/get-mysql-tables` — List MySQL tables

### Export Operations
- `POST /api/export` — Start background export job
- `GET /api/export-status` — Poll job status
- `POST /api/export-cancel` — Cancel running export

### Configuration
- `POST /api/save-config` — Save migration config
- `GET /api/list-configs` — List saved configs
- `GET /api/load-config/<id>` — Load config by ID
- `DELETE /api/delete-config/<id>` — Delete config

### Upload Management
- `POST /api/purge-uploads` — Delete all uploaded files

---

## Configuration

### Environment Variables

```bash
# Flask (set before running)
FLASK_ENV=production          # development | production
FLASK_DEBUG=0                 # 0 | 1

# Upload management
UPLOAD_TTL_SECONDS=86400      # Hours before auto-cleanup (default: 24h)
UPLOAD_CLEANUP_INTERVAL=3600  # Cleanup check interval in seconds

# Server
PORT=5000
HOST=0.0.0.0
```

### Docker Environment

Edit `docker-compose.yml` environment section before running.

---

## Troubleshooting

### "No Access ODBC drivers found"
- **Windows:** Install [Microsoft Access Database Engine](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
- **Linux/macOS:** Use mdb-tools or Docker image

### "Failed to connect to MySQL"
- Verify MySQL is running: `mysql -u root -p`
- Check credentials (host, port, user, password)
- Ensure database user has CREATE/INSERT/ALTER permissions

### "SQLAlchemy TypingOnly error"
- Update SQLAlchemy: `pip install --upgrade "SQLAlchemy>=2.0.24"`
- Restart the app

### Export hangs or is slow
- Increase batch size (up to 5000)
- Check MySQL max_allowed_packet: `SHOW VARIABLES LIKE 'max_allowed_packet'`
- Reduce data volume per export

### 413 Request Entity Too Large
- Default limit is 100MB; modify in `backend/app.py` line: `app.config['MAX_CONTENT_LENGTH']`

---

## Production Deployment

### Docker (Recommended)

```bash
docker build -t access-to-mysql:latest .
docker run -p 5000:5000 \
  -e FLASK_ENV=production \
  -e UPLOAD_TTL_SECONDS=86400 \
  access-to-mysql:latest
```

### Using Waitress (Windows/Mac/Linux)

```bash
python -m waitress --port=5000 --host=0.0.0.0 backend.app:app
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

---

## Performance Optimization

### For Large Datasets (1M+ rows)
1. Increase batch size to 5000-10000
2. Configure MySQL: `SET SESSION net_buffer_length=16384; SET SESSION max_allowed_packet=16M;`
3. Consider exporting in multiple batches
4. Use SSD storage

### Memory Usage
- Base: ~150MB
- Per table in memory: varies by row count
- Batch processing keeps memory constant

---

## Data Type Mapping

| Access Type | MySQL Type |
|-----------|-----------|
| Text | VARCHAR(255) |
| Number (Integer) | INT |
| Number (Long) | BIGINT |
| Number (Decimal) | DECIMAL |
| Date/Time | DATETIME |
| Yes/No | BOOLEAN |
| OLE Object | BLOB |
| Memo | TEXT |

---

## Security Considerations

⚠️ **This app is designed for local network use**

For internet deployment:
1. Use HTTPS/SSL certificates
2. Add authentication layer
3. Implement rate limiting
4. Use private database network
5. Audit all database operations
6. Regularly update dependencies: `pip install --upgrade -r backend/requirements.txt`

---

## Support & Documentation

- **Issues:** Check [GitHub Issues](https://github.com/yourrepo/issues)
- **Documentation:** See [SETUP-GUIDE.md](SETUP-GUIDE.md)
- **Architecture:** See [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
- **Deployment:** See [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

---

## License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## Version

**v1.0.0** - Production Release
- Background job processing with status polling
- Non-blocking export (single-threaded lock)
- Real-time progress tracking
- Complete REST API
- Docker support
- Comprehensive UI

---

## Changelog

### v1.0.0 (2026-02-16)
- ✅ Initial production release
- ✅ Background export jobs
- ✅ Real-time status updates
- ✅ Complete migration workflow
- ✅ Docker & Windows support

---

**Last Updated:** February 16, 2026
