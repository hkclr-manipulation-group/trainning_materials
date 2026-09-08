# 自学深度地图：先建立全貌，再沿专题深入

第一周仍以每天约3小时的入门主线为基准。新增专题用于替换当天较浅的重复练习或在后续继续学，不把所有论文和推导塞进七天。每个主题先讲动机和直觉，再给数学、实现、失败与验证。

| 主题 | 起步 | 新增深入内容 | 动手与证据 |
|---|---|---|---|
| 数学 | [数学台阶](beginner/MATH_STEPS.md) | [代数、集合、微积分、概率的分工](handbook/13_systems_deepening.md) | 矩阵维度、中央差分、局部近似误差 |
| 本体 | [本体手册](handbook/01_body.md) | [任务约束、传动、精度、惯量与刚度](handbook/13_systems_deepening.md) | 静态力矩、URDF与FK对照 |
| 通信 | [字节与时序](handbook/08_communication.md) | [历史、协议栈、分帧、仲裁、实时性](handbook/10_communication_stack_history.md) | [协议栈Notebook](notebooks/08_protocol_stack.ipynb) |
| 运动学 | [FK/IK基础](handbook/02_kinematics.md) | [几何、代数、解集、Jacobian、数据驱动](handbook/11_inverse_kinematics_families.md) | [方法比较Notebook](notebooks/09_ik_families.ipynb) |
| 控制 | [控制手册](handbook/03_control.md) | [采样、延迟、串级、前馈、LQR/MPC](handbook/13_systems_deepening.md) | [延迟实验](notebooks/10_visual_reasoning.ipynb) |
| 碰撞与规划 | [规划手册](handbook/04_planning.md) | [图、采样、优化、距离与边检查](handbook/13_systems_deepening.md) | A*逐步g/h/f、分级通过计数 |
| 感知与估计 | [估计手册](handbook/05_estimation.md) | [误差传播、RANSAC、ICP/PnP、可观测性](handbook/13_systems_deepening.md) | 像素/深度偏差、滤波与滞后 |
| AI | [AI手册](handbook/06_ai.md) | [表示、优化、多模态、拆分、闭环评价](handbook/13_systems_deepening.md) | 梯度轨迹、IK分支平均反例 |
| 软件与工具 | [软件手册](handbook/07_software.md) | [Git/GitHub/GitLab/Gitea到CI、环境、数据](handbook/12_developer_toolchain.md) | Issue、PR、CI示例、复现记录 |

## 一种方法真正学会的标准

能够说明它为什么被需要，写出输入输出与假设，手算一个小例子，运行实现，再构造一个失败案例。最后解释替代方法的取舍，并知道哪些结果还没有验证。

新增[逐步演示器](assets/interactive/concept_player.html)将“看哪里、发生了什么、为什么、不能推出什么”放在每一步画面里。它可离线打开，不需Jupyter；要修改算法代码则进入上表Notebook。

复习使用[扩展练习与解析](assessments/EXTENDED_QUESTIONS.md)。文献无需从第一页连续读到最后：先带着一个具体问题读定义、方法、实验条件和限制，再回课程实现做对照。
