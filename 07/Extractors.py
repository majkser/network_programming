class Extractors:
    @staticmethod
    def group_extractor(artist_data: dict) -> list:
        groups = []
        if 'groups' in artist_data:
            for group in artist_data['groups']:
                groups.append(group.get('name', 'Unknown Group'))
        return groups
    
    @staticmethod
    def name_extractor(artist_data: dict) -> str:
        return artist_data.get('name', 'Unknown Artist')
        