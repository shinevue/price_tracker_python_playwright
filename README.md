## Project overview

Object-oriented Python web scraper, capable of retrieving and storing products and prices data from popular e-commerce platforms. Currently, this applications works effectively for one of the biggest Polish electronic online stores.
My initial intention for this project was to build a general purpose object-oriented Python web scraper, however my work shifted to scraping products' prices data over time and storing it. Then, I came up with a scalable project structure idea and implemented it.

## Project structure
Application is divided into two main directories: `database/`, holding code responsible for database connections, ORM models and CRUD operations, and `src/`, holding main application logic, including (the most important):
+ `base/` - abstract base classes, determining the structure of scraping modules responsible for storing scraped pages and extracting specific data from them
+ `me/` - actual implementation of modules defined in `base/` for one of electronic e-commerce stores, ie. site-specific code for data extraction
+ `browser.py` - running & managing Playwright browsers, this is where pages are visited and initially scraped
+ `managers.py` - higher-level, universal (in terms of being site-independent) scraper logic, wrapping up and making use of the site-specific code

## Solutions & technologies used
+ Python
+ Playwright
+ SQLAlchemy ORM
+ Postgres Database
