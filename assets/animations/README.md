# 十二段动画：先预测，再播放，再停下来解释

动画都保存在这里，离线可看，不是外链视频。GIF循环播放，每段约7秒；每张静态分镜按左上、右上、左下、右下顺序阅读。图中均为教学模型或示意，非真机录像。

| 动画 | 四步分镜 | 播放前先猜什么 |
|---|---|---|
| [01 力矩](lever.gif) | [PNG](lever_steps.png) | 同一物体离转轴更远，转动作用会变大吗？ |
| [02 坐标](coordinates.gif) | [PNG](coordinates_steps.png) | (3,2)从哪里开始数，先横还是先竖？ |
| [03 角度](rotation.gif) | [PNG](rotation_steps.png) | 杆转竖直时，横向长度还剩多少？ |
| [04 正运动学](fk.gif) | [PNG](fk_steps.png) | 第二个角从哪里量？ |
| [05 逆运动学](ik.gif) | [PNG](ik_steps.png) | 每一步误差是否减小？ |
| [06 通信](protocol.gif) | [PNG](protocol_steps.png) | 发送完成时，反馈已经回来了吗？ |
| [07 A*找路](astar.gif) | [PNG](astar_steps.png) | 为什么不能直接穿墙？ |
| [08 轨迹](trajectory.gif) | [PNG](trajectory_steps.png) | 什么时候加速，什么时候停下？ |
| [09 反馈](feedback.gif) | [PNG](feedback_steps.png) | 接近目标后应怎样纠正？ |
| [10 滤波](filter.gif) | [PNG](filter_steps.png) | 平滑与及时响应可能冲突吗？ |
| [11 学习](learning.gif) | [PNG](learning_steps.png) | 预测线改变后，离样本更近了吗？ |
| [12 碰撞近似](collision.gif) | [PNG](collision_steps.png) | 外壳碰到是否必然等于实体碰到？ |

## 想暂停、逐帧或慢放

在培训仓库根运行`python labs/animation_player.py`，使用原生Python窗口。选择主题，点击播放/暂停、上一帧/下一帧，拖动速度条。它不需要浏览器或网络，不控制机器人。

没有Tk桌面环境时，直接看GIF和PNG。播放器速度是阅读速度，不是物理时间；物理时间以图中文字和数据表为准。动画内容已保存，观看不需要Pillow；仅维护重建时需要它。

## 哪些来自真实计算，哪些是说明性动画

IK、A*、轨迹、反馈、滤波按教学程序结果显示。FK按明确角度序列计算。力矩按固定质量与变化力臂计算。坐标、通信、碰撞是示意；学习动画按预设斜率变化解释拟合，不是优化器运行日志。相关数值见 [数据说明](../../references/DATA_GUIDE.md)。

生成脚本：`python tools/render_beginner_animations.py`，使用Pillow和已安装中文字体。现有 [14组静态技术图](../README.md) 仍可作为进一步阅读。
