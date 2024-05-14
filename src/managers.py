from datetime import datetime
import time

from sqlalchemy.orm import Session
from sqlalchemy.sql import func, cast
from sqlalchemy.sql.functions import concat
from sqlalchemy.dialects.postgresql import INTERVAL, insert
from database.models import MECategories, MEPrices, MEProducts
from database.crud import CRUD
from src.base.extractor_base import PageContent, SitemapContent, SitemapExtractor
from src import browser

from src.me.extractor_me import MECategoryExtractor
from src.me.site_me import MESiteData


class ExtractorManager:
    def __init__(self, site: str):
        match site:
            case "ME":
                self.extractor = MECategoryExtractor
                self.sitemap_extractor = SitemapExtractor
                self.site_data = MESiteData
            case _:
                raise Exception("Site not supported")

    def scrape_full_category(
        self,
        category_path: str,
        max_pages: int = 0,
        timeout: int = 5,
        render_javascript: bool = False,
    ) -> list:
        url = f"{self.site_data.domain}{category_path}?limit=50"
        # Initialize the browser
        b = browser.Browser(render_javascript=render_javascript)
        # Request the first page
        page: PageContent | None = b.visit_url(url=url)
        if not page:
            print("No page in response. Error: ")
            print(b.response_error)
            raise Exception(f"Error while accessing page {url}")
        extractor = self.extractor(page)
        max_pagination = extractor.extract_max_pagination()
        page_count = 0
        products = extractor.extract_category_page()
        if products:
            page_count += 1
        if max_pagination > 1 and not max_pages:
            # Iterate through the rest of the pages
            while page_count <= max_pagination:
                time.sleep(timeout)
                page_count += 1
                print(f"Page {page_count}...")
                url = f"{url}&page={page_count}"
                page: PageContent | None = b.visit_url(url=url)
                if not page:
                    print("No page in response. Error: ")
                    print(b.response_error)
                    continue
                extractor = self.extractor(page)
                products.extend(extractor.extract_category_page())
        return products

    def parse_sitemap_categories(self, sitemap_url: str):
        """Parse categories from the XML sitemap. The most reliable and accurate way of scraping for categories."""
        b = browser.Browser()
        sitemap_content = b.visit_url(sitemap_url, return_type=SitemapContent)
        if type(sitemap_content) != SitemapContent:
            raise Exception("Error while accessing sitemap")
        extractor = self.sitemap_extractor(sitemap_content)
        category_urls = extractor.extract_categories()
        if not category_urls:
            raise Exception("No categories found in sitemap")
        filtered_categories = self.sitemap_extractor.filter_categories(category_urls)

        return filtered_categories


class TaskManager:
    def __init__(self, db: Session, site: str):
        self.site = site
        self.db = db
        match site:
            case "ME":
                self.prices_model = MEPrices
                self.cat_model = MECategories
                self.products_model = MEProducts
            case _:
                raise Exception("Site not supported")

    def find_category_tasks(self, limit: int = 1):
        """Find categories that need to be checked, based on the last check and the check frequency."""
        crud = CRUD(self.cat_model)
        categories = crud.read_multi(
            db=self.db,
            limit=limit,
            sort_col="last_check",
            sort_order="asc",
            filters=[self.cat_model.regular_check.is_(True),
                     self.cat_model.last_check < (func.now() - cast(concat(self.cat_model.check_freq, ' DAYS'), INTERVAL))
                     ]
        )
        return categories

    def insert_or_update_product_list_data(self, category_id: int, products_list: list):
        for product in products_list:
            insert_st = insert(self.products_model).values(product_name=product.name,
                                                    product_code=product.product_code,
                                                    path=product.url,
                                                    category_id=category_id,
                                                    last_update=datetime.now())
            update_st = insert_st.on_conflict_do_update(constraint='me_products_pk',
                                                        set_=dict(last_update=datetime.now()))
            self.db.execute(update_st)
            result = self.db.scalars(update_st.returning(self.products_model.id), execution_options={'populate_existing': True})
            product_id = result.first()
            try:
                # price = int(product['price'][0])
                price = product.price
            except (KeyError, IndexError, ValueError):
                price = None
            price_obj = self.prices_model(product_id=product_id, price=price)
            self.db.add(price_obj)
        self.db.commit()



