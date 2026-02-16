# Access to MySQL Migration Tool

A modern, locally-hosted web application for migrating Microsoft Access databases to MySQL with a beautiful, professional interface.

## Features

✨ **Complete Migration Workflow**
- Upload and connect to Access Database (.mdb, .accdb)
- Connect to MySQL database
- Preview table structures and data
- Select specific tables to export
- Create MySQL tables automatically
- Export data with type mapping
- Override/update existing data

🎨 **Modern Interface**
- Bold, distinctive design with custom animations
- Real-time status indicators
- Table preview functionality
- Export progress tracking
- Responsive design

💾 **Configuration Management**
- Save export configurations
- Load previous configurations
- Reusable migration setups

📊 **Data Viewing**
- Preview Access database tables
- View exported MySQL data
- Row count and metadata display

## Prerequisites

- **Node.js** (v14 or higher)
- **MySQL Server** (v5.7 or higher)
- **Access Database** file (.mdb or .accdb)

## Installation

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Ensure MySQL is running**
   - Make sure your MySQL server is running
   - Have your MySQL credentials ready (host, user, password)
   - Optionally create a database, or the app will create one

## Usage

### 1. Start the Server

```bash
npm start
```

Or for development with auto-reload:
```bash
npm run dev
```

The application will start on `http://localhost:3000`

### 2. Open in Browser

Navigate to `http://localhost:3000` in your web browser.

### 3. Migration Workflow

**Step 1: Connect Databases**

1. **Upload Access Database**
   - Click "Select Access File"
   - Choose your .mdb or .accdb file
   - The app will automatically read all tables

2. **Connect to MySQL**
   - Enter MySQL host (default: localhost)
   - Enter MySQL user (default: root)
   - Enter password
   - Enter database name (will be created if it doesn't exist)
   - Click "Connect to MySQL"

**Step 2: Select Tables**

- Browse all available tables from your Access database
- Click on table cards to select/deselect them
- Click "Preview" to see table structure and sample data
- Selected tables are highlighted in green

**Step 3: Configure Export**

- Choose whether to override existing data
  - ✓ Checked: Drops and recreates tables (fresh import)
  - ✗ Unchecked: Keeps existing tables (may cause conflicts)
- Click "Export Selected Tables" to start migration
- Monitor progress in real-time

**Step 4: View Results**

- After export, select tables from the dropdown
- View migrated data in MySQL
- Verify row counts and data integrity

### 4. Save/Load Configurations

**Save Configuration**
- After selecting tables and configuring settings
- Click "Save Configuration"
- Configuration is saved with timestamp

**Load Configuration**
- Click "Load Configuration"
- Select from previously saved configurations
- All settings will be restored

## Technical Details

### Access to MySQL Type Mapping

The application automatically maps Access data types to MySQL:

| Access Type | MySQL Type |
|------------|------------|
| Long/Integer | INT |
| Double/Single | DOUBLE |
| Boolean | BOOLEAN |
| DateTime | DATETIME |
| Currency | DECIMAL(10,2) |
| Text | VARCHAR(size) |
| Memo | TEXT |

### File Structure

```
access-to-mysql-migrator/
├── server.js              # Express server & API endpoints
├── package.json           # Dependencies
├── public/
│   ├── index.html        # Main interface
│   ├── styles.css        # Custom styling
│   └── app.js            # Frontend logic
├── uploads/              # Temporary Access file storage
├── configs/              # Saved configurations
└── README.md
```

### API Endpoints

- `POST /api/upload-access` - Upload Access database
- `POST /api/connect-mysql` - Connect to MySQL
- `GET /api/access-tables` - List Access tables
- `POST /api/preview-table` - Preview Access table data
- `POST /api/export-tables` - Export tables to MySQL
- `GET /api/mysql-tables` - List MySQL tables
- `POST /api/view-mysql-table` - View MySQL table data
- `POST /api/save-config` - Save configuration
- `GET /api/list-configs` - List saved configurations
- `GET /api/load-config/:filename` - Load specific configuration

## Troubleshooting

### Access Database Won't Load
- Ensure the file is a valid .mdb or .accdb file
- Check file permissions
- File may be corrupted or encrypted

### MySQL Connection Fails
- Verify MySQL server is running
- Check credentials (host, user, password)
- Ensure MySQL user has CREATE DATABASE permission
- Check firewall settings

### Export Errors
- Some Access-specific data types may not map perfectly
- Large MEMO fields might need adjustment
- Check MySQL max_allowed_packet for large datasets

### Performance Issues
- Large databases (>1GB) may take several minutes
- Consider exporting tables in smaller batches
- Increase MySQL timeout settings if needed

## Security Considerations

⚠️ **This is a local development tool. Do NOT expose to the internet without:**
- Adding authentication
- Implementing input validation
- Sanitizing SQL queries
- Adding rate limiting
- Securing file uploads

## Dependencies

- **express** - Web server framework
- **multer** - File upload handling
- **mdb-reader** - Access database reader
- **mysql2** - MySQL client with Promise support
- **cors** - Cross-Origin Resource Sharing
- **body-parser** - Request body parsing

## Browser Support

- Chrome/Edge (recommended)
- Firefox
- Safari
- Modern browsers with ES6+ support

## License

MIT

## Support

For issues or questions:
1. Check the console for error messages (F12 in browser)
2. Check terminal output for server errors
3. Verify all prerequisites are installed correctly

## Future Enhancements

- [ ] Support for PostgreSQL
- [ ] Batch export with progress bar
- [ ] Data transformation rules
- [ ] Scheduled automatic migrations
- [ ] Export to SQL file
- [ ] Database comparison tool
- [ ] Multi-database support

---

**Made with ⚡ for seamless database migration**
