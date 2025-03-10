
import subprocess
import os
import sys
import time

def run_streamlit_app():
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置Streamlit应用路径
    app_path = os.path.join(script_dir, "blackjack_interactive.py")
    
    # 启动Streamlit应用
    print("正在启动二十一点交互式模拟应用...")
    print("应用启动后将自动在浏览器中打开")
    print("请稍候...")
    
    # 使用subprocess启动Streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", app_path, "--server.headless", "true"]
    process = subprocess.Popen(cmd)
    
    # 等待几秒钟让服务器启动
    time.sleep(3)
    
    # 保持进程运行直到用户关闭
    try:
        process.wait()
    except KeyboardInterrupt:
        process.terminate()

if __name__ == "__main__":
    run_streamlit_app()
