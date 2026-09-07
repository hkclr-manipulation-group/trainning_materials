"""Native offline GIF player with pause, single step and speed controls. Standard library."""
import argparse
from pathlib import Path

ANIMATIONS = {
    "01 伸直手臂与力矩": "lever", "02 从原点走到位置": "coordinates",
    "03 角度与横竖分量": "rotation", "04 两连杆正运动学": "fk",
    "05 逐步寻找关节角": "ik", "06 请求与反馈": "protocol",
    "07 方格地图找路": "astar", "08 加速与减速": "trajectory",
    "09 反馈纠正": "feedback", "10 测量与滤波": "filter",
    "11 用例子拟合规则": "learning", "12 近似碰撞外壳": "collision",
}
ASSETS = Path(__file__).resolve().parents[1]/"assets"/"animations"


def main(smoke_test=False):
    try:
        import tkinter as tk
        root = tk.Tk()
    except (ImportError, RuntimeError) as exc:
        raise SystemExit("Tk unavailable; open the bundled GIFs or *_steps.png instead. " + str(exc)) from exc
    except Exception as exc:
        raise SystemExit("Cannot initialize desktop/Tcl/Tk; use bundled GIFs or PNG storyboards. " + str(exc)) from exc
    if smoke_test:
        root.withdraw()
    root.title("机器人自学动画：暂停、逐帧与慢放")
    selection = tk.StringVar(value=next(iter(ANIMATIONS)))
    state = {"frames": [], "index": 0, "playing": False, "timer": None}
    label = tk.Label(root)
    label.pack()
    controls = tk.Frame(root)
    controls.pack(fill="x")
    status = tk.StringVar()
    delay = tk.IntVar(value=180)
    play_text = tk.StringVar(value="播放")

    def pause():
        state["playing"] = False
        play_text.set("播放")
        if state["timer"] is not None:
            root.after_cancel(state["timer"])
            state["timer"] = None

    def show():
        label.configure(image=state["frames"][state["index"]])
        status.set(f"第 {state['index']+1} / {len(state['frames'])} 帧；播放速度是阅读速度，不是物理时间")

    def step(delta=1):
        pause()
        state["index"] = (state["index"]+delta) % len(state["frames"])
        show()

    def tick():
        state["timer"] = None
        if state["playing"]:
            state["index"] = (state["index"]+1) % len(state["frames"])
            show()
            state["timer"] = root.after(delay.get(), tick)

    def toggle():
        if state["playing"]:
            pause()
        else:
            state["playing"] = True
            play_text.set("暂停")
            state["timer"] = root.after(delay.get(), tick)

    def load(_=None):
        pause()
        path = ASSETS/(ANIMATIONS[selection.get()]+".gif")
        frames = []
        for index in range(1000):
            try:
                frames.append(tk.PhotoImage(file=str(path), format=f"gif -index {index}"))
            except tk.TclError:
                if not frames:
                    raise
                break
        state.update(frames=frames, index=0)
        show()

    tk.OptionMenu(controls, selection, *ANIMATIONS, command=load).pack(side="left")
    tk.Button(controls, text="上一帧", command=lambda: step(-1)).pack(side="left")
    tk.Button(controls, textvariable=play_text, command=toggle).pack(side="left")
    tk.Button(controls, text="下一帧", command=step).pack(side="left")
    tk.Scale(root, from_=60, to=600, orient="horizontal", variable=delay,
             label="每帧停留毫秒（越大越慢）", length=700).pack()
    tk.Label(root, textvariable=status).pack()
    root.protocol("WM_DELETE_WINDOW", lambda: (pause(), root.destroy()))
    load()
    if smoke_test:
        assert len(state["frames"]) == 40
        step(); assert state["index"] == 1
        step(-1); assert state["index"] == 0
        toggle(); assert state["playing"]
        root.after_cancel(state["timer"])
        state["timer"] = None
        tick(); assert state["index"] == 1
        pause(); assert not state["playing"]
        selection.set("04 两连杆正运动学")
        load(); assert len(state["frames"]) == 40 and state["index"] == 0
        root.update_idletasks()
        root.destroy()
        print("Animation player smoke test passed: load, step, play, pause, switch")
    else:
        root.mainloop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke-test", action="store_true")
    main(parser.parse_args().smoke_test)
