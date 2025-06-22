# game_adventure

本目录为基于LangChain和大模型的文字冒险游戏主项目目录。

## 目录结构

```
game_adventure/
  main.py                # 启动入口
  game_engine.py         # 游戏主逻辑
  state_manager.py       # 状态与存档管理
  langchain_chain.py     # LangChain链路封装
  output_parser.py       # 输出解析
  prompts/               # Prompt模板目录
    scene_prompt.py
    option_prompt.py
  models/                # 数据模型
    player.py
    story_state.py
  requirements.txt       # 依赖包
  README.md              # 项目说明
```

## 说明
- main.py：项目启动入口，负责初始化和主循环
- game_engine.py：游戏主逻辑，包括剧情推进、玩家输入处理等
- state_manager.py：负责游戏状态、存档、读档等功能
- langchain_chain.py：封装LangChain链路，管理Prompt、Memory、OutputParser等
- output_parser.py：负责解析大模型输出，提取关键信息
- prompts/：存放各类Prompt模板
- models/：存放数据模型，如玩家、剧情状态等
- requirements.txt：依赖包列表
- README.md：本说明文件 


## 游戏如何启动
### （1）选择模型
在config.json中配置ollama本地大模型，录入本地电脑下载的模型，例如"model_name": "unsafe-llama3-14b:latest"
### （2）运行游戏
#### 方式一：运行main.py通过命令行获取游戏
#### 方式二：下载streamlit包， 运行 streamlit run .\app.py 可通过web页面运行该游戏

