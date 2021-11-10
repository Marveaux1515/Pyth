# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#import cv2
import sys
sys.path.append("..")
import threading
from model import predict_img,mode,cls_map
from config import SIDEGIG_DETAILS, INSTAGRAM_DETAILS
from Utils import Locator
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from tensorflow.keras import models
import numpy as np,matplotlib.pyplot as plt
import pandas as pd,os
PATH=r"C:\Program Files (x86)\chromedriver.exe"

URL="https://dashboard.sidegig.ng/public/account"
DEFAULT_URL="https://dashboard.sidegig.ng/public/account/user/jobs/active"
default_urls=[DEFAULT_URL,DEFAULT_URL+"/#step_1",DEFAULT_URL+"/#step-2"]
lock=threading.Lock()
PROD_IMAGE_FOLDER=os.path.join("Image_data","Prod_images")
if not os.path.exists(PROD_IMAGE_FOLDER):
    os.mkdir(PROD_IMAGE_FOLDER)

def agent(user,driver):   
    
    sidegig_agent=Locator(driver)
    def like():
        is_liked=sidegig_agent.get_attribute_("aria-label","Css",".fr66n .QBdPU svg._8-yf5")
        if is_liked=="Like":
            like_click=sidegig_agent.click("Css",".fr66n .QBdPU svg._8-yf5")
            driver.refresh()
            time.sleep(2)
            is_liked=sidegig_agent.get_attribute_("aria-label","Css",".fr66n .QBdPU svg._8-yf5")
            if is_liked=="Unlike":
                driver.back()
            else:
                driver.back()
                return False
        elif is_liked=="Unlike":
            driver.back()
        else:
            driver.back()
            return False
        return True
    def check_following(remain):
        fol_state=sidegig_agent.get_attribute_("aria-label","Css","._6VtSN")
        if fol_state.lower()=="following":
            print(f"is followed={fol_state}")
        else:
            print(fol_state)
            return False
        if not remain:
            driver.back()
        return True
    def follow(remain=False):
        try:
            follow_button= sidegig_agent.locate("Css","._6VtSN")
            if follow_button:
                follow_stat=follow_button.text.lower()
            
                if follow_stat !="follow":
                    isfollowed=check_following(remain)
                else:    
                    sidegig_agent.click("Css","._6VtSN")
                    time.sleep(5)
                    driver.refresh()
                    isfollowed=check_following(remain)
            else:
                driver.back()
                return False
        except TimeoutException:
            print("error loading page")
            driver.back()
            return False
        return isfollowed
    def follow_and_like():
        remain=True
        z=threading.Thread(target=follow,args=(remain,))
        z.start()
        z.join()
        if not z :return False
        posts=sidegig_agent.get_attribute_("href","Css","._bz0w a",multiple=2)
        for post_link in posts:
            print(post_link)
            driver.get(post_link)
            time.sleep(5)
            isliked=like()
            if not isliked: return False
        driver.back()
        return True

    def execute_job(job):
        return eval(f"{job}()",{"follow_and_like":follow_and_like,"follow":follow,"like":like})
    def instagram_tab(user,driver):
        driver.execute_script("window.open('about:blank', 'tab2');")
        driver.switch_to.window("tab2")
        driver.get('https://www.instagram.com/')
        instagram_username=INSTAGRAM_DETAILS["username"][user][0]
        instagram_password=INSTAGRAM_DETAILS["password"][user][0]
        sidegig_agent.input_([instagram_username,instagram_password],["Name","Name"],["username","password"])
        time.sleep(2)
        sidegig_agent.click("Tag_name","button",elem_idx=1)
        time.sleep(7)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
        return
    def preprocess_img(img_path):
        img_array=plt.imread(img_path)
        height, width, channels=36,120,4
        img_array=img_array.reshape(height, width,channels)
        img_arr_1=img_array[:,:img_array.shape[1]//2,:]
        img_arr_2=img_array[:,img_array.shape[1]//2:,:]
        return [img_arr_1,img_arr_2]
    def predict_add(img_path):
        height, width,channels=36,60,4
        sum=0
        for i,img_array in enumerate(preprocess_img(img_path)):
            img_array=img_array.reshape(1,height, width,channels)
            value=predict_img(img_array,model=mode[i],mapp=cls_map[i])
            sum+=value
        return sum
    def verify_job(user_img_folder):
        next_button=sidegig_agent.click("Css",".sw-btn-next")
        if next_button:
            prod_img_path=os.path.join(user_img_folder,f"{time.time()}.png")
            cap_image=sidegig_agent.snapshot(prod_img_path,"Css","#completeJob img")
            if cap_image:
                curr_img=os.listdir(user_img_folder)[-1]
                curr_img_path=os.path.join(user_img_folder,curr_img)
                verify_sum=predict_add(curr_img_path)
                if verify_sum:
                    insta_username=INSTAGRAM_DETAILS["username"][user][0]
                    job_details=sidegig_agent.input_([insta_username,verify_sum],["Id","Id"],["proof_text","captcha"])
                    if job_details:
                        submit=sidegig_agent.click("Id","btn-completeJob",refresh=False)
                        if submit:
                            time.sleep(7)
                            try:
                                assert driver.current_url in default_urls
                            except:
                                is_job_complete=sidegig_agent.locate("Css",".table-responsive",refresh=False)
                                if is_job_complete:
                                    return
                                elif sidegig_agent.locate("Css",".sw-btn-next"):
                                    #TODO call a function
                                    verify_job(user_img_folder)
                                    pass
                        else:
                            #TODO
                            pass
                    else:
                        #TODO
                        pass
                else:
                    #TODO
                    pass
            else:
                #TODO
                pass
        else:
            #TODO
            pass
        return


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
        sidegig_username= SIDEGIG_DETAILS["username"][user]
        sidegig_password= SIDEGIG_DETAILS["password"][user]
        user_img_folder=os.path.join(PROD_IMAGE_FOLDER, str(user))
        if os.path.exists(user_img_folder)==False:
            os.mkdir(user_img_folder)
        #input login details
        input=sidegig_agent.input_([sidegig_username,sidegig_password],["Id","Name"],["user_name","password"])
        if input:
            login=sidegig_agent.click("Id","loginBtn")
            if login:
                pop_up=sidegig_agent.click("Css",".modal-content .modal-footer .btn-secondary")
                if pop_up:
                    jobs=sidegig_agent.click("Css","li:nth-child(4) .side-menu__item",refresh=False)
                    if jobs:
                        pass
                    else:
                        driver.get(DEFAULT_URL)
                    job_check=sidegig_agent.locate("Css","tbody",base=True)
                    min_rate_index=sidegig_agent.find_min_rate("Css",".table-responsive td:nth-child(5)")
                    if min_rate_index:
                        view_job=sidegig_agent.click("Css",f"tr:nth-child({min_rate_index}) .btn-primary")
                    else:
                        view_job=sidegig_agent.click("Css",f"tr:nth-child({1}) .btn-primary")
                    if view_job:
                        job_description=sidegig_agent.search_job_description("Css","#step-1")
                        if job_description:
                            #instagram_tab(user,driver)
                            print("user ", user,":",job_description)
                            job_link=sidegig_agent.click("Css","#step-1 a")
                            if job_link:
                                time.sleep(5)
                                job_completed=execute_job(job_description)
                                job_completed=True
                                if len(driver.window_handles)>1:
                                    driver.close()
                                    driver.switch_to.window(driver.window_handles[0])
                                if job_completed:
                                    verify_job(user_img_folder)
                                else:
                                    #TODO
                                    pass
                            else:
                                #TODO
                                pass
                        else:
                            #TODO
                            pass
                    else:
                        #TODO
                        pass
                else:
                    #TODO
                    pass
            else:
                #TODO
                pass
        else:
            #TODO
            pass
       
        
        return
        
    #lock.release()

    side_gig_tab()

workers=[]
num_workers=1
for worker in range(num_workers):
    driver=webdriver.Chrome(PATH)
    thread_worker=threading.Thread(target=agent,args=(worker,driver))
    workers.append(thread_worker)
    thread_worker.start()
for trd_wrkr in workers:
    trd_wrkr.join()

