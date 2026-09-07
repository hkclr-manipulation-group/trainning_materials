# %% [markdown]
# # 第五天｜碰撞、路径与工作空间
#
# [正文](../lessons/day05_collision_workspace.md) · [规划手册](../handbook/04_planning.md)
#
# “能到达”至少要依次问：几何是否够得着？是否有满足限位的解？解是否碰撞？有没有连接过去的路径？本页每一步保留计数和原因。

# %% [markdown]
# ## 1. 球间隙与形状覆盖是两个问题
# 球间有符号间隙 `g=||c1−c2||−r1−r2`。g>0分开，g=0接触，g<0重叠。
# 拖小球会减少报碰撞，但如果真实零件超出了球的覆盖，也会漏检。因此下面的图只解释近似关系，不能用于决定真实机器人的碰撞球大小。

# %%
def show_spheres(radius_mm=15):
    radius = radius_mm/1000
    gap = sphere_gap((0, 0, 0), radius, (.020, 0, 0), radius)
    fig, ax = plt.subplots()
    for x in (0, .020):
        ax.add_patch(plt.Circle((x, 0), radius, alpha=.3))
        ax.plot([x-.008, x+.008], [0, 0], lw=6, color="black")
    ax.set(xlim=(-.025, .045), ylim=(-.025, .025), aspect="equal",
           xlabel="x / m", ylabel="y / m", title=f"sphere gap={gap*1000:.1f} mm; interval gap=4 mm")
    plt.show()
    return gap

sphere_widget = widgets.interactive(show_spheres, radius_mm=widgets.IntSlider(value=15, min=5, max=20))
display(sphere_widget)
assert abs(show_spheres(15) + .010) < 1e-12

# %% [markdown]
# ## 2. A*：为什么最短路是19步
# 网格宽12高8，起点(1,1)，终点(10,1)，x=5是一堵墙，仅y=6有缺口。必须先上5格、横移9格、再下5格，共19步。
# A* 优先考虑 `f=g+h` 最小的候选：g是已走代价，h用曼哈顿距离估算剩余路程。四邻接、每步代价1时 h 不高估；这里没有对角线和机器人尺寸。

# %%
blocked = {(5, y) for y in range(8) if y != 6}
plan = astar(12, 8, blocked, (1, 1), (10, 1))
fig, ax = plt.subplots()
ax.scatter(*zip(*blocked), marker="s", s=180, color="black", label="blocked")
ax.scatter(*zip(*plan["expanded"]), color="lightblue", label="expanded")
ax.plot(*zip(*plan["path"]), "o-", color="darkorange", label="path")
ax.set(xlim=(-.5, 11.5), ylim=(-.5, 7.5), aspect="equal", xlabel="grid x", ylabel="grid y")
ax.legend(); plt.show()
print("代价:", plan["cost"], "展开数量:", len(plan["expanded"]))
assert plan["cost"] == 19
assert all(p not in blocked for p in plan["path"])
assert all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1 for a,b in zip(plan["path"], plan["path"][1:]))
assert not astar(12, 8, blocked | {(5, 6)}, (1, 1), (10, 1))["success"]

# %% [markdown]
# ## 3. 起终点安全，边却可能穿过障碍
# 用线段从(0,0)到(1,0)，圆障碍中心(.5,0)、半径.1。端点都在圆外，但线段中间穿过圆。
# 点到线段距离的算法：先投影 t，限制到[0,1]，取最近点 a+t(b−a)。本例是点机器人；实体机器人需要考虑自身厚度。

# %%
def segment_clear(a, b, center, radius):
    a, b, c = map(lambda v: np.asarray(v, dtype=float), (a, b, center))
    d = b-a
    t = float(np.clip(np.dot(c-a, d)/np.dot(d, d), 0, 1)) if np.dot(d,d) else 0.
    return np.linalg.norm(c-(a+t*d)) > radius

assert math.dist((0, 0), (.5, 0)) > .1
assert math.dist((1, 0), (.5, 0)) > .1
assert not segment_clear((0, 0), (1, 0), (.5, 0), .1)
print("端点都安全，整条边不安全。")

# %% [markdown]
# ## 4. 工作空间：把每一级筛选写清楚
# 下面从平面网格取目标，先几何 IK，再限位，再检查两根零厚度线段与一个圆障碍。限位 q1∈[−90°,90°]、q2∈[−120°,120°] 是人为教学值。
# 只要某目标有一个解通过，就记为有效。它是**二维位置采样图**，没有方向约束、自碰撞、厚度、全局连通性或真实 dexterous 指标。

# %%
limits_deg = [(-90, 90), (-120, 120)]
obstacle, obstacle_r = (.25, .15), .07
def arm_clear(q):
    elbow = (.3*math.cos(q[0]), .3*math.sin(q[0]))
    return segment_clear((0, 0), elbow, obstacle, obstacle_r) and segment_clear(elbow, fk(*q), obstacle, obstacle_r)

counts = dict(sampled=0, geometric=0, within_limits=0, collision_free=0)
accepted = []
for x in np.linspace(-.5, .5, 31):
    for y in np.linspace(-.5, .5, 31):
        counts["sampled"] += 1
        candidates = ik(x, y)
        if not candidates:
            continue
        counts["geometric"] += 1
        valid_limits = [q for q in candidates if all(lo <= angle <= hi for angle,(lo,hi) in zip(np.degrees(q),limits_deg))]
        if not valid_limits:
            continue
        counts["within_limits"] += 1
        if any(arm_clear(q) for q in valid_limits):
            counts["collision_free"] += 1
            accepted.append((x, y))
print(counts)
assert counts["sampled"] >= counts["geometric"] >= counts["within_limits"] >= counts["collision_free"] > 0
fig, ax = plt.subplots()
if accepted:
    ax.scatter(*zip(*accepted), s=8)
ax.add_patch(plt.Circle(obstacle, obstacle_r, color="red", alpha=.3))
ax.set(aspect="equal", xlabel="x / m", ylabel="y / m", title="Sampled planar position workspace")
plt.show()

# %% [markdown]
# **修改任务：** 收紧 q2 上界，记录减少发生在哪一级；堵住墙的缺口，说明搜索返回无路的依据；把球缩到5 mm，解释“无重叠”为什么还不能证明零件不碰撞。
#
# **技术延伸：** 真实六轴结果必须报告采样范围、单位、随机种子、IK成功定义、碰撞忽略表和各级拒绝数。不同设计比较前保持这些口径一致，见[工程细节第6节](../handbook/09_engineering_details.md)。
