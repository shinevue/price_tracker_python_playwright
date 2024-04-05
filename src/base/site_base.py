from abc import ABC

from src.base.extractor_base import Extractor


class Site(ABC):
    def __init__(self, name: str, base_url: str, category_extractor: Extractor):
        self.name = name
        self.base_url = base_url
        self.category_extractor = category_extractor
