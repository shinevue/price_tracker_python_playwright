from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1200")

driver = webdriver.Chrome(options=options)
driver.get('https://onet.pl')
title = driver.title
print(title)
print(driver.page_source)
