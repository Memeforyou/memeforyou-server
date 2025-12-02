from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import time
import os
from loguru import logger
from downloader.DLutils import download_image, ImageDL
from preps.dblite import add_meme

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

def run_instagram_scrape(start_id: int, base_path: str) -> int:
    id_cursor = start_id

    driver = webdriver.Chrome()
    driver.get('https://www.instagram.com/accounts/login/')
    time.sleep(30)  # 직접 로그인(수동)

    target_account_url = 'https://www.instagram.com/buzzfeedtasty'
    #crawling 하고자 하는 계정에 따라 target_account_url을 바꿔줘야 함
    driver.get(target_account_url)
    time.sleep(5)

    already_seen = set()
    post_urls = []

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
                save_path = os.path.join(base_path, f"{id_cursor}.jpg")
                dl_response: ImageDL = download_image(url=img_url, save_path=save_path)
                if dl_response.success:
                    add_meme(original_url=img_url, width=dl_response.width, height=dl_response.height, src_url=post_url)
                    logger.info(f"Saved {save_path} from {post_url}")
                    id_cursor += 1
        except Exception as e:
            print("이미지 추출 오류:", e)

    driver.quit()
    logger.info("Instagram crawling & metadata dump done.")
    return id_cursor
