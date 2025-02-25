from flask import Flask, request, abort

from linebot.v3 import (
    WebhookHandler
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent
)

from datetime import date
import os

# my tools
from chatgpt_sample import chat_with_chatgpt
from booking_info_extraction_flow import (
    extract_dict_from_string,
    convert_date_to_thsr_format
)

from thsr_booking_steps import (
    create_driver,
    booking_with_info,
    select_train_and_submit_booking
)

app = Flask(__name__)

# 從環境變數裏頭取得access token與channel secret
configuration = Configuration(
    access_token=os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))

# User Data 預期狀態
# {
#     'user_id_a': {
#         'intent': '訂高鐵',
#         '出發站': '台北',
#         '到達站': '台南',
#         '出發日期': '2022/10/10',
#         '出發時辰': '10:00'
#     },
#     'user_id_b': {
#         'intent': '訂高鐵',
#         '到達站': '高雄',
#         '出發日期': '2022/11/11',
#     },
#     'user_id_c': {}
# }

# 先建立一個空字典，讓使用者可以更新與加入
user_data = {}

standard_format = {
    "出發站": "出發站名",
    "到達站": "到達站名",
    "出發日期": "YYYY/MM/DD",
    "出發時辰": "H:S"
}

today = date.today().strftime("%Y/%m/%d")  # 取得今天日期

#若 `user_id` 尚未存在於 `user_data`，則新增一筆資料。
#若 `user_id` 已存在，則更新該使用者的資訊。
# **代表關鍵字參數，允許函式接收不定數量的關鍵字參數**，並將它們存成字典（dictionary）
def update_user_data(user_id, **info_dict):
    if user_id not in user_data:
        user_data[user_id] = info_dict
    else:
        info_has_value = {
            slot_name: slot_value
            for slot_name, slot_value in info_dict.items() if slot_value
        }
        user_data[user_id].update(info_has_value)

# 取得使用者資料
def get_user_data(user_id):
    return user_data.get(user_id, {}) # 若 user_id 不存在，則回傳空字典 `{}`。



@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    user_id = event.source.user_id
    user_message = event.message.text
    user_data = get_user_data(user_id)
    necessary_slots = ["出發站", "到達站", "出發日期", "出發時辰"] # 訂票時需要填寫的欄位


    #📌 如果用戶還沒進入「訂高鐵」模式，且現在輸入「訂高鐵」
    #👉 user_data.get("intent", "") 會取得用戶目前的意圖（如果沒設定則回傳 ""）。
    #👉 當用戶第一次輸入「訂高鐵」時，系統會記錄這個意圖。
    if user_data.get("intent", "") != "訂高鐵" and user_message == "訂高鐵":
        update_user_data(user_id, intent="訂高鐵")  # 更新意圖為:訂高鐵
        # 問第一個問題: "請輸入你的高鐵訂位資訊..."
        bot_response = "請輸入你的高鐵訂位資訊，包含：出發站、到達站、出發日期、出發時辰: "  # 提示用戶輸入訂票資訊

    elif user_data.get("intent") == "訂高鐵":  # 意圖判斷
        # 上一輪的資訊狀態
        unfilled_slots = [
            key for key in necessary_slots if key not in user_data]  # 未填的資訊

        # user message information extraction
        system_prompt = f"""
        我想要從回話取得訂票資訊，包含：{"、".join(unfilled_slots)}。
        今天是 {today}，請把資料整理成python dictionary格式，例如：{standard_format}，
        不知道就填空字串，且回傳不包含其他內容。
        """
        booking_info = chat_with_chatgpt(user_message, system_prompt)
        booking_info = extract_dict_from_string(booking_info)  # 將 GPT 回應的字串轉換為 Python 字典。
        update_user_data(user_id, **booking_info) # 把剛取得的資訊更新到 user_data

        # 判斷已填的資訊
        user_data = get_user_data(user_id)  # 重新讀取一次user_data
        filled_slots = [
            key for key in necessary_slots if key in user_data]  # 已填的資訊
        unfilled_slots = [
            key for key in necessary_slots if key not in user_data]  # 未填的資訊
        
        
        # filled_slots = [key for key in necessary_slots if key in user_data]
        """ 等同於
        filled_slots = []
        for key in necessary_slots:  # 遍歷所有必要欄位
            if key in user_data:  # 如果該欄位已經填寫
                filled_slots.append(key)  # 加入 filled_slots
        """
        # 填寫狀態記錄到系統日誌中，方便偵錯
        app.logger.info(f"filled_slots: {filled_slots}")
        app.logger.info(f"unfilled_slots: {unfilled_slots}")

        if len(unfilled_slots) == 0:  # 全部填完
            # 轉換用戶提供的日期格式，讓其符合高鐵訂票系統所需的格式
            user_data = convert_date_to_thsr_format(user_data)

            # 創建一個新的 "driver" 物件，這裡目前只支持單一用戶，且 driver 是全域變數
            create_driver()  # 目前只支持單人，driver是global的

            # 使用用戶提供的資料進行高鐵訂票查詢，返回符合條件的列車資訊
            trains_info = booking_with_info(
                            start_station=user_data['出發站'],
                            dest_station=user_data['到達站'],
                            start_time=user_data['出發時辰'],
                            start_date=user_data['出發日期']
            )

            # 準備顯示列車資訊，並讓用戶選擇列車
            train_message = ""
            for idx, train in enumerate(trains_info):
                train_message += \
                    f"({idx}) - {train['train_code']}, \
                    行駛時間={train['duration']} | \
                    {train['depart_time']} -> \
                    {train['arrival_time']} \n"

            # 組織回應訊息，讓用戶選擇列車
            bot_response = f"已為您找到以下列車，請選擇0~9：\n{train_message}"

            # 更新用戶資料，將意圖改為「選擇高鐵」，並儲存查詢到的列車資訊
            update_user_data(user_id, intent="選高鐵", trains_info=trains_info)
        else:  # 部分填完
            # 問缺少的資訊
            bot_response = f"請補充你的高鐵訂位資訊，包含：{', '.join(unfilled_slots)}: "
        # 如果使用者正在選擇高鐵車次
    
    elif user_data.get("intent") == "選高鐵":
        try:
            # 依照使用者選擇的車次，進行訂位
            which_train = int(user_message) # 用戶選擇的列車索引（0~9）

            # 取得用戶資料中的列車資訊
            trains_info = user_data.get("trains_info")

            # 根據選擇的列車進行訂票操作
            select_train_and_submit_booking(trains_info, which_train)

            # 訂票成功後回應訊息
            bot_response = "訂票完成！"
            
        except Exception as e:
            # 如果無法從使用者回覆取得有效的數字（非0~9的數字），回傳錯誤提示
            app.logger.error(e)  # 記錄錯誤
            bot_response = "請輸入0~9的數字"

    # 如果用戶的意圖既不是訂票也不是選擇車次，則回應通用的聊天回應
    else:
        # 使用 GPT 模型生成回應，並限制回應為20字以內
        bot_response = chat_with_chatgpt(
            user_message=user_message,
            system_prompt="回應二十字以內"
        )

    # 準備回應訊息並轉換為文本訊息格式，以便回傳給用戶
    response_messages = [TextMessage(text=bot_response)]

    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        line_bot_api.reply_message_with_http_info(
            ReplyMessageRequest(
                reply_token = event.reply_token,
                messages = response_messages
            )
        )


if __name__ == "__main__":
    app.run(debug=True) 