import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


### Step 1, 2
driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/selenium/web/web-form.html")

### Step 4
driver.implicitly_wait(2)
print("driver already wait 2 secs")

### Step 5
# beautifulsoup的作法: 
# text_box = soup.find_element(name="my-text") # bs4的寫法
text_box = driver.find_element(by=By.NAME, value="my-text")
password_box = driver.find_element(by=By.NAME, value="my-password")
textarea_box = driver.find_element(by=By.TAG_NAME, value="textarea")

# submit_button = soup.find("button")
submit_button = driver.find_element(by=By.CSS_SELECTOR, value="button")
submit_button = driver.find_element(by=By.TAG_NAME, value="button")

## Step 5.2: 找到Dropdown , 選擇two
number_dropdown = driver.find_element(By.XPATH, "//select[@class='form-select' and @name='my-select']") 
                                                # 所有的select  @屬性='條件'  and  @屬性='條件
print(number_dropdown.text)
number_select = Select(number_dropdown)
number_select.select_by_visible_text("Two")

# Step 6
text_box.send_keys("qqqqqqqqqqqqqqqqq")
password_box.send_keys("111111111111111111")
textarea_box.send_keys("jdfoamo,foxapkfoapkoiprv,mfoke")
time.sleep(5)
submit_button.click()

# Step 7
message = driver.find_element(By.CLASS_NAME, "container")
print(message.text)



time.sleep(10) # 控制器暫停
driver.quit()