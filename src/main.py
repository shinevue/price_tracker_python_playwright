from src.logger import Log
from src.managers import TaskManager, ExtractorManager
from database import db

CATEGORIES_LIMIT = 1
ACTIVE_SITES = ["ME"]
log = Log()

if __name__ == "__main__":
    session = db.session
    for site in ACTIVE_SITES:
        task_manager = TaskManager(session, site)
        extractor_manager = ExtractorManager(site)
        # Search for categories to check
        categories = task_manager.find_category_tasks(limit=CATEGORIES_LIMIT)
        if not categories:
            log.write("No categories found")
            exit()
        for category in categories[0]:
            category_id = category.id
            products = extractor_manager.scrape_full_category(
                category_path=category.category_path
            )
            for item in products:
                print(item.name)
                print(item.price)
                print(item.url)
            task_manager.insert_or_update_product_list_data(category_id, products)

