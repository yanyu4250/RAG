from openai import OpenAI

#1.获取client对象，openai对象
client = OpenAI(
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

#2.调用模型
response = client.chat.completions.create(
    model="qwen3-max",
    messages=[#system:系统角色，assistant:助手角色，user:用户角色
        {"role": "system", "content": "你是一个编程专家，不说废话，回答简单明了"},
        {"role": "assistant", "content": "好的，我是变成专家并且话不多"},
        {"role": "user", "content": "输出1-10的和，用python代码"},
    ],
    stream=True #开启了流式输出
)

#3.处理结果
#print(response.choices[0].message.content)+
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content,
              end="",#每段之间以空格间隔
              flush=True#立刻刷新缓冲区
              )