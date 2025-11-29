from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import re
import csv
import os
from PIL import Image
import hashlib
import json
import io
from loguru import logger


def download_and_hash_image(img_url,save):
    try:
        resp = requests.get(img_url, timeout=10)
        resp.raise_for_status()
        img = Image.open(io.BytesIO(resp.content))
        img_hash = hashlib.sha1(resp.content).hexdigest()[:13]  # 13자리 고유값
        ext = img.format.lower()
        if ext == 'jpeg': ext = 'jpg'
        fname = f"{img_hash}.{ext}"
        img.save(os.path.join(save, fname))
        return fname
    except Exception as e:
        print("이미지 다운로드/해시 오류:", e)
        return None, None
    

# 상세 URL로 이동해 이미지 추출
def get_all_imgs_from_post(driver, post_url):
    imgs = []
    driver.get(post_url)
    time.sleep(3)
    """
    hashtags = []
    try:
        hashtag_a_tags = driver.find_elements(By.CSS_SELECTOR, 'a[href^="/explore/tags"]')
        hashtags = [a.text.strip() for a in hashtag_a_tags if a.text.strip()]
    except Exception as e:
        print("태그 추출 오류:", e)

    """
    # 그냥 태그 추출 X

    while True:
        try:
            img_elem = driver.find_element(By.XPATH, '//img')
            img_url = img_elem.get_attribute('src')
            if img_url not in [i['이미지_url'] for i in imgs]:
                imgs.append({"이미지_url": img_url})
            # 캐러셀 '다음' 버튼
            next_btn = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="다음"], button[aria-label="Next"]')
            next_btn.click()
            time.sleep(1)
        except NoSuchElementException:
            break
        except Exception as e:
            break
    return imgs

def run_instagram_crawl():
    BASE_DIR = os.path.dirname(__file__)
    SAVE_DIR = os.path.join(BASE_DIR, "output")
    METADATA_JSON = os.path.join(SAVE_DIR, "metadata_insta.json")
    os.makedirs(SAVE_DIR, exist_ok=True)

    driver = webdriver.Chrome()
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(30)  # 직접 로그인(수동)

    target_account_url = 'https://www.instagram.com/supermemememememememememe'
    #crawling 하고자 하는 계정에 따라 target_account_url을 바꿔줘야 함
    driver.get(target_account_url)
    time.sleep(5)

    already_seen = set()
    post_urls = []
    metadata_list = []
    data = []

    # 게시물들의 URL만 미리 모으는 파트(블록 → a → href)
    # 계정이나 검색어에 따라 정보가 바뀌므로 밑의 for 문 구문 정보를 수정해줘야함
    # range 안에 있는 숫자는 클수록 많은 정보 긁어옴 
    for _ in range(15):  
        try:
            blocks = driver.find_elements(By.CSS_SELECTOR, 'div._ac7v.x1ty9z65.xzboxd6') #검색어에 따른 수정 필요
            for block in blocks:
                a_tags = block.find_elements(By.TAG_NAME, 'a')
                for a in a_tags:
                    post_url = a.get_attribute('href')
                    if post_url and post_url not in already_seen:
                        already_seen.add(post_url)
                        post_urls.append(post_url)
        except Exception as e:
            print("블록/URL 추출 오류:", e)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)




    # 모든 URL 반복하며 상세 이미지 수집
    for post_url in post_urls:
        try:
            imgs = get_all_imgs_from_post(driver, post_url)
            for img_data in imgs:
                img_url = img_data["이미지_url"]
                fname = download_and_hash_image(img_url,SAVE_DIR)
                metadata_list.append({
                        "fname": fname,
                        "original_url": img_url,
                        "src_url": post_url,
                    })
        except Exception as e:
            print("이미지 추출 오류:", e)

    driver.quit()



    with open(METADATA_JSON, "w", encoding="utf-8") as f:
        json.dump(metadata_list, f, ensure_ascii=False, indent=2)

    logger.info(f"\nSaved {len(metadata_list)} unique images locally in '{SAVE_DIR}'.")
    logger.info(f"Metadata JSON saved to '{METADATA_JSON}'.")

    """
    print(f"저장된 이미지: {len(metadata_list)}개, JSON: {METADATA_JSON}")
    # 데이터 저장은 반드시 마지막에 모든 크롤링 후에!
    with open("output1.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["게시물_url", "이미지_url", "태그", "플랫폼"])
        for item in data:
            writer.writerow([item["게시물_url"], item["이미지_url"], ",".join(item["태그"]), item["플랫폼"]])
    """
    #csv로 저장하는 부분
    logger.info("Instagram crawling & metadata dump done.")
