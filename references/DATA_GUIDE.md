# 参考数据：先知道是什么，再拿来比较

这里提供可以直接打开的小数据文件，不要求下载大数据集。CSV是表格，JSON是带名称的数据。数值保留计算精度；纸笔对照时允许合理舍入。

## 1. 三种来源不能混在一起

**教学计算数据**由本仓库公式和脚本产生，用于核对作业；**本地文件快照**忠实记录项目URDF里写的内容，不能当成硬件实测；**外部数据集**在官方站点提供，这里只有阅读卡与链接，尚未下载。

我们没有把未验证参数写成额定规格，也没有提供伪造的真机测量。每份本地数据的文件名、行数、字段和SHA-256校验值见 [manifest.json](data/manifest.json)。校验值像文件指纹，文件内容变化后它会变化。

## 2. 直接可用的数据表

| 文件 | 一行代表什么 | 单位与条件 | 先核对什么 |
|---|---|---|---|
| [fk_reference.csv](data/fk_reference.csv) | 一种两连杆姿态 | 两杆.3/.2 m；输入deg，输出m和cm | (0°,90°)→(.3,.2) m |
| [lever_reference.csv](data/lever_reference.csv) | 一个质量和水平力臂组合 | kg、m、N·m；g近似9.81 m/s² | .5 kg、.4 m→1.962 N·m |
| [ik_trace.csv](data/ik_trace.csv) | 数值IK的一次检查 | 角度rad、位置与误差m | 目标(.3,.2) m，最终误差<1e-6 m |
| [trajectory_reference.csv](data/trajectory_reference.csv) | 轨迹某时刻 | s、rad、rad/s、rad/s² | 总时长2.5 s；峰值速度.5 |
| [pid_reference.csv](data/pid_reference.csv) | 简化动力学一个采样 | dt=.005 s，单位惯量，摩擦系数.3 | 指令限制±2 N·m |
| [filter_reference.csv](data/filter_reference.csv) | 一个测量与估计 | 教学标量；Q=.01、R=.25是方差 | 测量、估计、真值分别是哪列 |
| [learning_reference.csv](data/learning_reference.csv) | 一个合成回归样本 | 无物理单位；train/test已分开 | 只用train拟合 |
| [grid_reference.csv](data/grid_reference.csv) | 一个地图格点 | x/y为索引，blocked为0或1 | 墙的开口在y=6 |
| [path_reference.csv](data/path_reference.csv) | 路线上的一个点 | step为序号；相邻点移动1格 | 20个点组成19步 |

综合预期结果和生成条件见 [expected_results.json](data/expected_results.json)。数据由确定性公式生成，没有随机抽样；滤波中的噪声是确定的正弦组合，不是实际传感器测量。闭环PID的数值积分方法见源代码，结果不是连续动力学的精确解析解。

## 3. 第一个数值对照练习

| q1 | q2 | 先在脑中摆一下 | x、y（厘米） |
|---:|---:|---|---|
| 0° | 0° | 两杆都向右 | 50、0 |
| 0° | 90° | 第一杆右，第二杆上 | 30、20 |
| 90° | 0° | 两杆都向上 | 0、50 |
| 90° | −90° | 第一杆上，第二杆右 | 20、30 |
| 30° | 60° | 第二杆总方向90° | 约25.98、35 |

先画图再打开CSV。如果CSV中的理论0写成极小数，例如1e-17，这是浮点计算的常见舍入表现；不要按字符串要求它必须显示为0。

## 4. 团队模型的本地文件快照

[local_model_declarations.csv](data/local_model_declarations.csv)记录四个模型、共24个转动关节：spark2_v2、D20260901B、D20260902B60、D20260903B10。它保留原始关节名、父子连接、角度范围、声明速度/力矩、原点和轴。

2026-09-07工作区文件中，D2026三套的动态限值含0，spark2_v2里也有较大的声明值。**这些都是文件内容，不是验证后的物理能力。** 例题应问“这个值是否需要确认”，不能将0理解为机械臂永远不能动，也不能把大数直接送到硬件。

来源相对路径与每个URDF的SHA-256见 [local_model_sources.json](data/local_model_sources.json)。更新源文件后，旧表只代表旧快照。课程包本身可独立读取这份快照，不需要复制mesh或运行其他仓库。

## 5. 重建与使用范围

在培训仓库根运行`python tools/build_reference_data.py`重建教学表；加`--snapshot-models ../collision_shpere_generation/models`才会读取本地机器人源文件。没有同级项目时，不运行这个可选参数即可。

适合：手算核对、画图、编解码与算法单元测试。不适合：直接作为电机额定参数、真机控制增益、完整动力学仿真或机器人AI训练数据。扩展真实数据阅读见 [DATASETS.md](DATASETS.md)。
