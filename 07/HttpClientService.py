import time
import requests

class HttpClientService:
    def __init__(self, api_url):
        self._api_url = api_url
        self.headers = {'User-Agent': 'TestApp/1.0 (mikolaj.kowalski@student.uj.edu.pl)'}

    def get(self, path: str) -> dict:
        try:
            response = requests.get(self._api_url + path, headers=self.headers)
            if response.status_code == 429:  # 429 - Too Many Requests
                return self._retry(self.get, path)
            if response.status_code != 200:
                raise Exception(f"Error fetching data from {path}: {response.status_code} - {response.text}")
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching data from {path}: {e}")
        
    def _retry(self, method: callable, *args) -> dict:
        print("Rate limit exceeded. Czekam 60 sekund przed ponowną próbą...")
        time.sleep(60)
        return method(*args)