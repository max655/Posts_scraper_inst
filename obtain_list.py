from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
from bs4 import BeautifulSoup
import requests

driver = webdriver.Chrome()

driver.get('https://www.instagram.com')
time.sleep(2)
username = 'max423425'
password = '53456maks'

username_input = driver.find_element(By.NAME, 'username')
password_input = driver.find_element(By.NAME, 'password')

username_input.send_keys(username)
password_input.send_keys(password)

password_input.send_keys(Keys.RETURN)

time.sleep(5)

url = 'https://www.instagram.com/explore/tags/qatar/'
driver.get(url)

time.sleep(5)

"""last_height = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.7)
    new_height = driver.execute_script("return document.body.scrollHeight")
    if new_height == last_height:
        break
    last_height = new_height"""

main = driver.find_element(By.TAG_NAME, "main")
div = main.find_element(By.CLASS_NAME, 'x1qjc9v5')
print(div)
images = div.find_elements(By.TAG_NAME, 'img')
print(len(images))
for img in images:
   print(img.get_attribute('src'))
