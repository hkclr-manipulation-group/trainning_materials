# %% [markdown]
# # 第六天｜从像素到位置，从数据到模型
#
# [正文](../lessons/day06_perception_ai.md) · [感知手册](../handbook/05_estimation.md) · [AI手册](../handbook/06_ai.md)
#
# 今天使用合成数据，做四个明确的转换：像素+深度→相机点，相机点→基座点，带噪观测→估计，训练样本→预测模型。每一步都有单位或输入条件。

# %% [markdown]
# ## 1. 一个像素对应一条射线，深度才确定点
# 去畸变后的针孔模型：`X=(u−cx)*Z/fx`，`Y=(v−cy)*Z/fy`。
# fx/fy单位是像素，u/v是像素坐标，Z是沿光轴的深度（m），不是到相机中心的斜距。已知 fx=fy=600、主点(320,240)、像素(380,240)、Z=0.5 m，得到(0.05,0,0.5) m。
# 真实深度图需要知道单位、无效值、与彩色图的对齐关系；fx=600 是教学值。

# %%
fx, fy, cx, cy = 600., 600., 320., 240.
u, v, depth_m = 380., 240., .5
camera_point = np.array([(u-cx)*depth_m/fx, (v-cy)*depth_m/fy, depth_m, 1.])
T_base_camera = np.eye(4)
T_base_camera[:3, 3] = [.2, 0, .1]  # 仅平移的教学外参
base_point = T_base_camera @ camera_point
print("相机点 / m:", camera_point[:3], "基座点 / m:", base_point[:3])
assert np.allclose(base_point[:3], [.25, 0, .6])
print("像素偏差1 px导致的X变化 / mm:", depth_m/fx*1000)

# %% [markdown]
# ## 2. Kalman：用不确定性决定信谁
# 标量随机游走模型的四步：`P_prior=P+Q`；`K=P_prior/(P_prior+R)`；`x_new=x+K*(z−x)`；`P_new=(1−K)*P_prior`。
# Q/R 是方差，不是标准差。R越大表示本次测量越不可靠，K越小。初值 x=0、P=1、Q=.01、R=.25、z=1.2，K=1.01/1.26≈.8016，更新值≈.9619。

# %%
estimate, variance, gain = kalman_step(0, 1, 1.2, .01, .25)
print("K:", gain, "x:", estimate, "P:", variance)
assert abs(gain - 1.01/1.26) < 1e-12
assert abs(estimate - 1.2*1.01/1.26) < 1e-12

# %%
def compare_filter(measurement_variance=.25):
    x, p = 0., 1.
    truth, observations, estimates = [], [], []
    for k in range(60):
        actual = 1. if k < 30 else 1.5
        z = actual + .25*math.sin(2.3*k) + .08*math.cos(.8*k)
        x, p, _ = kalman_step(x, p, z, .01, measurement_variance)
        truth.append(actual); observations.append(z); estimates.append(x)
    fig, ax = plt.subplots()
    ax.plot(truth, label="truth"); ax.plot(observations, alpha=.5, label="measurement")
    ax.plot(estimates, label="estimate")
    ax.set(xlabel="sample", ylabel="teaching scalar", title=f"R={measurement_variance}")
    ax.legend(); plt.show()

filter_widget = widgets.interactive(compare_filter,
    measurement_variance=widgets.FloatLogSlider(value=.25, base=10, min=-2, max=1, step=.2, continuous_update=False))
display(filter_widget)
compare_filter()

# %% [markdown]
# 这组确定性扰动用于复现曲线，不满足所有高斯白噪声假设。曲线平滑可能同时带来目标突变后的延迟；滤波无法修复错误的外参或深度单位。
#
# ## 3. 真正训练一次：自己写梯度下降
# 拟合 `y_hat=w*x+b`。损失 `L=mean((y_hat−y)²)`，梯度 `dL/dw=2*mean(error*x)`，`dL/db=2*mean(error)`。
# 更新 `w←w−lr*dL/dw`、`b←b−lr*dL/db`。每轮先用同一组旧参数算两个梯度，再一起更新。本实验只有两个参数，能和闭式最小二乘作独立对照。
# 固定训练/测试拆分，测试样本不参与梯度计算；若用测试集选 lr，就需要另留最终测试集。

# %%
data_fn = lambda x: .5*x + .1 + .01*math.sin(7*x)
train = [(x, data_fn(x)) for x in (-1., -.6, -.2, .2, .6, 1.)]
test = [(x, data_fn(x)) for x in (-.8, -.4, 0., .4, .8)]
x_train = np.array([x for x,y in train]); y_train = np.array([y for x,y in train])
w, b, lr, epochs = 0., 0., .2, 100
history = []
for epoch in range(epochs):
    errors = w*x_train + b-y_train
    grad_w, grad_b = 2*np.mean(errors*x_train), 2*np.mean(errors)
    history.append((w, b, float(np.mean(errors**2))))
    w, b = w-lr*grad_w, b-lr*grad_b
closed_w, closed_b = fit_line(train)
baseline_b = float(np.mean(y_train))
print("梯度下降:", w, b, "闭式解:", closed_w, closed_b)
print("测试MSE:", mse(test,w,b), "常数基线:", mse(test,0,baseline_b))
assert np.allclose([w,b], [closed_w,closed_b], atol=1e-8)
assert mse(test,w,b) < mse(test,0,baseline_b)
assert not {x for x,y in train} & {x for x,y in test}

# %% [markdown]
# ## 4. 播放实际优化记录，观察参数怎样变化
# 下面每一帧来自刚才训练保存的 w/b，不是预先设计的移动线条。修改 lr 后重新训练再运行本块，就会得到不同记录；lr 太大可能发散。

# %%
def training_frame(step=0):
    w_i, b_i, loss = history[step]
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
    axes[0].scatter(*zip(*train), label="train")
    axes[0].scatter(*zip(*test), marker="x", label="held-out")
    axis_x = np.linspace(-1,1,100)
    axes[0].plot(axis_x, w_i*axis_x+b_i, label=f"w={w_i:.3f}, b={b_i:.3f}")
    axes[0].set(xlabel="x", ylabel="y", ylim=(-.55,.75)); axes[0].legend()
    axes[1].semilogy(range(step+1), [h[2] for h in history[:step+1]])
    axes[1].set(xlabel="epoch", ylabel="training MSE", xlim=(0,epochs), title=f"loss={loss:.6g}")
    plt.tight_layout(); plt.show()

frame = widgets.IntSlider(min=0, max=len(history)-1, value=0, description="epoch")
play = widgets.Play(min=0, max=len(history)-1, interval=150)
play_link = widgets.jslink((play, "value"), (frame, "value"))
training_output = widgets.interactive_output(training_frame, {"step": frame})
display(widgets.VBox([widgets.HBox([play,frame]), training_output]))
training_frame(len(history)-1)

# %% [markdown]
# ## 5. 这如何连接机器人 AI
# 回归学习一个数到另一个数；机器人行为克隆学习观测到动作，动作还要说明是关节位置、增量、速度还是末端位姿。图像、机器人状态和动作必须时间对齐。
# ACT预测一段动作序列；Diffusion Policy迭代去噪生成动作；RL根据奖励优化长期表现。它们不是把上面直线换个名字：需要模型结构、演示数据或环境、训练预算和任务评估。
#
# 本页实现梯度下降与标量滤波；ACT、Diffusion、RL只在手册和[文献卡](../references/READING_GUIDE.md)介绍，没有进行大模型训练。
#
# **修改任务：** 将测量方差R从.01改成1，比较阶跃后的跟随速度；将训练lr改成1.5，观察损失而不是只看最后输出；解释为何不同回合拆分比随机相邻帧拆分更能检验泛化。
#
# **参考答案：** 大R更少相信测量、跟随通常更慢；过大lr可能振荡发散；同一回合相邻帧高度相似，混入训练和测试会高估新场景表现。见[工程细节第7–8节](../handbook/09_engineering_details.md)。
