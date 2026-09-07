"""Native Tkinter two-link explorer: drag sliders or click a target. No devices."""
import math
from course_lab import fk, ik
from algorithm_lab import jacobian


def main():
    try:
        import tkinter as tk
    except ImportError as exc:
        raise SystemExit("Tkinter is unavailable. Use the PNG figures and algorithm_lab.py instead.") from exc
    root = tk.Tk()
    root.title("两连杆运动学自学实验（仅二维几何）")
    canvas = tk.Canvas(root, width=720, height=620, bg="#f8fafc")
    canvas.pack()
    state = {"target": None, "solutions": [], "branch": 0}
    variables = [tk.DoubleVar(value=30), tk.DoubleVar(value=60)]
    message = tk.StringVar()
    origin, scale = (360, 320), 520
    def point(x, y):
        return origin[0]+scale*x, origin[1]-scale*y
    def draw(*_):
        canvas.delete("all")
        for radius in (.1, .5):
            r = scale*radius
            canvas.create_oval(origin[0]-r, origin[1]-r, origin[0]+r, origin[1]+r,
                               outline="#cbd5e1", dash=(4, 4))
        canvas.create_line(40, origin[1], 680, origin[1], arrow="last", fill="#94a3b8")
        canvas.create_line(origin[0], 600, origin[0], 35, arrow="last", fill="#94a3b8")
        q = [math.radians(v.get()) for v in variables]
        elbow = (.3*math.cos(q[0]), .3*math.sin(q[0]))
        tip = fk(*q)
        canvas.create_line(*point(0, 0), *point(*elbow), width=10, fill="#2563eb")
        canvas.create_line(*point(*elbow), *point(*tip), width=10, fill="#0d9488")
        for p in ((0, 0), elbow, tip):
            x, y = point(*p)
            canvas.create_oval(x-6, y-6, x+6, y+6, fill="#0f172a")
        j = jacobian(*q)
        det = j[0][0]*j[1][1]-j[0][1]*j[1][0]
        status = f"末端 x={tip[0]:.4f} m  y={tip[1]:.4f} m；det(J)={det:.5f} m²/rad²"
        if state["target"] is not None:
            x, y = point(*state["target"])
            canvas.create_line(x-8, y-8, x+8, y+8, fill="#dc2626", width=2)
            canvas.create_line(x-8, y+8, x+8, y-8, fill="#dc2626", width=2)
            status += "\n目标几何可达：" + ("是" if state["solutions"] else "否")
            status += f"；当前位置误差 {math.dist(tip, state['target']):.4f} m"
        message.set(status)
    def apply_branch():
        if state["solutions"]:
            q = state["solutions"][state["branch"] % len(state["solutions"])]
            for variable, value in zip(variables, q):
                variable.set((math.degrees(value)+180) % 360-180)
        draw()
    def click(event):
        target = ((event.x-origin[0])/scale, (origin[1]-event.y)/scale)
        state.update(target=target, solutions=ik(*target), branch=0)
        apply_branch()
    def switch():
        state["branch"] += 1
        apply_branch()
    canvas.bind("<Button-1>", click)
    for i, variable in enumerate(variables):
        tk.Scale(root, label=f"q{i+1}（度）", from_=-180, to=180, resolution=.1,
                 orient="horizontal", length=650, variable=variable, command=draw).pack()
    tk.Button(root, text="切换 IK 分支", command=switch).pack()
    tk.Label(root, textvariable=message).pack()
    tk.Label(root, text="点击画布设目标；虚线是几何可达边界。没有真实关节限位、碰撞或姿态约束。").pack()
    draw()
    root.mainloop()


if __name__ == "__main__":
    main()
