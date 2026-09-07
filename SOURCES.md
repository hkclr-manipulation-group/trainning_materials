# 资料来源与阅读任务

先读新版 [分级文献阅读路线](references/READING_GUIDE.md)、[参考数据](references/DATA_GUIDE.md)和 [外部数据集卡](references/DATASETS.md)。本页继续保留工具与方法的详细来源。

整理日期：2026-09-07。网络资料优先官方文档、作者课程和维护者仓库。以下为原创教学说明加阅读导航，不是网页全文镜像；离线实验不依赖这些网站。

| 主题 | 来源 | 只读哪些内容 | 对应实践 |
|---|---|---|---|
| 编程 | [Python 官方教程](https://docs.python.org/3/tutorial/) | 控制流、函数、异常、虚拟环境 | Day 1 单位转换与错误输入 |
| 调试 | [VS Code Python debugging](https://code.visualstudio.com/docs/python/debugging) | 断点、单步、变量和启动配置 | 查看字节解码过程 |
| 版本控制 | [Pro Git：版本控制简介](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) | 版本历史与变更记录 | 小改动及差异检查 |
| CAD | [FreeCAD 官方手册](https://www.freecad.org/manual/a-freecad-manual.pdf) | 参数化设计与基本操作 | 两连杆草图；手册较早，界面按版本核对 |
| 运动学 | [Modern Robotics 4.1.1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-1-product-of-exponentials-formula-in-the-space-frame/) | 空间参考系与 FK 的输入输出 | 两连杆 FK/IK；指数积推导为进阶 |
| CAN | [Linux 内核 SocketCAN](https://www.kernel.org/doc/html/latest/networking/can.html) | 帧、过滤、错误和 CAN FD | 教学载荷的字段与边界 |
| 网络观察 | [Wireshark 用户手册](https://www.wireshark.org/docs/wsug_html_chunked/index.html) | 主窗口、打开文件、过滤 | 随仓库pcap自主练习 |
| 构建 | [CMake 官方教程](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) | 配置、构建、测试基本流程 | 可选模拟 C 项目构建 |
| ROS 2 | [Topics / Services / Actions](https://docs.ros.org/en/jazzy/How-To-Guides/Topics-Services-Actions.html) | 接口选择原则 | 为反馈、配置、长动作选择接口 |
| 相机标定 | [OpenCV 4.12 标定教程](https://docs.opencv.org/4.12.0/dc/dbb/tutorial_py_calibration.html) | 内参、畸变与误差 | 像素到三维的坐标链 |
| 仿真 | [MuJoCo 官方概览](https://mujoco.readthedocs.io/en/stable/overview.html) | 模型、状态、动力学与接触 | 区分 FK、简化控制和动力学仿真 |
| 机器人学习 | [LeRobot 官方概览](https://huggingface.co/docs/lerobot/index) | 数据、策略和评估的整体关系 | 从合成回归实验过渡到机器人数据 |

Python、SocketCAN、Pro Git、Modern Robotics 页面正文已读取；其余来源通过官方页面或官方搜索结果核对。ROS URDF 教程直连受网站访问保护，未把其受阻页面当作已读取依据；本课 URDF 内容主要结合团队实际模型和机器人基础概念编写。

上游 `latest`、`stable`、`main` 页面可能变化，使用前核对链接和安装版本。先满足当前项目兼容约束，不要求所有工具升级到最新。团队资料入口与证据范围见 [PROJECT_MAP.md](PROJECT_MAP.md)。

## 自学扩充：算法原始资料

以下用于核对方法和继续深入，正文已提供独立例题和本地图片，不要求逐页阅读才能完成主线。

| 资料 | 推荐关注 | 本课对应 |
|---|---|---|
| [Modern Robotics 数值IK](https://modernrobotics.northwestern.edu/nu-gm-book-resource/6-2-numerical-inverse-kinematics-part-1-of-2/) | 局部线性化、迭代与初值 | 运动学手册；二维DLS为课程自建 |
| [OMPL规划器目录](https://ompl.kavrakilab.org/planners.html) | PRM、RRT、Connect、RRT*的区别 | 规划手册与算法地图 |
| [MIT LQR](https://underactuated.mit.edu/lqr.html) | 线性模型、状态反馈和二次代价 | 控制进阶 |
| [MIT轨迹优化](https://underactuated.mit.edu/trajopt.html) | 决策变量、动态约束和优化 | 规划与MPC背景 |
| [OpenCV calib3d](https://docs.opencv.org/4.13.0/d9/d0c/group__calib3d.html) | 投影、PnP、RANSAC和手眼接口的定义 | 感知与标定 |
| [Open3D ICP](https://www.open3d.org/docs/release/tutorial/pipelines/icp_registration.html) | 初值、对应与迭代配准 | 估计进阶 |
| [ACT作者论文](https://tonyzhaozh.github.io/aloha/aloha.pdf) | 动作分块和Transformer策略 | 模仿学习导读 |
| [Diffusion Policy作者项目](https://diffusion-policy.cs.columbia.edu/) | 条件动作扩散与执行过程 | 模仿学习导读 |
| [PPO教学](https://spinningup.openai.com/en/latest/algorithms/ppo.html)、[SAC教学](https://spinningup.openai.com/en/latest/algorithms/sac.html) | 采样、策略更新、回放与熵 | 强化学习导读，旧安装命令不直接沿用 |

Modern Robotics、OMPL、MIT、OpenCV和Open3D的页面正文已读取；ACT、Diffusion Policy及PPO/SAC通过作者/官方搜索结果核对。图示均由本仓库代码制作，没有直接复制论文插图。

## 可编辑Python课堂的官方依据（2026-09-07至08核对）

| 官方资料 | 在课程中的用途 |
|---|---|
| [JupyterLab Notebook](https://jupyterlab.readthedocs.io/en/stable/user/notebook.html) | 文字、公式、代码、图像和交互输出组合；内核与文档的区别 |
| [启动JupyterLab](https://jupyterlab.readthedocs.io/en/stable/getting_started/starting.html) | 浏览器访问本机服务、课程工作目录 |
| [JupyterLab终端](https://jupyterlab.readthedocs.io/en/stable/user/terminal.html) | 终端与工具运行在服务所在机器 |
| [ipywidgets交互函数](https://ipywidgets.readthedocs.io/en/stable/examples/Using%20Interact.html) | 滑块触发Python函数与输出更新 |
| [nbclient执行](https://nbclient.readthedocs.io/en/latest/client.html) | 在新内核中完整验证Notebook |
| [JupyterLite限制](https://jupyterlite.readthedocs.io/en/stable/troubleshooting.html) | 解释纯浏览器Python与完整本机Python的差异 |

上述页面已读取。新增Notebook代码、讲解与图表为课程自建；这些来源用于核对平台行为，不是机器人硬件指标。更多工程技术说明见[工程细节](handbook/09_engineering_details.md)。
