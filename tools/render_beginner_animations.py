"""Build original offline GIF lessons and four-frame PNG storyboards with Pillow."""
import math
from pathlib import Path
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "labs"))
from course_lab import fk
from algorithm_lab import numerical_ik, planning_demo, trapezoid, pid_demo, filter_demo

OUT = ROOT / "assets" / "animations"
OUT.mkdir(parents=True, exist_ok=True)
FONT = Path("C:/Windows/Fonts/msyh.ttc")
if not FONT.exists():
    raise SystemExit("Set FONT in this script to an installed CJK TrueType font. Bundled GIFs need no font installation.")
FONTS = {n: ImageFont.truetype(str(FONT), n) for n in (18, 21, 24, 28, 32)}
BLUE, GREEN, RED, INK = "#2563eb", "#0d9488", "#dc2626", "#172033"
W, H, COUNT = 900, 560, 40


def text(draw, pos, value, size=24, color=INK):
    draw.text(pos, value, font=FONTS[size], fill=color)


def canvas(title, subtitle, footer, index):
    im = Image.new("RGB", (W, H), "#f8fafc")
    d = ImageDraw.Draw(im)
    text(d, (28, 18), title, 32)
    text(d, (28, 65), subtitle, 21)
    d.line((25, 102, 875, 102), fill="#cbd5e1", width=2)
    d.rounded_rectangle((20, 472, 880, 540), radius=10, fill="#e2e8f0")
    text(d, (35, 485), footer, 21)
    text(d, (790, 438), f"{index+1}/{COUNT}", 18)
    return im, d


def arrow(d, a, b, color=INK, width=3):
    d.line((*a, *b), fill=color, width=width)
    ang = math.atan2(b[1]-a[1], b[0]-a[0])
    points = [b, (b[0]-12*math.cos(ang-.45), b[1]-12*math.sin(ang-.45)),
              (b[0]-12*math.cos(ang+.45), b[1]-12*math.sin(ang+.45))]
    d.polygon(points, fill=color)


def dot(d, p, color=RED, radius=7):
    d.ellipse((p[0]-radius,p[1]-radius,p[0]+radius,p[1]+radius),fill=color)


def plot(d, points, box=(90, 145, 810, 420), limits=(0, 1, 0, 1), color=BLUE):
    x0,y0,x1,y1=box; xmin,xmax,ymin,ymax=limits
    def xy(x,y): return (x0+(x-xmin)/(xmax-xmin)*(x1-x0), y1-(y-ymin)/(ymax-ymin)*(y1-y0))
    d.line((x0,y0,x0,y1,x1,y1),fill="#64748b",width=2)
    if len(points)>1: d.line([xy(x,y) for x,y in points],fill=color,width=4)
    if points: dot(d,xy(*points[-1]),color)
    return xy


def arm(d, q, origin=(190, 400), scale=520):
    elbow=(.3*math.cos(q[0]), .3*math.sin(q[0])); tip=fk(*q)
    def xy(p):return (origin[0]+scale*p[0],origin[1]-scale*p[1])
    a,b,c=origin,xy(elbow),xy(tip)
    d.line((*a,*b),fill=BLUE,width=14); d.line((*b,*c),fill=GREEN,width=14)
    for p in (a,b,c):dot(d,p,INK)
    return tip,c


IK=numerical_ik()["history"]
PLAN=planning_demo()
TRAJECTORY=trapezoid()["samples"]
PID=pid_demo()
FILTER=filter_demo()


def frame(kind, i):
    t=i/(COUNT-1)
    if kind=="lever":
        length=.1+.3*t; torque=.5*9.81*length; x=140+length*1450
        im,d=canvas("01 为什么伸直手臂提东西更累？", "同一件 0.5 kg 的物体，离转轴越来越远。", "观察：质量不变，距离增大，转动作用也增大。",i)
        d.polygon([(115,390),(165,390),(140,340)],fill=INK)
        d.line((140,340,x,340),fill=BLUE,width=12)
        d.rectangle((x-25,340,x+25,385),fill=GREEN)
        arrow(d,(x,220),(x,310),RED);text(d,(x-40,180),"重力",24,RED)
        text(d,(150,410),f"距离 {length*100:.1f} cm",24)
        text(d,(90,125),f"力矩 = 0.5 × 9.81 × {length:.2f} ≈ {torque:.2f} N·m",24)
        return im
    if kind=="coordinates":
        im,d=canvas("02 位置是一份走路说明", "从原点出发：先向右 3 格，再向上 2 格。", "终点写作 (3, 2)：先写横向，再写竖向。",i)
        o=(230,395);s=65
        for j in range(5):
            d.line((o[0]+j*s,130,o[0]+j*s,420),fill="#dbe2ea")
            d.line((200,o[1]-j*s,650,o[1]-j*s),fill="#dbe2ea")
        arrow(d,o,(680,o[1]));arrow(d,o,(o[0],120))
        for j in range(1,5):
            text(d,(o[0]+j*s-5,o[1]+8),str(j),18)
            text(d,(o[0]-22,o[1]-j*s-10),str(j),18)
        target=(o[0]+3*s,o[1]-2*s)
        d.line((target[0]-10,target[1],target[0]+10,target[1]),fill=GREEN,width=3)
        d.line((target[0],target[1]-10,target[0],target[1]+10),fill=GREEN,width=3)
        x=min(t*2,1)*3; y=max(0,t*2-1)*2
        dot(d,(o[0]+x*s,o[1]-y*s),RED,12)
        text(d,(80,385),"原点 (0,0)",21);text(d,(655,400),"右 +x",21);text(d,(220,108),"上 +y",21)
        text(d,(target[0]+20,target[1]-28),"目标 (3,2)",24,GREEN)
        return im
    if kind=="rotation":
        angle=90*t; radians=math.radians(angle)
        im,d=canvas("03 角度改变方向，不改变杆长", "蓝杆长 30 cm；从水平转到竖直。", "转到 90° 时：向右长度是 0，向上长度是 30 cm。",i)
        o=(260,405);p=(o[0]+260*math.cos(radians),o[1]-260*math.sin(radians))
        arrow(d,o,(620,405));arrow(d,o,(260,115));d.line((*o,*p),fill=BLUE,width=12)
        d.line((p[0],p[1],p[0],405),fill=GREEN,width=3)
        dot(d,o,INK);dot(d,p,RED)
        text(d,(570,150),f"角度 {angle:.0f}°",28)
        text(d,(570,200),f"向右 {30*math.cos(radians):.1f} cm",24)
        text(d,(570,245),f"向上 {30*math.sin(radians):.1f} cm",24)
        return im
    if kind=="fk":
        q1=30; q2=90*t
        im,d=canvas("04 两根杆：第二个角从第一根杆接着量", "蓝杆 30 cm，绿杆 20 cm；蓝杆一直保持 30°。", "计算终点时，要把两根杆各自的横向、竖向位移相加。",i)
        p,_=arm(d,(math.radians(q1),math.radians(q2)))
        text(d,(560,150),f"第一个角：{q1}°",24)
        text(d,(560,195),f"第二个角：{q2:.0f}°",24)
        text(d,(560,240),f"绿杆朝向：{q1+q2:.0f}°",24)
        text(d,(560,305),f"终点 x={p[0]*100:.1f} cm",24,GREEN)
        text(d,(560,345),f"终点 y={p[1]*100:.1f} cm",24,GREEN)
        return im
    if kind=="ik":
        k=min(len(IK)-1,int(t*len(IK))); r=IK[k]
        im,d=canvas("05 反过来：已经知道目标，怎么调关节？", "每一步先检查差多少，再小幅调整角度。", "这是一次求解记录；找到解不代表所有目标都能找到解。",i)
        _,tip=arm(d,r["q_rad"])
        target=(190+.3*520,400-.2*520)
        d.line((target[0]-10,target[1]-10,target[0]+10,target[1]+10),fill=RED,width=3)
        d.line((target[0]-10,target[1]+10,target[0]+10,target[1]-10),fill=RED,width=3)
        text(d,(545,165),f"第 {k} 次检查",28)
        text(d,(545,220),f"误差 {r['error_m']*1000:.3f} mm",24,RED)
        text(d,(545,290),"红叉：目标",24);text(d,(545,335),"圆点：当前终点",24)
        return im
    if kind=="protocol":
        im,d=canvas("06 一条指令要经过哪些地方？", "电脑发出请求，再等待新反馈；返回的不是同一个包。", "发送完成 ≠ 动作完成。反馈里还要看状态、序号和时间。",i)
        for x,label in [(65,"电脑"),(340,"通信转换器"),(665,"设备")]:
            d.rounded_rectangle((x,205,x+165,305),radius=12,outline=BLUE,width=3)
            text(d,(x+20,235),label,24)
        phase=t*2
        x=150+600*phase if phase<=1 else 750-600*(phase-1)
        y=170 if phase<=1 else 355
        dot(d,(x,y),RED if phase<=1 else GREEN,12)
        text(d,(300,125),"请求：序号 7，目标角度 0.25 rad",21,RED)
        text(d,(300,390),"反馈：序号 7，当前状态与角度",21,GREEN)
        return im
    if kind=="astar":
        im,d=canvas("07 在方格地图里一步步找路", "每次只能上、下、左、右走一格；深色方格不能走。", "先找到墙上的开口。最终路线共 19 步，不是直线距离。",i)
        s=36;o=(205,130);n=int(t*len(PLAN["expanded"]))
        expanded=set(PLAN["expanded"][:n]);path=set(PLAN["path"]) if i==COUNT-1 else set()
        for y in range(8):
            for x in range(12):
                p=(x,y); color="#475569" if p in PLAN["blocked"] else GREEN if p in path else "#bfdbfe" if p in expanded else "white"
                px,py=o[0]+x*s,o[1]+(7-y)*s
                d.rectangle((px,py,px+s-2,py+s-2),fill=color)
        for x,y,mark in [(1,1,"起"),(10,1,"终")]:
            px,py=o[0]+x*s+s/2,o[1]+(7-y)*s+s/2
            dot(d,(px,py),RED,14)
            text(d,(px-9,py-12),mark,18,"white")
        text(d,(80,365),"起点 →",21);text(d,(660,365),"← 终点",21)
        text(d,(75,135),"已查看",21,BLUE);text(d,(75,170),f"{n} 个格点",21,BLUE)
        return im
    if kind=="trajectory":
        n=max(2,int(t*(len(TRAJECTORY)-1))+1);rows=TRAJECTORY[:n];r=rows[-1]
        im,d=canvas("08 走同样远，还要决定什么时候走多快", "从静止开始：加速 → 匀速 → 减速 → 停下。", "横轴是时间（秒），纵轴是速度（弧度/秒）。曲线下面积是转角。",i)
        plot(d,[(r['t_s'],r['v_rad_s']) for r in rows],limits=(0,2.5,0,.6))
        text(d,(650,115),f"t={r['t_s']:.2f} s",24)
        text(d,(95,115),"速度上限 0.5 rad/s",21)
        text(d,(95,425),"0",18);text(d,(745,425),"2.5 秒",18)
        return im
    if kind=="feedback":
        n=max(2,int(t*(len(PID)-1))+1);rows=PID[:n]
        im,d=canvas("09 一边走，一边看还差多少", "目标是 1 rad；蓝线是有反馈控制时的位置。", "接近目标后应减小推动；过头后需要往回修正。参数来自教学模型。",i)
        xy=plot(d,[(r['t_s'],r['q_rad']) for r in rows],limits=(0,6,0,1.2))
        d.line((*xy(0,1),*xy(6,1)),fill=RED,width=2)
        text(d,(680,110),"红线：目标",21,RED)
        text(d,(105,425),"0 秒",18);text(d,(755,425),"6 秒",18)
        return im
    if kind=="filter":
        n=max(2,int(t*(len(FILTER)-1))+1);rows=FILTER[:n]
        im,d=canvas("10 测量会抖动，估计要有所取舍", "灰线是带噪测量，绿线是估计，红线是教学真值。", "更平滑不一定更准确：真值变化时，估计可能跟得慢。",i)
        for key,color in [('measurement','#94a3b8'),('truth',RED),('estimate',GREEN)]:
            plot(d,[(r['step'],r[key]) for r in rows],limits=(0,59,0,2),color=color)
        text(d,(105,425),"第 0 个样本",18);text(d,(715,425),"第 59 个",18)
        return im
    if kind=="learning":
        slope=.1+.4*t;intercept=.1
        im,d=canvas("11 学习：调整规则，让预测靠近例子", "散点是例子，蓝线是预测；这里按预设步骤改变斜率。", "本动画展示拟合方向，不是优化器运行记录；最后还要用新例子考试。",i)
        xy=plot(d,[(-1,-slope+intercept),(1,slope+intercept)],limits=(-1.1,1.1,-.6,.8))
        for x in [-1,-.6,-.2,.2,.6,1]: dot(d,xy(x,.5*x+.1),GREEN,7)
        text(d,(280,110),f"预测值 = {slope:.2f} × 输入 + 0.10",24)
        return im
    if kind=="collision":
        radius=95-35*t
        im,d=canvas("12 粗略外壳碰到了，实体一定碰到了吗？", "深色是两个分开的教学物体；蓝圆是它们的近似外壳。", "外壳太大可能误报；随意缩小又可能漏报。真实模型需要检查覆盖。",i)
        for x in (345,495):
            d.rectangle((x-42,230,x+42,310),fill=INK)
            d.ellipse((x-radius,270-radius,x+radius,270+radius),outline=BLUE,width=4)
        overlap=2*radius-150
        text(d,(250,135),"蓝圆重叠" if overlap>0 else "蓝圆已分离",28,RED if overlap>0 else GREEN)
        text(d,(200,385),"这是二维示意，圆的大小不是三维拟合结果。",21)
        return im
    raise ValueError(kind)


def main(kinds=None):
    for kind in kinds or ["lever","coordinates","rotation","fk","ik","protocol","astar","trajectory","feedback","filter","learning","collision"]:
        frames=[frame(kind,i) for i in range(COUNT)]
        durations=[140]*COUNT;durations[0]=800;durations[-1]=1200
        frames[0].save(OUT/(kind+".gif"),save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
        strip=Image.new("RGB",(W,H),"white")
        for slot,idx in enumerate([0,COUNT//3,2*COUNT//3,COUNT-1]):
            strip.paste(frames[idx].resize((W//2,H//2),Image.Resampling.LANCZOS),((slot%2)*W//2,(slot//2)*H//2))
        strip.save(OUT/(kind+"_steps.png"))
        print(kind,flush=True)


if __name__ == "__main__":
    main()
