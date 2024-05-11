from sqlalchemy.orm import Session
from src.manager import TaskManager
from database import db


def test_find_category_tasks(db):
    print("testing category tasks")
    task_manager = TaskManager(db, "ME")
    categories = task_manager.find_category_tasks(limit=1)
    for c in categories[0]:
        print(c.__dict__)


if __name__ == "__main__":
    db = db.session
    test_find_category_tasks(db)
