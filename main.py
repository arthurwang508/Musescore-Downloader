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
import streamlit as st
import streamlit.components.v1 as components
import urllib
from webdriver_manager.chrome import ChromeDriverManager
import img2pdf
from selenium.webdriver.chrome.service import Service

ssl._create_default_https_context = ssl._create_unverified_context

st.title("Musecore Downloader")
st.markdown("##### Github link: [Here](https://github.com/arthurwang508/Musescore-Downloader)")
st.write("If there are bugs, please report them here: https://forms.gle/xkeV6UZHV7qSbMkT9")
enter_url = st.text_input("Enter the URL of the Musecore to download:")


chromedriver_autoinstaller.install()
op = webdriver.ChromeOptions()
op.add_argument('headless')
op.add_argument('--no-sandbox')     
op.add_argument('--disable-dev-shm-usage')
#run_driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options = op)
run_driver = webdriver.Chrome(options = op)

def fetch_score(url, driver = run_driver):
    status_placeholder = st.empty()
    status_placeholder.text("Fetching...")
    progress_bar = st.progress(0)
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
    time.sleep(5)
    score = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CLASS_NAME,'DyVse')))
    #score = driver.find_element(By.XPATH, "//*[@id=\"jmuse-scroller-component\"]/div[1]/div[1]")
    #score = driver.find_element(By.CLASS_NAME,'XGU1Y')
    #First class:  "XGU1Y"
    #Second class: "DyVse"

    actions.move_to_element(score)
    actions.click()

    actions.perform()

    actions_per_page = 19
    score_name = str(driver.find_element(By.CLASS_NAME, "GqiX6").get_attribute("alt"))
    #First class: "Hn_kk"
    #Second class: "GqiX6"
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
    #if init_page == total_page:
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    final_name = score_name[:(-(len(match_string)+9))]
    merger.write("score.pdf")
    
    progress_bar.progress(1.0)
    status_placeholder.text("Download finished")
    
    merger.close()
    driver.close()
    return final_name

    
if not enter_url:
    pass
else:
    try:
        urllib.request.urlopen(enter_url)
    except:
        st.error("Please enter a valid musescore link")
    components.html('''
                <iframe width="100%" height = "1000"
                src="{}/embed" 
                frameborder="0" allowfullscreen allow="autoplay; fullscreen"></iframe>
                '''.format(enter_url), height = 1000, scrolling = True)
    
    if st.button("Fetch file"):
        score_name = fetch_score(enter_url)
        def download():
            try:
                with open("score.pdf", "rb") as pdf_file:
                    PDFbyte = pdf_file.read()
                return PDFbyte
            except:
                pass
        try:
            st.download_button(label = "Download score", data = download(), file_name="%s.pdf"%(score_name))
        except:
            pass
    else:
        pass
