from openai import OpenAI
client = OpenAI()


def chat_with_chatgpt(user_message, system_prompt):
    completion = client.chat.completions.create(
        model="gpt-4o-mini", # model name (影響花多少錢)
        messages=[
            {
                "role": "system", 
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_message # user的內容
            }
        ]
    )

    return completion.choices[0].message

if __name__ == '__main__':
    chat_with_chatgpt(
        user_message="我要珍珠奶茶微微",
        system_prompt="你是飲料店的店員，有人向你點餐"
    )