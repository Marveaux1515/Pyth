# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#import cv2
import sys
sys.path.append("..")
import threading
from config import SIDEGIG_DETAILS, INSTAGRAM_DETAILS
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,re
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
import numpy as np
import pandas as pd
PATH=r"C:\Program Files (x86)\chromedriver.exe"
driver_1=webdriver.Chrome(PATH)
#driver_2=webdriver.Chrome(PATH)
URL="https://dashboard.sidegig.ng/public/account"
lock=threading.Lock()

def agent(user,driver):   
    
    
    def side_gig_tab():
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
        time.sleep(5)
        WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,".modal-content .modal-footer .btn-secondary")))
        close_popup_btn=driver.find_element_by_css_selector(".modal-content .modal-footer .btn-secondary")
        close_popup_btn.click()
        toggle_bar=driver.find_element_by_css_selector(".app-sidebar__toggle")
        toggle_bar.click()
        WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,"li:nth-child(4) .side-menu__item")))
        jobs=driver.find_element_by_css_selector("li:nth-child(4) .side-menu__item")
        jobs.click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "tbody")))
        rates=driver.find_elements_by_css_selector(".table-responsive td:nth-child(5)")
        rates=[rate.text for rate in rates]
        rates= [rate.split("/") for rate in rates]
        int_rates=[[int(rate)for rate in split_rate] for split_rate in rates]
        print(int_rates)
        normalized_rates= [(rate[1]-rate[0])*rate[1] for rate in int_rates]
        normalized_rates=np.log(np.array(normalized_rates))
        minimum_rate=normalized_rates.min()
        #minimum_rate_index=np.random.randint(low=1,high=len(normalized_rates))
        minimum_rate_index=2
        #if len(normalized_rates)>1:
            #minimum_rate_index=normalized_rates.argmin()
        view_job=driver.find_element_by_css_selector("tr:nth-child({}) .btn-primary".format(minimum_rate_index))
        actions.move_to_element(view_job).click().perform()
        time.sleep(5)
       # else:
            #minimum_rate_index=normalized_rates.argmin()
            #view_job=driver.find_element_by_css_selector(".btn-primary".format(minimum_rate_index))
            #actions.move_to_element(view_job).click().perform()
            #time.sleep(5)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "step-1")))
        job_description= driver.find_elements_by_css_selector("#step-1")
        job_terms=[terms.text for terms in job_description]
        def search_job_description(text):
            possible_jobs=["follow","like","comment", "save"]
            match_obj=re.search("(follow).*(like).*",text,re.S|re.I)
            if match_obj:
                job=match_obj.groups()
            else:
                def search_single_job_description(possible_job):
                    match_obj=re.search(f".*({possible_job}).*",text,re.S|re.I)
                    return match_obj
                for possible_job in possible_jobs:
                    match_obj=search_single_job_description(possible_job)
                    if match_obj:
                        job=match_obj.group(1)
                        return job.lower()
                if not match_obj:
                    return None
            return f"{job[0]}_and_{job[1]}".lower()
        print(job_terms, len(job_terms), sep="\n")
        instagram_tab(user,driver)
        def execute_job(job):
            def like():
                def like_and_check():
                    driver.maximize_window()
                    WebDriverWait(driver, 12).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,".fr66n .QBdPU svg._8-yf5")))
                    like_button= driver.find_element_by_css_selector(".fr66n .QBdPU svg._8-yf5")
                    is_liked=like_button.get_attribute("aria-label")
                    if is_liked=="Like":
                        ActionChains(driver).move_to_element(like_button).click().perform()
                        driver.refresh()
                        time.sleep(2)
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,".fr66n .QBdPU svg._8-yf5")))
                        like_button= driver.find_element_by_css_selector(".fr66n .QBdPU svg._8-yf5")
                        is_liked=like_button.get_attribute("aria-label")
                        if is_liked=="Unlike":
                            actions.move_to_element(like_button)
                            driver.back()
                            print("is liked= Sucess")
                            return "Success"
                        else:
                            print("Couldn't like the page")
                            print(f"is liked={is_liked}")
                            driver.back()
                            return "Failed to like"

                    elif is_liked=="Unlike":
                        driver.back()
                        print(f"is liked=Already liked")
                        return "Success"
                    return
                try:
                    like_and_check()
                except TimeoutException:
                    print("error loading page")
                    driver.back()
                except StaleElementReferenceException:
                    driver.refresh()
                    time.sleep(2)
                    like_and_check()
                return
            def follow(remain=False):
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR,"._6VtSN")))
                    follow_button= driver.find_element_by_css_selector("._6VtSN")
                    is_followed=follow_button.text.lower()
                    def check_following():
                        WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR,"._6VtSN")))
                        follow_button= driver.find_element_by_css_selector("._6VtSN span")
                        is_followed=follow_button.get_attribute("aria-label")
                        if is_followed.lower()=="following":
                            print(f"is followed={is_followed}")
                        else:
                            print(is_followed)
                        if not remain:
                            driver.back()
                        return
                    if is_followed !="follow":
                        check_following()
                    else:    
                        follow_button.click()
                        time.sleep(5)
                        driver.refresh()
                        check_following()
                except TimeoutException:
                    print("error loading page")
                    driver.back()
                return
            def follow_and_like():
                remain=True
                z=threading.Thread(target=follow,args=(remain,))
                z.start()
                z.join()
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR,"._bz0w")))
                posts= driver.find_elements_by_css_selector("._bz0w a")
                print(f"post_link_legth is {len(posts)}")
                posts=[post.get_attribute("href") for post in posts[:3]]
                for post_link in posts:
                    print(post_link)
                    driver.get(post_link)
                    time.sleep(5)
                    like()
                return
            eval(job+"()")
            return
        print(minimum_rate, normalized_rates, minimum_rate_index, sep="\n")
        print(driver.window_handles)
        job=search_job_description(str(job_terms))
        job_link= driver.find_elements_by_css_selector("#step-1 a")[0]
        job_link.click()
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(5)
        execute_job(job)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return
        
    #lock.release()
    def instagram_tab(user,driver):
        driver.execute_script("window.open('about:blank', 'tab2');")
        driver.switch_to.window("tab2")
        driver.get('https://www.instagram.com/')
        instagram_username=INSTAGRAM_DETAILS["user_name"][user][0]
        instagram_password=INSTAGRAM_DETAILS["password"][user][0]
        WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.NAME,"username")))
        driver.find_element_by_name("username").send_keys(instagram_username)
        WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.NAME,"password")))
        driver.find_element_by_name("password").send_keys(instagram_password)
        time.sleep(2)
        WebDriverWait(driver, 8).until(
                    EC.presence_of_element_located((By.TAG_NAME,"button")))
        driver.find_elements_by_tag_name("button")[1].click()
        time.sleep(5)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        
        #time.sleep(2)
        return

    side_gig_tab()

x=threading.Thread(target=agent,args=(0,driver_1))
#y=threading.Thread(target=agent, args=(1,driver_2))
x.start()
#y.start()
x.join()
#y.join()
