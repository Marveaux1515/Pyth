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

def get_stock_data(col_num):
    selector="#datacontainer td:nth-child({})".format(col_num)
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
          EC.presence_of_element_located((By.CSS_SELECTOR,".clickablePageNo")))
    navigation=driver.find_elements_by_css_selector(".clickablePageNo")
    
    for nav_no in range(len(navigation[1:])):
        
        
        ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
        nav=WebDriverWait(driver, 10,ignored_exceptions=ignored_exceptions ).until(
          EC.presence_of_element_located((By.CSS_SELECTOR,"li:nth-child({}) .clickablePageNo".format(nav_no+2))))
        nav.click()
        
        scrape()
    return
def main():
    
    print(driver.title)
    
    
    
    try:
        link=WebDriverWait(driver, 10).until(
              EC.presence_of_element_located((By.CSS_SELECTOR,"#snapshot tr:nth-child(8) td a")))
        link=driver.find_element_by_css_selector("snapshot tr:nth-child(8) td a")
        
    except:
        
        link=driver.find_element_by_css_selector("#snapshot tr:nth-child(8) td a")
    link.click()
    scrape()
    navigate_scrape()
    
    print("\n","\n",stock_dictionary,"\n","\n")
    chosen_companies=["DANGCEM","MTNN","MOBIL","ZENITHBANK"]
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
                          "Volume":None
                          }
        for variable in chosen_stock.keys():
            chosen_stock[variable]=stock_dictionary[variable][idx]
        chosen_stock["Date"]=datetime.now().strftime("%Y-%m-%d")
        filename=r"C:\Users\Administrator\Desktop\D_SCIENCE\practicals\python files/{}_stocks.csv".format(chosen_stock["company"])
        with open(filename,mode="a")as stock_file:
            writer=csv.DictWriter(stock_file,fieldnames=list(chosen_stock.keys()))
            if os.path.getsize(filename)==0 or os.path.exists(filename)==False :
                writer.writeheader()
            writer.writerow(chosen_stock)
    return
    
if __name__=="__main__":
    PATH="C:\Program Files (x86)\chromedriver.exe"
    driver=webdriver.Chrome(PATH)
    driver.get("http://www.nse.com.ng/")
    stock_dictionary={"company":[],
                      "open":[],
                      "High":[],
                      "Low":[],
                      "close":[],
                      "change":[],
                      "Trades":[],
                      "Volume":[]
                      }
    column_numbers=[1,3,4,5,6,7,8,9]
    stock_variables=list(stock_dictionary.keys())
    main()
    


