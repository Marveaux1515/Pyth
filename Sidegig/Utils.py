from audioop import mul
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
        self.wait_time=np.random.randint(low=20, high=25)
        self.driver=driver
        self.default_url = "https://app.sidegig.co/tasks/available"
        return
    def refresh(self,style_dict:dict,style_type:str,styling:str,isbase=False)->Union[bool,list]:
        
        try:
            if isbase:
                try:
                    self.driver.get(self.default_url)
                except:
                    self.driver.refresh()
            else:
                self.driver.refresh()
            WebDriverWait(self.driver, self.wait_time).until(
                    EC.presence_of_element_located((style_dict[style_type][0],style_dict[style_type][2])))
            web_element=eval(style_dict[style_type][1])
            
            return web_element
        except Exception as e:
            print(f"refresh exception as {e}",styling, "not found")

            return False
    def locate(self,style_type:str,styling:str,base=False,refresh=True,clickable=False)->Union[bool,list,str]:
        style_dict={'Id':[By.ID,"self.driver.find_element_by_id(styling)",styling],
                    'Name':[By.NAME,"self.driver.find_element_by_name(styling)",styling],
                    'Css':[By.CSS_SELECTOR,"self.driver.find_elements_by_css_selector(styling)",styling],
                    
                    'Tag_name':[By.TAG_NAME,"self.driver.find_elements_by_tag_name(styling)",styling]}
        if base:
            limit=np.inf
            sleep_time=np.random.randint(low=130, high=160)
        else:
            limit=2
            sleep_time=3
        count=0
        try:
            if not clickable:
                WebDriverWait(self.driver, self.wait_time).until(
                        EC.presence_of_element_located((style_dict[style_type][0],style_dict[style_type][2])))
                web_element=eval(style_dict[style_type][1])
                return web_element
            else:
                WebDriverWait(self.driver,self.wait_time).until(
                    EC.element_to_be_clickable((style_dict[style_type][0],style_dict[style_type][2]))
                )
                web_element=eval(style_dict[style_type][1])
                print("clicked")
                return web_element
        except Exception as e:
            print(f"location exception as {e}" ,styling, "not found")
            if refresh:
                islocated=False
                while  not islocated and count <limit:
                    islocated=self.refresh(style_dict,style_type,styling,isbase=base)
                    if self.default_url in self.driver.current_url and not base:
                        return False
                    if islocated:
                        return islocated
                    count+=1
                    time.sleep(sleep_time)
                else:
                    return islocated
            else:
                return False
    def input_(self,input_details:list,style_type:list,styling:list)->bool:
        for i in range(len(input_details)):
            elem=self.locate(style_type[i],styling[i],refresh=False)
            
            if elem:
                try:
                    elem.clear()
                    elem.send_keys(input_details[i])
                except:
                    return False
            else:
                return False
        return elem
    def click(self,style_type:str,styling:str,refresh:bool=True,elem_idx=0,check_url=True,clickable=True)-> bool:
        prev_url=self.driver.current_url
        elem=self.locate(style_type,styling,refresh=refresh,clickable=clickable)
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
        #time.sleep(5)
        curr_url=self.driver.current_url
        print(curr_url,"\t", link)
        if check_url:
            if link:
                count=0
                try:
                    assert curr_url ==link or re.search(f"^{link}[^/.*]",curr_url) is not None
                except AssertionError:
                    if self.default_url in curr_url:
                        return False
                    while curr_url !=link or re.search(f"^{link}[^/.*]",curr_url) is None:
                        if count>2:
                            return False
                        self.driver.get(link)
                        curr_url=self.driver.current_url
                        print(curr_url,"\t", link)
                        if self.default_url in curr_url:
                            return False
                        count+=1
                        time.sleep(5)
            else:
                try:
                    assert prev_url!= curr_url
                except AssertionError:
                    return False
        return True
    def get_attribute_(self,attrib,style_type,styling,multiple=False,refresh=True):
        elem=self.locate(style_type,styling,refresh=refresh)
        
        if elem:
            if isinstance(elem,list):
                if not multiple:
                    attr=elem[0].get_attribute(attrib)
                else:
                    
                    if multiple!=True:
                        if len(elem) > multiple:
                            attr=[element.get_attribute(attrib) for element in elem[:multiple]]
                            print("integ")
                        else:
                            attr=[element.get_attribute(attrib) for element in elem]
                    else:
                        attr=[element.get_attribute(attrib) for element in elem]
                        print("listtype")
            else:
                attr=elem.get_attribute(attrib)
        else:
            return False
        
        return attr
    def snapshot(self,f_path:str,style_type:str,styling:str):
        elem=self.locate(style_type,styling)
        if elem:
            try:
                src=elem[0].get_attribute("src")
                self.driver.get(src)
                elem_s=self.locate("Css","img",refresh=False)
                time.sleep(1)
                return elem_s[0].screenshot(f_path)
            except:
                return False

        else:
            return False
class SideLocator(Locator):
    def __init__(self, driver) -> None:
        super().__init__(driver)
    def search_job_description(self,style_type:str,styling:str)->str:
        elem=self.locate(style_type,styling)
        if elem:
            text=str([terms.text.lower() for terms in elem])
            print(text)
            possible_jobs=["follow","like","wedding","birthday","premium","save","comment","favorite","subscribe","view","share"]
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
            try:
                rates=[rate.text for rate in elem]
                rates= [rate.split("/") for rate in rates]
                int_rates=[[int(rate)for rate in split_rate] for split_rate in rates]
                print(int_rates)
                normalized_rates= [(rate[1]-rate[0])*rate[1] for rate in int_rates]
                normalized_rates=np.log(np.array(normalized_rates))
                minimum_rate=normalized_rates.min()
            except:
                return False
            #minimum_rate_index=np.random.randint(low=1,high=len(normalized_rates))
            #minimum_rate_index=2
            if len(normalized_rates)>1:
                minimum_rate_index=int(normalized_rates.argmin())+1
            else:
                minimum_rate_index=1
            return minimum_rate_index
        else:
            return False
        


