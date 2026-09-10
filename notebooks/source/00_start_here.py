# %% [markdown]
# # 可以修改、运行的机器人自学课堂
#
# 这里的文字、公式、图片和 Python 程序放在同一个文件中。先点击下面的代码块，按 **Shift+Enter**：电脑会执行它，再选中下一块。方括号出现 `[*]` 是正在计算，数字是执行次序。第一次先运行自动准备环境的代码块。
# 如果弹出 **Select Kernel**，在下拉框选择 **Training Python**，再点 **Select**；这一步是在选择负责计算的Python环境。选择后再运行一次代码块，确认方括号出现执行数字和输出。
#
# **今天先做三件事：改一个数 → 运行得到新结果 → 说明为什么变化。** 不必先学完所有公式。
#
# 本课在浏览器里操作，Python 在启动 JupyterLab 的电脑上执行。安装依赖后，七天实验无需外网、机器人或 GPU。文献链接需要网络。
#
# [完整操作说明](../INTERACTIVE.md) · [七天文字正文](../WEEK_PLAN.md) · [技术细节路线](../handbook/09_engineering_details.md)
#
# ## 接着做完整带练
# 
# [33节逐步正文](../ENGINEERING_PATH.md)已经接到四本新课堂：[13 CAN FD](13_canfd_workshop.ipynb)、[14 EtherCAT](14_ethercat_workshop.ipynb)、[15 电机控制](15_control_workshop.ipynb)、[16 系统联调](16_system_workshop.ipynb)。默认数值与曲线已保存；先预测，再运行和修改，最后对照每节解析。所有新实验均为离线教学。

# %% [markdown]
# ## 先试一次：把 300 改成 450
# `=` 是把右边结果存到左边名字中。长度除以 1000，是把毫米换成米；`print` 把结果显示在下面。修改只在重新运行后生效。

# %%
length_mm = 300  # 在这里改数值
length_m = length_mm / 1000
print(f"{length_mm} mm = {length_m:.3f} m")

# %% [markdown]
# ## 再试一次：拖动角度，观察真实重新计算
# 滑块调用下面的 Python 函数。300 mm 的杆向上转时，水平投影变短。图上的长度用米；角度传给 sin/cos 前转成弧度。
# 滑块不显示时先运行 `show_projection(45)`，静态图也能检验公式。

# %%
def show_projection(angle_deg=30):
    angle = math.radians(angle_deg)
    x, y = 0.3 * math.cos(angle), 0.3 * math.sin(angle)
    fig, ax = plt.subplots()
    ax.plot([0, x], [0, y], "o-", lw=5)
    ax.plot([x, x], [0, y], "--", color="gray")
    ax.set(xlim=(-.35, .35), ylim=(-.35, .35), xlabel="x / m", ylabel="y / m",
           title=f"angle={angle_deg} deg; x={x:.4f} m, y={y:.4f} m", aspect="equal")
    plt.show()

projection_widget = widgets.interactive(show_projection, angle_deg=widgets.IntSlider(value=30, min=-180, max=180))
display(projection_widget)
show_projection(45)

# %% [markdown]
# ## 按这条顺序完成一周
#
# | 日期 | 可编辑实验 | 要解释的问题 |
# |---|---|---|
# | 1 | [单位、函数和数据](01_units_and_code.ipynb) | 程序为什么会“算对了错误的单位”？ |
# | 2 | [本体、URDF和坐标变换](02_body_and_frames.ipynb) | CAD外观与关节运动有什么区别？ |
# | 3 | [通信、超时和状态](03_communication.ipynb) | 收到一个包为何不等于收到新反馈？ |
# | 4 | [FK、IK、轨迹与控制](04_kinematics_control.ipynb) | 有几何解，为何迭代还会失败？ |
# | 5 | [碰撞、搜索与工作空间](05_collision_planning.ipynb) | 无碰撞终点为何不保证路径安全？ |
# | 6 | [感知、滤波和学习](06_perception_learning.ipynb) | 误差降低是否代表机器人会抓取？ |
# | 7 | [工具调用与软件交付](07_tools_and_delivery.ipynb) | 怎么证明 AI 帮写的代码符合要求？ |
#
# 时间安排统一以[七天路线](../WEEK_PLAN.md)为准：先复习、读正文和看图，再手算、做一个实验、自检订正。手册推导和专题实验按需延后。
#
# ## 必须知道的四个操作
#
# 1. **保存：Ctrl+S。** 想保留原版，先用 File → Save Notebook As 另存为自己的文件。
# 2. **停止：工具栏方形按钮 Interrupt。** 程序卡住时先中断，不要连续点运行。
# 3. **重新验证：Kernel → Restart Kernel and Run All Cells。** 这会清掉旧变量，再从头计算；提交前用它检查是否偷偷依赖之前运行过的代码。
# 4. **脚本修改后刷新：** Notebook 中导入过的模块有缓存。改了 `labs/*.py` 后重启内核，或明确使用 `importlib.reload`。Notebook 的代码不会自动写回原来的脚本。
#
# 网页显示旧输出时，不代表当前代码运行过。`NameError` 常是上面的代码块没运行；`ModuleNotFoundError` 先检查内核是否为 **Training Python**。

# %%
# 快速确认图像、文件和解释器都可用。
assert (ROOT / "labs" / "data" / "two_link.urdf").is_file()
assert abs(math.radians(180) - math.pi) < 1e-12
display(Image(filename=str(ROOT / "assets" / "animations" / "fk_steps.png")))
print("准备完成。打开第一天实验。")

# %% [markdown]
# ## 完成主线后，按问题选一条扩展
#
# [扩展选课表](../EXTENSIONS.md)给出先修、例子、自检与参考资料。第一周只需要上表的01–07；下面五本专题按需选择。
#
# | 想解决的问题 | 实验 | 先读哪里 |
# |---|---|---|
# | 消息怎样分层、分帧、仲裁 | [08 协议栈](08_protocol_stack.ipynb) | [通信扩展](../handbook/17_extension_workshops.md#day3) |
# | IK为何多解、停滞、需要初值 | [09 IK方法](09_ik_families.ipynb) | [逆变换与优化](../handbook/17_extension_workshops.md#day4) |
# | 步长、延迟、滤波怎样改变结果 | [10 动画背后的计算](10_visual_reasoning.ipynb) | [系统深入](../handbook/13_systems_deepening.md) |
# | 矩阵乘法、坐标、左右乘与FK | [11 矩阵与FK](11_frames_matrices_fk.ipynb) | [矩阵起步](../handbook/17_extension_workshops.md#day1) |
# | 引脚、电平与时间怎样产生字节 | [12 物理链路](12_physical_links.ipynb) | [物理连接](../handbook/14_physical_connections.md) |
#
# 其他专题包括类与线程、六轴设计与惯量、规划理论、反向传播和系统集成，都从[扩展选课表](../EXTENSIONS.md)进入。看图用[逐步演示指南](../assets/interactive/README.md)；找专业文献用[先修与阅读路线](../handbook/16_prerequisites_and_deeper_topics.md)。

# %% [markdown]
# ## 接下来：11门工程课程
# 
# [工程课程总入口](../ENGINEERING_PATH.md)将各门类接到实际工作；[CAN FD](../engineering/04_canfd.md)和[EtherCAT](../engineering/05_ethercat.md)分别学习。先读对应正文，再按[工程实验说明](../labs/ENGINEERING.md)运行8类离线实验，最后用[工程报告](../templates/ENGINEERING_LAB.md)记录计算、配置、故障与验收。
# 
# 这些实验不会连接设备；真实接线、同步与运动验收另按工位完成。
