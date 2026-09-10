# 团队资料地图

2026-09-10新增工程阅读入口：[CAN FD课程](engineering/04_canfd.md)逐项对照`cxt_canfd`、`zlg_canfd`与`zlg_canfd_whj_motor`的配置/收发实现；[EtherCAT课程](engineering/05_ethercat.md)给出通用主站调试路线。本次工作区检索未找到可直接采用的EtherCAT工位实现，主站、ESI与驱动器型号仍需由实际工位资料确认。

以下路径按当前工作区检查，日期 2026-09-07。链接指向本仓库的同级项目；只复制本培训仓库时，基础讲义和实验仍可用，但这些项目链接需要相应仓库。

| 开发层 | 已有资料 | 本周读什么 | 注意边界 |
|---|---|---|---|
| 本体设计 | [spark2_design](../spark2_design) | 三套 D2026 模型目录、装配与导出组织 | CAD 限位需要工程确认 |
| 模型配置 | [cuarm_configuration](../cuarm_configuration/README.md) | 配置如何组合机器人模型 | 与具体机器人版本对应 |
| 碰撞模型 | [collision_shpere_generation](../collision_shpere_generation/README.md) | 模型打包、生成、viewer、导出 | 球间隙不是 STL 穿透深度 |
| 工作空间 | [robot_workspace_dexterous](../robot_workspace_dexterous/README.md) | 校验、诊断、采样和过滤 | CPU 诊断不能替代 GPU IK |
| SDK | [spark2_sdk](../spark2_sdk/README.md) | Python/C++ 分发、配置入口 | 原生模块与解释器 ABI 需匹配 |
| 运动学示例 | [calculate_kinematics.py](../spark2_sdk/spark2_python_dist/examples/calculate_kinematics.py) | seed、success、FK 复算 | SDK 输入单位单独核实 |
| 运动示例 | [move_point.py](../spark2_sdk/spark2_python_dist/examples/move_point.py) | 状态、使能、运动、反馈顺序 | 包含真实硬件调用，入门阶段静态阅读 |
| 应用验收 | [spark2_auto_test](../spark2_auto_test/README.md) | Python/C++ 测试职责、报告 | 这些验收并非都可脱机运行 |
| 桥接固件 | [USB-CAN 拓扑](../usb2can/docs/hardware_topology.md) | 主机通道 → SPI → F446 → CAN 映射 | 根 README 与实现可能不同步 |
| 电机通信应用 | [vision_robotics_skin_demo](../vision_robotics_skin_demo/README.md) | 协议库、控制器、学习客户端边界 | 型号和 CAN ID 以当前实现为准 |
| 标定 | [calibration](../calibration) | joint_pos_data、end_effector、变换脚本 | 历史标定不代表当前安装 |
| 上层控制 | [cuarm_panel_control](../cuarm_panel_control/README.md) | 上层进程和实时进程关系 | 原启动命令属于其运行环境 |
| 团队产品资料 | [spark2_doc](../spark2_doc/README.md) | 产品文档入口 | 产品说明与开发源码一起核对 |

## 阅读一份不熟悉的仓库

先读 README 的职责与运行边界；再找入口文件、配置、核心接口和测试；最后沿一个输入追踪到输出。记录“文档声称”“代码观察”“本机运行”三种证据，不把它们混为已验证事实。

例如查看 `usb2can`：根 README 部分描述早期交付骨架，而工作区已有固件目录及拓扑说明。应结合具体文件判断，不因 README 一句话就断言功能不存在。

## 本周选用的真实问题

1. CAD 导出的零速度限位会造成求解器区间退化；用于静态评估的显式占位值并不是硬件额定参数。
2. 非主轴方向的 URDF 关节轴可能遇到特定解析器限制；修复要保持 FK 等价，不能任意把轴改成 Z。
3. 球包络过大导致腕部折叠误判；需要几何证据，不能直接永久忽略相关连杆。
4. 不同设计的末端、限位和采样参数不同，工作空间图不能直接横向比较。

这些案例用于教授排错方法。开发中的紧贴球拟合尚不能作为课程已完成验证的结果；课程也不声称进行了真机或 GPU 验收。
