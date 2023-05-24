# -*- coding: utf-8 -*-
"""
Created on Fri Mar 10 13:37:18 2023

@author: narut
"""

import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager


def fetch_interviewbit_problems(num=700):
  result = []  
  url = "https://www.interviewbit.com/v2/problem_list/"
  
  # page_limit cannot exceed 20 for some reasons
  page_offset, page_limit = 0, 20
  page_num = num // page_limit
  if num % page_limit != 0: page_num += 1
  
  for i in range(page_num):
    params = {
      "page_offset": page_offset,
      "page_limit": page_limit
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
      if response.json()["items"]:
        result.extend(response.json()["items"])
        page_offset += page_limit
    else:
      print("Failed to fetch data")
      print(response)
      return None
  
  return result


def get_ac(wd, title):
# =============================================================================
#   Since the acceptance rate cannot be retrieved from API
#   We have to scrpae it from the website directly
# =============================================================================
  url = f"https://www.interviewbit.com/problems/{title}/"
  wd.get(url)

  try:
    span_elem = wd.find_element(By.CLASS_NAME, "p-tile__problem-success-percentage")
    ac_str = span_elem.text.split("%")[0]
    if ac_str:
      return float(span_elem.text.split("%")[0]) / 100
    else:
      return None
  except (NoSuchElementException,StaleElementReferenceException):
    return None


def get_description(title):
  url = f"https://www.interviewbit.com/problems/{title}/"
  response=requests.get(url)
  
  if response.status_code == 404:
    return None
  
  soup=BeautifulSoup(response.text,"html.parser")
  soup=str(soup)
  result=re.findall(r'\<meta\scontent.*name\=\"description\"\/\>',soup)
  if " Problem Constraints" in result[0]:
    ans=result[0].split(" Problem Constraints")
    ans=re.sub(r'\<meta\scontent\=(\'|\")',"",ans[0])
    ans=re.sub(r"Problem\sDescription\s","",ans)
    ans="".join(ans).split("-") # remove beginning
    ans=ans[1:]
    return "".join(ans)

  else:
    ans=re.findall(r'\-[^\:]*\.(?=[\s\:\w]*)',result[0]) # omit <meta content=\, and cut before first ":" (especially find For example :) 
    if len(ans)==0:
      
      if ":" in result[0]: # no for example
        ans=result[0].split(":") 
        ans=re.sub(r"\<meta\scontent\=(\'|\")","",ans[0])
        ans="".join(ans).split("-") # remove beginnig
        ans=ans[1:]
        
        return "".join(ans)
      else:
        return result
    else:
      ans=re.sub(r'(\'|\"){1}',"",ans[0]) # omit quotation mark
      ans="".join(ans).split("-") # remove beginnimg
      ans=ans[1:]
    return "".join(ans)
  

if __name__ == "__main__":
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--no-sandbox')
  chrome_options.headless = True
  wd = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
  
  p_list = fetch_interviewbit_problems()
  for p in p_list:
    print(p)
  
  
  