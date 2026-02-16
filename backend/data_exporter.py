"""
Data Exporter Module
Handles the export of data from Access to MySQL
"""

import logging
import pandas as pd
from typing import List, Dict, Any
import pymysql
from database_handler import DatabaseHandler

logger = logging.getLogger(__name__)


class DataExporter:
    """Handler for exporting data from Access to MySQL"""
    
    def __init__(self):
        self.db_handler = DatabaseHandler()
    
    def export_tables(
        self,
        access_conn,
        mysql_conn,
        table_names: List[str],
        override_data: bool = True,
        create_tables: bool = True,
        batch_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Export multiple tables from Access to MySQL
        
        Args:
            access_conn: Access database connection
            mysql_conn: MySQL database connection
            table_names: List of table names to export
            override_data: Whether to override existing data
            create_tables: Whether to create tables if they don't exist
            batch_size: Batch size for data insertion
            
        Returns:
            List of export results for each table
        """
        results = []
        
        for table_name in table_names:
            try:
                logger.info(f"Starting export for table: {table_name}")
                
                result = self.export_single_table(
                    access_conn,
                    mysql_conn,
                    table_name,
                    override_data=override_data,
                    create_table=create_tables,
                    batch_size=batch_size
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error exporting table {table_name}: {str(e)}")
                results.append({
                    'table_name': table_name,
                    'success': False,
                    'error': str(e),
                    'rows_exported': 0
                })
        
        return results
    
    def export_single_table(
        self,
        access_conn,
        mysql_conn,
        table_name: str,
        override_data: bool = True,
        create_table: bool = True,
        batch_size: int = 1000
    ) -> Dict[str, Any]:
        """
        Export a single table from Access to MySQL
        
        Args:
            access_conn: Access database connection
            mysql_conn: MySQL database connection
            table_name: Name of the table to export
            override_data: Whether to override existing data
            create_table: Whether to create table if it doesn't exist
            batch_size: Batch size for data insertion
            
        Returns:
            Dictionary with export results
        """
        try:
            # Get table schema from Access
            schema = self.db_handler.get_table_schema(access_conn, table_name, 'access')
            
            # Create table in MySQL if needed
            if create_table:
                self._create_mysql_table(mysql_conn, table_name, schema, override_data)
            
            # Clear existing data if override is enabled
            if override_data:
                self._clear_mysql_table(mysql_conn, table_name)
            
            # Export data in batches
            total_rows = 0
            
            for batch_df in self.db_handler.read_table_data(access_conn, table_name, 'access', batch_size):
                if not batch_df.empty:
                    rows_inserted = self._insert_batch(mysql_conn, table_name, batch_df)
                    total_rows += rows_inserted
                    logger.info(f"Inserted {rows_inserted} rows into {table_name} (total: {total_rows})")
            
            logger.info(f"Successfully exported {total_rows} rows from {table_name}")
            
            return {
                'table_name': table_name,
                'success': True,
                'rows_exported': total_rows,
                'schema': schema
            }
            
        except Exception as e:
            logger.error(f"Error in export_single_table for {table_name}: {str(e)}")
            raise
    
    def _create_mysql_table(self, connection, table_name: str, schema: List[Dict[str, Any]], drop_if_exists: bool = False):
        """
        Create MySQL table based on Access schema
        
        Args:
            connection: MySQL database connection
            table_name: Name of the table to create
            schema: Table schema from Access
            drop_if_exists: Whether to drop table if it exists
        """
        try:
            cursor = connection.cursor()
            
            # Drop table if requested
            if drop_if_exists:
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                logger.info(f"Dropped existing table: {table_name}")
            
            # Check if table exists
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            if cursor.fetchone():
                logger.info(f"Table {table_name} already exists, skipping creation")
                cursor.close()
                return
            
            # Build CREATE TABLE statement
            columns = []
            
            for col in schema:
                col_name = col['name']
                col_type = self.db_handler.access_to_mysql_type(col['type'])
                nullable = 'NULL' if col.get('nullable', True) else 'NOT NULL'
                
                columns.append(f"`{col_name}` {col_type} {nullable}")
            
            create_stmt = f"CREATE TABLE `{table_name}` (\n  " + ",\n  ".join(columns) + "\n)"
            
            cursor.execute(create_stmt)
            connection.commit()
            
            logger.info(f"Created table: {table_name}")
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error creating MySQL table {table_name}: {str(e)}")
            raise
    
    def _clear_mysql_table(self, connection, table_name: str):
        """
        Clear all data from MySQL table
        
        Args:
            connection: MySQL database connection
            table_name: Name of the table to clear
        """
        try:
            cursor = connection.cursor()
            cursor.execute(f"TRUNCATE TABLE `{table_name}`")
            connection.commit()
            cursor.close()
            
            logger.info(f"Cleared data from table: {table_name}")
            
        except pymysql.Error as e:
            # Table might not exist, that's okay
            if e.args[0] != 1146:  # Table doesn't exist error code
                logger.error(f"Error clearing MySQL table {table_name}: {str(e)}")
                raise
    
    def _insert_batch(self, connection, table_name: str, dataframe: pd.DataFrame) -> int:
        """
        Insert a batch of data into MySQL table
        
        Args:
            connection: MySQL database connection
            table_name: Name of the table
            dataframe: Pandas DataFrame with data to insert
            
        Returns:
            Number of rows inserted
        """
        try:
            cursor = connection.cursor()
            
            # Prepare column names
            columns = list(dataframe.columns)
            column_str = ", ".join([f"`{col}`" for col in columns])
            
            # Prepare placeholders
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Prepare INSERT statement
            insert_stmt = f"INSERT INTO `{table_name}` ({column_str}) VALUES ({placeholders})"
            
            # Convert DataFrame to list of tuples
            # Handle NaN values and convert to None
            data = []
            for _, row in dataframe.iterrows():
                row_data = []
                for val in row:
                    if pd.isna(val):
                        row_data.append(None)
                    else:
                        row_data.append(val)
                data.append(tuple(row_data))
            
            # Execute batch insert
            cursor.executemany(insert_stmt, data)
            connection.commit()
            
            rows_inserted = cursor.rowcount
            cursor.close()
            
            return rows_inserted
            
        except Exception as e:
            logger.error(f"Error inserting batch into {table_name}: {str(e)}")
            connection.rollback()
            raise
    
    def validate_export(self, access_conn, mysql_conn, table_name: str) -> Dict[str, Any]:
        """
        Validate that data was exported correctly
        
        Args:
            access_conn: Access database connection
            mysql_conn: MySQL database connection
            table_name: Name of the table to validate
            
        Returns:
            Dictionary with validation results
        """
        try:
            access_count = self.db_handler.get_table_row_count(access_conn, table_name, 'access')
            mysql_count = self.db_handler.get_table_row_count(mysql_conn, table_name, 'mysql')
            
            is_valid = access_count == mysql_count
            
            return {
                'table_name': table_name,
                'valid': is_valid,
                'access_rows': access_count,
                'mysql_rows': mysql_count,
                'difference': abs(access_count - mysql_count)
            }
            
        except Exception as e:
            logger.error(f"Error validating export for {table_name}: {str(e)}")
            return {
                'table_name': table_name,
                'valid': False,
                'error': str(e)
            }
