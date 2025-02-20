import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select # 下拉是選單用
from selenium.common.exceptions import NoSuchElementException # 把遇到的意外import進來處理(handle exception)
from ocr_component import get_captcha_code
import pprint
from selenium.webdriver.common.alert import Alert

options = webdriver.ChromeOptions() # 創立driver物件所需的參數物件
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(options=options)
driver.get("https://irs.thsrc.com.tw/IMINT/?utm_source=thsrc&utm_medium=btnlink&utm_term=booking")
accept_cookie_button = driver.find_element(By.ID, "cookieAccpetBtn")
accept_cookie_button.click()


#
### 第一頁
#


# 選擇起始站
select_start_station = driver.find_element(
    By.XPATH, "//select[@class='uk-select' and @name='selectStartStation']") 
Select(select_start_station).select_by_visible_text("台中")

# 選擇終點站
select_destination_station = driver.find_element(
    By.XPATH, "//select[@class='uk-select' and @name='selectDestinationStation']") 
Select(select_destination_station).select_by_visible_text("新竹")

# 出發時間
select_time = driver.find_element(
    By.XPATH, "//select[@class='uk-select out-time' and @name='toTimeTable']") 
Select(select_time).select_by_visible_text("18:30")

# 出發日期(input)
form_groups = driver.find_element(
    By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()

start_date = '二月 21, 2025'
form_groups_selsct = driver.find_element(
    By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()

while True:
    # 驗證碼
    picture = driver.find_element(by=By.ID, value='BookingS1Form_homeCaptcha_passCode')
    picture.screenshot('captcha.png') # 截圖
    captcha_code = get_captcha_code()
    picture_input = driver.find_element(By.ID, 'securityCode')
    picture_input.send_keys(captcha_code)
    time.sleep(2)

    # 送出資料
    result_input = driver.find_element(By.ID, 'SubmitButton').click()
    time.sleep(5)

    # check validation is success or not
    # 去找警告有沒有發生，有發生代表錯誤要再試一次，但如果沒有錯誤找不到錯誤時出現的element就不管他直接跳出迴圈到下一步
    try:
        time.sleep(5)
        driver.find_element(By.ID, 'BookingS2Form_TrainQueryDataViewPanel')
        print("驗證碼正確, 進到第二步驟")
        break
    except NoSuchElementException:
        print("驗證碼錯誤，重新驗證")


#
### 第二頁
#


# 找出發時間，到達時間，搭車時間，建成一個字典
choose = driver.find_element(By.CLASS_NAME, "result-listing")
choose = choose.find_elements(By.TAG_NAME, "label")

thsr_list = []
i = 0
for element in choose:
    queryDeparture = element.find_element(By.ID, "QueryDeparture").text
    queryArrival = element.find_element(By.ID, "QueryArrival").text
    durations = element.find_element(By.CLASS_NAME, "duration")
    durations = durations.find_elements(By.TAG_NAME, "span")
    duration = durations[1].text
    train_code = element.find_element(By.ID, "QueryCode").text

    radio = element.find_element(By.CLASS_NAME, "btn-radio")  # 限定在 element 內找 input 按鈕
    
    thsr_list.append({
        "queryDeparture": queryDeparture,
        "queryArrival": queryArrival,
        "duration": duration,
        "train_code": train_code,
        "radio": radio,
        "A number": i
    })

    i += 1

pprint.pprint(thsr_list)
train_num = int(input("Choose your train: "))
thsr_list[train_num]["radio"].click()

check = driver.find_element(
    By.XPATH, "//input[@name='SubmitButton' and @class='uk-button uk-button-primary uk-button-large btn-next']").click()


#
### 第三頁
#
time.sleep(3)
id_card_input = input("請輸入身份證字號: \n")
id_card = driver.find_element(By.ID, "idNumber").send_keys(id_card_input)


phone_num_input = input("請輸入電話: \n")
phone_num = driver.find_element(By.ID, "mobilePhone").send_keys(phone_num_input)

email_input = input("請輸入email: \n")
email = driver.find_element(By.ID, "email").send_keys(email_input)

agree_btn = driver.find_element(By.XPATH, "//input[@name='agree' and @class='uk-checkbox']").click()
time.sleep(5)
isSubmit = driver.find_element(By.ID, "isSubmit").click()


time.sleep(1000)
driver.quit()



""" 老師的答案
trains_info = list()
trains = driver.find_element(
    By.CLASS_NAME, 'result-listing').find_elements(By.TAG_NAME, 'label')

for train in trains:
    info = train.find_element(By.CLASS_NAME, 'uk-radio')

    trains_info.append(
        {
            'depart_time': info.get_attribute('querydeparture'),
            'arrival_time': info.get_attribute('queryarrival'),
            'duration': info.get_attribute('queryestimatedtime'),
            'train_code': info.get_attribute('querycode'),
            'radio_box': info,
        }
    )
"""