import os,sys,threading
from time import sleep, time
sys.path.append("..")
from Utils import Locator
from config import SIDEGIG_DETAILS
from selenium import webdriver
CAPTCHA_PATH=r"C:\Users\DELL\Pictures\Sidegig"
DRIVER_PATH=r"C:\Program Files (x86)\chromedriver.exe"
images_folders=os.listdir(CAPTCHA_PATH)
folder_no=len(images_folders)
def save_images(driver,user):
    driver.maximize_window()
    width=driver.get_window_size().get("width")
    height=driver.get_window_size().get("height")

    driver.get(URL)
    image_download_folder=os.path.join(CAPTCHA_PATH,f"Sidegigcaptcha{folder_no}")
    if os.path.exists(image_download_folder)==False:
        os.mkdir(image_download_folder)
    sidegig_username= SIDEGIG_DETAILS["username"][1]
    sidegig_password= SIDEGIG_DETAILS["password"][1]
    #instance of the user defined Locator class
    img_saver=Locator(driver=driver)
    #login details
    input=img_saver.input_([sidegig_username,sidegig_password],["Id","Name"],["user_name","password"])
    if input:
        login=img_saver.click("Id","loginBtn")
    if login:
        pop_up=img_saver.click("Css",".modal-content .modal-footer .btn-secondary")
    if pop_up:
        jobs=img_saver.locate("Css","li:nth-child(4) .side-menu__item",refresh=False)
        if jobs:
            jobs=img_saver.click("Css","li:nth-child(4) .side-menu__item")
        else:
            toggle_bar=img_saver.click("Css",".app-sidebar__toggle")
            if toggle_bar:
                jobs=img_saver.click("Css","li:nth-child(4) .side-menu__item")
        try:
            #make all threads\windows visible
            driver.set_window_size((width/4)*0.95,height)
            driver.set_window_position((width/(4/user))*0.95,0, windowHandle='current')
        except ZeroDivisionError:
            driver.set_window_size((width/4)*0.95,height)
            driver.set_window_position(0,0, windowHandle='current')
    if jobs:
        def get_image():
            num_jobs=img_saver.locate("Css",".btn-primary")
            num_jobs=len(num_jobs)
            idx=1
            while idx <= num_jobs:
                num_jobs=img_saver.locate("Css",".btn-primary")
                num_jobs=len(num_jobs)
                
                view_job=img_saver.click("Css",f"tr:nth-child({idx}) .btn-primary")
                idx+=1
                if view_job:
                    for i in range (2):
                        image_path= os.path.join(image_download_folder,f"image{time()} {user}.png")
                        next_button=img_saver.click("Css",".sw-btn-next")
                        if next_button:
                            captcha_image=img_saver.locate("Css","#completeJob img")
                            if captcha_image:
                                try:
                                    captcha_image[0].screenshot(image_path)
                                    if i==0:
                                        driver.refresh()
                                        sleep(1)
                                    elif i==1:
                                        driver.get(DEFAULT_URL+f"?page={page_no-1}")
                                except:
                                    pass
                            else:
                                driver.get(DEFAULT_URL+f"?page={page_no-1}")
                                continue
                        else:
                            driver.get(DEFAULT_URL+f"?page={page_no-1}")
                            continue
                else:
                    driver.get(DEFAULT_URL+f"?page={page_no-1}")
                    continue
            return 
        page_no=2
        get_image()
        page_no+=1
        #driver.maximize_window()
        navlink=img_saver.locate("Css",".page-link")
        while page_no < len(navlink):
            img_saver.click("Css",f".page-item:nth-child({page_no}) .page-link")
            get_image()
            navlink=img_saver.locate("Css",".page-link")
            page_no+=1
            sleep(3)
        driver.close()
        return

URL="https://dashboard.sidegig.ng/public/account"
DEFAULT_URL="https://dashboard.sidegig.ng/public/account/user/jobs/active"
driver_1=webdriver.Chrome(DRIVER_PATH)
driver_2=webdriver.Chrome(DRIVER_PATH)
driver_3=webdriver.Chrome(DRIVER_PATH)
driver_4=webdriver.Chrome(DRIVER_PATH)
#driver.maximize_window()
first_worker=threading.Thread(target=save_images,args=(driver_1,0))
second_worker=threading.Thread(target=save_images,args=(driver_2,1))
third_worker=threading.Thread(target=save_images,args=(driver_3,2))
fourth_worker=threading.Thread(target=save_images,args=(driver_4,3))
first_worker.start()
second_worker.start()
third_worker.start()
fourth_worker.start()
first_worker.join()
second_worker.join()
third_worker.join()
fourth_worker.join()


