# 工具使用：先完成任务，再增加工具

基础路线只安装Python和编辑器，Git用于版本练习。CAD可用已有软件。ROS、CUDA、仿真器和硬件抓包设备作为可选进阶项。自学工具数据见 [算法与通信实验](labs/ALGORITHMS.md)，无设备也能完成主线。

## 1. 本机环境：Windows 主线

进入 `trainning_materials` 目录，执行：

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\python.exe labs/course_lab.py all
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

课程使用 Python 3.10+，全部基础实验为标准库，不需要 `pip install`。直接使用虚拟环境解释器，无需修改 PowerShell 执行策略。Linux/macOS 对应解释器路径为 `.venv/bin/python`；创建环境时可用 `python3 -m venv .venv`。

在 VS Code 打开仓库文件夹，选择这个虚拟环境的 Python 解释器。打开 `labs/course_lab.py`，在 `decode_frame` 中设置断点，给启动参数填 `protocol`，启动调试，观察 `payload`、`node`、`angle_mrad`。再单步到返回值，确认 250 转为 0.25。参考 [VS Code 官方 Python 调试指南](https://code.visualstudio.com/docs/python/debugging)。

## 2. 必做操作卡

| 工具 | 本周操作 | 成功证据 |
|---|---|---|
| 终端 | 确认当前目录、运行脚本、读退出码 | 记录完整命令和结果 |
| VS Code | 断点、单步、变量窗口、搜索引用 | 解释一个值在哪里改变 |
| Python / venv | 创建隔离环境、查看解释器 | `python -c "import sys; print(sys.executable)"` |
| Git | status、diff、暂存指定文件 | 一次能解释的差异 |
| rg / 编辑器搜索 | 搜 `decode_frame` 和 `velocity` | 找到定义和使用位置 |
| CAD | 尺寸约束、拉伸、装配零位、导出 | 尺寸图和单位核对表 |
| CSV / 表格软件 | 打开控制输出，作折线图 | 横轴秒、纵轴弧度 |
| 原生碰撞查看器 | 拖轴、隔离碰撞对、导出 JSON | 可复现姿态记录 |

PowerShell 常用 `Get-Location`、`Get-ChildItem`、`Get-Content -Encoding UTF8`。查找函数可用 `rg -n "decode_frame" labs tests`；没有 rg 时用编辑器全局搜索即可。

Git 练习在自己的仓库分支完成：`git status` → `git switch -c training/my-first-change` → 改一行注释 → `git diff` → `git add labs/course_lab.py` → `git diff --cached` → 提交。运行前确认分支名未占用；只暂存此次改动。Git 记录和恢复版本的概念见 [官方 Pro Git](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control)。

## 3. 工程工具自主练习卡

| 工具 | 解决的问题 | 自主操作任务 | 环境 |
|---|---|---|---|
| CMake + 编译器 | 配置并构建 C/C++ 项目 | 区分 configure、build、test 的输出 | 编译器须另行准备 |
| Wireshark | 网络报文观察 | 打开 `labs/data/teaching_udp.pcap`，用 `udp.port == 5000` 显示过滤器查看4帧 | 无软件时使用同目录CSV |
| CAN 厂商工具 / SocketCAN | 观察 CAN 帧和错误 | 读一份离线日志，核对 ID、长度和字节 | 实际驱动依平台和适配器 |
| STM32CubeMX / 调试器 | 外设配置和固件调试 | 阅读工程时钟、SPI、CAN 配置及启动代码 | 不要求学员刷写板卡 |
| 逻辑分析仪 / 示波器 | 数字时序 / 电气波形 | 用表格画 `labs/data/spi_mode0.csv`，按上升沿读A5；理解何时需要仪器 | 自带合成数据，仪器可选 |
| ROS 2 / RViz | 节点接口、坐标和可视化 | 先解释topic/service/action，再在可选环境中观察TF树 | 第一周不要求安装 |
| MuJoCo | 动力学与接触仿真 | 区分模型参数与运行状态，观察仿真步进 | 可选独立环境 |
| AI 编程助手 | 解释、修改与评审代码 | 用任务模板完成一个边界处理改动 | 依团队可用工具 |

CMake 的配置步骤生成构建系统，构建步骤调用编译器，测试步骤运行已配置的测试；具体见 [官方教程](https://cmake.org/cmake/help/latest/guide/tutorial/index.html)。团队已有 `vision_robotics_skin_demo` 时，可选练习在该目录使用：

```powershell
cmake -S . -B build-training -DVRS_ENABLE_HARDWARE=OFF
cmake --build build-training --config Release
ctest --test-dir build-training -C Release --output-on-failure
```

这是该项目文档列出的模拟构建路线，课程基础验收不依赖它；需先确认本机 C 编译器和对应项目版本。

Wireshark 的捕获过滤与显示过滤是两个阶段，不能混用表达式。其能力与界面见 [官方用户手册](https://www.wireshark.org/docs/wsug_html_chunked/index.html)。它不替代 SPI 逻辑分析仪，CAN 观察也依赖适配器及捕获支持。

ROS 2 的 topic 适合持续数据流，service 适合短请求响应，action 适合有反馈和取消的长任务；阅读 [官方接口选择说明](https://docs.ros.org/en/jazzy/How-To-Guides/Topics-Services-Actions.html)。本课程固定引用 Jazzy 文档来说明概念，不宣称它是最新版本，也不要求团队现有项目依赖 ROS。

## 4. 碰撞工具环境

在 `collision_shpere_generation` 项目自己的环境中按 README 安装 `python -m pip install -e ".[viewer]"`，运行 viewer。需要桌面、Qt 和 OpenGL。工作空间 GPU 计算另需相容的 cuRobo/CUDA 环境；不要把这些依赖装进本课程标准库实验环境。

工具使用记录至少写下：操作系统、工具版本、工作目录、命令、输入、预期、实际结果。界面按钮位置或依赖版本随工具更新，按 [来源索引](SOURCES.md) 核对对应版本。

## 5. 原生交互窗口故障处理

运行`python labs/kinematics_explorer.py`。若提示没有tkinter或找不到init.tcl，先执行`python -m tkinter`验证当前Python的Tcl/Tk组件，检查是否使用了预期解释器。Windows可修复Python安装中的Tcl/Tk组件，Linux通常需系统对应的Tk包；按你的平台处理，不要复制别人电脑的绝对路径到项目。

如果当前环境没有桌面或暂时无法修复，直接使用 [PNG图示](assets/README.md) 和 `algorithm_lab.py`完成同样的概念与数值实验。核心课程不依赖GUI环境。
