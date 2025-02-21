from flask import Flask, render_template  # 匯入 Flask 模組，建立 Web 伺服器
from markupsafe import escape  # 用來防止 XSS 攻擊（轉義 HTML 特殊字元）
from chatgpt_sample import chat_with_chatgpt  # 匯入自訂函式，與 ChatGPT 進行對話

# 創建 Flask 應用程式 __name__ 代表目前執行的 Python 模組
app = Flask(__name__)  

# 設定首頁路由，當使用者訪問 http://127.0.0.1:5000/ 會回傳 "Hello World!"
@app.route("/")
def hello_world():
    return f"<p>Hello World!</p>"

# 設定 /test/ 路由，當使用者訪問 http://127.0.0.1:5000/test/ 會回傳 "It's test!"
@app.route("/test/")
def hello_test():
    return f"<p>It's test!</p>"

# 設定變數路由，<int:user_id> 代表 user_id 必須是「整數」
# 訪問範例：http://127.0.0.1:5000/test/123/
@app.route("/test/<int:user_id>/")  
def hello_user(user_id):                   
    return f"<p>Hello USER-{escape(user_id)}!</p>"  # escape() 轉義防止 XSS 攻擊

# 設定變數路由，<path:subpath> 代表 subpath 可以包含斜線（/）
# 訪問範例：http://127.0.0.1:5000/test/some/path/to/file/
@app.route("/test/<path:subpath>/")
def hello_path(subpath):
    return f"<p>Hello PATH-{escape(subpath)}, World!</p>"

# 讓 Flask 與 ChatGPT 進行互動，user_message 代表使用者輸入的訊息
# 訪問範例：http://127.0.0.1:5000/test/你好/
@app.route("/test/<user_message>/")  
def hello_home(user_message):
    chatgpt_response = chat_with_chatgpt(
        user_message=user_message,
        system_prompt="你是後端管理員，有前端使用者會呼叫你"
    )
    return chatgpt_response  # 回傳 ChatGPT 產生的回應

# 設定一個新的路由，渲染 HTML 頁面
@app.route("/sample/")  
def show_html_sample():
    return render_template(
        "flask_html_sample.html",
        name="Tony",
        numbers=[11, 22, 33, 44, 55],
        pairs=[('A', 1), ('B', 2), ('C', 3)],
        dict_data={'A': 1, 'B': 2, 'C': 3}
        )      # 使用 render_template() 渲染 templates 目錄中的 flask_html_sample.html 檔案，並將其顯示在瀏覽器上
        # 將name(參數名)送到前端網頁



# 啟動 Flask 伺服器，debug=True 代表會自動重新載入程式碼變更
if __name__ == "__main__":

    app.run(debug=True)