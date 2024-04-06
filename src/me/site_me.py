from dataclasses import dataclass


@dataclass
class MECategorySelectors:
    pagination_limit = """//div[contains(@class,'pagination')]//span[@class='from']/text()"""
    product_container = """//div[@class='offer-box']"""
    product_name = """.//h1[contains(@class, 'name')]/text()"""
    price = """.//div[@class='prices']//div[contains(@class,'main-price')]/@mainprice"""
    price_with_code = """.//div[@class='price-box']//div[contains(@class,'main-price')]/@mainprice"""
    main_price = """//div[contains(@class, 'summary-box')]//div[contains(@class,'summary')]//div[contains(@class, 'price-box')]//div[contains(@class,'main-price')]/@mainprice"""
    product_url = """.//h2[contains(@class,'name')]//a/@href"""
    product_code = """.//div[@class='content']//div[@class='flex-row']//span[contains(@class,'id')]/text()"""



@dataclass
class MESiteData:
    domain = 'https://www.mediaexpert.pl',
    category_sitemap_url = 'https://www.mediaexpert.pl/sitemap/sitemap.product_categories.xml',
    aliases = ['mediaexpert', 'mediaexpert.pl', 'me'],
    xpath_selectors = {'category_list': """//div[contains(@class,'menu-category-list')]/ul/li/a/@href""",
                      'inner_categories': """//div[@class='content']//div[@class='row']//a/@href""",
                      'product_url': """//div[@id='section_list-items']//div[@class="offers-list"]//div[@class="offer-box"]//h2[@class='name is-section']//a/@href""",
                      'main_price': """//div[contains(@class, 'summary-box')]//div[contains(@class,'summary')]//div[contains(@class, 'price-box')]//div[contains(@class,'main-price')]/@mainprice""",
                      'product_name': """//h1[@class='name is-title']/text()[1]""",
                      'category_page_pagination_limit': """//div[contains(@class,'pagination')]//span[@class='from']/text()""",
                      'product_container_category_page': """//div[@class='offer-box']""",
                      'product_name_category_page': """.//h2[contains(@class,'name')]//a/text()""",
                      'price_category_page': """.//div[@class='prices']//div[contains(@class,'main-price')]/@mainprice""",
                      'product_url_category_page': """.//h2[contains(@class,'name')]//a/@href""",
                      'product_code': """.//div[@class='content']//div[@class='flex-row']//span[contains(@class,'id')]/text()"""
                      },

