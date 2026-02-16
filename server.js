const express = require('express');
const multer = require('multer');
const MDBReader = require('mdb-reader');
const mysql = require('mysql2/promise');
const cors = require('cors');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(express.static('public'));

// File upload configuration
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    const uploadDir = './uploads';
    if (!fs.existsSync(uploadDir)) {
      fs.mkdirSync(uploadDir);
    }
    cb(null, uploadDir);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

// Store connections
let currentAccessDB = null;
let currentMySQLConnection = null;

// MySQL connection configuration
let mysqlConfig = {
  host: 'localhost',
  user: 'root',
  password: '',
  database: ''
};

// API Endpoints

// Upload Access Database
app.post('/api/upload-access', upload.single('accessFile'), async (req, res) => {
  try {
    const filePath = req.file.path;
    const buffer = fs.readFileSync(filePath);
    const reader = new MDBReader(buffer);
    
    currentAccessDB = {
      path: filePath,
      reader: reader,
      tables: reader.getTableNames()
    };

    res.json({
      success: true,
      filename: req.file.originalname,
      tables: currentAccessDB.tables
    });
  } catch (error) {
    console.error('Error reading Access database:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Connect to MySQL
app.post('/api/connect-mysql', async (req, res) => {
  try {
    const { host, user, password, database } = req.body;
    
    mysqlConfig = { host, user, password, database };
    
    // Test connection
    const connection = await mysql.createConnection({
      host: host || 'localhost',
      user: user || 'root',
      password: password || ''
    });

    // Create database if it doesn't exist
    if (database) {
      await connection.query(`CREATE DATABASE IF NOT EXISTS \`${database}\``);
      await connection.query(`USE \`${database}\``);
    }

    currentMySQLConnection = connection;

    res.json({
      success: true,
      message: 'Connected to MySQL successfully'
    });
  } catch (error) {
    console.error('MySQL connection error:', error);
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get Access Database Tables
app.get('/api/access-tables', (req, res) => {
  try {
    if (!currentAccessDB) {
      return res.status(400).json({
        success: false,
        error: 'No Access database loaded'
      });
    }

    res.json({
      success: true,
      tables: currentAccessDB.tables
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get table preview (first 10 rows)
app.post('/api/preview-table', (req, res) => {
  try {
    const { tableName } = req.body;
    
    if (!currentAccessDB) {
      return res.status(400).json({
        success: false,
        error: 'No Access database loaded'
      });
    }

    const table = currentAccessDB.reader.getTable(tableName);
    const data = table.getData({ limit: 10 });
    const columns = table.getColumnNames();

    res.json({
      success: true,
      columns: columns,
      data: data,
      totalRows: table.getRowCount()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Export tables to MySQL
app.post('/api/export-tables', async (req, res) => {
  try {
    const { tables, override } = req.body;

    if (!currentAccessDB) {
      return res.status(400).json({
        success: false,
        error: 'No Access database loaded'
      });
    }

    if (!currentMySQLConnection) {
      return res.status(400).json({
        success: false,
        error: 'Not connected to MySQL'
      });
    }

    const results = [];

    for (const tableName of tables) {
      try {
        const table = currentAccessDB.reader.getTable(tableName);
        const columns = table.getColumns();
        const data = table.getData();

        // Drop table if override is true
        if (override) {
          await currentMySQLConnection.query(`DROP TABLE IF EXISTS \`${tableName}\``);
        }

        // Create table
        const columnDefs = columns.map(col => {
          let type = 'TEXT';
          
          // Map Access types to MySQL types
          switch (col.type) {
            case 'Long':
            case 'Integer':
              type = 'INT';
              break;
            case 'Double':
            case 'Single':
              type = 'DOUBLE';
              break;
            case 'Boolean':
              type = 'BOOLEAN';
              break;
            case 'DateTime':
              type = 'DATETIME';
              break;
            case 'Currency':
              type = 'DECIMAL(10,2)';
              break;
            case 'Text':
              type = `VARCHAR(${col.size || 255})`;
              break;
            case 'Memo':
              type = 'TEXT';
              break;
            default:
              type = 'TEXT';
          }

          return `\`${col.name}\` ${type}`;
        }).join(', ');

        const createTableSQL = `CREATE TABLE IF NOT EXISTS \`${tableName}\` (${columnDefs})`;
        await currentMySQLConnection.query(createTableSQL);

        // Clear existing data if override
        if (override) {
          await currentMySQLConnection.query(`DELETE FROM \`${tableName}\``);
        }

        // Insert data
        if (data.length > 0) {
          const columnNames = columns.map(col => `\`${col.name}\``).join(', ');
          const placeholders = columns.map(() => '?').join(', ');

          for (const row of data) {
            const values = columns.map(col => {
              const value = row[col.name];
              if (value === null || value === undefined) return null;
              if (value instanceof Date) return value;
              return value;
            });

            const insertSQL = `INSERT INTO \`${tableName}\` (${columnNames}) VALUES (${placeholders})`;
            await currentMySQLConnection.query(insertSQL, values);
          }
        }

        results.push({
          table: tableName,
          success: true,
          rowsExported: data.length
        });
      } catch (error) {
        results.push({
          table: tableName,
          success: false,
          error: error.message
        });
      }
    }

    res.json({
      success: true,
      results: results
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Get MySQL tables
app.get('/api/mysql-tables', async (req, res) => {
  try {
    if (!currentMySQLConnection) {
      return res.status(400).json({
        success: false,
        error: 'Not connected to MySQL'
      });
    }

    const [rows] = await currentMySQLConnection.query('SHOW TABLES');
    const tables = rows.map(row => Object.values(row)[0]);

    res.json({
      success: true,
      tables: tables
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// View MySQL table data
app.post('/api/view-mysql-table', async (req, res) => {
  try {
    const { tableName } = req.body;

    if (!currentMySQLConnection) {
      return res.status(400).json({
        success: false,
        error: 'Not connected to MySQL'
      });
    }

    const [rows] = await currentMySQLConnection.query(`SELECT * FROM \`${tableName}\` LIMIT 100`);
    const [countResult] = await currentMySQLConnection.query(`SELECT COUNT(*) as count FROM \`${tableName}\``);
    
    const columns = rows.length > 0 ? Object.keys(rows[0]) : [];

    res.json({
      success: true,
      columns: columns,
      data: rows,
      totalRows: countResult[0].count
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Save export configuration
app.post('/api/save-config', (req, res) => {
  try {
    const { config } = req.body;
    const configPath = './configs';
    
    if (!fs.existsSync(configPath)) {
      fs.mkdirSync(configPath);
    }

    const filename = `config-${Date.now()}.json`;
    const filepath = path.join(configPath, filename);
    
    fs.writeFileSync(filepath, JSON.stringify(config, null, 2));

    res.json({
      success: true,
      filename: filename,
      filepath: filepath
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Load export configuration
app.get('/api/list-configs', (req, res) => {
  try {
    const configPath = './configs';
    
    if (!fs.existsSync(configPath)) {
      return res.json({
        success: true,
        configs: []
      });
    }

    const files = fs.readdirSync(configPath)
      .filter(file => file.endsWith('.json'))
      .map(file => ({
        filename: file,
        created: fs.statSync(path.join(configPath, file)).mtime
      }));

    res.json({
      success: true,
      configs: files
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

// Load specific config
app.get('/api/load-config/:filename', (req, res) => {
  try {
    const filepath = path.join('./configs', req.params.filename);
    const config = JSON.parse(fs.readFileSync(filepath, 'utf8'));

    res.json({
      success: true,
      config: config
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message
    });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
  console.log('Access to MySQL Migration Tool Ready!');
});
