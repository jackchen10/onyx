from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
def read_root():
    print("==========欢迎登录==============")
    return {"message": "欢迎登录"}

@app.get("/loop")
def do_loop():
    results = []
    print("==========开始循环==============")
    for i in range(1, 11):
        msg = f"循环次数: {i}"
        print(msg)  # 输出到日志
        results.append(msg)
    print("==========循环结束==============")
    return {"logs": results}

@app.get("/shutdown")
def shutdown():
    return {"message": "结束程序"}  # 实际上不会终止服务，只是个提示

if __name__ == "__main__":
    # 允许通过 python main.py 直接运行
    uvicorn.run(app, host="0.0.0.0", port=8008)