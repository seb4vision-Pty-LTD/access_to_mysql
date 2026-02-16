# Quick Start Guide

## Prerequisites Check

Before starting, ensure you have:
- ✅ Python 3.8+
- ✅ MySQL Server
- ✅ Access ODBC Driver (Windows) or mdbtools (Linux/Mac)

## Installation (5 minutes)

### Option 1: Automatic Installation

**Linux/Mac:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```cmd
install.bat
```

### Option 2: Manual Installation

```bash
# Install Python dependencies
cd backend
pip install -r requirements.txt

# Create directories
mkdir -p data/uploads configs logs

# Copy environment file
cp .env.example .env
```

## Running the Application

### 1. Start Backend
```bash
cd backend
python app.py
```
Backend runs on: http://localhost:5000

### 2. Open Frontend
Simply open `frontend/index.html` in your browser

Or use a simple HTTP server:
```bash
cd frontend
python -m http.server 8000
```
Then visit: http://localhost:8000

## First-Time Usage

### 1. Connect to Access Database
- Click "Choose File"
- Select your .accdb or .mdb file
- Click "Upload & Connect"

### 2. Connect to MySQL
- Enter host: `localhost`
- Enter port: `3306`
- Enter username: `root`
- Enter password: (your MySQL password)
- Enter database name: `my_database`
- Click "Connect to MySQL"

### 3. Select and Export Tables
- Click "Load Tables"
- Select tables you want to export
- Click "Start Export"
- Wait for completion

### 4. Verify Export
- Select a table from the "View MySQL Database" section
- Preview the data

## Common Issues

### "No Access ODBC drivers found"
**Windows:** Install [Microsoft Access Database Engine](https://www.microsoft.com/en-us/download/details.aspx?id=54920)
**Linux:** `sudo apt-get install mdbtools`

### "Failed to connect to MySQL"
- Check if MySQL is running: `sudo systemctl status mysql`
- Verify credentials are correct
- Ensure database exists

### "Connection refused"
- Make sure backend is running on port 5000
- Check for port conflicts

## Docker Deployment

For containerized deployment:

```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Access the application at http://localhost

## Need Help?

- Check `README.md` for detailed documentation
- View logs in `logs/app.log`
- Review API documentation in README.md
- Check troubleshooting section

## Production Deployment

For production use:

1. **Security**: Change default passwords in `.env`
2. **HTTPS**: Use SSL certificates with Nginx
3. **Firewall**: Configure firewall rules
4. **Backup**: Regular backups of configs and data
5. **Monitoring**: Set up logging and monitoring

See README.md for detailed production deployment instructions.
