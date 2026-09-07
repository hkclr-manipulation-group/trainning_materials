# 一周安排：本体 → 通信 → 控制 → AI

本路线完全自学。每天约 6 小时：短讲义45分钟、手册例题75分钟、实验90分钟、工具与项目阅读60分钟、测验45分钟、笔记与求助45分钟。共42小时；具体方法见 [自学说明](SELF_STUDY.md)。

| 天 | 主题与讲义 | 核心工具 | 当天交付 | 当天过关条件 |
|---|---|---|---|---|
| 1 | [系统、单位与编程](lessons/day01_system_and_code.md) | Python、终端、VS Code、Git | 系统图、单位实验、一次断点观察 | 能说清输入输出，解释度与弧度 |
| 2 | [本体、CAD 与 URDF](lessons/day02_body_and_urdf.md) | CAD、XML、模型查看器 | 两连杆尺寸图、力矩估算、URDF 字段表 | 能核对坐标、质量、轴、限位 |
| 3 | [通信与嵌入式](lessons/day03_communication.md) | struct、日志、协议表、离线报文 | 一帧报文逐字节解读、超时实验 | 能区别传输成功和动作完成 |
| 4 | [运动学与控制](lessons/day04_control.md) | Python、调试器、CSV | FK/IK 复算、闭环曲线、限速验证 | 能解释反馈、采样周期、饱和 |
| 5 | [碰撞、工作空间与集成](lessons/day05_collision_workspace.md) | 原生 Python 查看器、配置、测试 | 一个碰撞案例报告、对照实验设计 | 能区别 IK 失败、碰撞拒绝与过滤 |
| 6 | [感知、标定与机器人 AI](lessons/day06_perception_ai.md) | 数据表、相机模型、小型学习实验 | 坐标链、数据划分、模型误差报告 | 能识别泄漏，说明模型部署边界 |
| 7 | [vibe coding 与工程交付](lessons/day07_vibe_coding.md) | AI编程助手、Git diff、unittest | 综合任务、自评与复现记录 | 自己在另一目录按README重跑成功 |

## 先修补课与学习深度

零编程基础者，先读 [数学与代码](handbook/00_foundations.md)，跟着已给出的代码和答案练习，必要时增加2–4小时。会写代码者可直接做边界测试。遇到具体问题可以请教同事，但资料、实验和自评不依赖授课。

## 每天补充阅读哪些内容

| 天 | 手册必读 | 新实验 / 深入任务 |
|---|---|---|
| 1 | [基础](handbook/00_foundations.md) 1–4节 | 手算坐标变换；逐行追踪函数 |
| 2 | [本体](handbook/01_body.md) 1–5节；[运动学](handbook/02_kinematics.md) 1–3节 | 尺寸、力矩、坐标和 FK |
| 3 | [通信](handbook/08_communication.md) 1–5节 | 随仓库日志、重复与超时 |
| 4 | [运动学](handbook/02_kinematics.md) 4–7节；[控制](handbook/03_control.md) 1–4节 | 数值 IK、交互窗口、PID、梯形轨迹 |
| 5 | [规划](handbook/04_planning.md) 1–5节 | A*、构型空间、状态和边检查 |
| 6 | [估计](handbook/05_estimation.md) 1–4节；[AI](handbook/06_ai.md) 1–4节 | Kalman、标定手算、数据划分 |
| 7 | [软件](handbook/07_software.md) 1–5节 | 边界测试、复现、自评结业任务 |

手册进阶节、[算法地图](handbook/ALGORITHMS.md) 与 [专项题](assessments/ALGORITHM_EXERCISES.md) 可在后续两周深入，不要求第一周全部掌握。

第一周必须会：单位、坐标、输入输出、日志、反馈闭环、简单测试与复现。第一周能够解释：CAD 到 URDF、CAN 分层、FK/IK、碰撞近似、数据到策略。动力学推导、实时系统、有限元分析、强化学习算法细节和完整模型训练列为后续专题。

## 统一验收

每日测验 5 题，每题 4 分，至少 14/20；未达到者先订正当天错误再做综合任务。每日实验保留命令、输出和解释，不能只交截图。结业任务按 [评分表](assessments/CAPSTONE.md) 评分，至少 70/100，并完成其中三个必过项。

若只有五个工作日，把第6、7天顺延；不要压缩动手时间。无真机、GPU或同级仓库时，使用本仓库模型、算法和日志完成主线。CAD未就绪时先交纸笔尺寸与坐标图，之后补软件操作。
