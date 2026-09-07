# %% [markdown]
# # 第一天｜数据从输入走到结果
#
# [先读正文](../lessons/day01_system_and_code.md)。本实验把“手臂有多长、转多快”变成明确输入与输出。先修只有除法。
#
# 今天的交付：一个把速度和时间变成位移的小函数，以及至少三组独立预期。`assert` 是可执行的判断：条件不成立时停止并报错，提醒我们检查假设。

# %% [markdown]
# ## 1. 单位是接口的一部分
# 1 m=1000 mm，1 s=1000 ms，转一圈=360°=2π rad。角度单位错用不一定报错，却会算错。
# 100 Hz 表示每秒 100 次，周期 `dt=1/100=0.01 s`。只写循环 100 次并不能保证程序真在一秒内完成。

# %%
frequency_hz = 100
speed_deg_s = 30
duration_ms = 200
dt_s = 1 / frequency_hz
angle_rad = math.radians(speed_deg_s) * duration_ms / 1000
print("周期 / s:", dt_s, "位移 / rad:", angle_rad, "位移 / deg:", math.degrees(angle_rad))
assert abs(math.degrees(angle_rad) - 6) < 1e-12
print("把30°误当30 rad:", math.cos(30), "正确:", math.cos(math.radians(30)))

# %% [markdown]
# ## 2. 写一个有合同的函数
# 输入速度单位为 rad/s、时间单位为 s；输出 rad。时间不能负数，数值不能 NaN/无穷。
# `def` 定义功能，`return` 交回结果；调用函数才真正计算。允许负速度表示反方向。

# %%
def displacement(speed_rad_s, duration_s):
    if not all(math.isfinite(v) for v in (speed_rad_s, duration_s)):
        raise ValueError("输入必须是有限数")
    if duration_s < 0:
        raise ValueError("时间不能是负数")
    return speed_rad_s * duration_s

assert displacement(.5, 2) == 1.0
assert displacement(-.5, 2) == -1.0
assert displacement(.5, 0) == 0
try:
    displacement(.5, -1)
except ValueError as error:
    print("预期拒绝:", error)
else:
    raise AssertionError("负时间应该报错")

# %% [markdown]
# ## 3. 读取参考表，先认列名再画图
# CSV 是每行一条记录的文本。表头里的 `_m`、`_deg` 表示单位，读取后字符串须转为数。
# 这些是教学公式生成的参考点，并非机器人的实测日志。连接散点也不表示一条可执行轨迹。

# %%
with (ROOT / "references" / "data" / "fk_reference.csv").open(encoding="utf-8-sig") as stream:
    rows = list(csv.DictReader(stream))
print("列名:", list(rows[0]))
print("首行:", rows[0])
fig, ax = plt.subplots()
ax.scatter([float(r["x_m"]) for r in rows], [float(r["y_m"]) for r in rows])
ax.set(xlabel="x / m", ylabel="y / m", aspect="equal", title="Synthetic FK reference points")
plt.show()

# %% [markdown]
# ## 4. 自己修改，再证明
# 把速度改为 −90°/s，时间改为 500 ms。先在纸上写 −45°，再验证；补一个 NaN 输入的异常检查。
#
# **技术补充：** 文件描述数据，函数转换数据，测试比较结果，日志保留经过。实际系统再加时间戳、序号和版本，这样同事才能复现。见 [工程细节第1节](../handbook/09_engineering_details.md)。
#
# **自检答案：** 位移为 −π/4 rad；NaN 不能当普通位置使用；Hz 是频率而非速度。程序数值正确不代表单位、参考系和采样时间正确。
