import os,sys,threading
from time import sleep, time
sys.path.append("..")
from Utils import Locator
from config import SIDEGIG_DETAILS
from selenium import webdriver
CAPTCHA_PATH=r"C:\Users\DELL\Pictures\Sidegig"
PATH=r"C:\Program Files (x86)\chromedriver.exe"
images_folders=os.listdir(CAPTCHA_PATH)
folder_no=len(images_folders)
#images=os.listdir(f"{CAPTCHA_PATH}\\{images_folders[0]}")
"""for dir in images_folders:
    images=f"{CAPTCHA_PATH2}\\{dir}"
    for image in os.listdir(images):
        os.rename(f"{images}\\{image}",f"{images}\\{image[:-4]} {dir}.png")
    print(os.listdir(images))"""
def save_images(driver,user):
    driver.maximize_window()
    width=driver.get_window_size().get("width")
    height=driver.get_window_size().get("height")
    driver.set_window_size(width,height//2)
    if user==1:
        driver.set_window_position(0,height//2-10, windowHandle='current')
    else:
        driver.set_window_position(0,0, windowHandle='current')
    driver.get(URL)
    image_download_folder=os.path.join(CAPTCHA_PATH,f"Sidegigcaptcha{folder_no}")
    if os.path.exists(image_download_folder)==False:
        os.mkdir(image_download_folder)
    sidegig_username= SIDEGIG_DETAILS["username"][1]
    sidegig_password= SIDEGIG_DETAILS["password"][1]
    img_saver=Locator(driver=driver)
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
    if jobs:
        def get_image():
            num_jobs=img_saver.locate("Css",".btn-primary")
            num_jobs=len(num_jobs)

            for idx in range(num_jobs):
                num_jobs=img_saver.locate("Css",".btn-primary")
                num_jobs=len(num_jobs)
                image_path= os.path.join(image_download_folder,f"image{time()}.png")
                ind=idx+1
                view_job=img_saver.click("Css",f"tr:nth-child({ind}) .btn-primary")
                if view_job:
                    next_button=img_saver.click("Css",".sw-btn-next")
                    if next_button:
                        sleep(2)
                        captcha_image=img_saver.locate("Css","#completeJob img")
                        if captcha_image:
                            captcha_image[0].screenshot(image_path)
                            driver.get(DEFAULT_URL+f"?page={page_no-1}")
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
        #driver.maximize_window()
        navlink=img_saver.locate("Css",".page-link")
        for page_no in range(3,len(navlink)):
            img_saver.click("Css",f".page-item:nth-child({page_no}) .page-link")
            get_image()
            sleep(3)
        return

URL="https://dashboard.sidegig.ng/public/account"
DEFAULT_URL="https://dashboard.sidegig.ng/public/account/user/jobs/active"
driver_1=webdriver.Chrome(PATH)
driver_2=webdriver.Chrome(PATH)
#driver.maximize_window()
first_worker=threading.Thread(target=save_images,args=(driver_1,0))
second_worker=threading.Thread(target=save_images,args=(driver_2,1))
first_worker.start()
second_worker.start()
first_worker.join()
second_worker.join()


