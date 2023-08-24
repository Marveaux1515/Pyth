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
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime,timedelta
from selenium.common.exceptions import TimeoutException
import numpy as np,matplotlib.pyplot as plt
import os
PATH=r"C:\Program Files (x86)\chromedriver.exe"

URL="https://app.sidegig.co/login"
DEFAULT_URL="https://app.sidegig.co/tasks/available"
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
        except Exception as e:
            print(e)
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
    def revert_to_default(url=DEFAULT_URL,link=None,cancel=False):
        if cancel:
            try:
                cancel_job=driver.get(link)
                print(cancel_job)
                
                return
            except:
                time.sleep(2)
                revert_to_default(link=link,cancel=cancel)
        else:
            try:
                driver.get(url)
                return
            except:
                time.sleep(2)
                revert_to_default(url,link,cancel)
    def verify_job(user_img_folder,link,desc,username,verify_count=0):
        print("verify_count :",verify_count)
        view_task_status=sidegig_agent.locate("Css","p#last span")
        if view_task_status:
            print("TASK STATUS:  ",view_task_status[0].text)
            if "complete" in view_task_status[0].text.lower():
                revert_to_default()
                return
        
        if verify_count>2:
            revert_to_default()
            return 
        else:
            next_button=sidegig_agent.click("Css","#btn",check_url=False)
        
        if next_button:
            prod_img_path=os.path.join(user_img_folder,f"{time.time()}.png")
            curr_url=driver.current_url
            cap_image=sidegig_agent.snapshot(prod_img_path,"Css","fieldset.current img")
            
            driver.back()
            if cap_image:
                curr_img=os.listdir(user_img_folder)[-1]
                curr_img_path=os.path.join(user_img_folder,curr_img)
                verify_sum=predict_add(curr_img_path)
                if verify_sum:
                    
                    insta_username=INSTAGRAM_DETAILS["username"][user][0]
                    job_details=sidegig_agent.input_([verify_sum],["Id"],["captcha"])
                    if job_details:
                        try:
                            time.sleep(5)
                            job_details.submit()
                            submit=True
                        except:
                            submit=False
                        # sidegig_agent.click("Css","#proof_of_work button",refresh=False,check_url=False)
                        if submit:
                            
                            alert=sidegig_agent.locate("Css",".show p", refresh=False)
                            count=0
                            while not alert:
                                if count>0:
                                    verify_count=1
                                    revert_to_default(url=curr_url)
                                    verify_job(user_img_folder,link,desc,username,verify_count)
                                if driver.current_url in default_urls:
                                    with open(f"{username}.html","a") as f:
                                        f.write(f"<p>{desc[0]}</p><a href='{desc[1]}'>{desc[1]}</a><br><br>")
                                    return
                                alert=sidegig_agent.locate("Css",".show p", refresh=False)
                                count+=1
                            # print("alert \t",alert.text)
                            if alert:
                                alert=alert[0]
                                if "success" in alert.text.lower():
                                    verify_count=0

                                    with open(f"{username}.html","a") as f:
                                        f.write(f"<p>{desc[0]}</p><a href='{desc[1]}'>{desc[1]}</a><br><br>")

                                    return 
                                elif "wrong captcha" in alert.text.lower():
                                    try:
                                        rename_folder=os.path.join("Image_data","Download_rename_images")
                                        if os.path.exists(rename_folder)==False:
                                            os.mkdir(rename_folder)
                                        os.rename(curr_img_path,os.path.join(rename_folder,curr_img))
                                        verify_count+=1
                                        verify_job(user_img_folder,link,desc,username,verify_count)
                                    except:
                                        revert_to_default()
                                        return
                                elif "previously complete" in alert.text.lower():
                                    verify_count=0
                                    print("previously completed")

                                    with open(f"{username}.html","a") as f:
                                        f.write(f"<p>{desc[0]}</p><a href='{desc[1]}'>{desc[1]}</a><br><br>")
                                    revert_to_default()
                                    return 
                                elif "username field" in alert.text.lower():
                                    revert_to_default(link=link,cancel=True)
                                    return
                                else:
                                    revert_to_default()
                                    return
                            else:
                                return
                        else:
                            print("not submitted 0")
                            revert_to_default()
                    else:
                        print("not submitted 1")
                        revert_to_default()
                else:
                   print("not submitted 2")
                   revert_to_default()
            else:
                print("not submitted 3")
                revert_to_default()
        else:
            print("not submitted 4")
            revert_to_default()
        return True


    def side_gig_tab():
        driver.get(URL)
        driver.maximize_window()
        width=driver.get_window_size().get("width")
        height=driver.get_window_size().get("height")
        try:
            #make all threads\windows visible
            driver.set_window_size(870,height)
            driver.set_window_position((width/(num_workers/user))*0.95,0, windowHandle='current')
        except ZeroDivisionError:
            driver.set_window_size(870,height)
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
        input=sidegig_agent.input_([sidegig_username,sidegig_password],["Id","Id"],["email","password"])
        login=sidegig_agent.click("Css",".login",refresh=False)
        
        revert_to_default()
        job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",refresh=False)
        while not job_check and driver.current_url!= DEFAULT_URL:
             driver.get(URL)
             input=sidegig_agent.input_([sidegig_username,sidegig_password],["Id","Id"],["email","password"])
             login=sidegig_agent.click("Css",".button",refresh=False)
             job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",refresh=False)
        driver.get(DEFAULT_URL)
        num_comment=9


        
        job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",base=True)
        print(f"no of jobs = {len(job_check)}")
        while job_check:
            #waiting between job searches 
            time.sleep(1)
            min_rate_index=sidegig_agent.find_min_rate("Css","tbody td:nth-child(4)")
            if min_rate_index:
                cancel_job_link=sidegig_agent.get_attribute_("href","Css",f"tr:nth-child({min_rate_index}) a",multiple=True)[1]
                cancel_job_link=str(cancel_job_link).replace("view","cancel")
                print(cancel_job_link)
                job_elem=sidegig_agent.locate("Css","tbody td:nth-child(1)",refresh=False)
                job_titles=[job.text.lower() for job in job_elem]
                job_title_selected=job_titles[min_rate_index-1]
                
                if user==3 or user==4:
                    if "ig" not in job_title_selected:
                        revert_to_default(link=cancel_job_link,cancel=True)
                        job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",base=True)
                        continue
                else:
                    if "ig" not in job_title_selected and "favor" not in job_title_selected and "yt" not in job_title_selected and "tk" not in job_title_selected:
                        revert_to_default(link=cancel_job_link,cancel=True)
                        job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",base=True)
                        continue
                if num_comment>=10:
                    if "comment" in job_titles[min_rate_index-1] and "premium" not in job_titles[min_rate_index-1] and "birthday" not in job_titles[min_rate_index-1]:
                        revert_to_default(link=cancel_job_link,cancel=True)
                        job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",base=True)
                        continue
                    else:
                        job_title=sidegig_agent.search_job_description("Css",f"tbody tr:nth-child({min_rate_index}) td:nth-child(1)")
                        view_job=sidegig_agent.click("Css",f"tr:nth-child({min_rate_index}) a")
                else:
                    job_title=sidegig_agent.search_job_description("Css",f"tbody tr:nth-child({min_rate_index}) td:nth-child(1)")
                    view_job=sidegig_agent.click("Css",f"tr:nth-child({min_rate_index}) a")
            else:
                
                cancel_job_link=sidegig_agent.get_attribute_("href","Css","tr:nth-child(1) a")
                cancel_job_link=str(cancel_job_link).replace("view","cancel")
                job_title=sidegig_agent.search_job_description("Css","tbody tr:nth-child(1) td:nth-child(1)")
                view_job=sidegig_agent.click("Css","tr:nth-child(1) a")
            if view_job:
                
                if job_title:
                    print("job_title",job_title)
                    if job_title=="comment":
                        num_comment+=1 
                    print("user ", user,":",job_title,"num of comments: ",num_comment)
                    job_link=sidegig_agent.get_attribute_("href","Css",".copyLink a",refresh=False)
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
                            revert_to_default()
                    else:
                        revert_to_default(link=cancel_job_link,cancel=True)
                else:
                    print("BNBFSGSG")
                    revert_to_default(link=cancel_job_link,cancel=True)
            else:
                revert_to_default()
            print("BNDDHD    KKL")
            job_check=sidegig_agent.locate("Css","tbody td:nth-child(3)",base=True)
        return
        
    #lock.release()

    side_gig_tab()

workers=[]
num_workers=3
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

