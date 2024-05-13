from src.logger import Log
from src.manager import TaskManager, ExtractorManager
from database import db

CATEGORIES_LIMIT = 1
ACTIVE_SITES = ["ME"]
log = Log()

if __name__ == "__main__":
    db = db.session
    for site in ACTIVE_SITES:
        task_manager = TaskManager(db, site)
        extractor_manager = ExtractorManager(site)
        # Search for categories to check
        categories = task_manager.find_category_tasks(limit=CATEGORIES_LIMIT)
        if not categories:
            log.write("No categories found")
            exit()
        for category in categories[0]:
            products = extractor_manager.scrape_full_category(
                category_path=category.category_path
            )
            for product in products:
                print(product.name)
                print(product.price)
                print(product.url)
