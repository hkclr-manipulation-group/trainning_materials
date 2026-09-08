# 参考文献：按难度读，不从第一页硬啃

本页给“为什么读、先读哪里、读完回答什么”。书和论文主要面向大学及以上读者；中学生先完成本课程的故事、动画和小题，再按兴趣深入。资料核对日期2026-09-07。

## A级：先看故事、图和示例

**R1：Dellaert与Hutchinson，Introduction to Robotics and Perception。** 在线书围绕具体机器人问题组织内容。先读Introduction里的应用场景，问“观测是什么，动作是什么”。不要一开始就跑全部notebook。[作者在线书](https://www.roboticsbook.org/S10_introduction.html)

**R2：Python官方教程。** 第一次只查变量、if、for、函数和异常；官方教程假设读者已有一些编程概念，因此先完成本课程的从零操作卡更合适。[官方教程](https://docs.python.org/3/tutorial/)

**R3：NIST单位换算资料。** 用于核对单位而非背常数。标准重力加速度约定值为9.80665 m/s²，本课手算采用9.81近似；它不等于在你的实验室测得的当地重力。[NIST换算表](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9)

## B级：完成纸条与代码后，学习系统数学

**R4：Kevin M. Lynch、Frank C. Park，Modern Robotics: Mechanics, Planning, and Control，Cambridge University Press，2017。** 先看第4章FK的图，再看第6章IK和第9章轨迹。进入矩阵、微积分推导前补数学。作者页面提供合法预印本、配套视频以及部分带答案练习，也说明正式书的先修要求。[作者书籍页](https://hades.mech.northwestern.edu/index.php/Modern_Robotics)

读后问题：为什么一个机构可以有多个IK解？为什么工具偏移也属于FK链？本课程没有复制整本书或受限答案，优先使用作者公开提供的练习。

**R5：Steven M. LaValle，Planning Algorithms，Cambridge University Press，2006。** 先读第2章离散规划中图搜索的思想，再读第5章采样规划的图。问题是“状态是什么、边是什么、失败说明什么”。[作者在线版](https://lavalle.pl/planning/)

**R6：Russ Tedrake，Underactuated Robotics在线讲义。** 作为控制进阶资料，先理解模型、状态与反馈，再看LQR和轨迹优化。第一周不要求推Riccati方程。[LQR章节](https://underactuated.mit.edu/lqr.html)、[轨迹优化章节](https://underactuated.mit.edu/trajopt.html)

## C级：带着数据和算法问题看论文

**R7：Tony Z. Zhao、Vikash Kumar、Sergey Levine、Chelsea Finn，Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware，2023，arXiv:2304.13705。** ACT原始工作。先看任务、硬件与方法总图；再问“为什么输出动作段、示教怎样采集”。论文任务结果只适用于其报告条件，不直接变成我们机器人的保证。[论文](https://arxiv.org/abs/2304.13705)

**R8：Cheng Chi等，Diffusion Policy: Visuomotor Policy Learning via Action Diffusion，2023起，arXiv:2303.04137。** 先看观测如何影响动作生成，再看去噪步骤和执行方式。这里保留arXiv标识；页面有2024年修订版，做精确复现时固定具体版本。[论文](https://arxiv.org/abs/2303.04137)、[作者项目](https://diffusion-policy.cs.columbia.edu/)

**R9：Alexander Khazatsky等，DROID: A Large-Scale In-The-Wild Robot Manipulation Dataset，2024起，arXiv:2403.12945。** 先看数据采集、任务划分和评估条件。要回答“为什么同一个任务在多个场景采集有价值”。[论文](https://arxiv.org/abs/2403.12945)

**R10：Open X-Embodiment Collaboration，Open X-Embodiment: Robotic Learning Datasets and RT-X Models，2023起，arXiv:2310.08864。** 先看多机器人数据如何组织，记录动作与观测差异；不要先下载全部内容。[论文](https://arxiv.org/abs/2310.08864)

## 怎样记一张文献卡

写下题名、作者、年份、网址/标识、阅读版本；再用自己的话写：解决什么问题、输入输出、用了什么数据、如何评估、有哪些限制、与我们项目有什么关系。图看懂了再追公式，不必逐句翻译全文。

网页会变化，论文也会更新。引用某个数值时写清表格、实验条件和版本。本文核对了书籍页、官方项目与论文摘要/元数据，没有声称完整复现这些研究。可导入文献工具的条目见 [references.bib](references.bib)，更多工具文档见 [SOURCES.md](../SOURCES.md)。

## 新增阅读卡：通信从历史读到字节

**先带着问题读：为什么有了可靠TCP，机器人仍然需要超时、序号和状态机？** 先看[协议栈讲义](../handbook/10_communication_stack_history.md)，再分别查[RFC768](https://www.rfc-editor.org/rfc/rfc768)的UDP字段、[RFC1122](https://www.rfc-editor.org/rfc/rfc1122.html)的分层，以及[RFC9293](https://www.rfc-editor.org/rfc/rfc9293)的字节流服务。RFC的规范性关键词有明确含义，先理解本课程用到的部分即可。

动手：运行[08实验](../notebooks/08_protocol_stack.ipynb)，对照50字节PCAP帧，写清14、20、8、8各自属于哪层。接着把同一条应用消息任意分成两块，确认解析结果不依赖接收边界。历史阅读的任务是说明需求怎样促成分层与标准，不必背年份。

## 新增阅读卡：IKFlow与多样逆解

[IKFlow: Generating Diverse Inverse Kinematics Solutions](https://arxiv.org/abs/2111.08933)适合在理解FK、IK多解、局部Jacobian与训练/验证划分后阅读。先问：同一目标有多个关节答案时，为什么直接回归平均值可能失败？作者如何用条件生成模型产生不同候选？候选又怎样验证？

阅读顺序：问题定义→模型输入输出→数据生成→实验约束和误差口径→失败与局限。记录目标是否包含姿态、机构自由度、关节范围、碰撞条件和耗时测量方式，再决定是否能与我们的项目对比。

本课[09实验](../notebooks/09_ik_families.ipynb)先用两连杆给出约139.4mm的分支平均误差，再比较最近邻初值与数值精修。这个实验帮助理解“数据给初值、模型验证答案”，没有复现IKFlow神经网络，也不能代替论文的性能实验。

## 工具文档怎样查

先在[工具链手册](../handbook/12_developer_toolchain.md)确定当前问题属于代码版本、协作、运行环境还是数据记录，再查对应官方文档的最小示例。练习从“按钮在哪里”转向“操作改变了哪个状态、怎样检查结果、怎样恢复”。平台界面和版本会变，文档入口集中在[来源索引](../SOURCES.md)。
