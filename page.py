from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

browser = webdriver.Firefox()
browser.maximize_window()  # 最大化窗口,可以选择设置
wait = WebDriverWait(browser, 10)

def index_page(page):
    try:
        browser.get('http://data.eastmoney.com/bbsj/201806/lrb.html')
        print('正在爬取第:%s页' % page)
        wait.until(EC.presence_of_element_located((By.ID, "dt_1")))
        # 判断是否是第1页，如果大于1就输入跳转，否则等待加载完成。
        if page > 1:
            # 确定页数输入框
            input = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="PageContgopage"]')))
            input.click()
            input.clear()
            input.send_keys(page)
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#PageCont > a.btn_link')))
            submit.click()
            time.sleep(2)
        # 确认成功跳转到输入框中的指定页
        wait.until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, '#PageCont > span.at'), str(page)))
    except Exception:
        return None

def main():
    for page in range(1, 5):  # 测试翻4页
        index_page(page)

if __name__ == '__main__':
    main()