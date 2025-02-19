import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select

driver = webdriver.Chrome()
driver.get("https://irs.thsrc.com.tw/IMINT/?utm_source=thsrc&utm_medium=btnlink&utm_term=booking")

cookie = driver.find_element(By.ID, "cookieAccpetBtn")
cookie.click()

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

# 出發日期(input) #####難######
form_groups = driver.find_element(
    By.XPATH, "//input[@class='uk-input' and @readonly='readonly']").click()

start_date = '二月 21, 2025'
form_groups_selsct = driver.find_element(
    By.XPATH, f"//span[@class='flatpickr-day' and @aria-label='{start_date}']").click()

# 驗證碼
picture = driver.find_element(By.ID, 'BookingS1Form_homeCaptcha_passCode')
picture.screenshot('captcha.png') # 截圖

picture_input = driver.find_element(By.ID, 'securityCode')
picture_input.send_keys('1111')


# 送出資料
result_input = driver.find_element(By.ID, 'SubmitButton').click()



time.sleep(5)
driver.quit()