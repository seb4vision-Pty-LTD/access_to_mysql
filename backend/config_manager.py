"""
Configuration Manager Module
Handles saving, loading, and managing export configurations
"""

import json
import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manager for export configurations"""
    
    def __init__(self, config_folder: str):
        """
        Initialize ConfigManager
        
        Args:
            config_folder: Path to folder where configs are stored
        """
        self.config_folder = config_folder
        os.makedirs(config_folder, exist_ok=True)
    
    def save_config(self, config_name: str, config_data: Dict[str, Any]) -> str:
        """
        Save an export configuration
        
        Args:
            config_name: Name of the configuration
            config_data: Configuration data dictionary
            
        Returns:
            Configuration ID (hash)
        """
        try:
            # Generate unique ID based on name and timestamp
            config_id = self._generate_config_id(config_name)
            
            # Add metadata
            config_data['config_id'] = config_id
            config_data['config_name'] = config_name
            
            if 'created_at' not in config_data:
                config_data['created_at'] = datetime.now().isoformat()
            
            config_data['updated_at'] = datetime.now().isoformat()
            
            # Save to file
            filepath = os.path.join(self.config_folder, f"{config_id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration saved: {config_name} ({config_id})")
            
            return config_id
            
        except Exception as e:
            logger.error(f"Error saving config: {str(e)}")
            raise
    
    def load_config(self, config_id: str) -> Optional[Dict[str, Any]]:
        """
        Load a configuration by ID
        
        Args:
            config_id: Configuration ID
            
        Returns:
            Configuration data or None if not found
        """
        try:
            filepath = os.path.join(self.config_folder, f"{config_id}.json")
            
            if not os.path.exists(filepath):
                logger.warning(f"Configuration not found: {config_id}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            logger.info(f"Configuration loaded: {config_id}")
            
            return config_data
            
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise
    
    def list_configs(self) -> List[Dict[str, Any]]:
        """
        List all saved configurations
        
        Returns:
            List of configuration summaries
        """
        try:
            configs = []
            
            for filename in os.listdir(self.config_folder):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.config_folder, filename)
                    
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            config_data = json.load(f)
                        
                        # Create summary
                        summary = {
                            'config_id': config_data.get('config_id'),
                            'config_name': config_data.get('config_name'),
                            'created_at': config_data.get('created_at'),
                            'updated_at': config_data.get('updated_at'),
                            'tables': config_data.get('tables', []),
                            'table_count': len(config_data.get('tables', [])),
                            'access_file': config_data.get('access_file', {}).get('filename', 'N/A'),
                            'mysql_database': config_data.get('mysql', {}).get('database', 'N/A')
                        }
                        
                        configs.append(summary)
                        
                    except Exception as e:
                        logger.error(f"Error reading config file {filename}: {str(e)}")
                        continue
            
            # Sort by updated_at (most recent first)
            configs.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            
            logger.info(f"Found {len(configs)} configurations")
            
            return configs
            
        except Exception as e:
            logger.error(f"Error listing configs: {str(e)}")
            raise
    
    def delete_config(self, config_id: str) -> bool:
        """
        Delete a configuration
        
        Args:
            config_id: Configuration ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            filepath = os.path.join(self.config_folder, f"{config_id}.json")
            
            if not os.path.exists(filepath):
                logger.warning(f"Configuration not found: {config_id}")
                return False
            
            os.remove(filepath)
            logger.info(f"Configuration deleted: {config_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting config: {str(e)}")
            raise
    
    def update_config(self, config_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing configuration
        
        Args:
            config_id: Configuration ID
            updates: Dictionary with updates
            
        Returns:
            True if updated, False if not found
        """
        try:
            config_data = self.load_config(config_id)
            
            if not config_data:
                return False
            
            # Apply updates
            config_data.update(updates)
            config_data['updated_at'] = datetime.now().isoformat()
            
            # Save
            filepath = os.path.join(self.config_folder, f"{config_id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration updated: {config_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating config: {str(e)}")
            raise
    
    def export_config(self, config_id: str, export_path: str) -> bool:
        """
        Export a configuration to a specific path
        
        Args:
            config_id: Configuration ID
            export_path: Path where to export the config
            
        Returns:
            True if exported successfully
        """
        try:
            config_data = self.load_config(config_id)
            
            if not config_data:
                return False
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration exported to: {export_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error exporting config: {str(e)}")
            raise
    
    def import_config(self, import_path: str) -> Optional[str]:
        """
        Import a configuration from a file
        
        Args:
            import_path: Path to the config file to import
            
        Returns:
            Configuration ID if successful, None otherwise
        """
        try:
            if not os.path.exists(import_path):
                logger.error(f"Import file not found: {import_path}")
                return None
            
            with open(import_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Generate new ID
            config_name = config_data.get('config_name', 'Imported Config')
            config_id = self._generate_config_id(config_name)
            
            # Update metadata
            config_data['config_id'] = config_id
            config_data['created_at'] = datetime.now().isoformat()
            config_data['updated_at'] = datetime.now().isoformat()
            
            # Save
            filepath = os.path.join(self.config_folder, f"{config_id}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Configuration imported: {config_name} ({config_id})")
            
            return config_id
            
        except Exception as e:
            logger.error(f"Error importing config: {str(e)}")
            raise
    
    @staticmethod
    def _generate_config_id(config_name: str) -> str:
        """
        Generate a unique configuration ID
        
        Args:
            config_name: Name of the configuration
            
        Returns:
            Unique ID (hash)
        """
        # Create hash based on name and timestamp
        unique_string = f"{config_name}_{datetime.now().isoformat()}"
        config_id = hashlib.md5(unique_string.encode()).hexdigest()[:12]
        
        return config_id
