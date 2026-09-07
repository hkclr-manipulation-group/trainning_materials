# %% [markdown]
# # 第四天｜从“末端去哪”到“关节如何动”
#
# [正文](../lessons/day04_control.md) · [运动学推导](../handbook/02_kinematics.md) · [控制推导](../handbook/03_control.md)
#
# 这一天内容较多，可分两次：先完成 FK/IK，再做轨迹/PID。目标是把**目标位置 → 关节解 → 带时间的参考 → 反馈控制**四步分开检验。

# %% [markdown]
# ## 1. FK：把两段位移相加
# 第一杆的世界方向是 q1；第二杆相对第一杆转 q2，所以它的世界方向是 q1+q2。
# `x=l1*cos(q1)+l2*cos(q1+q2)`，`y=l1*sin(q1)+l2*sin(q1+q2)`。
# 这里 l1=0.3 m，l2=0.2 m。滑块单位是度，传入函数时转换为弧度。你可以直接改下面函数，运行后滑块就会使用新版本。

# %%
def draw_arm(q1_deg=30, q2_deg=60):
    q1, q2 = np.radians([q1_deg, q2_deg])
    elbow = (.3*math.cos(q1), .3*math.sin(q1))
    tip = fk(q1, q2)
    fig, ax = plt.subplots()
    ax.plot([0, elbow[0], tip[0]], [0, elbow[1], tip[1]], "o-", lw=5)
    for radius in (.1, .5):
        ax.add_patch(plt.Circle((0, 0), radius, fill=False, ls="--", color="gray"))
    ax.set(xlim=(-.55, .55), ylim=(-.55, .55), aspect="equal", xlabel="x / m", ylabel="y / m",
           title=f"tip=({tip[0]:.4f}, {tip[1]:.4f}) m; det J={np.linalg.det(jacobian(q1,q2)):.5f}")
    plt.show()

arm_widget = widgets.interactive(draw_arm,
    q1_deg=widgets.IntSlider(value=30, min=-180, max=180, continuous_update=False),
    q2_deg=widgets.IntSlider(value=60, min=-180, max=180, continuous_update=False))
display(arm_widget)
draw_arm(30, 60)
assert np.allclose(fk(math.pi/2, 0), [0, .5])

# %% [markdown]
# ## 2. IK：先用几何给出独立答案
# 余弦定理给出 `c2=(x²+y²−l1²−l2²)/(2*l1*l2)`，于是 `q2=±acos(c2)`。
# `q1=atan2(y,x)−atan2(l2*sin(q2),l1+l2*cos(q2))`。
# 无限位、无障碍的位置可达半径在 0.1…0.5 m。两杆只有两个自由度，一般不能同时满足任意 x、y、工具方向三个约束。

# %%
target_m = (.3, .2)  # 改为 (.6, 0) 验证几何不可达
solutions = ik(*target_m)
for q in solutions:
    print("解 / deg:", np.degrees(q), "FK误差 / m:", math.dist(fk(*q), target_m))
    assert math.dist(fk(*q), target_m) < 1e-12
print("解的数量:", len(solutions))
assert ik(.6, 0) == []

# %% [markdown]
# ## 3. 雅可比 J：小步变化的换算表
# J 的第 i 列表示只改变第 i 个关节时末端怎样动。局部有 `Δp≈JΔq`，不是任意大步都精确。
# 下面在 q=(0,90°) 用一阶预测与真实 FK 差值比较，再用中央差分独立检查导数。微分的直觉是“把步长越取越小”；太小又会受浮点相减误差影响。

# %%
q = np.array([0., math.pi/2])
dq = np.array([.01, 0.])
J = np.array(jacobian(*q))
predicted = J @ dq
actual = np.array(fk(*(q+dq))) - np.array(fk(*q))
print("J =", J, "预测 / m:", predicted, "实际 / m:", actual)
eps = 1e-6
J_fd = np.column_stack([(np.array(fk(*(q+eps*np.eye(2)[i]))) -
                          np.array(fk(*(q-eps*np.eye(2)[i]))))/(2*eps) for i in range(2)])
assert np.allclose(J, J_fd, atol=1e-9)
assert np.allclose(J, [[-.2, -.2], [.3, 0.]])

# %% [markdown]
# ## 4. 数值 IK：误差、阻尼、限步和回溯
# 求 `Δq=Jᵀ(JJᵀ+λ²I)⁻¹e`，其中 e=目标−当前位置。它来自最小化 `||JΔq−e||²+λ²||Δq||²`：一边靠近目标，一边抑制过大的关节步长。
# 实际实现用线性方程求解，不必显式求逆；本课 2×2 系统直接解。λ 越大通常步子越保守，但不保证越快；本公式数值依赖长度和角度单位。
# 每一步还限制关节增量范数≤0.25 rad；若 FK 误差没下降，就将步长减半，最多回溯16次。默认终点容差1e−6 m，迭代预算200。

# %%
def compare_ik(damping=.03):
    result = numerical_ik(target=(.3, .2), seed=(.3, .6), damping=damping)
    errors = [row["error_m"] for row in result["history"]]
    fig, ax = plt.subplots()
    ax.semilogy(range(len(errors)), np.maximum(errors, 1e-16), "o-")
    ax.set(xlabel="iteration", ylabel="position error / m", title=f"lambda={damping}: {result['reason']}")
    plt.show()
    print("最终误差 / m:", result["error_m"], "记录数:", len(errors))
    return result

ik_widget = widgets.interactive(compare_ik, damping=widgets.FloatLogSlider(value=.03, base=10, min=-3, max=0, step=.2, continuous_update=False))
display(ik_widget)
result = compare_ik(.03)
assert result["success"] and result["error_m"] <= 1e-6

# %% [markdown]
# ## 5. 有解也可能卡住：不要把失败都叫不可达
# 完全伸直 q=(0,0) 时 J 的 x 行为零。目标 (.3,0) 的误差只有 x 分量，一阶算法可能得到零更新。几何解仍然存在，换一个弯曲的初值可以收敛。

# %%
stuck = numerical_ik(target=(.3, 0), seed=(0, 0))
retry = numerical_ik(target=(.3, 0), seed=(.3, .6))
print("直杆初值:", stuck["reason"], "弯曲初值:", retry["reason"])
assert ik(.3, 0) and not stuck["success"] and retry["success"]

# %% [markdown]
# ## 6. 轨迹：位置必须附带时间
# 静止到静止移动 D=1 rad，vmax=0.5 rad/s，amax=1 rad/s²。
# 加速用时 ta=vmax/amax=0.5 s；加减速总位移 vmax²/amax=0.25 rad；匀速用时(1−0.25)/0.5=1.5 s，总计2.5 s。
# 若 D<0.25 rad，达不到 vmax，就用三角速度，峰值 sqrt(D*amax)。这里没有 jerk 限制和多轴同步。

# %%
profile = trapezoid(distance=1, vmax=.5, amax=1)
fig, axes = plt.subplots(3, 1, sharex=True, figsize=(7, 6))
for ax, key, unit in zip(axes, ["q_rad", "v_rad_s", "a_rad_s2"], ["q / rad", "v / rad/s", "a / rad/s2"]):
    ax.plot([r["t_s"] for r in profile["samples"]], [r[key] for r in profile["samples"]])
    ax.set_ylabel(unit)
axes[-1].set_xlabel("time / s")
plt.tight_layout(); plt.show()
assert profile["duration_s"] == 2.5
assert trapezoid(distance=.04)["shape"] == "triangle"

# %% [markdown]
# ## 7. 控制：命令并不等于实际位置
# 使用教学动力学 `q̈=(τ−0.3*q̇)/I`，I=1 kg·m²，|τ|≤2 N·m。PID 输出 `Kp*e+Ki*积分−Kd*q̇`；微分放在测量速度上，避免目标突变产生直接微分尖峰。
# 每步先更新速度，再更新位置，是半隐式 Euler。积分只在未饱和或能使输出退出饱和时累积，减少积分饱和。参数不能直接搬到真机。

# %%
def plot_pid(kp=16., kd=6.):
    rows = pid_demo(kp=kp, ki=4, kd=kd)
    times = [r["t_s"] for r in rows]
    fig, axes = plt.subplots(2, 1, sharex=True, figsize=(7, 5))
    axes[0].plot(times, [r["q_rad"] for r in rows]); axes[0].axhline(1, color="gray", ls="--")
    axes[0].set_ylabel("q / rad")
    axes[1].plot(times, [r["torque_nm"] for r in rows]); axes[1].set(xlabel="time / s", ylabel="torque / N m")
    plt.tight_layout(); plt.show()
    print("采样峰值超调:", max(0, max(r["q_rad"] for r in rows)-1),
          "最后记录误差:", 1-rows[-1]["q_rad"])
    assert max(abs(r["torque_nm"]) for r in rows) <= 2

pid_widget = widgets.interactive(plot_pid,
    kp=widgets.FloatSlider(value=16, min=2, max=30, step=2, continuous_update=False),
    kd=widgets.FloatSlider(value=6, min=0, max=12, step=1, continuous_update=False))
display(pid_widget)
plot_pid()

# %% [markdown]
# **修改任务：** 比较 Kd=0 与6的超调；比较 IK λ=0.003 与0.3的迭代数；给出一组几何可达但被你指定的 q2 范围排除的目标。
#
# **自检答案：** IK 解不含时间；轨迹含时间但不保证跟踪；PID 依赖模型、采样和反馈；奇异初值导致的失败不能证明全局不可达。更完整的三维姿态误差与限位诊断见[工程细节第4–5节](../handbook/09_engineering_details.md)。
