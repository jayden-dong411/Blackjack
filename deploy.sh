#!/bin/bash

echo "二十一点应用部署脚本"
echo "===================="
echo ""

echo "请选择部署方式："
echo "1. 本地运行"
echo "2. Docker部署"
echo "3. 退出"
read -p "请输入选项 (1-3): " choice

case $choice in
  1)
    echo "正在准备本地运行环境..."
    pip install -r requirements.txt
    echo "依赖安装完成，正在启动应用..."
    streamlit run blackjack_interactive.py
    ;;
  2)
    echo "正在使用Docker部署..."
    if command -v docker &> /dev/null; then
      if command -v docker-compose &> /dev/null; then
        echo "使用docker-compose部署..."
        docker-compose up -d
        echo "部署完成！请访问 http://localhost:8501"
      else
        echo "使用docker部署..."
        docker build -t blackjack-app .
        docker run -d -p 8501:8501 blackjack-app
        echo "部署完成！请访问 http://localhost:8501"
      fi
    else
      echo "错误：未检测到Docker。请先安装Docker后再尝试。"
      exit 1
    fi
    ;;
  3)
    echo "退出部署脚本"
    exit 0
    ;;
  *)
    echo "无效选项，请重新运行脚本并选择有效选项。"
    exit 1
    ;;
esac 