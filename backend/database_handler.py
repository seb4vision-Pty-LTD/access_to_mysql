"""
Database Handler Module
Handles connections and operations for both Access and MySQL databases
"""

import pyodbc
import pymysql
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

logger = logging.getLogger(__name__)


class DatabaseHandler:
    """Handler for database connections and operations"""
    
    def __init__(self):
        self.access_drivers = self._get_access_drivers()
    
    def _get_access_drivers(self) -> List[str]:
        """Get available Access ODBC drivers"""
        drivers = [driver for driver in pyodbc.drivers() if 'Access' in driver or 'Microsoft Access Driver' in driver]
        logger.info(f"Available Access drivers: {drivers}")
        return drivers
    
    def connect_access(self, filepath: str):
        """
        Connect to Access database
        
        Args:
            filepath: Path to the Access database file
            
        Returns:
            Database connection object or None
        """
        try:
            if not self.access_drivers:
                raise Exception("No Access ODBC drivers found. Please install Microsoft Access Database Engine.")
            
            # Try each available driver
            for driver in self.access_drivers:
                try:
                    conn_str = (
                        f"DRIVER={{{driver}}};"
                        f"DBQ={filepath};"
                        "ExtendedAnsiSQL=1;"
                    )
                    
                    connection = pyodbc.connect(conn_str, autocommit=True)
                    logger.info(f"Successfully connected to Access database using driver: {driver}")
                    return connection
                    
                except pyodbc.Error as e:
                    logger.warning(f"Failed to connect with driver {driver}: {str(e)}")
                    continue
            
            raise Exception("Failed to connect with any available Access driver")
            
        except Exception as e:
            logger.error(f"Error connecting to Access database: {str(e)}")
            raise
    
    def connect_mysql(self, config: Dict[str, Any]):
        """
        Connect to MySQL database
        
        Args:
            config: Dictionary containing MySQL connection parameters
            
        Returns:
            Database connection object or None
        """
        try:
            connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            logger.info(f"Successfully connected to MySQL database: {config['database']}")
            return connection
            
        except pymysql.Error as e:
            logger.error(f"Error connecting to MySQL: {str(e)}")
            raise
    
    def get_access_tables(self, connection) -> List[str]:
        """
        Get list of tables from Access database
        
        Args:
            connection: Access database connection
            
        Returns:
            List of table names
        """
        try:
            cursor = connection.cursor()
            tables = []
            
            # Get all tables (excluding system tables)
            for table_info in cursor.tables(tableType='TABLE'):
                table_name = table_info.table_name
                # Exclude system tables
                if not table_name.startswith('MSys') and not table_name.startswith('~'):
                    tables.append(table_name)
            
            cursor.close()
            logger.info(f"Found {len(tables)} tables in Access database")
            return sorted(tables)
            
        except Exception as e:
            logger.error(f"Error getting Access tables: {str(e)}")
            raise
    
    def get_mysql_tables(self, connection) -> List[str]:
        """
        Get list of tables from MySQL database
        
        Args:
            connection: MySQL database connection
            
        Returns:
            List of table names
        """
        try:
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            
            tables = [row[list(row.keys())[0]] for row in cursor.fetchall()]
            
            cursor.close()
            logger.info(f"Found {len(tables)} tables in MySQL database")
            return sorted(tables)
            
        except Exception as e:
            logger.error(f"Error getting MySQL tables: {str(e)}")
            raise
    
    def get_table_schema(self, connection, table_name: str, db_type: str = 'access') -> List[Dict[str, Any]]:
        """
        Get schema information for a table
        
        Args:
            connection: Database connection
            table_name: Name of the table
            db_type: Type of database ('access' or 'mysql')
            
        Returns:
            List of column information dictionaries
        """
        try:
            cursor = connection.cursor()
            schema = []
            
            if db_type == 'access':
                # Get column information from Access
                cursor.execute(f"SELECT * FROM [{table_name}] WHERE 1=0")
                
                for column in cursor.description:
                    schema.append({
                        'name': column[0],
                        'type': self._get_type_name(column[1]),
                        'nullable': column[6] if len(column) > 6 else True,
                        'size': column[3] if len(column) > 3 else None
                    })
            else:
                # Get column information from MySQL
                cursor.execute(f"DESCRIBE `{table_name}`")
                
                for row in cursor.fetchall():
                    schema.append({
                        'name': row['Field'],
                        'type': row['Type'],
                        'nullable': row['Null'] == 'YES',
                        'key': row['Key'],
                        'default': row['Default']
                    })
            
            cursor.close()
            return schema
            
        except Exception as e:
            logger.error(f"Error getting table schema: {str(e)}")
            raise
    
    def get_table_row_count(self, connection, table_name: str, db_type: str = 'access') -> int:
        """
        Get row count for a table
        
        Args:
            connection: Database connection
            table_name: Name of the table
            db_type: Type of database ('access' or 'mysql')
            
        Returns:
            Number of rows
        """
        try:
            cursor = connection.cursor()
            
            if db_type == 'access':
                cursor.execute(f"SELECT COUNT(*) FROM [{table_name}]")
            else:
                cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Exception as e:
            logger.error(f"Error getting row count: {str(e)}")
            raise
    
    def get_table_preview(self, connection, table_name: str, limit: int = 100, db_type: str = 'access') -> Dict[str, Any]:
        """
        Get preview data from a table
        
        Args:
            connection: Database connection
            table_name: Name of the table
            limit: Maximum number of rows to return
            db_type: Type of database ('access' or 'mysql')
            
        Returns:
            Dictionary with columns and rows
        """
        try:
            cursor = connection.cursor()
            
            if db_type == 'access':
                cursor.execute(f"SELECT TOP {limit} * FROM [{table_name}]")
            else:
                cursor.execute(f"SELECT * FROM `{table_name}` LIMIT {limit}")
            
            columns = [column[0] for column in cursor.description]
            rows = []
            
            for row in cursor.fetchall():
                if isinstance(row, dict):
                    rows.append([str(row[col]) if row[col] is not None else None for col in columns])
                else:
                    rows.append([str(val) if val is not None else None for val in row])
            
            cursor.close()
            
            return {
                'columns': columns,
                'rows': rows,
                'row_count': len(rows)
            }
            
        except Exception as e:
            logger.error(f"Error getting table preview: {str(e)}")
            raise
    
    def read_table_data(self, connection, table_name: str, db_type: str = 'access', batch_size: int = 1000):
        """
        Read table data in batches (generator)
        
        Args:
            connection: Database connection
            table_name: Name of the table
            db_type: Type of database ('access' or 'mysql')
            batch_size: Number of rows per batch
            
        Yields:
            Pandas DataFrame batches
        """
        try:
            if db_type == 'access':
                query = f"SELECT * FROM [{table_name}]"
            else:
                query = f"SELECT * FROM `{table_name}`"
            
            # Use pandas to read in chunks
            for chunk in pd.read_sql(query, connection, chunksize=batch_size):
                yield chunk
                
        except Exception as e:
            logger.error(f"Error reading table data: {str(e)}")
            raise
    
    def close_connection(self, connection):
        """Close database connection"""
        try:
            if connection:
                connection.close()
                logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")
    
    @staticmethod
    def _get_type_name(type_code) -> str:
        """Convert ODBC type code to string name"""
        type_mapping = {
            -7: 'BIT',
            -6: 'TINYINT',
            -5: 'BIGINT',
            -4: 'LONGVARBINARY',
            -3: 'VARBINARY',
            -2: 'BINARY',
            -1: 'LONGVARCHAR',
            1: 'CHAR',
            2: 'NUMERIC',
            3: 'DECIMAL',
            4: 'INTEGER',
            5: 'SMALLINT',
            6: 'FLOAT',
            7: 'REAL',
            8: 'DOUBLE',
            9: 'DATE',
            10: 'TIME',
            11: 'TIMESTAMP',
            12: 'VARCHAR',
        }
        
        return type_mapping.get(type_code, f'UNKNOWN({type_code})')
    
    @staticmethod
    def access_to_mysql_type(access_type: str) -> str:
        """
        Convert Access data type to MySQL data type
        
        Args:
            access_type: Access data type
            
        Returns:
            Equivalent MySQL data type
        """
        type_mapping = {
            'BIT': 'BOOLEAN',
            'TINYINT': 'TINYINT',
            'SMALLINT': 'SMALLINT',
            'INTEGER': 'INT',
            'BIGINT': 'BIGINT',
            'FLOAT': 'FLOAT',
            'REAL': 'REAL',
            'DOUBLE': 'DOUBLE',
            'NUMERIC': 'DECIMAL',
            'DECIMAL': 'DECIMAL',
            'CHAR': 'CHAR',
            'VARCHAR': 'VARCHAR(255)',
            'LONGVARCHAR': 'TEXT',
            'DATE': 'DATE',
            'TIME': 'TIME',
            'TIMESTAMP': 'DATETIME',
            'BINARY': 'BINARY',
            'VARBINARY': 'VARBINARY(255)',
            'LONGVARBINARY': 'BLOB',
        }
        
        # Handle complex types with parentheses
        base_type = access_type.split('(')[0].upper()
        
        return type_mapping.get(base_type, 'VARCHAR(255)')
