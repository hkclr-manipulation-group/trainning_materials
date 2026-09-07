# 入门术语表

| 术语 | 中文与一句话解释 |
|---|---|
| Link / Joint | 连杆 / 关节；刚体与连接关系 |
| DOF | 自由度；描述系统构型需要的独立变量数 |
| Payload | 负载；必须说明是否包含工具和转接件 |
| Torque | 力矩；转动作用，常用 N·m |
| Gear ratio | 减速比；需明确输入输出的定义 |
| Backlash | 背隙；换向时传动的间隙效应 |
| Stiffness | 刚度；载荷引起变形的关系 |
| URDF | 机器人 link/joint 及相关属性的 XML 描述 |
| Mesh | 网格；以顶点和面近似几何表面 |
| Frame | 坐标系；说明位置、方向的参考 |
| TCP（机器人） | 工具中心点或工具坐标框架 |
| TCP（网络） | 传输控制协议；与工具中心点无关 |
| Pose | 位姿；位置加方向 |
| FK / IK | 正 / 逆运动学；关节到位姿 / 位姿到关节 |
| Seed | 数值求解的初始猜测 |
| Jacobian | 雅可比；局部关节运动到任务运动的映射 |
| Singularity | 奇异；局部运动映射降秩等退化情况 |
| Trajectory | 轨迹；带时间参数的运动 |
| Feedback | 反馈；系统测量状态返回控制器 |
| Saturation | 饱和；输出达到限制，不能继续按公式增大 |
| Latency / Jitter | 延迟 / 抖动；耗时与其变化 |
| CAN ID | CAN 标识符；不自动等于节点号 |
| Endianness | 字节序；多字节数值的字节排列 |
| ABI | 二进制接口约定；影响原生库能否兼容加载 |
| SDK | 软件开发工具包；接口、库、示例与文档的组合 |
| RWS / DWS | 可达 / 灵巧工作空间；需说明采样与判据 |
| Collision margin | 碰撞余量；人为扩展的距离约束 |
| Intrinsics / Extrinsics | 相机内参 / 外参；投影参数 / 坐标变换 |
| Observation / Action | 观测 / 动作；策略的输入 / 输出 |
| Episode | 一段完整交互或任务轨迹 |
| Data leakage | 数据泄漏；评估信息不恰当地进入训练或选型 |
| Sim-to-real | 仿真到现实迁移；需处理模型与真实系统差异 |
| VLA | 视觉语言动作模型；结合图像、语言和动作表示 |
| Regression test | 回归测试；防止已知正确行为再次被破坏 |
| Vibe coding | 通过自然语言与 AI 快速迭代代码的协作方式 |
