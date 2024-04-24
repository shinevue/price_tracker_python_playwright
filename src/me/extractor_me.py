from src.base.extractor_base import CategoryExtractor, ProductExtractor, SitemapExtractor
from src.base.product_base import Product
from src.exceptions import UnmatchingPrices
from src.logger import Log
from src.me.site_me import MECategorySelectors

from src import utils


log = Log()


class MESitemapExtractor(SitemapExtractor):
    pass


class MECategoryExtractor(CategoryExtractor):
    def extract_max_pagination(self) -> int:
        """ Extracts the maximum number of pages from the category page """
        try:
            limit = self.page.html_tree.xpath(MECategorySelectors.pagination_limit)
            if len(limit) == 0:
                return 1
            return int(limit[0])
        except Exception as e:
            print(e)
            return 0

    def extract_category_page(self) -> list[Product | None]:
        """ Extracts all products data from a single category page """
        result = []
        product_codes = []
        try:
            product_codes = self.page.html_tree.xpath(
                """/html/head/meta[@property='product:skusPage']/@content"""
            )[0].split(",")
        except IndexError:
            print("No product codes found.")
            log.write(f"Error - {self.page.url} - No product codes found.")

        product_boxes = self.page.html_tree.xpath(MECategorySelectors.product_container)

        assert (
            len(product_codes) == len(product_boxes)
        ), f"product codes lenghts doesnt match number of products for site {self.page.url}"

        # print("product codes:", product_codes)
        # print("product codes count:", len(product_codes))

        empty_prices, coupon_prices, normal_prices = 0, 0, 0
        for index, pc in enumerate(product_boxes):
            product_url, product_name, product_price = [], [], []
            product = Product(product_code=product_codes[index],
                              name="Unknown")
            try:
                try:
                    product_url: list = pc.xpath(MECategorySelectors.product_url)
                    product.url = product_url[0]
                except Exception as e:
                    log.write(f"no product URL found at product #{index}")
                    print("exception:", e)
                try:
                    for name_regex in MECategorySelectors.product_name:
                        product_name: list = pc.xpath(name_regex)
                        if product_name:
                            product.name = product_name[0].strip()
                            break
                except Exception as e:
                    log.write(f"no product name found at product #{index}")
                    print("exception:", e)
                try:
                    product_price: list = pc.xpath(MECategorySelectors.price)
                    if product_price:
                        normal_prices += 1
                    else:
                        product_price: list = pc.xpath(
                            MECategorySelectors.price_with_code
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

        msg = f"""
        Url Extraction Overview for URL: \n{self.page.url}\n
        --Found prices: \n 
        ----Normal: {normal_prices}\n 
        ----Coupon: {coupon_prices}\n 
        ----Empty: {empty_prices}\n"""
        log.write(msg)
        print(msg)
        return result


class MEProductExtractor(ProductExtractor):
    """ Extracts product data from a single-product page """
    def extract_product_data(self) -> Product:
        product_item = Product()
        for name_regex in MECategorySelectors.product_name:
            product_item.name = self.page.html_tree.xpath(name_regex)[0]
            if product_item.name:
                break
        prices_found = self.page.html_tree.xpath(MECategorySelectors.main_price)
        if prices_found:
            if utils.compare_list_elements(prices_found):
                product_item.price = float(
                    prices_found[0][:-2] + "." + prices_found[0][-2:]
                )
            else:
                print("prices_found: ", prices_found)
                raise UnmatchingPrices
        return product_item
