"""
Author : Arjun Prakash
Last edit : 19/01
"""

import time
import csv

from fake_useragent import UserAgent

import json
from lxml import html
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


def read_cookies(
        file_path:str
) -> list:
    
    with open(file_path,'r',encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)
        cookie_dict = [row for row in csv_reader]
    
    return cookie_dict

def setup_chrome_driver(
        headless: bool = False
) -> webdriver.Chrome:
    chrome_options = Options()

    if headless:
       chrome_options.add_argument("--headless") 

    ua = UserAgent()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument(f"--user-agent={ua.chrome}")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=chrome_options)

def add_cookies(
        driver: webdriver.Chrome,
        cookies: dict
) -> None:
    
    for cookie in cookies:
        try:
            cook = {
                'name': cookie['Name'],
                'value': cookie['Value'],
                'domain': cookie['Domain'],
                'path': cookie.get('Path', '/'),
                'secure': cookie['Secure'].lower() == 'true',
            }
            driver.add_cookie(cook)

            print(f"Added cookie : {cookie}")
        
        except Exception as e:
            print(f"Error {e} while adding cookie {cookie}")

    driver.refresh()

def wait_for_element(
        driver: webdriver.Chrome,
        by: By,
        value: str,
        timeout: int = 10
) -> WebDriverWait:
    
    return WebDriverWait(driver=driver,timeout=timeout).until(
        EC.presence_of_element_located((by,value))
    )


def click_on_xpath(
        driver: webdriver.Chrome,
        by: By,
        xpath: str,
        timeout: int = 10
) -> None:
    
    button = WebDriverWait(driver=driver,timeout=timeout).until(
        EC.element_to_be_clickable((by.XPATH, xpath))
    )
    button.click()
    print("Xpath clicked successfully")


def extract_content(
        tree: html.parse,
        xpaths: dict
) -> csv:

    output = {}    
    for names,xpath in xpaths.items():
        
        extracts_clean = []
        extracts = tree.xpath(xpath)

        if extracts:
            for extract in extracts:
                extracts_clean.append(extract.strip())
        
        output[names] = extracts_clean
    
    print(f"Extracted {len(xpaths)} Content for tree : {tree}")
    return output

def scrapper_pipeline(
        driver: webdriver.Chrome,
        steps: dict
) -> webdriver.Chrome:
    
    for method,element in steps.items():
        
        method = method.lower()

        if method == 'get':
            driver.get(element)
            print(f"Navigated to: {driver.current_url}")
        
        elif method == 'click':

            try:
                click_on_xpath(
                    driver=driver,
                    by = By,
                    xpath = element,
                    timeout=3
                )
            except Exception as e:
                print(f"Tried clicking on element {element}, but met with an error : {e}")
        
        elif method == 'save':
            page_source = driver.page_source
            with open(f"data/html/{element}","w",encoding='utf-8') as file:
                file.write(page_source)
                print(f"{element} written succusfully")

        elif method == 'extract_and_save':
            
            assert type(element) == dict

            try:
                filename = element['filename']
                xpaths = element['xpaths']

                tree = html.fromstring(driver.page_source)

                output = extract_content(
                    tree=tree,
                    xpaths=xpaths
                )

                with open(f"data/json/{filename}",'w',encoding='utf-8') as file:
                    json.dump(
                        output,
                        file,
                        indent=4,
                        ensure_ascii=False
                    )

            except Exception as e:
                print(f"Skipping extract due to error : {e}")


        elif method == 'sleep':
            print("Sleeping")
            time.sleep(element)
        
        else:
            raise Exception (f"method {method} not yet supported!")

    return driver




