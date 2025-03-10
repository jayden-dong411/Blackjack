# 二十一点交互式模拟应用

这是一个使用Streamlit构建的二十一点（Blackjack）游戏交互式模拟应用。

## 功能特点

- 完整的二十一点游戏体验
- 实时概率分析和决策建议
- 资金管理和统计跟踪
- 美观的用户界面

## 本地运行

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行应用：
   ```
   python blackjack_launcher.py
   ```
   或直接使用Streamlit：
   ```
   streamlit run blackjack_interactive.py
   ```

## 部署为网站

### 方法1：使用Streamlit Cloud（推荐）

1. 在GitHub上创建一个仓库并上传所有文件
2. 访问 [Streamlit Cloud](https://streamlit.io/cloud)
3. 注册并连接您的GitHub账户
4. 选择您的仓库和主文件（blackjack_interactive.py）
5. 点击部署

### 方法2：使用Docker部署

1. 构建Docker镜像：
   ```
   docker build -t blackjack-app .
   ```

2. 运行容器：
   ```
   docker run -p 8501:8501 blackjack-app
   ```

   或使用docker-compose：
   ```
   docker-compose up
   ```

3. 访问 http://localhost:8501

### 方法3：部署到Heroku

1. 安装Heroku CLI并登录
2. 在项目目录中初始化Git仓库：
   ```
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. 创建Heroku应用：
   ```
   heroku create your-app-name
   ```

4. 部署应用：
   ```
   git push heroku master
   ```

5. 打开应用：
   ```
   heroku open
   ```

## 自定义配置

您可以通过修改`blackjack_interactive.py`文件来自定义游戏规则和界面。 