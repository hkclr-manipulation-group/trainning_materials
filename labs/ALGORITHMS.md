# 算法实验步骤与失败复现

Python 3.10+标准库，仓库根运行。先读对应手册，手算预期，再运行。

| 实验 | 命令 | 预期 | 失败对照 |
|---|---|---|---|
| 阻尼数值IK | `python labs/algorithm_lab.py ik` | converged，位置误差<1e-6 m | 改为伸直seed与向内目标，出现stationary_seed |
| A* | `python labs/algorithm_lab.py planning` | cost=19，路径经过墙开口 | 封住开口，应返回无路 |
| 梯形速度 | `python labs/algorithm_lab.py trajectory` | T=2.5 s，vp=.5 rad/s | D=.1时变三角形 |
| Kalman | `python labs/algorithm_lab.py filter` | 60条估计，输出方差和增益 | 修改Q/R观察变化处滞后 |
| PID | `python labs/algorithm_lab.py pid` | 力矩≤2 N·m，趋近1 rad | 取消D，观察振荡与超调 |

运行全部：`python labs/algorithm_lab.py all`。结果写入`outputs/algorithms_all.json`；单项结果写入对应`algorithms_<name>.json`，不会改机器人模型。

## 直接调用函数做对照

在仓库根启动 `python`，输入：

```python
import sys
sys.path.insert(0, "labs")
from algorithm_lab import numerical_ik, trapezoid, astar, kalman_step
from course_lab import ik

r = numerical_ik(target=(0.3, 0), seed=(0, 0))
print(r["success"], r["reason"], ik(0.3, 0))
print(trapezoid(distance=0.1)["duration_s"])
print(astar(3, 3, {(1,0),(1,1),(1,2)}, (0,0), (2,0))["success"])
print(kalman_step(0, 1, 2, 0, 1))
```

预期依次看到：数值IK失败但解析IK有解；约.63246秒；False；(1.0,.5,.5)。函数返回的失败是实验目标之一，不要为了输出成功而放宽全部限制。

## 离线通信工具作业

读取 [事件日志](data/protocol_events.csv)，计算最后有效反馈年龄；在表格中画 [SPI采样](data/spi_mode0.csv)，按上升沿读取10100101。

若有Wireshark：直接打开 [teaching_udp.pcap](data/teaching_udp.pcap)，无需启动抓包。显示过滤器`udp.port == 5000`应保留4帧；最后一帧时间.060 s。UDP载荷用课程的自创格式，不会被自动识别成电机协议；选中Packet Bytes手工查A1标记。事件日志.181秒的CHECK没有网络包，因此不在pcap中。

这些数据由`python tools/make_teaching_data.py`合成；脚本不打开网络设备，不发包。无Wireshark也可用CSV完成必做任务。
