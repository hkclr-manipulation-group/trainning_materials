"""Rebuild bundled educational PNG/SVG figures. Requires matplotlib only."""
import math
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Arc, Circle, FancyArrowPatch, FancyBboxPatch, Rectangle

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"labs"))
from course_lab import fk, ik
from algorithm_lab import jacobian, numerical_ik, planning_demo, trapezoid, filter_demo, pid_demo

plt.rcParams.update({"font.family": ["Microsoft YaHei", "DejaVu Sans"],
                     "axes.unicode_minus": False, "font.size": 11,
                     "svg.fonttype": "path", "figure.facecolor": "white"})
OUT = ROOT/"assets"/"figures"
OUT.mkdir(parents=True, exist_ok=True)
BLUE, GREEN, RED = "#2563eb", "#0d9488", "#dc2626"


def save(fig, name):
    fig.savefig(OUT/(name+".png"), dpi=150, bbox_inches="tight")
    fig.savefig(OUT/(name+".svg"), bbox_inches="tight")
    plt.close(fig)


def box(ax, x, y, text, color=BLUE, w=2.1, h=.85):
    ax.add_patch(FancyBboxPatch((x-w/2, y-h/2), w, h, boxstyle="round,pad=.06",
                               facecolor="#f1f5f9", edgecolor=color, linewidth=1.6))
    ax.text(x, y, text, ha="center", va="center", fontsize=10)


def arrow(ax, p, q, text=None):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle="->", mutation_scale=14, color="#475569"))
    if text:
        ax.text((p[0]+q[0])/2, (p[1]+q[1])/2+.12, text, ha="center", fontsize=9)


def flow(name, title, top, bottom=None):
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.set(xlim=(-1.3, 10.3), ylim=(-.9, 3.7), title=title)
    ax.axis("off")
    xs = [i*3 for i in range(len(top))]
    for x, label in zip(xs, top):
        box(ax, x, 2.5, label)
    for a, b in zip(xs, xs[1:]):
        arrow(ax, (a+1.13, 2.5), (b-1.13, 2.5))
    if bottom:
        for x, label in zip(xs, bottom):
            box(ax, x, .25, label, GREEN)
            arrow(ax, (x, 2.03), (x, .73))
    save(fig, name)


def arm(ax, q, color=BLUE, label=None):
    e = (.3*math.cos(q[0]), .3*math.sin(q[0]))
    p = fk(*q)
    ax.plot([0, e[0], p[0]], [0, e[1], p[1]], "o-", lw=4, color=color, label=label)
    ax.set_aspect("equal")
    ax.set(xlabel="x / m", ylabel="y / m", xlim=(-.12, .57), ylim=(-.3, .53))
    ax.grid(alpha=.2)
    return e, p


def main():
    flow("system", "一条机器人开发链：上层目标怎样落到物理系统",
         ["任务 / AI\n目标与约束", "规划与控制\n参考值与反馈", "通信 / 驱动\n报文与执行", "机械本体\n关节与工具"],
         ["验收与数据", "误差 / 限位", "状态 / 时间戳", "编码器 / 感知"])

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.set(xlim=(-.4, 2.6), ylim=(-.3, 1.6), title="坐标变换：同一点，两个参考系")
    ax.set_aspect("equal"); ax.grid(alpha=.2)
    for end, label in [((.8, 0), "x_A"), ((0, .8), "y_A")]:
        arrow(ax, (0, 0), end); ax.text(*end, label, color=BLUE)
    for end, label in [((1, 1.1), "x_B"), ((.4, .5), "y_B")]:
        arrow(ax, (1, .5), end); ax.text(*end, label, color=GREEN)
    ax.plot(1, 1.5, "o", color=RED); ax.text(1.08, 1.43, "p_B=(1,0)\np_A=(1,1.5)")
    ax.plot(1, .5, "o", color=GREEN); ax.text(1.08, .45, "B 原点：t=(1,0.5)")
    ax.text(1.5, .05, "R = 逆时针 90°\np_A = R p_B + t")
    save(fig, "frames")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    q = (math.pi/6, math.pi/3)
    e, p = arm(axes[0], q)
    axes[0].set_title("FK：第二角是相对第一杆的角")
    axes[0].text(.08, .13, "l1=0.3 m\nq1=30°")
    axes[0].text(.28, .24, "l2=0.2 m\nq2=60°")
    axes[0].annotate("末端 (0.2598,0.35)", p, xytext=(.04, .44), arrowprops={"arrowstyle": "->"})
    for i, solution in enumerate(ik(.3, .2)):
        arm(axes[1], solution, [BLUE, GREEN][i], "肘形分支 "+str(i+1))
    axes[1].legend(); axes[1].set_title("IK：相同位置可对应不同关节角")
    save(fig, "two_link")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    result = numerical_ik()
    hist = result["history"]
    axes[0].plot([r["xy_m"][0] for r in hist], [r["xy_m"][1] for r in hist], "o-", color=BLUE)
    axes[0].plot(.3, .2, "x", ms=12, color=RED, label="目标")
    axes[0].set(xlabel="x / m", ylabel="y / m", title="阻尼最小二乘 IK：末端迭代路径")
    axes[0].legend(); axes[0].grid(alpha=.2)
    axes[1].semilogy([r["iteration"] for r in hist], [max(r["error_m"], 1e-15) for r in hist], "o-")
    axes[1].set(xlabel="迭代次数", ylabel="位置误差 / m", title="同一运行的误差变化")
    axes[1].grid(alpha=.2)
    save(fig, "ik_iterations")

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))
    for ax, q, title in zip(axes, [(0, math.pi/2), (0, 0)], ["弯曲：两个局部运动方向", "伸直：雅可比降秩"]):
        j = jacobian(*q)
        speeds = [(math.cos(t*math.pi/100), math.sin(t*math.pi/100)) for t in range(201)]
        xy = [(sum(j[0][k]*v[k] for k in range(2)), sum(j[1][k]*v[k] for k in range(2))) for v in speeds]
        ax.plot([p[0] for p in xy], [p[1] for p in xy], color=BLUE)
        ax.set(xlim=(-.6,.6), ylim=(-.6,.6), xlabel="vx / m/s", ylabel="vy / m/s", title=title)
        ax.set_aspect("equal"); ax.grid(alpha=.2)
    fig.suptitle("关节速度单位圆经 J 映射；假设 ||qdot||=1 rad/s")
    save(fig, "jacobian")

    def segment_distance(p, a, b):
        ab = (b[0]-a[0], b[1]-a[1])
        t = max(0, min(1, ((p[0]-a[0])*ab[0]+(p[1]-a[1])*ab[1])/(ab[0]**2+ab[1]**2)))
        return math.dist(p, (a[0]+t*ab[0], a[1]+t*ab[1]))
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    arm(axes[0], (math.pi/6, math.pi/3))
    axes[0].add_patch(Circle((.25,.15), .07, color=RED, alpha=.35))
    axes[0].set_title("工作空间：零厚度杆与圆形障碍物")
    samples = []
    for a in range(-180, 181, 3):
        for b in range(-180, 181, 3):
            q = (math.radians(a), math.radians(b))
            e = (.3*math.cos(q[0]), .3*math.sin(q[0]))
            if min(segment_distance((.25,.15),(0,0),e), segment_distance((.25,.15),e,fk(*q))) <= .07:
                samples.append((a,b))
    axes[1].scatter([p[0] for p in samples], [p[1] for p in samples], s=3, color=RED)
    axes[1].set(xlabel="q1 / 度", ylabel="q2 / 度", title="构型空间：红色样本是碰撞关节组合", xlim=(-180,180), ylim=(-180,180))
    save(fig, "cspace")

    result = planning_demo()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for x,y in result["expanded"]:
        ax.add_patch(Rectangle((x-.5,y-.5),1,1,facecolor="#dbeafe",edgecolor="white"))
    for x,y in result["blocked"]:
        ax.add_patch(Rectangle((x-.5,y-.5),1,1,facecolor="#475569"))
    path = result["path"]
    ax.plot([p[0] for p in path],[p[1] for p in path],"o-",color=GREEN,label="四邻域最短路")
    ax.text(1, .35, "起点"); ax.text(9.5,.35,"终点"); ax.legend()
    ax.set(xlim=(-.5,11.5), ylim=(-.5,7.5), xlabel="格点 x", ylabel="格点 y", title="A*：浅蓝为扩展节点；墙上开口在 y=6")
    ax.set_aspect("equal"); save(fig,"astar")

    fig, axes = plt.subplots(3,1,figsize=(10,7),sharex=True)
    for distance, style in [(1.0,"-"),(.1,"--")]:
        r=trapezoid(distance=distance)
        for ax,key,label in zip(axes,["q_rad","v_rad_s","a_rad_s2"],["位置 / rad","速度 / rad/s","加速度 / rad/s²"]):
            ax.plot([s["t_s"] for s in r["samples"]],[s[key] for s in r["samples"]],style,label=f"距离 {distance} rad")
            ax.set_ylabel(label); ax.grid(alpha=.2)
    axes[0].legend(); axes[0].set_title("同样的速度与加速度上限：长行程梯形，短行程三角形")
    axes[-1].set_xlabel("时间 / s"); save(fig,"trajectory")

    fig, ax=plt.subplots(figsize=(12,4.5)); ax.set(xlim=(-1,11),ylim=(-1,3.5)); ax.axis("off")
    for x,label in [(0,"参考 q_ref"),(3,"控制器\nP / I / D"),(6,"限幅\n输出约束"),(9,"被控对象\n惯量与摩擦")]:
        box(ax,x,2,label,w=1.7)
    for x in (0,3,6): arrow(ax,(x+.94,2),(x+2.05,2))
    box(ax,6,0,"测量 q、速度",GREEN,w=2.5)
    arrow(ax,(9,1.5),(7.3,0)); arrow(ax,(4.7,0),(3,1.5),"反馈（误差相减）")
    ax.set_title("控制闭环：饱和与反馈都影响下一次输出"); save(fig,"control_loop")

    fig,axes=plt.subplots(2,1,figsize=(10,6),sharex=True)
    for label,args in [("P",dict(ki=0,kd=0)),("PD",dict(ki=0)),("PID + 条件积分",{})]:
        rows=pid_demo(**args)
        axes[0].plot([r["t_s"] for r in rows],[r["q_rad"] for r in rows],label=label)
        axes[1].plot([r["t_s"] for r in rows],[r["torque_nm"] for r in rows],label=label)
    axes[0].axhline(1,color="black",ls="--",lw=1); axes[0].legend()
    axes[0].set(ylabel="位置 / rad",title="相同简化惯量模型，不同反馈项；不能当作真机整定参数")
    axes[1].set(xlabel="时间 / s",ylabel="力矩指令 / N·m")
    for ax in axes: ax.grid(alpha=.2)
    save(fig,"pid_response")

    rows=filter_demo(); fig,ax=plt.subplots(figsize=(10,4.5))
    for key,label,style in [("truth","教学真值","--"),("measurement","带噪测量","."),("estimate","标量 Kalman 估计","-")]:
        ax.plot([r["step"] for r in rows],[r[key] for r in rows],style,label=label)
    ax.set(xlabel="样本序号",ylabel="标量位置（教学单位）",title="滤波权衡：减小测量波动，也可能滞后真实变化")
    ax.legend(); ax.grid(alpha=.2); save(fig,"kalman")

    flow("protocol", "数据通信：相同角度经过不同表示", ["物理量\n0.250 rad","量化整数\n250 mrad","小端四字节\nfa 00 00 00","接收后解析\n0.250 rad"],
         ["单位是否一致？","范围 / 舍入？","长度 / 字节序？","新反馈 / 超时？"])
    flow("perception", "像素到机器人：每一步都需要自己的参数", ["像素 (u,v)\n与有效深度 Z","相机三维点\np_camera","基座三维点\nT_base_camera","工具目标\n姿态与抓取偏置"],
         ["时间戳 / 畸变","内参 fx fy cx cy","标定与当前状态","规划 / 碰撞 / 控制"])
    flow("learning", "学习系统：按整段轨迹划分，评估独立保留", ["观测 + 动作\n时间对齐的数据","训练集\n拟合参数","验证集\n选择方法","测试集\n最终评估"],
         ["单位 / 坐标","模型与损失","超参数与基线","闭环任务与失败统计"])
    print("Generated", len(list(OUT.glob("*.png"))), "PNG/SVG figure pairs in", OUT)


if __name__ == "__main__":
    main()
