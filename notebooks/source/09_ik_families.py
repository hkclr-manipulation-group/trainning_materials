# %% [markdown]
# # IK专题｜同一目标，用不同思路求解并比较
#
# [完整方法地图](../handbook/11_inverse_kinematics_families.md) · [运动学基础](../handbook/02_kinematics.md)
# 范围固定为二维两杆位置IK。几何/代数解、数值解与数据驱动seed使用同一个FK、同一单位。本页没有碰撞、限位或方向约束，也没有复现IKFlow神经网络。

# %% [markdown]
# ## 1. 代数消元和几何关系得到同一个数
# 将x/y方程平方相加，消去q1。用c²+s²=1找两个s分支，再用atan2恢复角度；每个候选仍代回FK。

# %%
target = (.3, .2)
l1, l2 = .3, .2
c2 = (target[0]**2+target[1]**2-l1*l1-l2*l2)/(2*l1*l2)
assert abs(c2) <= 1
algebraic = []
for sign in (1, -1):
    s2 = sign*math.sqrt(max(0,1-c2*c2))
    q2 = math.atan2(s2,c2)
    q1 = math.atan2(target[1],target[0])-math.atan2(l2*s2,l1+l2*c2)
    algebraic.append((q1,q2))
    print("候选 / deg:", np.degrees([q1,q2]), "FK误差 / m:", math.dist(fk(q1,q2),target))
    assert math.dist(fk(q1,q2),target) < 1e-12

# %% [markdown]
# ## 2. 解集不是随便平均的向量集合
# 蓝绿两个解都正确；红色是两个关节向量的普通平均。这里q2平均为0，手臂伸直，末端离目标约139.4mm。

# %%
from expanded_lab import branch_average_example, ik_dataset, nearest_seed, ik_benchmark
example = branch_average_example()
fig, axes = plt.subplots(1,3,figsize=(12,3.5))
for ax,q,title,color in zip(axes,[*example["solutions"],example["mean_q"]],["valid A","valid B","mean is not IK"],["tab:blue","tab:green","tab:red"]):
    elbow=(.3*math.cos(q[0]),.3*math.sin(q[0])); p=fk(*q)
    ax.plot([0,elbow[0],p[0]],[0,elbow[1],p[1]],"o-",color=color,lw=4)
    ax.scatter(*target,marker="x",s=100,color="black")
    ax.set(xlim=(-.1,.55),ylim=(-.15,.5),aspect="equal",title=title,xlabel="x / m",ylabel="y / m")
plt.tight_layout(); plt.show()
print("平均构型位置误差 / mm:", example["error_m"]*1000)
assert abs(example["error_m"]-(.5-math.sqrt(.13))) < 1e-12

# %% [markdown]
# ## 3. 425条模型数据，怎样给出一个初值
# 在一个肘部分支采样关节，再用FK生成(x,q)。最近邻在任务位置空间找一个相近样本，返回它的q作为seed。它不是精确逆解，也不是神经网络。
# 后续DLS每步复算真实FK；这把数据提供的起点与几何修正结合起来。

# %%
dataset = ik_dataset()
seed = nearest_seed(target,dataset)
refined = numerical_ik(target=target,seed=seed)
print("样本数:",len(dataset),"最近邻误差 / m:",math.dist(fk(*seed),target))
print("细化:",refined["reason"],"误差 / m:",refined["error_m"])
assert len(dataset) == 425 and refined["success"]
fig,ax=plt.subplots()
ax.scatter([p[0] for p,q in dataset],[p[1] for p,q in dataset],s=5,label="training positions")
ax.scatter(*target,marker="x",s=120,label="target")
ax.scatter(*fk(*seed),marker="s",s=60,label="nearest seed FK")
ax.set(aspect="equal",xlabel="x / m",ylabel="y / m"); ax.legend(); plt.show()

# %% [markdown]
# ## 4. 30个离网格目标：看误差、成功数与迭代，不只看一张图
# 这些目标不用于建库。固定seed对照为(.3,.6)rad；两个DLS使用相同阻尼、容差与预算。
# 本小实验只支持这个模型和这组目标；未测墙钟性能，也不能据此给方法排名。建库成本和分布外目标要单独考虑。

# %%
rows = ik_benchmark()
for row in rows:
    assert min(math.dist(p,(row["x_m"],row["y_m"])) for p,q in dataset) > 1e-9
    assert row["refined_error_m"] <= row["nearest_error_m"]+1e-12
assert all(row["refined_success"] for row in rows)
import statistics
summary = {
    "samples":len(rows), "retrieval_mean_error_mm":1000*statistics.mean(r["nearest_error_m"] for r in rows),
    "refined_success":sum(r["refined_success"] for r in rows),
    "fixed_seed_success":sum(r["fixed_seed_success"] for r in rows),
    "refined_median_updates":statistics.median(r["refined_updates"] for r in rows),
    "fixed_seed_median_updates":statistics.median(r["fixed_seed_updates"] for r in rows),
}
display(summary)
fig,ax=plt.subplots()
ax.semilogy([r["nearest_error_m"] for r in rows],"o-",label="nearest only")
ax.semilogy([max(r["refined_error_m"],1e-16) for r in rows],"o-",label="nearest + DLS")
ax.set(xlabel="held-out target index",ylabel="FK error / m"); ax.legend(); plt.show()
out=ROOT/"outputs"; out.mkdir(exist_ok=True)
with (out/"ik_method_comparison.csv").open("w",encoding="utf-8",newline="") as stream:
    writer=csv.DictWriter(stream,fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)

# %% [markdown]
# ## 5. 分布外目标：数据查到邻居，不等于存在解
# 输入(.6,0)m时最近邻仍能返回某个q，但几何上已超过0.5m最大半径。接口应区别“返回候选”和“满足任务”。

# %%
outside=(.6,0)
candidate=nearest_seed(outside,dataset)
print("候选的FK误差 / m:",math.dist(fk(*candidate),outside),"解析解:",ik(*outside))
assert not ik(*outside) and math.dist(fk(*candidate),outside) >= .1-1e-12

# %% [markdown]
# **继续修改：** 减少建库密度，比较原始误差与细化迭代；加入另一分支时不要直接平均周期角度。把目标换成六维位姿前，先修改任务定义、误差和Jacobian，不是只增加三个输入数字。
# **自检答案：** 最近邻一定能在非空数据里找“最近的”，却不保证达到目标。检验逆解应使用FK和约束；另一正确分支不应因为与某个标签q不同就被判错。
