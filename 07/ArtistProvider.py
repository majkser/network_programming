class ArtistProvider:
    def __init__(self, http_client_service):
        self._http_client_service = http_client_service

    def get_artist_data(self, artist_id: int) -> dict:
        return self._http_client_service.get(f'/artists/{artist_id}')