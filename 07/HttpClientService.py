import requests

class HttpClientService:
    def __init__(self, api_url):
        self._api_url = api_url

    def get(self, path: str) -> dict:
        try:
            response = requests.get(self._api_url + path)
            if response.status_code != 200:
                raise Exception(f"Error fetching data from {path}: {response.status_code} - {response.text}")
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Error fetching data from {path}: {e}")