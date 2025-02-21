from flask import Flask  # 匯入 Flask 模組
from markupsafe import escape
from chatgpt_sample import chat_with_chatgpt # 要用flask串接chatgpt



# 創建 Flask 應用程式 __name__表示目前執行的程式
app = Flask(__name__)  

# 使用函式裝飾器，建立一個路由 ( Routes )，可針對主網域 / 發出請求

@app.route("/")
def hello_world():
    return f"<p>Hello World!</p>"

@app.route("/test/")
def hello_test():
    return f"<p>It's test!</p>"

@app.route("/test/<int:user_id>/")  
def hello_user(user_id):                   # 發出請求後會執行 hello_world() 的函式
    return f"<p>Hello USER-{escape(user_id)}!</p>"    # 回傳 HTML 內容


@app.route("/test/<path:subpath>/")
def hello_path(subpath):
    return f"<p>Hello PATH-{escape(subpath)}, World!</p>"


@app.route("/test/<user_message>/")  
def hello_home(user_message):
    chatgpt_response = chat_with_chatgpt(
        user_message= user_message,
        system_prompt="你是後端管理員，有前端使用者會呼叫你"
    )
    return chatgpt_response

# 如果要使用 python xxx.py 執行
if __name__ == "__main__":
    app.run(debug=True)