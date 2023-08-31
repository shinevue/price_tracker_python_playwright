class XPathSelector:
    MX = {
        'main_price': ['/html/body/div[1]/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div/span[1]//text()',
                       '/html/body/div[1]/div[2]/div[3]/div/div/div[2]/div/div[3]/div/div[3]/div[1]/div/div/div/div[2]/span[1]//text()'],

        'cents': ['/html/body/div[1]/div[2]/div[3]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/div/div/span[2]/span[1]//text()',
                  '/html/body/div[1]/div[2]/div[3]/div/div/div[2]/div/div[3]/div/div[3]/div[1]/div/div/div/div[2]/span[2]/span[1]//text()']
          }

    class ME:
        # main_price = """//div[@class='price-box']//*[@mainprice][1]/@mainprice"""
        main_price = """//div[contains(@class, 'summary-box')]//div[contains(@class,'summary')]//div[contains(@class, 'price-box')]//div[contains(@class,'main-price')]/@mainprice"""
        product_name = """//h1[@class='name is-title']/text()[1]"""
