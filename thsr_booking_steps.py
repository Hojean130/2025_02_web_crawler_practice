import pprint
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select  # 用於處理下拉式選單
from selenium.common.exceptions import NoSuchElementException  # 用於捕捉異常錯誤
from ocr_component import get_captcha_code  # OCR 辨識驗證碼函式

# Project import from from booking_info_extraction_flow
from booking_info_extraction_flow import (
    ask_booking_infomation,
    ask_missing_infomation,
    convert_date_to_thsr_format
)


def create_driver():
    """建立 Selenium WebDriver 並開啟高鐵訂票網站"""
    options = webdriver.ChromeOptions()  # 建立 Chrome 選項物件
    options.add_argument("--disable-blink-features=AutomationControlled")  # 避免被網站偵測為自動化工具
    global driver  # 定義全域變數 driver
    driver = webdriver.Chrome(options=options)  # 建立 Chrome 瀏覽器實例
    driver.get("https://irs.thsrc.com.tw/IMINT/")  # 開啟高鐵訂票網站


def booking_with_info(start_station, dest_station, start_time, start_date):
    """執行第一步：選擇車站、時間、日期，並通過驗證碼"""
    
    # 點擊接受 Cookie 按鈕
    accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")
    accept_cookie_button.click()

    # 選擇起點站
    start_station_element = driver.find_element(By.NAME, 'selectStartStation')
    Select(start_station_element).select_by_visible_text(start_station)

    # 選擇終點站
    dest_station_element = driver.find_element(By.NAME, 'selectDestinationStation')
    Select(dest_station_element).select_by_visible_text(dest_station)

    # 選擇出發時間
    start_time_element = driver.find_element(By.NAME, 'toTimeTable')
    Select(start_time_element).select_by_visible_text(start_time)

    # 選擇出發日期
    driver.find_element(By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()
    driver.find_element(By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()

    while True:
        # 取得驗證碼圖片並存檔
        captcha_img = driver.find_element(By.ID, 'BookingS1Form_homeCaptcha_passCode')
        captcha_img.screenshot('captcha.png')
        
        # 使用 OCR 讀取驗證碼
        captcha_code = get_captcha_code()
        captcha_input = driver.find_element(By.ID, 'securityCode')
        captcha_input.send_keys(captcha_code)
        time.sleep(2)

        # 送出表單
        driver.find_element(By.ID, 'SubmitButton').click()
        
        # 檢查是否成功進入下一步
        try:
            time.sleep(5)
            driver.find_element(By.ID, 'BookingS2Form_TrainQueryDataViewPanel')
            print("驗證碼正確, 進到第二步驟")
            break
        except NoSuchElementException:
            print("驗證碼錯誤，重新驗證")

    # 獲取所有可選車次資訊
    trains_info = list()
    trains = driver.find_element(By.CLASS_NAME, 'result-listing').find_elements(By.TAG_NAME, 'label')
    for train in trains:
        info = train.find_element(By.CLASS_NAME, 'uk-radio')
        trains_info.append(
            {
                'depart_time': info.get_attribute('querydeparture'),  # 出發時間
                'arrival_time': info.get_attribute('queryarrival'),  # 到達時間
                'duration': info.get_attribute('queryestimatedtime'),  # 行車時間
                'train_code': info.get_attribute('querycode'),  # 車次編號
                'radio_box': info,  # 選擇車次的按鈕
            }
        )
    
    # 顯示所有車次資訊
    for idx, train in enumerate(trains_info):
        print(f"({idx}) - {train['train_code']}, 行駛時間={train['duration']} | {train['depart_time']} -> {train['arrival_time']}")
    
    return trains_info


def select_train_and_submit_booking(trains_info):
    """執行第二步：選擇車次並填寫個人資料"""
    
    # 讓使用者選擇車次
    which_train = int(input("Choose your train. Enter from 0~9: "))
    trains_info[which_train]['radio_box'].click()

    # 送出訂票請求
    driver.find_element(By.NAME, 'SubmitButton').click()
    print("選擇車次完成, 進到第三步驟")

    # 截圖保存訂票摘要
    driver.find_element(By.CLASS_NAME, 'ticket-summary').screenshot('thsr_summary.png')

    # 輸入個人資訊
    input_personal_id = driver.find_element(By.ID, 'idNumber')
    personal_id = os.getenv('PERSONAL_ID')  # 取得環境變數中的身分證號碼
    input_personal_id.send_keys(personal_id)

    input_phone_number = driver.find_element(By.ID, 'mobilePhone')
    phone_number = os.getenv('PERSONAL_PHONE_NUMBER')  # 取得環境變數中的手機號碼
    input_phone_number.send_keys(phone_number)

    input_email = driver.find_element(By.ID, 'email')
    email = os.getenv('PERSONAL_EMAIL')  # 取得環境變數中的 Email
    input_email.send_keys(email)

    # 勾選同意條款並提交表單
    driver.find_element(By.NAME, 'agree').click()
    driver.find_element(By.ID, 'isSubmit').click()

    # 截圖保存訂票結果
    screenshot_filename = 'thsr_booking_result.png'
    driver.find_element(By.CLASS_NAME, 'ticket-summary').screenshot(screenshot_filename)
    print("訂票完成!")

    return screenshot_filename


if __name__ == "__main__":
    """主程式執行流程"""

    # 訂票參數
    # start_station = '台中'
    # dest_station = '板橋'
    # start_time = '18:00'
    # start_date = '二月 25, 2025'

    # Step 1：向使用者詢問訂票資訊
    booking_info = ask_booking_infomation()
    
    # Step 2：檢查是否有缺少的資訊，並請使用者補充
    booking_info = ask_missing_infomation(booking_info)
    
    # Step 3：調整日期格式，以便爬蟲使用
    booking_info = convert_date_to_thsr_format(booking_info)

    create_driver()  # 建立瀏覽器驅動
    
    # Step 4：選擇車次
    trains_info = booking_with_info(
        start_station= booking_info['出發站'], 
        dest_station= booking_info['抵達站'], 
        start_time= booking_info['出發時辰'], 
        start_date= booking_info['出發日期'])
    
    # Step 5：選擇車次並填寫個人資料
    select_train_and_submit_booking(trains_info)


    time.sleep(10)  # 等待 10 秒確保訂票完成
    driver.quit()  # 關閉瀏覽器
    