# 自学资料验证记录

## 2026-09-08：协议栈、IK家族、工具链与全课程深入

新增4篇深入手册、3本Notebook和20道含解析的扩展题；七天正文、原手册、课程首页和工具说明已连接到新的专题入口。下方保留此前验证记录，测试数量按各次验证的实际范围记录。

| 核验 | 本次结果 |
|---|---|
| 核心测试 | `python -m unittest discover -s tests -v`，43项通过；新增TCP任意切分、错误长度、CAN仲裁、IK分支平均、检索初值与延迟模型检查 |
| 新增Notebook | 08、09、10各自在新内核中完整运行，分别5、6、4个代码块，共15个通过；本次未重复执行代码未变的原8本 |
| Notebook总量 | 11本；00首页仅新增深入阅读导航，其余原课程代码未改 |
| 可编辑实验 | PCAP逐层解析、TCP长度分帧、CAN ID仲裁、代数IK、近邻初值+DLS、局部近似、延迟及滤波对照均实际运行 |
| 离线演示 | 9主题244帧SVG均可解析；本机Edge实测播放、暂停、前后单步、主题切换、进度跳转通过；全部244帧文字边界检查通过，无JavaScript异常 |
| 视觉复核 | 查看协议栈、IK多解、Jacobian、A*和碰撞覆盖的浏览器截图，中文、数值与图形可读；4张静态SVG与播放器共用生成帧 |
| 本地链接 | 52份Markdown和11本Notebook，492处本地链接全部存在；不代表所有外部站点或锚点都已验证 |
| Python语法 | tools、labs、tests及Notebook源文件共30个Python文件通过AST解析 |

本次Notebook结果保存在 `outputs/executed_notebooks/report_selected.json`，原8本的记录仍为同目录 `report.json`。演示器检查脚本为 `tools/check_concept_player.py`，报告和9张主题截图在 `outputs/concept_player_check/`；这些outputs产物是本机验证记录，不随课程源文件提交。

复跑新增实验：`python tools/check_notebooks.py 08_protocol_stack.ipynb 09_ik_families.ipynb 10_visual_reasoning.ipynb`。重建演示和静态图：`python tools/build_concept_player.py`。浏览器检查额外需要Playwright和本机Edge，学员直接打开HTML无需安装它们。

数据驱动IK使用425条教学样本和30个留出目标，实际实现为检索初值与DLS精修；IKFlow等神经网络方法只作论文导读。CAN演示限11位标准ID仲裁阶段；TCP实验为本地字节流解析，不接真实网络设备。碰撞图是二维矩形与近似圆，不表示已验证团队机器人网格或折叠姿态。

GitHub/GitLab/Gitea、容器及CI内容是操作讲义和模板，本次未执行远端建库、PR、CI或部署；CI示例仍放在templates中。没有运行真机、GPU策略训练或论文完整复现。

## 此前验证记录

日期：2026-09-07，Windows / Python 3.10。

交互课堂追加验证：2026-09-07至08。8本Notebook在各自新内核中执行，共43个代码块全部成功，无错误输出；结果保存在 `outputs/executed_notebooks/report.json` 和执行后的笔记副本中。第七天实际调用算法脚本并运行核心测试，35项通过。

2026-09-08使用本机Edge进行浏览器实测：带令牌访问Jupyter、选择Training Python、执行入门笔记、将300修改为450并得到 `450 mm = 0.450 m`、保存后复读文件确认改动、滑块从30°变为31°且Python生成新的图像，全部通过。截图已人工查看，中文、代码、计算结果与曲线显示正常。记录在 `outputs/browser_smoke/report.json`；示例图收录于交互课堂说明。验证后关闭测试服务；未部署公共网站。

启动器使用独立的会话运行目录，避免Windows普通账户与隔离测试账户复用具有不同访问权限的Jupyter登录文件。这个调整也在上述浏览器实测中验证。

交互环境使用项目 `.venv`：JupyterLab 4.6.3、ipykernel 7.3.0、nbclient 0.11.0、nbformat 5.10.4、ipywidgets 8.1.7、jupyterlab-widgets 3.0.15、NumPy 1.24.4、Matplotlib 3.10.9。本机环境复用了已安装的系统包，另外将widget前端扩展安装到项目环境；文档中的新环境安装步骤不依赖这些本机路径。

`python tools/check_learning_links.py` 覆盖43份Markdown和8本Notebook中的本地链接；最终检查347处链接时均存在。新增七天实验、工程细节与课程入口已经互相连接。命令行链接检查只验证路径存在，不验证每个网页或段落锚点。

| 验证 | 结果 |
|---|---|
| `python labs/course_lab.py all` | 六个基础实验运行成功 |
| `python labs/algorithm_lab.py all` | 五个算法实验运行成功，IK收敛、A*代价19、轨迹2.5秒 |
| `python -m unittest discover -s tests -v` | 35项测试通过，含参考数据校验 |
| Markdown相对链接 | 41份Markdown检查时无失效本地链接；图示路径均存在 |
| 图片 | 14组PNG/SVG已生成，抽查两连杆、雅可比、感知链与PID图的中文显示 |
| 教学数据 | pcap含4帧，IPv4长度与校验正确；SPI上升沿数据为A5 |
| 教学URDF | XML可解析，2个转动关节、1个固定工具关节 |
| 原生窗口 | 点击目标、切换分支、环外目标和滑块重绘的隐藏窗口检查通过 |
| 新增参考数据 | 9类教学CSV、4模型24关节声明快照；清单哈希、行数及关键独立预期通过检查 |
| 零基础内容 | 七天正文重写，补充数学台阶、操作卡、算法故事和21道就地自检题 |
| 新增动画与分镜 | 12段GIF共480帧均可解码，每段7.32秒；12张四步PNG分镜齐全，抽查坐标、两连杆与A*排版 |
| 动画播放器 | 隐藏窗口检查通过：载入40帧、前后单步、播放、暂停与主题切换；采用下述本机Tcl/Tk测试环境 |

本机原有Tcl脚本路径无法直接初始化，因此窗口检查使用复制到工作区build目录的同一套已安装Tcl/Tk运行时，并仅在测试进程中设置TCL_LIBRARY/TK_LIBRARY。没有把该绝对路径或运行时加入课程依赖。普通Python安装需带可用Tcl/Tk；故障处理见 [工具说明](TOOLS.md)。

未执行真机控制、GPU求解、完整机器人策略训练或Wireshark界面操作。pcap使用独立字节解析检查，基础自学也可直接读CSV。算法讲解中没有本地实现的项目在 [算法地图](handbook/ALGORITHMS.md) 明确标注。
