from chatgpt_sample import chat_with_chatgpt
from datetime import date
import json

standard_format = {
    "出發站": "出發站名",
    "到達站": "到達站名",
    "出發日期": "YYYY/MM/DD",
    "出發時辰": "H:S"
}

today = date.today().strftime("%Y/%m/%d")  # 取得今天日期


def ask_booking_infomation():
    print("Ask booking information")

    user_response = input(
        "請輸入你的高鐵訂位資訊，包含：出發站、到達站、出發日期、出發時辰: ")
    system_prompt = f"""
    我想要從回話取得訂票資訊，包含：出發站、到達站、出發日期、出發時辰。
    今天是 {today}，請把資料整理成python dictionary格式，例如：{standard_format}，
    不知道就填空字串，且回傳不包含其他內容。
    """
    return chat_with_chatgpt(user_response, system_prompt)


def ask_missing_infomation(booking_info):  # Slot filling
    print("Ask missing information")
    missing_slots = [key for key, value in booking_info.items() if not value]
    if not missing_slots:
        print("All slots are filled")
        return booking_info
    else:
        user_response = input(
            f"請補充你的高鐵訂位資訊，包含：{', '.join(missing_slots)}: ")

        system_prompt = f"""
        我想要從回話取得訂票資訊，包含：{', '.join(missing_slots)}。
        並與 {booking_info} 合併，今天是 {today} 。
        請把資料整理成python dictionary格式，例如：{standard_format}，不知道就填空字串，且回傳不包含其他內容。。
        """
        return chat_with_chatgpt(user_response, system_prompt)


if __name__ == '__main__':
    # Step 1
    booking_info = ask_booking_infomation()

    # Step 2
    booking_info = ask_missing_infomation(
        json.loads(booking_info.replace("'", "\"")))