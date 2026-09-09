# 从纸条机械臂开始：机器人开发自学

这是一套无需讲师的机器人开发入门资料。从两根纸条和几个数字开始，逐步认识本体、通信、运动、避障、感知AI与软件开发。第一周每天约3小时，目标是理解各模块怎样配合，并交付一个自己能解释、能复现的角度到位置小工具。

**第一次来，打开[七天路线](WEEK_PLAN.md)，然后读[第一天](lessons/day01_system_and_code.md)。** 每天只沿“正文→一个实验→自检→下一天”前进。需要补基础或继续深入时，再用下面的入口。

| 你现在需要什么 | 去哪里 | 读到哪里可以回来 |
|---|---|---|
| 知道今天学什么、交什么 | [七天路线](WEEK_PLAN.md) | 当天过关题与衔接说明 |
| 单位、坐标、角度或符号不懂 | [数学小台阶](beginner/MATH_STEPS.md) | 补会当前例题需要的一步 |
| 不会打开终端或运行代码 | [电脑操作卡](beginner/COMPUTER_FIRST_STEPS.md) | 能运行和修改一个输入 |
| 边读边改Python | [交互课堂安装](INTERACTIVE.md) → [课堂首页](notebooks/00_start_here.ipynb) | 当天01–07实验；08–12是选学 |
| 想学本周暂缓的内容 | [扩展选课表](EXTENSIONS.md) | 一个专题的解释、算例、自检和参考阅读 |
| 已有基础，按具体问题查技术细节 | [深度地图](DEPTH_MAP.md) | 对应手册与实验 |

## 一周围绕同一个问题

桌上有一块积木，机械臂怎样把它移到目标位置？我们先约定单位和任务，再描述手臂结构；结构需要命令和反馈；角度需要换成位置；运动需要避障；目标需要从感知得到；最后把这些知识整理成可靠的小工具。

学习例子统一使用30cm与20cm两杆。第一周有意把复杂任务拆开，各个练习可以独立完成。第七天交付的是FK小工具，完整抓取系统作为[后续系统集成专题](handbook/17_extension_workshops.md#day7)继续学习。

## 怎样看图、做实验和自检

先预测画面下一步，再播放或手算，最后说明结果为什么变化。[16主题逐步演示](assets/interactive/concept_player.html)可离线打开，支持暂停和单步；[12段动画与分镜](assets/animations/README.md)用于配合正文，[技术图示](assets/README.md)供深入阅读时查阅。不是每天都要看完所有图。

正文每篇都有三题和答案；先用它们过关。需要额外练习时用[基础衔接题](assessments/FOUNDATION_BRIDGES.md)、[扩展题](assessments/EXTENDED_QUESTIONS.md)或[算法题](assessments/ALGORITHM_EXERCISES.md)。不会时按[自学方法](SELF_STUDY.md)定位具体一步，再带着[问题卡](templates/LEARNING_QUESTION.md)请教同事。

## 资料库：用到时再查

| 资料 | 用途 |
|---|---|
| [参考数据](references/DATA_GUIDE.md)、[外部数据集](references/DATASETS.md) | 核对教学计算、模型声明和数据来源 |
| [文献阅读路线](references/READING_GUIDE.md)、[先修与深入阅读](handbook/16_prerequisites_and_deeper_topics.md) | 按问题挑章节，补大学数学与专业原理 |
| [算法故事](beginner/ALGORITHM_STORIES.md)、[算法地图](handbook/ALGORITHMS.md) | 从直觉进入方法比较和技术细节 |
| [项目地图](PROJECT_MAP.md)、[工具说明](TOOLS.md)、[来源索引](SOURCES.md) | 回到团队文件与实际工具 |
| [基础实验](labs/README.md)、[算法实验](labs/ALGORITHMS.md) | 查命令行实验的输入、输出和限制 |
| [OpenMAIC参考方案](OPENMAIC.md) | 了解在线AI答疑的适配与待验证事项；不是主线安装要求 |

安装一次后双击`start_classroom.cmd`启动本机JupyterLab：浏览器显示课程，本机Python计算。当前提供本地课堂，尚未部署公共网址。只想运行基础计算，可在仓库根目录执行`python labs/course_lab.py all`；其他命令见实验说明。

教学数据、模型文件声明与硬件实测应区分；本课程不把离线实验写成真机验证。实际检查范围见[验证记录](VALIDATION.md)。
