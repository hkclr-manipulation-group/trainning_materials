# %% [markdown]
# # 第二天｜从杆长到 URDF，再到坐标变换
#
# [先读正文](../lessons/day02_body_and_urdf.md)。
# 今天使用仓库自带的两连杆 URDF；无需复制机器人网格。先理解平面，再看同样规则怎样扩展到三维。
#
# 目标：解释关节 origin、axis 和 visual origin 分别做什么，算出工具点坐标，检查文件中的限位声明。

# %% [markdown]
# ## 1. 杆越长，支撑同一重物需要的力矩越大
# 水平静止、忽略杆自重时，`τ=m g L`。本课取 g=9.81 m/s²。0.5 kg 放在 0.3 m 处，需要约 1.4715 N·m 的静态关节力矩。
# 电机还要应对杆自重、加速度、摩擦和减速器效率，所以这个数不是选型额定值。完整负载见[本体手册](../handbook/01_body.md)。

# %%
mass_kg, gravity, arm_m = .5, 9.81, .3
torque_nm = mass_kg * gravity * arm_m
print("静态重物力矩 / N m:", torque_nm)
assert abs(torque_nm - 1.4715) < 1e-12

# %% [markdown]
# ## 2. 直接读 XML：不要从渲染图猜关节
# link 是刚体，joint 把 parent 与 child 接起来。`origin` 给出 q=0 时的固定变换，`axis` 是关节坐标系里的运动轴。
# visual 的 origin 只摆放外观几何；改变它不等于移动关节。固定 tool_offset 也会改变末端位置，不能漏乘。

# %%
import xml.etree.ElementTree as ET
robot = ET.parse(ROOT / "labs" / "data" / "two_link.urdf").getroot()
for joint in robot.findall("joint"):
    print(joint.attrib, "parent=", joint.find("parent").get("link"),
          "child=", joint.find("child").get("link"), "origin=", joint.find("origin").attrib)
    if joint.get("type") == "revolute":
        limits = {k: float(v) for k, v in joint.find("limit").attrib.items()}
        axis = np.array([float(v) for v in joint.find("axis").get("xyz").split()])
        assert limits["lower"] < limits["upper"] and limits["velocity"] > 0
        assert abs(np.linalg.norm(axis) - 1) < 1e-12
        print("  limit:", limits, "axis:", axis)

# %% [markdown]
# ## 3. 平面齐次矩阵：让旋转和平移使用同一种乘法
# 点写成 `[x,y,1]`。矩阵 `T=[[cosθ,-sinθ,tx],[sinθ,cosθ,ty],[0,0,1]]` 把局部点转到父坐标系。
# 第一步旋转局部点，第二步加平移。矩阵乘积从右侧开始作用，所以顺序不能交换。
# 我们的 URDF 是 `R(q1) · Tx(0.3) · R(q2) · Tx(0.2)`；最后一个 Tx 是工具偏移。

# %%
def transform2(theta=0, x=0, y=0):
    c, s = math.cos(theta), math.sin(theta)
    return np.array([[c, -s, x], [s, c, y], [0., 0., 1.]])

q1, q2 = math.radians(30), math.radians(60)
T = transform2(q1) @ transform2(x=.3) @ transform2(q2) @ transform2(x=.2)
point = T @ np.array([0., 0., 1.])
print("工具点 / m:", point[:2], "工具方向 / deg:", math.degrees(q1 + q2))
assert np.allclose(point[:2], [.2598076211353316, .35])
assert np.allclose(point[:2], fk(q1, q2))
print("先平移和先旋转的差别:")
print(transform2(math.pi/2) @ transform2(x=.3))
print(transform2(x=.3) @ transform2(math.pi/2))

# %% [markdown]
# ## 4. 三维轴旋转不是“只支持 X/Y/Z”
# 真实 URDF 轴可能倾斜。把非零轴归一化成单位向量 a，构造叉乘矩阵 K，再用 Rodrigues 公式：
# `R=I+sinθ K+(1−cosθ)K²`。三维齐次变换是 4×4，右上角三行是平移。
# 下面用倾斜轴检查 `RᵀR=I`、`det(R)=1`，并确认旋转轴自身不动；它演示轴旋转，不是通用 URDF 加载器。

# %%
def rotation_axis(axis, theta):
    a = np.asarray(axis, dtype=float)
    if a.shape != (3,) or not np.isfinite(a).all() or not math.isfinite(theta):
        raise ValueError("需要有限的三维轴和角度")
    norm = np.linalg.norm(a)
    if norm < 1e-12:
        raise ValueError("轴不能为零")
    x, y, z = a / norm
    K = np.array([[0, -z, y], [z, 0, -x], [-y, x, 0]])
    return np.eye(3) + math.sin(theta)*K + (1-math.cos(theta))*(K @ K)

axis = np.array([0, .0078204, .99997])
R = rotation_axis(axis, .7)
assert np.allclose(R.T @ R, np.eye(3))
assert abs(np.linalg.det(R)-1) < 1e-12
assert np.allclose(R @ axis, axis)
print("倾斜轴旋转检查通过")

# %% [markdown]
# ## 5. 回到我们的文件：发现问题而不自动改参数
# 下面读随教材保存的本地 URDF 声明快照。速度为 0 的声明会令某些规划器得到上下界均为 0，无法规划运动。
# 文件中的 0 或 100 都不证明硬件的真实额定速度；修复参数前要查规格、驱动配置与单位。快照来源和哈希在[数据说明](../references/DATA_GUIDE.md)。

# %%
with (ROOT / "references" / "data" / "local_model_declarations.csv").open(encoding="utf-8-sig") as stream:
    model_rows = list(csv.DictReader(stream))
print("共", len(model_rows), "个关节声明；列名:", list(model_rows[0]))
display(model_rows[:3])

# %% [markdown]
# **修改实验：** 把工具长度 0.2 改成 0.25，先预测末端沿第二杆方向多走 0.05 m；修改参考公式相应杆长再比较。把 q2 设为 0°，应得到沿 q1 方向的 0.5 m 直杆。
#
# **自检：** 为什么不能靠缩放 mesh 修复错误的 joint origin？答案：前者改变几何外观，后者改变运动链。三维 RPY 次序、惯量和加载诊断见[技术细节第2节](../handbook/09_engineering_details.md)。
