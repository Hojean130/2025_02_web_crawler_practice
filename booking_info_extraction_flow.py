from chatgpt_sample import chat_with_chatgpt  # 引入 ChatGPT API 互動函數
from datetime import date  # 引入 datetime 模組來取得今天日期
import json  # 引入 json 模組處理字典與字串轉換


# 定義標準的訂票資訊格式
standard_format = {
    "出發站": "出發站名",
    "到達站": "到達站名",
    "出發日期": "YYYY/MM/DD",  # 使用 datetime 模組的格式
    "出發時辰": "H:S"
}

# 取得今天的日期，並格式化為 YYYY/MM/DD
today = date.today().strftime("%Y/%m/%d")


def ask_booking_infomation():
    """向使用者詢問高鐵訂票資訊，並使用 ChatGPT 解析輸入內容。"""
    print("Ask booking information")
    
    # 讓使用者輸入訂票資訊
    user_response = input(
        "請輸入你的高鐵訂位資訊，包含：出發站、到達站、出發日期、出發時辰: ")
    
    # 設定系統提示詞，要求 ChatGPT 將輸入解析成 Python 字典格式
    system_prompt = f"""
    我想要從回話取得訂票資訊，包含：出發站、到達站、出發日期、出發時辰。
    今天是 {today}，請把資料整理成 python dictionary 格式，例如：{standard_format}，
    不知道就填空字串，且回傳不包含其他內容。
    """
    
    # 透過 ChatGPT 解析使用者輸入
    booking_info = chat_with_chatgpt(user_response, system_prompt)
    
    # 轉換回 Python 字典，並返回結果
    return json.loads(booking_info.replace("'", "\""))


def ask_missing_infomation(booking_info):  # Slot filling
    """檢查是否有缺少的訂票資訊，並提示使用者補充。"""
    print("Ask missing information")
    
    # 找出尚未填寫的欄位
    missing_slots = [key for key, value in booking_info.items() if not value]
    
    if not missing_slots:
        print("All slots are filled")
        return booking_info  # 若所有欄位都有填寫，直接返回
    
    # 提示使用者補充缺少的資訊
    user_response = input(
        f"請補充你的高鐵訂位資訊，包含：{', '.join(missing_slots)}: ")
    
    # 設定系統提示詞，請 ChatGPT 合併補充資訊
    system_prompt = f"""
    我想要從回話取得訂票資訊，包含：{', '.join(missing_slots)}。
    並與 {booking_info} 合併，今天是 {today}。
    請把資料整理成 python dictionary 格式，例如：{standard_format}，
    不知道就填空字串，且回傳不包含其他內容。
    """
    
    # 透過 ChatGPT 解析補充資訊，並更新訂票資訊
    booking_info = chat_with_chatgpt(user_response, system_prompt)
    return json.loads(booking_info.replace("'", "\""))


def convert_date_to_thsr_format(booking_info):
    """將出發日期格式轉換為台灣高鐵網站使用的格式（例如：'2025/02/25' -> '二月 25, 2025'）。"""
    
    # 定義數字月份對應的中文月份名稱
    map_number_to_chinese_word = {
        "01": "一月", "02": "二月", "03": "三月", "04": "四月",
        "05": "五月", "06": "六月", "07": "七月", "08": "八月",
        "09": "九月", "10": "十月", "11": "十一月", "12": "十二月"
    }
    
    # 解析日期，將其轉換為高鐵網站格式
    Year, Month, Day = booking_info['出發日期'].split('/')
    booking_info['出發日期'] = f"{map_number_to_chinese_word[Month]} {Day}, {Year}"
    
    print("格式轉換後......")
    print(booking_info)
    return booking_info


if __name__ == '__main__':
    # Step 1：向使用者詢問訂票資訊
    booking_info = ask_booking_infomation()
    
    # Step 2：檢查是否有缺少的資訊，並請使用者補充
    booking_info = ask_missing_infomation(booking_info)
    
    # Step 3：調整日期格式，以便爬蟲使用
    booking_info = convert_date_to_thsr_format(booking_info)