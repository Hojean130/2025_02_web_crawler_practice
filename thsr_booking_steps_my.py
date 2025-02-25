import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # 用來操作下拉選單
from selenium.common.exceptions import NoSuchElementException  # 處理元素未找到的異常
from ocr_component import get_captcha_code  # 匯入 OCR 元件來識別驗證碼
import pprint
from selenium.webdriver.common.alert import Alert  # 用來處理彈出警告框
import os  # 用來處理環境變數

def create_driver():
    # 配置 Chrome 選項，禁止啟用瀏覽器自動化的提示
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    global driver  # 定義全域變數 driver
    driver = webdriver.Chrome(options=options)  # 初始化 WebDriver
    driver.get("https://irs.thsrc.com.tw/IMINT/?utm_source=thsrc&utm_medium=btnlink&utm_term=booking")  # 打開台灣高鐵訂票頁面


accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")  # 找到接受 Cookie 的按鈕
accept_cookie_button.click()  # 點擊接受

### 
# 第一頁 - 設置訂票基本資料
###
def booking_with_info(start_station, dest_station, start_time, start_date):
    """執行第一步：選擇車站、時間、日期，並通過驗證碼"""
    # 選擇起始站
    start_station = driver.find_element(
        By.XPATH, "//select[@class='uk-select' and @name='selectStartStation']") 
    Select(start_station).select_by_visible_text("台中")  # 選擇「台中」作為起始站

    # 選擇終點站
    dest_station = driver.find_element(
        By.XPATH, "//select[@class='uk-select' and @name='selectDestinationStation']") 
    Select(dest_station).select_by_visible_text("新竹")  # 選擇「新竹」作為終點站

    # 設定出發時間
    start_time = driver.find_element(
        By.XPATH, "//select[@class='uk-select out-time' and @name='toTimeTable']") 
    Select(start_time).select_by_visible_text("18:30")  # 設定出發時間為 18:30

    # 設定出發日期（點擊日期選擇框）
    driver.find_element(
        By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()  # 點擊日期框
    driver.find_element(
        By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()  # 選擇具體日期

    ### 驗證碼處理
    while True:
        # 取得驗證碼圖片並存檔
        picture = driver.find_element(by=By.ID, value='BookingS1Form_homeCaptcha_passCode')
        picture.screenshot('captcha.png')  # 截圖
        captcha_code = get_captcha_code()  # 使用 OCR 解讀圖片中的驗證碼
        picture_input = driver.find_element(By.ID, 'securityCode')
        picture_input.send_keys(captcha_code)  # 輸入解讀出的驗證碼
        time.sleep(2)

        # 送出資料
        driver.find_element(By.ID, 'SubmitButton').click()
        time.sleep(5)

        # 檢查是否成功進入下一步
        try:
            time.sleep(5)
            driver.find_element(By.ID, 'BookingS2Form_TrainQueryDataViewPanel')  # 嘗試找到第二頁的元素
            print("驗證碼正確, 進到第二步驟")  # 驗證碼正確，進入第二步
            break
        except NoSuchElementException:
            print("驗證碼錯誤，重新驗證")  # 如果沒有找到該元素，表示驗證碼錯誤，重新嘗試

    # 查找所有可選的車次資訊
    choose = driver.find_element(By.CLASS_NAME, "result-listing")
    choose = choose.find_elements(By.TAG_NAME, "label")

    # 儲存所有車次的資訊
    thsr_list = []
    i = 0
    for element in choose:
        # 提取每個車次的出發時間、到達時間、行車時間、車次編號
        queryDeparture = element.find_element(By.ID, "QueryDeparture").text
        queryArrival = element.find_element(By.ID, "QueryArrival").text
        durations = element.find_element(By.CLASS_NAME, "duration")
        durations = durations.find_elements(By.TAG_NAME, "span")
        duration = durations[1].text
        train_code = element.find_element(By.ID, "QueryCode").text

        # 找到選擇車次的按鈕（通常是 radio button）
        radio = element.find_element(By.CLASS_NAME, "btn-radio")
        
        # 儲存這些資訊為字典
        thsr_list.append({
            "queryDeparture": queryDeparture,
            "queryArrival": queryArrival,
            "duration": duration,
            "train_code": train_code,
            "radio": radio,
            "A number": i
        })

        i += 1

    # 打印所有車次資訊並讓用戶選擇
    pprint.pprint(thsr_list)
    return thsr_list



def select_train_and_submit_booking(thsr_list):
    """執行第二步：選擇車次並填寫個人資料"""
    # 輸入車次編號
    train_num = int(input("Choose your train: "))  
    # 點擊選擇該車次
    thsr_list[train_num]["radio"].click()  

    # 送出選擇的車次
    driver.find_element(
        By.XPATH, "//input[@name='SubmitButton' and @class='uk-button uk-button-primary uk-button-large btn-next']").click()
    print("選擇車次完成, 進到第三步驟")

    # 截圖保存訂票摘要
    driver.find_element(By.CLASS_NAME, 'ticket-summary').screenshot('thsr_summary.png')

    time.sleep(1)

    # 輸入個人資訊
    id_card = driver.find_element(By.ID, "idNumber")
    personal_id = os.getenv('PERSONAL_ID')  # 從環境變數中獲取身份證字號
    id_card.send_keys(personal_id)

    phone_num = driver.find_element(By.ID, "mobilePhone")
    personal_phone_num = os.getenv('PERSONAL_PHONE_NUMBER')  # 從環境變數中獲取電話號碼
    phone_num.send_keys(personal_phone_num)

    email = driver.find_element(By.ID, "email")
    personal_email = os.getenv('PERSONAL_EMAIL')  # 從環境變數中獲取電子郵件
    email.send_keys(personal_email)


    # 勾選同意條款並提交表單
    driver.find_element(By.XPATH, "//input[@name='agree' and @class='uk-checkbox']").click()
    driver.find_element(By.ID, "isSubmit").click()

    # 訂票完成後截圖
    screenshot_filename = 'thsr_booking_result.png'
    driver.find_element(
        By.CLASS_NAME, "ticket-summary"
    ).screenshot(screenshot_filename)

    print("訂票完成")
    return screenshot_filename


if __name__ == "__main__":
    """主程式執行流程"""
    
    # 訂票參數
    start_station = '台中'
    dest_station = '板橋'
    start_time = '18:00'
    start_date = '二月 25, 2025'

    create_driver()  # 建立瀏覽器驅動
    
    # 執行第一步和第二步：選擇車次
    trains_info = booking_with_info(start_station, dest_station, start_time, start_date)
    
    # 執行第三步和第四步：選擇車次並填寫個人資料
    select_train_and_submit_booking(trains_info)

    time.sleep(10)  # 等待 10 秒確保訂票完成
    driver.quit()  # 關閉瀏覽器








time.sleep(2000)
driver.quit()  # 關閉瀏覽器
