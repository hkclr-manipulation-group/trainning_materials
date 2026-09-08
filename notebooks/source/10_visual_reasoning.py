# %% [markdown]
# # 视觉推理专题｜让动画解释原因
#
# [各主题深化](../handbook/13_systems_deepening.md) · [动画阅读与改进说明](../assets/interactive/README.md)
# 每次保持大部分条件不变，只改一个变量。先说预测，再看差异；图里的数字是计算结果，不能只凭“看起来更平滑”判断好坏。
# 新离线演示器有9个主题及逐步字幕；本页用可编辑Python改变参数，观察实际重算。

# %% [markdown]
# ## 1. 同一个J预测不同大小的关节步长
# 绿点是固定J的线性预测，蓝点是实际FK。步子变大后，误差线更容易看见；数值IK通常会在下一步重新线性化。

# %%
def local_prediction(scale=.2):
    q=np.array([0.,math.pi/2]); dq=np.array([.7,.2])*scale
    p=np.array(fk(*q)); actual=np.array(fk(*(q+dq))); predicted=p+np.array(jacobian(*q))@dq
    t=np.linspace(0,scale,60); arc=np.array([fk(*(q+np.array([.7,.2])*a)) for a in t])
    fig,ax=plt.subplots()
    ax.plot(arc[:,0],arc[:,1],color="tab:blue",label="actual FK")
    ax.plot([p[0],predicted[0]],[p[1],predicted[1]],"--",color="tab:green",label="fixed J prediction")
    ax.plot([actual[0],predicted[0]],[actual[1],predicted[1]],"o:",color="tab:red",label="error")
    ax.set(xlim=(.02,.34),ylim=(.17,.45),aspect="equal",xlabel="x / m",ylabel="y / m",
           title=f"scale={scale:.2f}, error={math.dist(actual,predicted)*1000:.2f} mm")
    ax.legend(); plt.show()

local_widget=widgets.interactive(local_prediction,scale=widgets.FloatSlider(value=.2,min=.01,max=1,step=.01,continuous_update=False))
display(local_widget)
local_prediction(1.)

# %% [markdown]
# ## 2. 同样Kp和dt，只增加反馈延迟
# 模型是无饱和的速度积分器，非真实电机。无延迟时误差满足e[k+1]=(1−Kp*dt)e[k]；有延迟时不能继续使用这个一阶递推。
# 图上同时画出延迟系统的真实位置和它使用的旧测量，帮助解释为什么“还在继续推”。

# %%
from expanded_lab import delay_response
def compare_delay(delay_steps=8,kp=12.):
    baseline=delay_response(0,kp=kp); delayed=delay_response(delay_steps,kp=kp)
    times=[r["time_s"] for r in baseline]
    fig,ax=plt.subplots()
    ax.axhline(1,color="black",ls=":",label="target")
    ax.plot(times,[r["q_rad"] for r in baseline],label="zero delay")
    ax.plot(times,[r["q_rad"] for r in delayed],label="delayed: actual q")
    ax.plot(times,[r["measured_rad"] for r in delayed],"--",label="delayed: measurement used")
    ax.set(xlabel="time / s",ylabel="q / rad",title=f"delay={delay_steps*10} ms, Kp={kp}/s")
    ax.legend(); plt.show()
    print("延迟系统采样峰值 / rad:",max(r["q_rad"] for r in delayed))

delay_widget=widgets.interactive(compare_delay,
    delay_steps=widgets.IntSlider(value=8,min=0,max=12,continuous_update=False),
    kp=widgets.FloatSlider(value=12,min=2,max=16,step=2,continuous_update=False))
display(delay_widget)
compare_delay()

# %% [markdown]
# ## 3. 从“平滑”继续问“会不会太迟”
# Kalman的小R更相信测量，大R更保守。比较固定噪声、固定Q、固定阶跃时的两组结果；看跳变后几个样本，而不是只看平稳段。

# %%
series=[]; a=b=0.; pa=pb=1.
for k in range(60):
    truth=1. if k<30 else 1.5
    z=truth+.25*math.sin(2.3*k)+.08*math.cos(.8*k)
    a,pa,_=kalman_step(a,pa,z,.01,.01)
    b,pb,_=kalman_step(b,pb,z,.01,1.)
    series.append((truth,z,a,b))
fig,ax=plt.subplots()
for i,name in enumerate(["truth","measurement","R=.01","R=1"]):
    ax.plot([r[i] for r in series],label=name,alpha=.45 if i==1 else 1)
ax.axvline(30,color="gray",ls=":"); ax.set(xlabel="sample",ylabel="teaching scalar"); ax.legend(); plt.show()

# %% [markdown]
# **观察报告：** 指出你看的是哪条线；写出保持不变的条件、修改参数、实际数值和解释，再写一个不能从图中推出的结论。例如本页延迟曲线不能证明真实电机的稳定范围。
# 如果动画不好懂，先暂停在两个关键帧，比较目标、当前状态、预测状态和误差。不要靠提高播放速度掩盖缺少解释。
