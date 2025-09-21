# Copyright (c) 2025 左岚. All rights reserved.
import subprocess
import os

# 设置环境变量以允许阻塞调用
os.environ["BG_JOB_ISOLATED_LOOPS"] = "true"

# 使用 --allow-blocking 参数启动 LangGraph
subprocess.run(["langgraph", "dev", "--allow-blocking"])
