from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import urllib
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from PyPDF2 import PdfMerger
import streamlit as st
import ssl
import os
import chromedriver_autoinstaller
import img2pdf
ssl._create_default_https_context = ssl._create_unverified_context



def download_score(url, remove = False):
    status_placeholder = st.empty()
    status_placeholder.text("Downloading...")
    progress_bar = st.progress(0)
    chromedriver_autoinstaller.install()
    op = webdriver.ChromeOptions()
    op.add_argument('headless')
    driver = webdriver.Chrome(options = op)
    try:
        driver.get(url)
            
        driver.set_window_size(1050, 1080)

        actions = ActionChains(driver)
        progress_bar.progress(0.2)

        try:
            driver.find_element(By.CLASS_NAME, "Wjhvd")
            ad_1 = driver.find_element(By.CLASS_NAME, "Wjhvd")
            actions.move_to_element(ad_1).click()
            actions.perform()
        except:
            pass
            
        try:
            driver.find_element(By.CLASS_NAME, "jq0nX")
            ad_2 = driver.find_element(By.CLASS_NAME, "jq0nX")
            actions.move_to_element(ad_2).click()
            actions.perform()
        except:
            pass

        score = driver.find_element(By.CLASS_NAME,'XGU1Y')

        actions.move_to_element(score)
        actions.click()

        actions.perform()

        actions_per_page = 19
        score_name = str(driver.find_element(By.CLASS_NAME, "Hn_kk").get_attribute("alt"))
        regex = re.compile('([0-9]+)\sof\s([0-9]+)')
        match_string = regex.search(score_name).group()
        match_list = match_string.split(" ")
        total_page = int(match_list[-1])

        init_page=1
        pdf_list = []
        for i in range(1,actions_per_page*total_page+1):
            actions.key_down(Keys.DOWN)
            if i % actions_per_page ==0:
                
                progress_bar.progress(0.2+0.6*(init_page/total_page))
                status_placeholder.text("Fetching page %d of %d"%(init_page, total_page))
                actions.perform()
                time.sleep(10)
                image_xpath = "//*[@id=\"jmuse-scroller-component\"]/div[%d]/img"%(init_page)
                #image_url = driver.find_element(By.XPATH, image_xpath).get_attribute("src")
                image_url = str(WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, image_xpath))).get_attribute("src"))
                svg_file_name = "score_page_%d.svg"%(init_page)
                png_file_name = "score_page_%d.png"%(init_page)
                pdf_file_name = "score_page_%d.pdf"%(init_page)
                try:
                    urllib.request.urlretrieve(image_url, svg_file_name)
                    drawing = svg2rlg(svg_file_name)
                    renderPDF.drawToFile(drawing, pdf_file_name)   
                    os.remove(svg_file_name) 
                except:
                    urllib.request.urlretrieve(image_url, png_file_name)
                    with open(pdf_file_name, "wb") as f:
                        f.write(img2pdf.convert(png_file_name))
                    os.remove(png_file_name)
                pdf_list.append(pdf_file_name)
                init_page+=1

        merger = PdfMerger()
        for pdf in pdf_list:
            merger.append(pdf)
        final_name = score_name[:(-(len(match_string)+9))]
        merger.write("%s.pdf"%(final_name))
        progress_bar.progress(1.0)
        status_placeholder.text("Download finished")
        merger.close()
        if remove == False:
            for remove_pdf in pdf_list:
                os.remove(remove_pdf)
        driver.close()
    except:
        st.error("Session error, please refresh")
