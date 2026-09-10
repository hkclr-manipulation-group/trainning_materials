# 工程实验：用可复现数据练诊断

[工程课程](../ENGINEERING_PATH.md) · 实现：[engineering_lab.py](engineering_lab.py)

Python 3.10+标准库即可，在培训仓库根目录运行，不访问硬件。所有输入与输出都在脚本中可见；先手算再运行，之后改变一个输入验证自己的解释。输出保存到`outputs/engineering_<实验名>.json`。

| 命令末尾的实验名 | 原始输入 | 应观察到什么 | 再修改一次 |
|---|---|---|---|
| `math` | q=(0.4,0.8)rad、h=1e-6rad | 解析与差分雅可比误差很小；重力矩4.0221N·m | 将h改大，比较差分误差 |
| `canfd` | 长度0、8、9、12、33、64及65 | 9→12字节，33→48字节，65拒绝；载荷预算61.44% | 改节点数/频率，解释为何只算载荷不够 |
| `ethercat` | `27 00 18 fc ff ff`，WKC 6/4，期望6 | 位置-1000，状态使能；WKC4不发布输入；截断拒绝 | 改状态字附加位，状态不应被无关位破坏 |
| `timing` | 五次开始时间和持续时间 | 平均间隔1ms仍有1次截止违例，迟到0.2ms | 只加长一次计算，看哪个指标变化 |
| `planning` | 0到1，障碍[0.49,0.51] | 端点检查误通过，中点发现碰撞 | 改障碍位置，说明固定中点也不能保证全覆盖 |
| `perception` | fx500、u370、cx320、Z1m、40ms时差 | X=0.1m，单像素2mm，时间错配8mm | 改速度与延迟，看误差是否按模型增长 |
| `ai` | episode A跨训练/测试 | 报告A泄漏，整段分组无该类重叠 | 用新episode但相同场景，解释检测范围 |
| `software` | 开始→故障→通信恢复→复位 | 仅通信恢复不重新运动，复位后回READY | 加断连事件，确认旧start不直接运行 |

例如：

```text
python labs/engineering_lab.py canfd
python labs/engineering_lab.py ethercat
python labs/engineering_lab.py all
```

要修改函数输入，可在Python中直接调用：

```python
import sys
sys.path.insert(0, "labs")
from engineering_lab import fd_layout, decode_teaching_pdo, sample_segment
print(fd_layout(25))  # 容量32，填充7
print(decode_teaching_pdo(bytes.fromhex("40 00 00 00 00 00")))
print(sample_segment(0, 1, (.24, .26), 2))  # 这次连中点也漏检
```

这些实验只实现说明中明确的教学模型：没有CAN总线仲裁模拟、EtherCAT主站、完整CiA 402控制器、三维碰撞或真实视觉/策略模型。填写[工程任务报告](../templates/ENGINEERING_LAB.md)时，另列真实设备与完整算法验证。
