from abc import ABC
from dataclasses import dataclass

from src.base.extractor_base import CategoryExtractor, ProductExtractor


@dataclass
class Site():
    domain: str
    xpath_selectors: dict
    aliases: list[str] = []
    category_sitemap_url: str | None = None
    product_extractor: ProductExtractor | None = None
    category_extractor: CategoryExtractor | None = None

