import pandas as pd
import json
import os
from typing import Dict, List, Any, Optional

class DataManager:
    """
    Centralized data manager for handling Excel spreadsheets and reference data
    """
    
    def __init__(self, data_folder: str = "data"):
        self.data_folder = data_folder
        self.excel_files = {
            # 'pumps': 'pumps_catalog.xlsx',
            # 'nozzles': 'nozzles_catalog.xlsx',
            'washing_components': 'Washing_components.xlsx', 
            'pipes': 'Pipes.xlsx',
            'connectors': 'Connectors.xlsx',
            'dirt': 'Dirt_Types.xlsx',
            'fluids': 'Fluids.xlsx',
            'bends': 'Bend_Radius.xlsx'
        }

        self.data = {
            'washing_components': None,
            'pipes': None,
            'connectors': None,
            'dirt': None,
            'fluids': None,
            'bends': None
        }
        
        # Load washing components data
        self.data['washing_components'] = self.get_component_data()
        
    def load_data(self, file_key: str) -> pd.DataFrame:
        if file_key not in self.excel_files:
            raise ValueError(f"File key '{file_key}' not found in excel files mapping.")
        
        file_path = os.path.join(self.data_folder, self.excel_files[file_key])
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Data file '{file_path}' does not exist.")
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            return df
        except Exception as e:
            raise RuntimeError(f"Failed to load data from '{file_path}': {e}")
        
    def get_component_data(self):
        data = self.load_data('washing_components')
        json_data = data.to_dict(orient='records')
        return json_data
    
    def get_pipes_data(self):
        if self.data['pipes'] is None:
            data = self.load_data('pipes')
            self.data['pipes'] = data.to_dict(orient='records')
        return self.data['pipes']
    
    def get_connectors_data(self):
        if self.data['connectors'] is None:
            data = self.load_data('connectors')
            self.data['connectors'] = data.to_dict(orient='records')
        return self.data['connectors']
    
    def get_dirt_data(self):
        if self.data['dirt'] is None:
            data = self.load_data('dirt')
            self.data['dirt'] = data.to_dict(orient='records')
        return self.data['dirt']
    
    def get_fluids_data(self):
        if self.data['fluids'] is None:
            data = self.load_data('fluids')
            records = data.to_dict(orient='records')
            
            # Filter to get unique fluid names only
            seen_names = set()
            unique_fluids = []
            for item in records:
                name = item.get('LLG Name')
                if name and name not in seen_names:
                    seen_names.add(name)
                    unique_fluids.append(item)
            
            self.data['fluids'] = unique_fluids
        return self.data['fluids']
    
    def get_bends_data(self):
        if self.data['bends'] is None:
            data = self.load_data('bends')
            self.data['bends'] = data.to_dict(orient='records')
        return self.data['bends']

        
if __name__ == "__main__":
    # Example usage
    data_manager = DataManager()
    try:
        washing_component_df = data_manager.load_data('washing_components')
        print(washing_component_df.head())
        pipes_df = data_manager.load_data('pipes')
        print(pipes_df.head())
        connectors_df = data_manager.load_data('connectors')
        print(connectors_df.head())
        dirt_df = data_manager.load_data('dirt')
        print(dirt_df.head())
        fluids_df = data_manager.load_data('fluids')
        print(fluids_df.head())
        bends_df = data_manager.load_data('bends')
        print(bends_df.head())
    
        print(data_manager.get_component_data())
        print(data_manager.data)
    except Exception as e:
        print(f"Error loading data: {e}")