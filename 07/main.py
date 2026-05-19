import sys
from HttpClientService import HttpClientService
from ArtistProvider import ArtistProvider
from Extractors import Extractors

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("podaj ID artystów jako argumenty wywołania programu")
        sys.exit(1)

    http_client = HttpClientService("https://api.discogs.com")
    artist_provider = ArtistProvider(http_client)
    extractors = Extractors()
    
    group_to_artists_map = {}
    for arg in sys.argv[1:]:
        try:
            artist_id = int(arg)
            if artist_id <= 0:
                raise ValueError
        except ValueError:
            print(f"Błąd: Podany argument '{arg}' nie jest poprawnym numerycznym identyfikatorem.")
            sys.exit(1)

        try:
            artist_data = artist_provider.get_artist_data(artist_id)
        except Exception as e:
            print(f"Błąd podczas pobierania danych artysty {artist_id}: {e}")
            sys.exit(1)
        
        artist_name = extractors.name_extractor(artist_data)
        groups = extractors.group_extractor(artist_data)
        
        for group in groups:
            if group not in group_to_artists_map:
                group_to_artists_map[group] = []

            if artist_name not in group_to_artists_map[group]:
                group_to_artists_map[group].append(artist_name)
 
    for group in sorted(group_to_artists_map.keys()):
        if len(group_to_artists_map[group]) > 1:
            print(f"{group} -> {', '.join(group_to_artists_map[group])}")
