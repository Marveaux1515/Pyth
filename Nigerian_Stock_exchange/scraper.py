# -*- coding: utf-8 -*-
"""
Created on Fri Dec 18 09:18:23 2020

@author: Administrator
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
import  csv,os
import numpy as np
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains


def get_stock_data(col_num):
    selector="#ngx_equities_trading_statistics td:nth-child({})".format(col_num)
    try:
        stock_data=WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,selector)))
        stock_data=driver.find_elements_by_css_selector(selector)
        
        stock_data=[data.text for data in stock_data]
    except StaleElementReferenceException:
        stock_data=driver.find_elements_by_css_selector(selector)
        
        stock_data=[data.text for data in stock_data]
    return stock_data
def scrape():
    counter=0
    for num in column_numbers:
        stock_data=get_stock_data(num)
        stock_dictionary[stock_variables[counter]].extend(stock_data)
        counter+=1
    return
def navigate_scrape():
    
    navigation=WebDriverWait(driver, 10).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,".paginate_button")))
    navigation=driver.find_elements_by_css_selector(".paginate_button")
    for nav_no in range(len(navigation[3:])):
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
        nav=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions ).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,".paginate_button:nth-child({})".format(nav_no+2))))
        nav.click()
        
        scrape()
    return
def main():
    
    print(driver.title)
    
    
    
    try:
        WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,"#cookie_action_close_header")))
       
        cookie=driver.find_element_by_css_selector("#cookie_action_close_header")
        cookie.click()
    except:
        driver.refresh()
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR,"#cookie_action_close_header")))
            cookie=driver.find_element_by_css_selector("#cookie_action_close_header")
            cookie.click()
        except NoSuchElementException:
            pass
    
    
    scrape()
    navigate_scrape()
    
    print("\n","\n",stock_dictionary,"\n","\n")
    chosen_companies=["DANGCEM","GLAXOSMITH","MTNN","NESTLE","CONOIL","ZENITHBANK"]
    chosen_stock_indices=[stock_dictionary["company"].index(value) for value in chosen_companies if value in stock_dictionary["company"]]
    print(chosen_stock_indices)
    for idx in chosen_stock_indices:    
        chosen_stock={"company":None,
                          "open":None,
                          "High":None,
                          "Low":None,
                          "close":None,
                          "change":None,
                          "Trades":None,
                          "Volume":None,
                          "Date":None
                          }
        for variable in chosen_stock.keys():
            chosen_stock[variable]=stock_dictionary[variable][idx]
        
        filename="Companies_stock_data\{}_stocks.csv".format(chosen_stock["company"])
        with open(filename,mode="a")as stock_file:
            writer=csv.DictWriter(stock_file,fieldnames=list(chosen_stock.keys()))
            if os.path.getsize(filename)==0 or os.path.exists(filename)==False :
                writer.writeheader()
            writer.writerow(chosen_stock)
    complete_stock_data=pd.DataFrame(stock_dictionary)
    complete_stock_data.to_csv(FULL_STOCK_FILE, mode="a")

    return
    
if __name__=="__main__":
    PATH="C:\Program Files (x86)\chromedriver.exe"
    FULL_STOCK_FILE="Companies_stock_data\Complete_Nigerian_Stock_Exchange_Data.csv"
    driver=webdriver.Chrome(PATH)
    driver.get("https://ngxgroup.com/exchange/data/equities-price-list/")
    stock_dictionary={"company":[],
                      "open":[],
                      "High":[],
                      "Low":[],
                      "close":[],
                      "change":[],
                      "Trades":[],
                      "Volume":[],
                      "Date":[]
                      }
    column_numbers=[1,3,4,5,6,7,8,9,11]
    stock_variables=list(stock_dictionary.keys())
    main()
    


