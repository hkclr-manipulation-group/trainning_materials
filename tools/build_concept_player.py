"""Precompute SVG teaching frames in Python; emit a fully offline step player."""
from pathlib import Path
import html
import json
import math
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "labs"))
from course_lab import fk
from algorithm_lab import jacobian, numerical_ik, planning_demo, kalman_step
from expanded_lab import arbitration_trace, branch_average_example, delay_response

BLUE, GREEN, RED, GRAY = "#2563eb", "#059669", "#dc2626", "#64748b"


def label(x, y, text, size=21, color="#172033"):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}">{html.escape(str(text))}</text>'


def line(a, b, color=GRAY, width=3, dash=""):
    return f'<line x1="{a[0]:.2f}" y1="{a[1]:.2f}" x2="{b[0]:.2f}" y2="{b[1]:.2f}" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'


def rect(x,y,w,h,fill="#e2e8f0",stroke="none"):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}"/>'


def circle(p, r=6, color=BLUE):
    return f'<circle cx="{p[0]:.2f}" cy="{p[1]:.2f}" r="{r}" fill="{color}"/>'


def arm(q, origin=(200,420), scale=480, color=BLUE):
    elbow = (.3*math.cos(q[0]), .3*math.sin(q[0])); end=fk(*q)
    def xy(p): return (origin[0]+scale*p[0], origin[1]-scale*p[1])
    return line(origin,xy(elbow),color,7)+line(xy(elbow),xy(end),color,7)+circle(origin,7,GRAY)+circle(xy(elbow),7,color)+circle(xy(end),7,color), xy


def polyline(points, color=BLUE, width=3, dash=""):
    return f'<polyline points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-dasharray="{dash}"/>'


def frame(title, body, focus, observation, reason, limit):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 680" role="img" '
            'font-family="Microsoft YaHei, Noto Sans CJK SC, sans-serif">'
            f'<title>{html.escape(title)}</title><rect width="1100" height="680" fill="#f8fafc"/>'
            + label(28,48,title,30)+label(28,88,"先预测，再单步；颜色之外还有文字、数值和线型。",20,GRAY)
            + body + rect(20,491,1060,171,"#e8eef7")
            + label(35,521,"看哪里："+focus,20)+label(35,557,"观察："+observation,20)
            + label(35,593,"解释："+reason,20)+label(35,629,"边界："+limit,19,GRAY)+'</svg>')


def stack_frames():
    names=["应用载荷", "UDP数据报", "IPv4包", "Ethernet捕获记录"]
    totals=[8,16,36,50]
    result=[]
    for step, layer in enumerate([0,1,2,3,3,2,1,0]):
        receiver=step>=4
        body=label(60,132,"发送端：逐层封装",24)+label(610,132,"接收端：逐层取出",24)
        for side, left in enumerate([60,610]):
            for i,name in enumerate(names):
                active=(side==int(receiver) and i==layer)
                body+=rect(left,155+i*75,420,60,"#dbeafe" if active else "#edf1f6",BLUE if active else "none")
                body+=label(left+18,191+i*75,f"{name}：{totals[i]} B",22,BLUE if active else GRAY)
        body+=line((490,413),(592,413),GREEN,5)+label(492,391,"链路",19,GREEN)
        descriptions=["原始8字节，还没加网络头。", "加8字节UDP头，长度字段为16。", "再加20字节IPv4基本头，合计36。", "再加14字节Ethernet头，捕获示意为50。"]
        obs=("接收端当前检查：" if receiver else "发送端当前构造：")+names[layer]
        result.append(frame("协议栈：同一份载荷怎样被封装和拆出",body,names[layer],obs,
                            descriptions[layer],"图形不按字节比例；50 B不包含真实线上填充、FCS等全部开销。"))
    return result


def can_frames():
    frames=[]
    for state in arbitration_trace():
        body=label(40,143,"只演示标准数据帧的11位ID，先发高位；0为显性。",22)
        ids=[0x120,0x100]
        for row,ident in enumerate(ids):
            y=190+row*90
            body+=label(40,y+36,f"ID 0x{ident:03X}",23)
            for col,bit in enumerate(range(10,-1,-1)):
                fill="#fee2e2" if ident==0x120 and state["bit"]<5 else "#e2e8f0"
                if bit==state["bit"]: fill="#fef3c7"
                body+=rect(210+col*70,y,57,55,fill)+label(230+col*70,y+36,(ident>>bit)&1,25)
        body+=label(55,416,f"正在比较 bit {state['bit']}；总线读值={state['bus']}；仍在发送："+", ".join(hex(i) for i in state['active']),24)
        losing=state['bit']<=5
        frames.append(frame("CAN仲裁：发1却读到0的节点退出",body,"黄色列；看0x120在bit5发1。",
            "0x120已退出，0x100继续。" if losing else "目前高位相同，两个节点都继续。",
            "显性0覆盖隐性1；低优先级节点不破坏胜出的帧。",
            "未模拟扩展帧、RTR、数据段、CRC、ACK、位填充与完整重发机制。"))
    return frames


def branch_frames():
    example=branch_average_example(); frames=[]
    for step in range(4):
        body=""
        for i,(q,name,color) in enumerate(zip([*example['solutions'],example['mean_q']],
                        ["解A：正确", "解B：正确", "平均关节角：错误"],[BLUE,GREEN,RED])):
            origin=(85+350*i,430)
            visible=step>i or step==3
            _,xy=arm(q,origin,430,color)
            target=xy(example['target'])
            body+=label(40+350*i,141,name,23,color)+circle(target,9,"#111827")+label(target[0]-42,target[1]-22,"固定目标",18)
            if visible:
                drawing,_=arm(q,origin,430,color); body+=drawing
                body+=label(35+350*i,460,f"q=({math.degrees(q[0]):.1f}°, {math.degrees(q[1]):.1f}°)",20,color)
                if i==2: body+=line(xy(fk(*q)),target,RED,3,"6 4")
        frames.append(frame("IK多解：两个正确解取平均，不一定还是解",body,"三幅图使用相同杆长和黑色目标。",
            ["先确定目标，不移动目标来迁就解。","解A命中目标。","解B也命中目标。","红臂取关节角平均后伸直，末端偏离约139.4 mm。"][step],
            "FK是非线性映射：FK(平均q)一般不等于平均FK(q)。",
            "只做二维位置IK，无限位和碰撞；逆解数据不能盲目混合分支做平均。"))
    return frames


def jacobian_frames():
    q=(0., math.pi/2); p=fk(*q); j=jacobian(*q); frames=[]
    for k in range(31):
        factor=k/30; dq=(.7*factor,.2*factor)
        actual=fk(q[0]+dq[0],q[1]+dq[1])
        predicted=tuple(p[r]+sum(j[r][c]*dq[c] for c in range(2)) for r in range(2))
        body,xy=arm((q[0]+dq[0],q[1]+dq[1]),(175,440),560,BLUE)
        arc=[xy(fk(q[0]+.7*t/30,q[1]+.2*t/30)) for t in range(k+1)]
        body+=polyline(arc,BLUE,4)+line(xy(p),xy(predicted),GREEN,4,"8 5")+circle(xy(predicted),8,GREEN)
        body+=line(xy(actual),xy(predicted),RED,3,"4 4")
        body+=label(590,168,"蓝实线/蓝点：真实FK",24,BLUE)+label(590,210,"绿虚线/绿点：固定J的一阶预测",24,GREEN)
        body+=label(590,270,f"Δq=({dq[0]:.3f}, {dq[1]:.3f}) rad",22)
        body+=label(590,315,f"两者差距={math.dist(actual,predicted)*1000:.2f} mm",24,RED)
        body+=label(590,363,"J始终在初始q=(0°,90°)计算",20)
        frames.append(frame("Jacobian：局部直线预测与真实弯曲轨迹",body,"红色连接线，就是预测误差。",
            f"步长比例={factor:.2f}；当前位置误差={math.dist(actual,predicted)*1000:.2f} mm。",
            "小步近似准确；把同一个J用于大步，曲率带来的偏差增大。",
            "这是固定线性化点的对照；数值IK通常每步重新计算J。"))
    return frames


def ik_frames():
    good=numerical_ik(target=(.3,0),seed=(.3,.6)); frames=[]
    for i,state in enumerate(good['history']):
        body,xy=arm(state['q_rad'],(160,435),510,BLUE)
        body+=circle(xy((.3,0)),10,"#111827")+label(590,160,"同一目标(.3,0)m，不同初值",24)
        body+=label(590,220,f"弯曲初值：第{i}次更新后的误差",22,BLUE)+label(590,258,f"{state['error_m']:.8f} m",26,BLUE)
        body+=label(590,326,"直杆初值q=(0,0)：局部更新为0",22,RED)+label(590,365,"误差停在0.20000000 m",24,RED)
        body+=label(590,420,"几何解存在：局部停滞 ≠ 全局无解",21)
        frames.append(frame("数值IK：看每一步实际构型和误差",body,"蓝臂随真实DLS迭代变化；黑点是固定目标。",
            f"弯曲初值的误差={state['error_m']:.8f} m；直杆对照没有下降。",
            "直杆在这个目标方向的一阶运动能力不足；换seed能改变局部路径。",
            "实际记录，不插值伪造迭代；不包含限位、姿态或碰撞约束。"))
    return frames


def astar_frames():
    plan=planning_demo(); blocked=set(plan['blocked']); frames=[]
    # BFS gives independent g-values for the displayed four-neighbor grid.
    distances={(1,1):0}; queue=[(1,1)]
    for p in queue:
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n=(p[0]+dx,p[1]+dy)
            if 0<=n[0]<12 and 0<=n[1]<8 and n not in blocked and n not in distances:
                distances[n]=distances[p]+1; queue.append(n)
    for k,current in enumerate(plan['expanded']):
        expanded=set(plan['expanded'][:k+1]); body=""
        for x in range(12):
            for y in range(8):
                p=(x,y); fill="#1e293b" if p in blocked else "#bfdbfe" if p in expanded else "#edf2f7"
                if p==current: fill="#f59e0b"
                body+=rect(40+x*45,420-y*38,40,33,fill)
        def xy(p): return (60+p[0]*45,436-p[1]*38)
        body+=label(*xy((1,1)),"起",17)+label(*xy((10,1)),"终",17)
        if k==len(plan['expanded'])-1: body+=polyline([xy(p) for p in plan['path']],GREEN,5)
        g=distances[current]; h=abs(current[0]-10)+abs(current[1]-1)
        body+=label(650,172,f"当前扩展节点：{current}",24)+label(650,227,f"g={g}，h={h}，f={g+h}",28)
        body+=label(650,294,f"已扩展 {k+1} 个节点",23)+label(650,349,"蓝：已经扩展；橙：当前",22)
        body+=label(650,401,"最后绿色路径代价：19步",22,GREEN)
        frames.append(frame("A*：每次为什么选这个格子",body,"橙色格子和右侧g/h/f，黑格不可通行。",
            f"当前f={g+h}；最后要绕到y=6的缺口，路径共19步。",
            "g是已走代价，h是曼哈顿估计；同分节点仍有确定的排序规则。",
            "蓝色是已扩展集合，不是候选队列；点机器人四邻接网格，不是真实机械臂。"))
    return frames


def feedback_frames():
    fresh, delayed=delay_response(0),delay_response(8); frames=[]
    def xy(t,q): return (80+t/2.5*730,445-(q+.1)/1.8*280)
    for k in range(0,len(fresh),5):
        body=line(xy(0,0),xy(2.5,0))+line(xy(0,0),xy(0,1.6))+line(xy(0,1),xy(2.5,1),GRAY,2,"6 5")
        body+=polyline([xy(r['time_s'],r['q_rad']) for r in fresh[:k+1]],BLUE,4)
        body+=polyline([xy(r['time_s'],r['q_rad']) for r in delayed[:k+1]],RED,4,"8 3")
        body+=label(75,151,"q / rad（虚线目标=1）",21)+label(390,470,"时间 / s：0 → 2.5",20)
        body+=label(830,190,"蓝：无延迟",20,BLUE)+label(830,230,"红：延迟80ms",20,RED)
        body+=label(830,289,f"t={fresh[k]['time_s']:.2f}s",22)+label(830,330,f"红臂q={delayed[k]['q_rad']:.3f}",20,RED)
        body+=label(830,367,f"旧测量={delayed[k]['measured_rad']:.3f}",20)
        frames.append(frame("反馈延迟：控制器还在用过去的位置",body,"两条曲线的Kp=12/s、dt=.01s、目标完全相同。",
            f"红线实际位置={delayed[k]['q_rad']:.3f}rad，但反馈位置={delayed[k]['measured_rad']:.3f}rad。",
            "过时反馈改变了闭环行为；提高发送频率不自动消除链路延迟。",
            "教学速度积分器，无饱和、无真实电机动力学；播放速度不是控制频率。"))
    return frames


def filter_frames():
    records=[]; a=b=0.; pa=pb=1.
    for k in range(60):
        truth=1. if k<30 else 1.5; z=truth+.25*math.sin(2.3*k)+.08*math.cos(.8*k)
        a,pa,_=kalman_step(a,pa,z,.01,.01); b,pb,_=kalman_step(b,pb,z,.01,1.)
        records.append((truth,z,a,b))
    frames=[]
    def xy(k,value): return (70+k/59*750,455-value/1.9*290)
    for k in range(60):
        body=line((70,155),(70,455))+line((70,455),(820,455))
        for column,color,dash in ((0,"#111827","6 4"),(1,"#94a3b8","2 3"),(2,BLUE,""),(3,RED,"")):
            body+=polyline([xy(i,row[column]) for i,row in enumerate(records[:k+1])],color,3,dash)
        body+=label(850,183,"黑虚线：真值",20)+label(850,225,"灰：测量",20,GRAY)
        body+=label(850,267,"蓝：R=.01",20,BLUE)+label(850,309,"红：R=1.0",20,RED)
        body+=label(850,362,f"样本{k}",24)+label(350,480,"样本序号；标量无物理单位",19)
        frames.append(frame("滤波：更平滑，也可能更迟钝",body,"第30个样本处真值从1跳到1.5。",
            f"测量={records[k][1]:.3f}，小R估计={records[k][2]:.3f}，大R估计={records[k][3]:.3f}。",
            "R表示测量方差；大R更少相信测量，突变后通常需要更多更新。",
            "固定教学扰动，不是严格高斯白噪声实验；平滑不等于标定正确。"))
    return frames


def collision_frames():
    frames=[]
    corner=math.hypot(.008,.002)
    for radius in (.015,.012,.009,.005):
        body=''
        for center in (300,500):
            body+=f'<circle cx="{center}" cy="300" r="{radius*10000}" fill="#bfdbfe" fill-opacity=".5" stroke="{BLUE}" stroke-width="3"/>'
            body+=rect(center-80,280,160,40,"#fef3c7","#111827").replace('rx="8"', 'rx="0"')
        body+=line((380,365),(420,365),GREEN,4)+label(350,399,"真实间隙4 mm",21,GREEN)
        covered=radius>=corner
        gap=(.02-2*radius)*1000
        body+=label(730,169,f"每个圆半径={radius*1000:.0f} mm",24,BLUE)
        body+=label(730,222,f"圆间隙={gap:.1f} mm",24,RED if gap<0 else GREEN)
        body+=label(730,285,"覆盖角点需至少8.25 mm",22)
        body+=label(730,335,"角点覆盖："+("满足" if covered else "不满足"),24,GREEN if covered else RED)
        if not covered:
            body+=circle((370,290),6,RED)+label(60,180,"红点在零件内，却落在小圆外",23,RED)+line((300,187),(370,282),RED,2)
        frames.append(frame("碰撞近似：圆过大误报，过小又可能漏检",body,"黄色矩形保持不变，只改蓝色圆半径。",
            f"真实两矩形始终相隔4 mm；圆模型间隙={gap:.1f} mm。",
            "9 mm圆仍覆盖这个矩形且不重叠；5 mm圆已不能覆盖零件。",
            "二维矩形教学例子；未验证真实网格、折叠姿态或机器人自碰撞。"))
    return frames


def main():
    scenes=[("协议栈",stack_frames()),("CAN逐位仲裁",can_frames()),("IK两解与平均",branch_frames()),
            ("Jacobian局部近似",jacobian_frames()),("IK迭代与停滞",ik_frames()),("A*逐步搜索",astar_frames()),
            ("反馈延迟对照",feedback_frames()),("滤波与滞后",filter_frames()),("碰撞近似覆盖",collision_frames())]
    from foundation_scenes import extra_scenes
    scenes.extend(extra_scenes())
    data=[{"name":name,"frames":frames} for name,frames in scenes]
    page='''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>机器人概念逐步演示</title><style>
body{margin:0;background:#edf2f7;color:#172033;font:17px "Microsoft YaHei",sans-serif}main{max-width:1150px;margin:auto;padding:18px}
h1{font-size:25px;margin:8px 0}p{line-height:1.7}nav{display:flex;gap:10px;flex-wrap:wrap;align-items:center;background:white;padding:14px;border-radius:12px}
button,select,input{font:inherit}button,select{padding:9px 13px;border:1px solid #aabbd2;border-radius:7px;background:#fff}button:focus-visible,select:focus-visible,input:focus-visible{outline:3px solid #2563eb}
button:disabled{opacity:.45}#stage{background:#fff;border-radius:12px;margin-top:14px;overflow:auto}svg{display:block;width:100%;min-width:700px}
input[type=range]{flex:1;min-width:180px}#caption{min-height:25px}a{color:#165ac0}
</style><main><h1>机器人概念逐步演示</h1><p>先读“看哪里”，猜下一步，再单步播放。全部数值由课程Python计算；此页离线显示预计算结果，不执行你修改的Python代码。</p>
<nav><label>主题 <select id="scene" aria-label="演示主题"></select></label><button id="prev">上一步</button><button id="play">播放</button><button id="next">下一步</button>
<label>速度 <select id="speed"><option value="1200">慢</option><option value="650" selected>中</option><option value="200">快</option></select></label>
<input id="step" type="range" min="0" value="0" aria-label="步骤"><output id="position" aria-live="polite"></output></nav>
<div id="stage"></div><p id="caption">默认暂停，不会自动播放。最后一步自动停止；切换主题回到第一步。</p>
<p><a href="../../DEPTH_MAP.md">自学深度地图</a> · <a href="../../INTERACTIVE.md">修改并运行Python的课堂说明</a> · 播放速度仅影响观察节奏。</p></main><script>
const scenes=__DATA__;const select=document.querySelector('#scene'),step=document.querySelector('#step'),play=document.querySelector('#play'),speed=document.querySelector('#speed');let timer=null;
scenes.forEach((s,i)=>{const o=document.createElement('option');o.value=i;o.textContent=s.name;select.append(o)});
function stop(){clearInterval(timer);timer=null;play.textContent='播放';play.setAttribute('aria-pressed','false')}
function render(){const s=scenes[Number(select.value)],i=Number(step.value);step.max=s.frames.length-1;document.querySelector('#stage').innerHTML=s.frames[i];document.querySelector('#position').textContent=`${i+1} / ${s.frames.length}`;document.querySelector('#prev').disabled=i===0;document.querySelector('#next').disabled=i===s.frames.length-1}
function advance(){if(Number(step.value)>=Number(step.max)){stop();return}step.value=Number(step.value)+1;render();if(step.value===step.max)stop()}
play.onclick=()=>{if(timer){stop();return}if(step.value===step.max)step.value=0;render();play.textContent='暂停';play.setAttribute('aria-pressed','true');timer=setInterval(advance,Number(speed.value))};
select.onchange=()=>{stop();step.value=0;render()};step.oninput=()=>{stop();render()};speed.onchange=()=>{if(timer){stop();play.click()}};
document.querySelector('#prev').onclick=()=>{stop();step.value=Number(step.value)-1;render()};document.querySelector('#next').onclick=()=>{stop();advance()};
document.addEventListener('visibilitychange',()=>{if(document.hidden)stop()});stop();render();
</script></html>'''.replace('__DATA__',json.dumps(data,ensure_ascii=False))
    out=ROOT/'assets'/'interactive'; out.mkdir(parents=True,exist_ok=True)
    (out/'concept_player.html').write_text(page,encoding='utf-8')
    previews = {'protocol_stack.svg': (0, 3), 'ik_branches.svg': (2, -1),
                'jacobian.svg': (3, -1), 'collision_coverage.svg': (8, 2)}
    previews.update({'matrix_product.svg': (9,-1), 'frame_coordinates.svg': (10,-1), 'transform_order.svg': (11,-1), 'fk_chain.svg': (12,-1), 'uart_sampling.svg': (13,5), 'can_physical.svg': (14,2), 'spi_wiring.svg': (15,3)})
    for filename, (scene_index, frame_index) in previews.items():
        (out/filename).write_text(data[scene_index]['frames'][frame_index], encoding='utf-8')
    manifest={"generator":"tools/build_concept_player.py","scenes":[{"name":name,"frames":len(frames)} for name,frames in scenes],
              "scope":"Python-precomputed teaching SVG frames; not live hardware or a general simulator"}
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Scenes:',len(scenes),'frames:',sum(len(frames) for _,frames in scenes))


if __name__=='__main__':
    main()
