# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
PATH="C:\Program Files (x86)\chromedriver.exe"
driver=webdriver.Chrome(PATH)
URL="https://sidegig.ng/public/account"
driver.get(URL)
actions=ActionChains(driver)
WebDriverWait(driver, 8).until(
              EC.presence_of_element_located((By.ID,"user_name")))
driver.find_element_by_id("user_name").send_keys("Marveaux")
time.sleep(1)
driver.find_element_by_name("password").send_keys("Dunce1515")
time.sleep(2)
driver.find_element_by_id("loginBtn").click()
WebDriverWait(driver, 5).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,"li:nth-child(4) .side-menu__item")))
jobs=driver.find_element_by_css_selector("li:nth-child(4) .side-menu__item")
dashboard=driver.find_element_by_css_selector(".border-0:nth-child(1) h3")
actions.move_to_element(dashboard).click(dashboard).perform()
jobs.click()