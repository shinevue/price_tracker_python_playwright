from dataclasses import dataclass


@dataclass
class ME:
    DOMAIN = 'https://www.mediaexpert.pl'
    ALIASES = ['mediaexpert', 'mediaexpert.pl', 'me']
    XPathSelectors = {'category_list': """//div[contains(@class,'menu-category-list')]/ul/li/a/@href""",
                      'inner_categories': """//div[@class='content']//div[@class='row']//a/@href""",
                      'product_url': """//div[@id='section_list-items']//div[@class="offers-list"]//div[@class="offer-box"]//h2[@class='name is-section']//a/@href""",
                      # main_price = """//div[@class='price-box']//*[@mainprice][1]/@mainprice"""
                      'main_price': """//div[contains(@class, 'summary-box')]//div[contains(@class,'summary')]//div[contains(@class, 'price-box')]//div[contains(@class,'main-price')]/@mainprice""",
                      'product_name': """//h1[@class='name is-title']/text()[1]""",

                      'category_page_pagination_limit': """//div[contains(@class,'pagination')]//span[@class='from']/text()""",
                      'product_container_category_page': """//div[@class='offer-box']""",
                      'product_name_category_page': """.//h2[contains(@class,'name')]//a/text()""",
                      'price_category_page': """.//div[@class='prices']//div[contains(@class,'main-price')]/@mainprice""",
                      'product_url_category_page': """.//h2[contains(@class,'name')]//a/@href"""
                      }
