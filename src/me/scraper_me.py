from src.base.scraper_base import CategoryScraper, ProductScraper
from src.base.product_base import Product
from src.exceptions import UnmatchingPrices
from src.logger import Log
from src.me.selectors_me import DomainDataME

from src import utils


log = Log()


class MECategoryScraper(CategoryScraper):
    def extract_max_pagination(self) -> int:
        try:
            limit = self.page.html_tree.xpath(DomainDataME.XPathSelectors['category_page_pagination_limit'])
            if len(limit) == 0:
                return 1
            return int(limit[0])
        except Exception as e:
            print(e)

    def extract_products_data(self) -> list[Product | None]:
        result = []
        product_codes = []
        try:
            product_codes = self.page.html_tree.xpath(
                """/html/head/meta[@property='product:skusPage']/@content"""
            )[0].split(",")
        except IndexError:
            print("No product codes found.")
            log.write(f"Error - {self.page.url} - No product codes found.")

        product_boxes = self.page.html_tree.xpath(
            DomainDataME.XPathSelectors["product_container_category_page"]
        )

        assert (
            len(product_codes) == len(product_boxes)
        ), f"product codes lenghts doesnt match number of products for site {self.page.url}"

        # print("product codes:", product_codes)
        # print("product codes count:", len(product_codes))

        empty_prices, coupon_prices, normal_prices = 0, 0, 0
        for index, pc in enumerate(product_boxes):
            product_url, product_name, product_price = [], [], []
            product = Product(product_code=product_codes[index])
            try:
                try:
                    product_url: list = pc.xpath(
                        DomainDataME.XPathSelectors["product_url_category_page"]
                    )
                    product.url = product_url[0]
                except Exception as e:
                    log.write(f"no product URL found at product #{index}")
                    print("exception:", e)
                try:
                    product_name = pc.xpath(
                        DomainDataME.XPathSelectors["product_name_category_page"]
                    )[0].strip()
                    product.name = product_name
                except Exception as e:
                    log.write(f"no product name found at product #{index}")
                    print("exception:", e)
                try:
                    product_price: list = pc.xpath(
                        DomainDataME.XSelector.CategoryPage.price
                    )
                    if product_price:
                        normal_prices += 1
                    else:
                        product_price: list = pc.xpath(
                            DomainDataME.XSelector.CategoryPage.price_with_code
                        )
                        if product_price:
                            coupon_prices += 1
                        print(f"price after 2 selector: {product_price}")
                    if product_price:
                        product.price = int(product_price[0]) / 100  # Get value in PLN
                    else:
                        empty_prices += 1
                except Exception as e:
                    log.write(f"no price found at product #{index}")
                    print("exception:", e)


            except Exception as e:
                print(f"error at {self.page.url}")
                print("exception:", e)
            result.append(product)

        msg = f"""Found prices: \n Normal: {normal_prices}\n Coupon: {coupon_prices}\n Empty: {empty_prices}\n"""
        log.write(msg)
        print(msg)
        return result


class MEProductScraper(ProductScraper):
    def extract_product_data(self) -> Product:
        product_item = Product()
        product_item.name = self.page.html_tree.xpath(
            DomainDataME.XPathSelectors["product_name"]
        )[0]
        prices_found = self.page.html_tree.xpath(
            DomainDataME.XPathSelectors["main_price"]
        )
        if prices_found:
            if utils.compare_list_elements(prices_found):
                product_item.price = float(
                    prices_found[0][:-2] + "." + prices_found[0][-2:]
                )
            else:
                print("prices_found: ", prices_found)
                raise UnmatchingPrices
        return product_item
