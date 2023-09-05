from dataclasses import dataclass


@dataclass
class ME:
    XPathSelectors = {'category_list': """//div[contains(@class,'menu-category-list')]/ul/li/a/@href""",
                      # main_price = """//div[@class='price-box']//*[@mainprice][1]/@mainprice"""
                      'main_price': """//div[contains(@class, 'summary-box')]//div[contains(@class,'summary')]//div[contains(@class, 'price-box')]//div[contains(@class,'main-price')]/@mainprice""",
                      'product_name': """//h1[@class='name is-title']/text()[1]"""}
