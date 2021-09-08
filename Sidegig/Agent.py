# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#import cv2
import sys
sys.path.append("..")
import threading
from config import SIDEGIG_DETAILS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
PATH=r"C:\Program Files (x86)\chromedriver.exe"
driver_1=webdriver.Chrome(PATH)
driver_2=webdriver.Chrome(PATH)
URL="https://dashboard.sidegig.ng/public/account"
lock=threading.Lock()

def agent(user,driver):   
    
    driver.get(URL)
    driver.maximize_window()
    width=driver.get_window_size().get("width")
    height=driver.get_window_size().get("height")
    driver.set_window_size(width//2,height)
    
    print(height, width)
    if user==1:
        driver.set_window_position(width//2-10,0, windowHandle='current')
    else:
        driver.set_window_position(0,0, windowHandle='current')
    #lock.acquire()
    actions=ActionChains(driver)
    time.sleep(2)
    sidegig_username= SIDEGIG_DETAILS["user_name"][user]
    sidegig_password= SIDEGIG_DETAILS["password"][user]
    WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID,"user_name")))
    driver.find_element_by_id("user_name").send_keys(sidegig_username)
   
    WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.NAME,"password")))
    driver.find_element_by_name("password").send_keys(sidegig_password)
    #time.sleep(2)
    WebDriverWait(driver, 8).until(
                EC.presence_of_element_located((By.ID,"loginBtn")))
    driver.find_element_by_id("loginBtn").click()
    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,".modal-content .modal-footer .btn-secondary")))
    close_popup_btn=driver.find_element_by_css_selector(".modal-content .modal-footer .btn-secondary")
    close_popup_btn.click()
    toggle_bar=driver.find_element_by_css_selector(".app-sidebar__toggle")
    toggle_bar.click()
    WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,"li:nth-child(4) .side-menu__item")))
    jobs=driver.find_element_by_css_selector("li:nth-child(4) .side-menu__item")
    jobs.click()
    print(driver.window_handles)
    #lock.release()
    

x=threading.Thread(target=agent,args=(0,driver_1))
y=threading.Thread(target=agent, args=(1,driver_2))
x.start()
y.start()
x.join()
y.join()
