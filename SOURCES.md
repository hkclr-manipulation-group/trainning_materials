# 资料来源与阅读任务

整理日期：2026-09-07。网络资料优先官方文档、作者课程和维护者仓库。以下为原创教学说明加阅读导航，不是网页全文镜像；离线实验不依赖这些网站。

| 主题 | 来源 | 只读哪些内容 | 对应实践 |
|---|---|---|---|
| 编程 | [Python 官方教程](https://docs.python.org/3/tutorial/) | 控制流、函数、异常、虚拟环境 | Day 1 单位转换与错误输入 |
| 调试 | [VS Code Python debugging](https://code.visualstudio.com/docs/python/debugging) | 断点、单步、变量和启动配置 | 查看字节解码过程 |
| 版本控制 | [Pro Git：版本控制简介](https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control) | 版本历史与变更记录 | 小改动及差异检查 |
| CAD | [FreeCAD 官方手册](https://www.freecad.org/manual/a-freecad-manual.pdf) | 参数化设计与基本操作 | 两连杆草图；手册较早，界面按版本核对 |
| 运动学 | [Modern Robotics 4.1.1](https://modernrobotics.northwestern.edu/nu-gm-book-resource/4-1-1-product-of-exponentials-formula-in-the-space-frame/) | 空间参考系与 FK 的输入输出 | 两连杆 FK/IK；指数积推导为进阶 |
| CAN | [Linux 内核 SocketCAN](https://www.kernel.org/doc/html/latest/networking/can.html) | 帧、过滤、错误和 CAN FD | 教学载荷的字段与边界 |
| 网络观察 | [Wireshark 用户手册](https://www.wireshark.org/docs/wsug_html_chunked/index.html) | 主窗口、打开文件、过滤 | 离线 pcap 演示 |
| 构建 | [CMake 官方教程](https://cmake.org/cmake/help/latest/guide/tutorial/index.html) | 配置、构建、测试基本流程 | 可选模拟 C 项目构建 |
| ROS 2 | [Topics / Services / Actions](https://docs.ros.org/en/jazzy/How-To-Guides/Topics-Services-Actions.html) | 接口选择原则 | 为反馈、配置、长动作选择接口 |
| 相机标定 | [OpenCV 4.12 标定教程](https://docs.opencv.org/4.12.0/dc/dbb/tutorial_py_calibration.html) | 内参、畸变与误差 | 像素到三维的坐标链 |
| 仿真 | [MuJoCo 官方概览](https://mujoco.readthedocs.io/en/stable/overview.html) | 模型、状态、动力学与接触 | 区分 FK、简化控制和动力学仿真 |
| 机器人学习 | [LeRobot 官方概览](https://huggingface.co/docs/lerobot/index) | 数据、策略和评估的整体关系 | 从合成回归实验过渡到机器人数据 |

Python、SocketCAN、Pro Git、Modern Robotics 页面正文已读取；其余来源通过官方页面或官方搜索结果核对。ROS URDF 教程直连受网站访问保护，未把其受阻页面当作已读取依据；本课 URDF 内容主要结合团队实际模型和机器人基础概念编写。

上游 `latest`、`stable`、`main` 页面可能变化，授课前检查链接和安装版本。课程不统一推荐“所有工具升级到最新”，应先满足当前项目的兼容约束。团队资料入口和证据范围见 [PROJECT_MAP.md](PROJECT_MAP.md)。
