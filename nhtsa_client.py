import requests
import json
from typing import Dict, List, Any

class NHTSAClient:
    def __init__(self):
        self.base_url = "https://vpic.nhtsa.dot.gov/api"
    
    def get_vehicle_data(self, vin: str) -> Dict[str, Any]:
        """Get vehicle information by VIN"""
        try:
            url = f"{self.base_url}/vehicles/decodevin/{vin}?format=json"
            response = requests.get(url)
            data = response.json()
            
            if data.get('Results'):
                formatted_data = {
                    'vin': vin,
                    'make': self._extract_value(data, 'Make'),
                    'model': self._extract_value(data, 'Model'),
                    'year': self._extract_value(data, 'Model Year'),
                    'body_style': self._extract_value(data, 'Body Class'),
                    'engine': self._extract_value(data, 'Engine Model'),
                    'fuel_type': self._extract_value(data, 'Fuel Type - Primary'),
                    'transmission': self._extract_value(data, 'Transmission Style'),
                    'drive_type': self._extract_value(data, 'Drive Type'),
                    'doors': self._extract_value(data, 'Doors'),
                    'seats': self._extract_value(data, 'Seats'),
                    'country': self._extract_value(data, 'Plant Country'),
                    'plant_city': self._extract_value(data, 'Plant City')
                }
                return formatted_data
        except Exception as e:
            print(f"Error fetching NHTSA data: {e}")
        return {}
    
    def get_recall_data(self, make: str, model: str, year: str) -> List[Dict[str, Any]]:
        """Get recall information"""
        try:
            url = f"https://api.nhtsa.gov/recalls/recallsByVehicle"
            params = {
                'make': make,
                'model': model,
                'modelYear': year
            }
            response = requests.get(url, params=params)
            data = response.json()
            
            recalls = []
            if data.get('results'):
                for recall in data['results']:
                    recalls.append({
                        'recall_number': recall.get('NHTSACampaignNumber'),
                        'component': recall.get('Component'),
                        'summary': recall.get('Summary'),
                        'consequence': recall.get('Consequence'),
                        'remedy': recall.get('Remedy'),
                        'date': recall.get('ReportReceivedDate')
                    })
            return recalls
        except Exception as e:
            print(f"Error fetching recall data: {e}")
        return []
    
    def get_safety_ratings(self, make: str, model: str, year: str) -> Dict[str, Any]:
        """Get safety ratings"""
        try:
            url = f"https://api.nhtsa.gov/SafetyRatings/vehicle/modelyear/{year}/make/{make}/model/{model}"
            response = requests.get(url)
            data = response.json()
            return data.get('Results', [])
        except Exception as e:
            print(f"Error fetching safety ratings: {e}")
        return {}
    
    def _extract_value(self, data: Dict[str, Any], variable: str) -> str:
        """Extract specific value from NHTSA response"""
        for result in data.get('Results', []):
            if result.get('Variable') == variable:
                return result.get('Value', '')
        return ''