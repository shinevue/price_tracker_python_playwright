import utils
from pw_scraper import PlayScraper

if __name__ == '__main__':
    urls = utils.read_urls('urls.txt')
    for url in urls:
        my_url = PlayScraper(url=url, render_javascript=True)
        my_url.run()
        my_url.content.save_html()
        print(my_url.content)
        print('found_price: ', my_url.content.price)
        # print(etree.tostring(my_url.content.html_tree, pretty_print=True))
