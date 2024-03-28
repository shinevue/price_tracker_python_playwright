from src.base.scraper_base import CategoryScraper, ProductScraper
from src.base.product_base import Product
from src.exceptions import UnmatchingPrices
from src.logger import Log
from src.me.selectors_me import DomainDataME

from src import utils


log = Log()


class MECategoryScraper(CategoryScraper):
    def extract_products_urls(self) -> list[str | None]:
        ...

    def extract_products_data(self) -> list[Product | None]:
        result = []
        product_codes = []
        try:
            product_codes = self.page.html_tree.xpath('''/html/head/meta[@property='product:skusPage']/@content''')[0].split(',')
        except IndexError:
            print("No product codes found.")
            pass
        product_boxes = self.page.html_tree.xpath(DomainDataME.XPathSelectors['product_container_category_page'])

        assert len(product_codes) == len(product_boxes), f'product codes lenghts doesnt match number of products for site {self.page.url}'

        print('product codes:', product_codes)
        print('product codes count:', len(product_codes))

        empty_prices, coupon_prices, normal_prices = 0, 0, 0
        for index, pc in enumerate(product_boxes):
            product_url, product_name, product_price = [], [], []
            try:
                try:
                    product_url: list = pc.xpath(DomainDataME.XPathSelectors['product_url_category_page'])[0]
                except Exception as e:
                    log.write(f'no product URL found at product #{index}')
                    print('exception:', e)
                try:
                    product_name = pc.xpath(DomainDataME.XPathSelectors['product_name_category_page'])[0].strip()
                except Exception as e:
                    log.write(f'no product name found at product #{index}')
                    print('exception:', e)
                try:
                    product_price: list = pc.xpath(DomainDataME.XSelector.CategoryPage.price)
                    normal_prices += 1 if product_price else normal_prices
                    if not product_price:
                        product_price: list = pc.xpath(DomainDataME.XSelector.CategoryPage.price_with_code)
                        coupon_prices += 1 if product_price else coupon_prices
                        print(f'price after 2 selector: {product_price}')
                    else:
                        empty_prices += 1
                except Exception as e:
                    log.write(f'no price found at product #{index}')
                    print('exception:', e)

                msg = f"""Found prices: \n Normal: {normal_prices}\n Coupon: {coupon_prices}\n Empty: {empty_prices}\n"""
                log.write(msg)
                print(msg)

            except Exception as e:
                print(f"error at {self.page.url}")
                print('exception:', e)

            result.append({'product_name': product_name,
                            'product_code': product_codes[index],
                            'price': product_price,
                            'url': product_url})
        return result


class MEProductScraper(ProductScraper):
    def extract_product_data(self) -> Product:
        product_item = Product()
        product_item.name = self.page.html_tree.xpath(DomainDataME.XPathSelectors['product_name'])[0]
        prices_found = self.page.html_tree.xpath(DomainDataME.XPathSelectors['main_price'])
        if prices_found:
            if utils.compare_list_elements(prices_found):
                product_item.price = float(prices_found[0][:-2] + '.' + prices_found[0][-2:])
            else:
                print('prices_found: ', prices_found)
                raise UnmatchingPrices
        return product_item
