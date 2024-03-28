from abc import ABC


class Site(ABC):
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
