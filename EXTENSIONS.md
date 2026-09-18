# 扩展资料

[首页](README.md) · [学习路线](WEEK_PLAN.md)

按当前问题选一项即可。每个专题都有本地解释、算例和自检，外部资料打不开也可以先学。

## 随课深入

| 基础课 | 想进一步了解 | 入口 |
|---|---|---|
| 1 任务与代码 | 矩阵、类与线程 | [矩阵](handbook/17_extension_workshops.md#day1) · [对象与并发](handbook/17_extension_workshops.md#software) |
| 2 本体与模型 | 团队模型比较、六轴设计、惯量 | [模型比较](references/LESSON_EXTENSIONS.md#day2) · [结构到动力学](handbook/17_extension_workshops.md#day2) |
| 3 通信与反馈 | 协议分层、抓包、SPI与电气连接 | [通信工具](references/LESSON_EXTENSIONS.md#day3) · [总线连接](handbook/17_extension_workshops.md#day3) |
| 4 运动与控制 | 逆变换、数值IK、PID与优化 | [运动与控制补充](references/LESSON_EXTENSIONS.md#day4) · [推导与算例](handbook/17_extension_workshops.md#day4) |
| 5 碰撞与规划 | 工作空间比较、高维规划 | [规划补充](references/LESSON_EXTENSIONS.md#day5) · [高维与概率保证](handbook/17_extension_workshops.md#day5) |
| 6 感知与AI | 学习方法、数据集、网络训练 | [AI与数据](references/LESSON_EXTENSIONS.md#day6) · [训练推导](handbook/17_extension_workshops.md#day6) |
| 7 软件交付 | 扩展项目、真机部署与系统集成 | [后续项目](references/LESSON_EXTENSIONS.md#day7) · [从工具到系统](handbook/17_extension_workshops.md#day7) |

先修顺序：坐标 → 矩阵 → 刚体变换 → Jacobian → 数值IK；力矩与矩阵 → 动力学；函数与导数 → 网络训练；集合与概率 → 采样规划；函数与状态 → 并发与集成。缺哪一步，就补对应例子。

## 面向实际工作

| 工作方向 | 资料 |
|---|---|
| 接线、读反馈、调电机 | [单电机实操路线](PRACTICAL_PATH.md) · [工位记录](templates/MOTOR_COMMISSIONING.md) |
| 选型、配置、计算与排错 | [11门工程专题](ENGINEERING_PATH.md) · [工程实验](labs/ENGINEERING.md) |
| 机械臂方案设计与团队评审 | [设计开发流程](ROBOT_DEVELOPMENT_PATH.md) · [评审模板](templates/ROBOT_DESIGN_REVIEW.md) |
| 按技术问题查公式与方法 | [深度地图](DEPTH_MAP.md) · [算法故事](beginner/ALGORITHM_STORIES.md) · [算法地图](handbook/ALGORITHMS.md) |

机械方向可从结构与惯量开始，运动方向从变换与IK开始，感知方向从坐标与误差开始，软件方向从接口与通信开始。

## 图、实验与参考阅读

| 资料 | 用途 |
|---|---|
| [逐步演示](assets/interactive/concept_player.html) · [动画与分镜](assets/animations/README.md) · [技术图示](assets/README.md) | 看清过程与几何关系 |
| [交互课堂](INTERACTIVE.md) · [课堂首页](notebooks/00_start_here.ipynb) | 01–07基础，08–12原理专题，13–16工程带练 |
| [基础实验](labs/README.md) · [算法实验](labs/ALGORITHMS.md) | 查运行命令、输入输出和限制 |
| [参考数据](references/DATA_GUIDE.md) · [外部数据集](references/DATASETS.md) | 核对计算、模型声明和数据来源 |
| [文献路线](references/READING_GUIDE.md) · [先修与深入阅读](handbook/16_prerequisites_and_deeper_topics.md) | 按问题选择书籍与论文 |
| [项目地图](PROJECT_MAP.md) · [工具说明](TOOLS.md) · [来源索引](SOURCES.md) | 查团队文件与工具 |
| [OpenMAIC参考方案](OPENMAIC.md) | 在线AI答疑的适配方案，非基础课安装要求 |
| [验证记录](VALIDATION.md) | 查看实际检查范围；教学计算、模型声明和硬件实测分别记录 |

本地课堂尚未部署公共网址。命令行运行基础计算时，在培训资料目录执行 `python labs/course_lab.py all`。

## 练习与记录

基础课以文末三题为自检。额外练习见[基础衔接题](assessments/FOUNDATION_BRIDGES.md)、[原题库](assessments/QUESTIONS.md)、[扩展题](assessments/EXTENDED_QUESTIONS.md)和[算法题](assessments/ALGORITHM_EXERCISES.md)。扩展项目用[结业评分表](assessments/CAPSTONE.md)，工程训练用[工程考核](assessments/ENGINEERING_CHECKPOINTS.md)与[任务报告](templates/ENGINEERING_LAB.md)。

按当前问题选一个专题即可。深入时记下问题、输入与单位、结果、一个失败条件和下一步；需要请教时用[问题卡](templates/LEARNING_QUESTION.md)。
