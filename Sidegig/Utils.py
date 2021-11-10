from typing import Union
import numpy as np
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time,re
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException,TimeoutException
from selenium.webdriver.common.action_chains import ActionChains

class Locator():
    def __init__(self,driver) -> None:
        self.wait_time=np.random.randint(low=8, high=12)
        self.driver=driver
        return
    def refresh(self,style_dict:dict,style_type:str,styling:str)->Union[bool,list]:
        self.driver.refresh()
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((style_dict[style_type][0],style_dict[style_type][2])))
            web_element=eval(style_dict[style_type][1])
            return web_element
        except TimeoutException or StaleElementReferenceException or NoSuchElementException as e:
            print(f"refresh exception as {e}",styling, "not found")

            return False
    def locate(self,style_type:str,styling:str,base=False,refresh=True)->Union[bool,list]:
        style_dict={'Id':[By.ID,"self.driver.find_element_by_id(styling)",styling],
                    'Name':[By.NAME,"self.driver.find_element_by_name(styling)",styling],
                    'Css':[By.CSS_SELECTOR,"self.driver.find_elements_by_css_selector(styling)",styling],
                    
                    'Tag_name':[By.TAG_NAME,"self.driver.find_elements_by_tag_name(styling)",styling]}
        if base:
            limit=np.inf
            sleep_time=15
        else:
            limit=1
            sleep_time=5
        count=0
        try:
            WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((style_dict[style_type][0],style_dict[style_type][2])))
            web_element=eval(style_dict[style_type][1])
            return web_element
        except TimeoutException or StaleElementReferenceException or NoSuchElementException as e:
            print(f"location exception as {e}" ,styling, "not found")
            if refresh:
                islocated=False
                while  not islocated and count <=limit:
                    islocated=self.refresh(style_dict,style_type,styling)
                    count+=1
                    time.sleep(sleep_time)
                else:
                    return islocated
            else:
                return False
    def input_(self,input_details:list,style_type:list,styling:list)->bool:
        for i in range(len(input_details)):
            elem=self.locate(style_type[i],styling[i])
            
            if elem:
                elem.send_keys(input_details[i])
            else:
                return False
        return True
    def click(self,style_type:str,styling:str,refresh:bool=True,elem_idx=0)-> bool:
        elem=self.locate(style_type,styling,refresh=refresh)
        style_dict={'Id':[By.ID,"self.driver.find_element_by_id(styling)",styling],
                    'Name':[By.NAME,"self.driver.find_element_by_name(styling)",styling],
                    'Css':[By.CSS_SELECTOR,"self.driver.find_elements_by_css_selector(styling)",styling],
                    'Tag_name':[By.TAG_NAME,"self.driver.find_elements_by_tag_name(styling)",styling]}
        if elem:
            actions=ActionChains(self.driver)
            link=self.get_attribute_("href",style_type,styling)
            if isinstance(elem,list):
                try:
                    elem[elem_idx].click()
                except:
                    try:
                        actions.move_to_element(elem[elem_idx]).click().perform()
                    except:
                        return False
                    
            else:
                try:
                    elem.click()
                except:
                    try:
                        actions.move_to_element(elem).click().perform()
                    except:
                        return False
                    
        else:
            return False
        time.sleep(3)
        curr_url=self.driver.current_url
        print(curr_url,"\t", link)
        """try:
            assert curr_url ==link or re.search(f"{link}$",curr_url) is not None
        except AssertionError:
            while curr_url !=link or re.search(f"{link}$",curr_url) is None:
                self.driver.get(link)
                curr_url=self.driver.current_url"""

        return True
    def get_attribute_(self,attrib,style_type,styling,multiple=False):
        elem=self.locate(style_type,styling)
        if elem:
            if isinstance(elem,list):
                if not multiple:
                    attr=elem[0].get_attribute(attrib)
                else:
                    if len(elem) > multiple:
                        attr=[element.get_attribute for element in elem[:multiple]]
                    else:
                        attr=[element.get_attribute for element in elem]
                
            else:
                attr=elem.get_attribute(attrib)
        else:
            return False
        return attr
    def snapshot(self,f_path:str,style_type:str,styling:str):
        elem=self.locate(style_type,styling)
        if elem:
            return elem[0].screenshot(f_path)
        else:
            return False
    def search_job_description(self,style_type:str,styling:str)->str:
        elem=self.locate(style_type,styling)
        if elem:
            text=str([terms.text for terms in elem])

            possible_jobs=["follow","like","save"]
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
        else:
            return False
    def find_min_rate(self,style_type:str,styling:str)->Union[int,bool]:
        elem=self.locate(style_type,styling)
        if elem:
            rates=[rate.text for rate in elem]
            rates= [rate.split("/") for rate in rates]
            int_rates=[[int(rate)for rate in split_rate] for split_rate in rates]
            print(int_rates)
            normalized_rates= [(rate[1]-rate[0])*rate[1] for rate in int_rates]
            normalized_rates=np.log(np.array(normalized_rates))
            minimum_rate=normalized_rates.min()
            #minimum_rate_index=np.random.randint(low=1,high=len(normalized_rates))
            #minimum_rate_index=2
            if len(normalized_rates)>1:
                minimum_rate_index=int(normalized_rates.argmin())+1
            else:
                minimum_rate_index=1
            return minimum_rate_index
        else:
            return False
        


