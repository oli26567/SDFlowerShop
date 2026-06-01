class FlowerQueryService:
    def __init__(self, repository):
        self.repository = repository

    def get_catalog(self, color=None, sort=None):
        return self.repository.get_filtered_sorted(color, sort)

    def get_by_id(self, flower_id):
        return self.repository.get_by_id(flower_id)