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
from Utils import SideLocator
from selenium import webdriver
from selenium.webdriver.common.alert import Alert
import time
from datetime import datetime,timedelta
from selenium.common.exceptions import TimeoutException
import numpy as np,matplotlib.pyplot as plt
import os
PATH=r"C:\Program Files (x86)\chromedriver.exe"

URL="https://app.sidegig.co"
DEFAULT_URL="https://app.sidegig.co/account/user/jobs/active"
default_urls=[DEFAULT_URL,DEFAULT_URL+"#step_1",DEFAULT_URL+"#step-2"]
lock=threading.Lock()
PROD_IMAGE_FOLDER=os.path.join("Image_data","Prod_images")
if not os.path.exists(PROD_IMAGE_FOLDER):
    os.mkdir(PROD_IMAGE_FOLDER)

def agent(user,driver):   
    
    sidegig_agent=SideLocator(driver)
    def like():
        try:
            is_liked=sidegig_agent.get_attribute_("aria-label","Css",".fr66n .QBdPU svg._8-yf5")
            if is_liked=="Like":
                like_click=sidegig_agent.click("Css",".fr66n .QBdPU svg._8-yf5",check_url=False)
                time.sleep(4)
                driver.back()
            elif is_liked=="Unlike":
                driver.back()
            else:
                driver.back()
                return False
            return True
        except:
            return False
    def check_following(remain):
        print("checking-follow..........")
        fol_state=sidegig_agent.get_attribute_("aria-label","Css","._6VtSN")
        print()
        if fol_state:
            if fol_state.lower()=="following":
                print(f"is followed={fol_state}")
            else:
                print(fol_state)
                return False
            if not remain:
                driver.back()
        else:
            return False
        return True
    def follow(remain=False):
        try:
            follow_button= sidegig_agent.locate("Css","._6VtSN")
            if follow_button:
                follow_stat=follow_button[0].text.lower()
                print("follow_status = ",follow_stat)
                if follow_stat !="follow":
                    isfollowed=check_following(remain)
                else:    
                    follow_click=sidegig_agent.click("Css","._6VtSN",check_url=False)
                    time.sleep(5)
                    isfollowed=True
                    driver.back()
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
            time.sleep(3)
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
        time.sleep(9)
        #driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)
        return
    def preprocess_img(img_path):
        img_array=plt.imread(img_path)
        height, width, channels=36,120,4
        try:
            img_array=img_array.reshape(img_array.shape[0], width,channels)
            img_arr_1=img_array[:,:img_array.shape[1]//2,:]
            img_arr_2=img_array[:,img_array.shape[1]//2:,:]
            return [img_arr_1,img_arr_2]
        except:
            return
    def predict_add(img_path):
        height, width,channels=36,60,4
        sum=0
        img_processed=preprocess_img(img_path)
        if not img_processed:
            return None
        for i,img_array in enumerate(img_processed):
            print(img_array.shape)
            img_array=img_array.reshape(1,img_array.shape[0], width,channels)
            value=predict_img(img_array,model=mode[i],mapp=cls_map[i])
            sum+=value
        return sum
    def revert_to_default(link,cancel=False):
        
        driver.get(DEFAULT_URL)
        if cancel:
            try:
                cancel_job=driver.get(link)
                print(cancel_job)
                return
            except:
                return
        else:
            return
    def verify_job(user_img_folder,link,desc,username,verify_count=0):
        print("verify_count :",verify_count)
        if verify_count>2:
            driver.get(DEFAULT_URL)
            return 
        elif verify_count>=1:
            next_button=True
        else:
            next_button=sidegig_agent.click("Css",".sw-btn-next")
        
        if next_button:
            prod_img_path=os.path.join(user_img_folder,f"{time.time()}.png")
            time.sleep(1)
            cap_image=sidegig_agent.snapshot(prod_img_path,"Css","#completeJob img")
            if cap_image:
                curr_img=os.listdir(user_img_folder)[-1]
                curr_img_path=os.path.join(user_img_folder,curr_img)
                verify_sum=predict_add(curr_img_path)
                if verify_sum:
                    insta_username=INSTAGRAM_DETAILS["username"][user][0]
                    job_details=sidegig_agent.input_([insta_username,verify_sum],["Id","Id"],["proof_text_2","captcha"])
                    if job_details:
                        submit=sidegig_agent.click("Id","btn-completeJob",refresh=False,check_url=False)
                        if submit:
                            
                            alert=sidegig_agent.locate("Id","toast-container", refresh=False)
                            count=0
                            while not alert:
                                if count>0:
                                    driver.refresh()
                                    if driver.current_url in default_urls:
                                        return
                                    verify_count=1
                                    verify_job(user_img_folder,link,desc,username,verify_count)
                                if driver.current_url in default_urls:
                                    break
                                alert=sidegig_agent.locate("Id","toast-container", refresh=False)
                                count+=1
                            print("alert \t",alert.text)
                            if "success" in alert.text.lower():
                                verify_count=0
                                with open(f"{username}.html","a") as f:
                                    f.write(f"<p>{desc[0]}</p><a href='{desc[1]}'>{desc[1]}</a><br><br>")

                                return 
                            elif "invalid" in alert.text.lower():
                                rename_folder=os.path.join("Image_data","Download_rename_images")
                                if os.path.exists(rename_folder)==False:
                                    os.mkdir(rename_folder)
                                os.rename(curr_img_path,os.path.join(rename_folder,curr_img))
                                driver.refresh()
                                if driver.current_url in default_urls:
                                    return
                                verify_count+=1
                                verify_job(user_img_folder,link,desc,username,verify_count)
                            else:
                                driver.get(DEFAULT_URL)
                                return
                        else:
                            print("not submitted 0")
                            revert_to_default(link)
                    else:
                        print("not submitted 1")
                        revert_to_default(link)
                else:
                   print("not submitted 2")
                   revert_to_default(link)
            else:
                print("not submitted 3")
                revert_to_default(link)
        else:
            print("not submitted 4")
            revert_to_default(link)
        return True


    def side_gig_tab():
        driver.get(URL)
        driver.maximize_window()
        width=driver.get_window_size().get("width")
        height=driver.get_window_size().get("height")
        try:
            #make all threads\windows visible
            driver.set_window_size((width/num_workers)*0.95,height)
            driver.set_window_position((width/(num_workers/user))*0.95,0, windowHandle='current')
        except ZeroDivisionError:
            driver.set_window_size((width/num_workers)*0.95,height)
            driver.set_window_position(0,0, windowHandle='current')
        #lock.acquire()
        #actions=ActionChains(driver)
        time.sleep(2)
        sidegig_username= SIDEGIG_DETAILS["username"][user]
        sidegig_password= SIDEGIG_DETAILS["password"][user]
        user_img_folder=os.path.join(PROD_IMAGE_FOLDER, str(user))
        if os.path.exists(user_img_folder)==False:
            os.mkdir(user_img_folder)
        #input login details
        #instagram_tab(user,driver)
        input=sidegig_agent.input_([sidegig_username,sidegig_password],["Id","Name"],["user_name","password"])
        login=sidegig_agent.click("Id","loginBtn",refresh=False)
        alert=sidegig_agent.locate("Id","toast-container", refresh=False)
        #print(f" {alert.text.lower()} \n {'success' in alert.text.lower()}")
        while not alert:
            driver.refresh()
            input=sidegig_agent.input_([sidegig_username,sidegig_password],["Id","Name"],["user_name","password"])
            login=sidegig_agent.click("Id","loginBtn",refresh=False)
            alert=sidegig_agent.locate("Id","toast-container", refresh=False)
        else:
            pop_up=sidegig_agent.locate("Css",".modal-content .modal-footer .btn-secondary")
            
        driver.get(DEFAULT_URL)
        job_check=sidegig_agent.locate("Css","tbody td:nth-child(6)",base=True)
        print(f"no of jobs = {len(job_check)}")
        while job_check:
            #waiting between job searches
            time.sleep(3)
            min_rate_index=sidegig_agent.find_min_rate("Css",".table-responsive td:nth-child(5)")
            if min_rate_index:
                cancel_job_link=sidegig_agent.get_attribute_("href","Css",f"tr:nth-child({min_rate_index}) .confirmation")
                view_job=sidegig_agent.click("Css",f"tr:nth-child({min_rate_index}) .btn-primary")
            else:
                cancel_job_link=sidegig_agent.get_attribute_("href","Css",f"tr:nth-child({1}) .confirmation")
                view_job=sidegig_agent.click("Css",f"tr:nth-child({1}) .btn-primary")
            if view_job:
                job_title=sidegig_agent.search_job_description("Css","#step-1")
                if job_title:
                    print("user ", user,":",job_title)
                    job_link=sidegig_agent.get_attribute_("href","Css","#step-1 a",refresh=False)
                    if job_link:
                        #time.sleep(5)
                        #job_completed=execute_job(job_title)
                        job_completed=True
                        if len(driver.window_handles)>2:
                            driver.close()
                            driver.switch_to.window(driver.window_handles[0])
                        if job_completed:
                            job_description=(job_title, job_link)
                            verify_job(user_img_folder,cancel_job_link,job_description,sidegig_username)
                        else:
                            revert_to_default(cancel_job_link)
                    else:
                        revert_to_default(cancel_job_link,cancel=True)
                else:
                    print("BNBFSGSG")
                    revert_to_default(cancel_job_link)
            else:
                driver.refresh()
            print("BNDDHD    KKL")
            job_check=sidegig_agent.locate("Css","tbody td:nth-child(6)",base=True)
        return
        
    #lock.release()

    side_gig_tab()

workers=[]
num_workers=2
options=webdriver.ChromeOptions()
# options.add_argument("--disable-dev-shm-usage")
# options.add_argument("--no-sandbox")
# options.add_argument("--remote-debugging-port=9222")
for worker_id in range(num_workers):
    driver=webdriver.Chrome(PATH,options=options)
    thread_worker=threading.Thread(target=agent,args=(worker_id,driver))
    workers.append(thread_worker)
    thread_worker.start()
for trd_wrkr in workers:
    trd_wrkr.join()

