# 随课扩展

[扩展资料](../EXTENSIONS.md) · [基础路线](../WEEK_PLAN.md)

这里收录基础课相关的专业细节，按需要查阅。

<a id="day2"></a>

## 本体：团队模型比较

真实项目中的D2026与spark2_v2不能只凭外观判断是不是同一个机器人。应比较杆长、关节轴、零度姿态、运动范围与工具位置。

[本地模型参数快照](DATA_GUIDE.md)记录了文件参数和校验值。“文件写了100”不等于硬件真的允许100；CAD导出的0也可能是未填写。读数字时一起核对来源和含义。

CAD操作见[本体手册](../handbook/01_body.md)，选型与标定见[本体、传动与电气](../engineering/02_body.md)和[模型与标定](../engineering/06_kinematics.md)。

[返回第二课](../lessons/day02_body_and_urdf.md)

<a id="day3"></a>

## 通信：协议与观察工具

UART、SPI、USB、CAN不都处于同一层。SPI常用于板内芯片连接，USB常连接电脑与设备，CAN常用于设备总线；设备在通道上传送自己的应用消息。

TCP像连续送来的纸带，程序要识别消息边界；UDP像独立信件，可能丢失、重复或乱序。详细能力与限制见[通信手册](../handbook/08_communication.md)。

用Wireshark打开[教学pcap](../labs/data/teaching_udp.pcap)，无需连接设备或启动抓包。过滤条件为 `udp.port == 5000`，应看到4条消息；观察时间、方向和字节。没有软件可读[事件日志](../labs/data/protocol_events.csv)。

SPI练习使用[spi_mode0.csv](../labs/data/spi_mode0.csv)：找CLK从0变1的行，读取同一行MOSI，8位应为10100101，即A5。操作步骤见[算法实验](../labs/ALGORITHMS.md)。

工程专题：[接口与网络](../engineering/03_interfaces.md) · [CAN FD](../engineering/04_canfd.md) · [EtherCAT](../engineering/05_ethercat.md)。

[返回第三课](../lessons/day03_communication.md)

<a id="day4"></a>

## 运动：IK、轨迹与控制方法

运行 `python labs/algorithm_lab.py ik`，查看最终误差，并对照[迭代表](data/ik_trace.csv)中的位置和差距。交互拖动可运行 `python labs/kinematics_explorer.py`；没有图形环境就看基础课动画与数据表。

轨迹分段计算见[控制手册](../handbook/03_control.md)。PID在比例控制上加入累积误差和误差变化率；PID、LQR、MPC的比较见[算法故事](../beginner/ALGORITHM_STORIES.md)。

进一步练习：[运动学与标定](../engineering/06_kinematics.md) · [控制与实时执行](../engineering/07_control.md)。

[返回第四课](../lessons/day04_control.md)

<a id="day5"></a>

## 规划：工作空间与模型比较

工作空间图会在多个位置尝试求解。某点试了16种工具方向，12种成功，覆盖比例为12÷16=0.75。该点在本次采样下可达；若筛选条件要求全部方向成功，它就不会显示。

因此，“图空了”可能来自筛选条件、模型、碰撞或求解失败。比较团队模型时保持采样设置一致，并说明尺寸、限位和工具差异，参考[模型数据说明](DATA_GUIDE.md)。

腕部折叠问题中，应先检查碰撞球是否贴合零件，再判断真实机构，不能只为通过检查而永久忽略碰撞对。RRT、PRM等方法见[算法故事](../beginner/ALGORITHM_STORIES.md)，工程练习见[碰撞、规划与工作空间](../engineering/08_planning.md)。

[返回第五课](../lessons/day05_collision_workspace.md)

<a id="day6"></a>

## AI：学习方法与数据集

模仿学习从人的示范学习观测与动作的对应；强化学习通过交互得到奖励或扣分，调整行为；视觉语言动作模型把图片与语言任务结合到动作预测。

ACT预测一段动作，Diffusion Policy通过逐步去噪生成动作。接入机器人前，要核对输出是角度还是速度、度还是弧度、关节顺序是否一致，以及动作是否过期。模型输出和SDK输入都是6个数，也不代表可以直接连接。

[文献路线](READING_GUIDE.md)介绍相关书籍与论文，[外部数据集卡](DATASETS.md)介绍DROID和Open X-Embodiment。先看字段与任务，再决定是否下载数据。

工程专题：[感知与估计](../engineering/09_perception.md) · [AI与策略部署](../engineering/10_ai.md)。

[返回第六课](../lessons/day06_perception_ai.md)

<a id="day7"></a>

## 软件：后续项目

基础课完成角度到位置工具、三个手算测试和使用说明。想继续练习，可以读取JSON并解析教学报文，完成[结业任务](../assessments/CAPSTONE.md)；再增加日志统计、数值IK或路径分析。

完整六轴设计、真机整定和大型策略训练需要后续专题与实践。算法从[故事](../beginner/ALGORITHM_STORIES.md)进入[手册](../handbook/ALGORITHMS.md)，系统实现见[软件工程与交付](../engineering/11_software.md)，相关基础见[工程数学](../engineering/01_math.md)。

[返回第七课](../lessons/day07_vibe_coding.md)
