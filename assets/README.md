# 图示索引与使用方法

下面14组图由课程代码生成，PNG直接阅读，SVG可放大或用于笔记。所有机械尺寸、地图与数据均为教学例，不是真机测量。公式和图中的单位对应正文。

| 图 | 看图时回答什么 | 矢量版 |
|---|---|---|
| [系统链](figures/system.png) | 目标在哪一层变成动作？状态在哪里返回？ | [SVG](figures/system.svg) |
| [坐标变换](figures/frames.png) | 先旋转还是先平移？点在两个框架各是多少？ | [SVG](figures/frames.svg) |
| [两连杆与IK分支](figures/two_link.png) | 为什么相同末端位置有不同肘形？ | [SVG](figures/two_link.svg) |
| [数值IK迭代](figures/ik_iterations.png) | 误差怎样随迭代变化？停止依据是什么？ | [SVG](figures/ik_iterations.svg) |
| [雅可比速度映射](figures/jacobian.png) | 伸直时丢失哪个瞬时方向？ | [SVG](figures/jacobian.svg) |
| [构型空间](figures/cspace.png) | 世界里的一个障碍为什么变成许多角度组合？ | [SVG](figures/cspace.svg) |
| [A*搜索](figures/astar.png) | 路径为何绕行？长度能否手数？ | [SVG](figures/astar.svg) |
| [时间轨迹](figures/trajectory.png) | 短行程为什么没有匀速段？ | [SVG](figures/trajectory.svg) |
| [控制闭环](figures/control_loop.png) | 限幅怎样影响反馈？ | [SVG](figures/control_loop.svg) |
| [PID响应](figures/pid_response.png) | 超调、输出饱和、最终误差在哪里看？ | [SVG](figures/pid_response.svg) |
| [Kalman滤波](figures/kalman.png) | 平滑与跟踪真实变化如何取舍？ | [SVG](figures/kalman.svg) |
| [通信表示](figures/protocol.png) | 一个角度在哪一步变成整数和字节？ | [SVG](figures/protocol.svg) |
| [感知坐标链](figures/perception.png) | 像素到基座需要哪些参数？ | [SVG](figures/perception.svg) |
| [学习流程](figures/learning.png) | 训练、选型与最终评估分别用哪份数据？ | [SVG](figures/learning.svg) |

学习流程图箭头表示工作顺序，不表示将测试数据交给训练器；正文规定按完整轨迹分组并独立保留测试。构型空间只示范零厚度平面连杆与圆形障碍，不证明真实网格碰撞精度。

## 交互探索

```powershell
python labs/kinematics_explorer.py
```

拖动q1/q2，观察末端；点击可达环内的点，切换IK分支；点击环外，观察不可达提示；把两杆伸直，观察det(J)接近0。这个原生Tk窗口不需要浏览器或网络，也没有设备控制。没有Tk时照静态图做命令行实验。

## 重建图片（可选，不是学习前提）

图已随仓库提供。维护图片时安装matplotlib，在仓库根运行`python tools/render_figures.py`。脚本使用Windows的Microsoft YaHei字体；其他系统需配置可用中文字体。核心实验不需要matplotlib。生成器从相同的FK、IK、规划、控制数据生成曲线，修改算法后应重建并核对图片。
