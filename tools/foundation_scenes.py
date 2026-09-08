"""Prerequisite scenes with visible operands, frames, wires and sampled bits."""
import math
from build_concept_player import frame,label,line,rect,circle,polyline,BLUE,GREEN,RED,GRAY

def matrix_frames():
    a=[[1,2],[3,4]];b=[[2,0],[1,2]];c=[[4,4],[10,8]];frames=[]
    for step in range(4):
        ri,cj=divmod(step,2);body=''
        for left,name,values in [(80,'A',a),(390,'B',b),(750,'C = A B',c)]:
            body+=label(left,150,name,27)
            for i in range(2):
                for j in range(2):
                    active=(name=='A' and i==ri) or (name=='B' and j==cj) or (name.startswith('C') and i==ri and j==cj)
                    text=str(values[i][j]) if not name.startswith('C') or i*2+j<=step else '?'
                    body+=rect(left+j*100,180+i*75,86,62,'#dbeafe' if active else '#edf1f6',BLUE if active else 'none')
                    body+=label(left+32+j*100,222+i*75,text,30,BLUE if active else GRAY)
        body+=label(315,251,'×',32)+label(665,251,'=',32)
        calculation=f'{a[ri][0]}×{b[0][cj]} + {a[ri][1]}×{b[1][cj]} = {c[ri][cj]}'
        body+=label(90,390,f'C的第{ri+1}行、第{cj+1}列：'+calculation,29)
        frames.append(frame('矩阵乘法：行与列怎样生成一个格子',body,'蓝色A行、B列和C中的对应位置。',calculation,
            '对应相乘后相加；没有选中的行列不参与这个格子的计算。','此处普通矩阵乘法；NumPy的逐元素乘法不是同一个操作。'))
    return frames

def axes(origin,angle,length=100):
    x,y=origin
    ex=(x+length*math.cos(angle),y-length*math.sin(angle));ey=(x-length*math.sin(angle),y-length*math.cos(angle))
    return line(origin,ex,RED,3)+line(origin,ey,GREEN,3)+label(ex[0]+5,ex[1],'x',18,RED)+label(ey[0]+5,ey[1],'y',18,GREEN)

def coordinates_frames():
    frames=[];scale=620
    def xy(x,y):return (105+x*scale,425-y*scale)
    pa=(.4,.2);origin=(.2,.1);point=xy(*pa)
    for degrees in range(0,91,5):
        t=math.radians(degrees);dx,dy=pa[0]-origin[0],pa[1]-origin[1]
        pb=(math.cos(t)*dx+math.sin(t)*dy,-math.sin(t)*dx+math.cos(t)*dy)
        body=axes(xy(0,0),0,90)+label(73,452,'A系原点',19)
        body+=axes(xy(*origin),t,110)+label(170,388,'B系原点',19)
        body+=circle(point,7,'#111827')+label(point[0]-30,point[1]-25,'固定的杯子位置',21)
        elbow=xy(origin[0]+math.cos(t)*pb[0],origin[1]+math.sin(t)*pb[0])
        body+=line(xy(*origin),elbow,BLUE,3,'5 3')+line(elbow,point,BLUE,3,'5 3')
        body+=label(620,170,f'只转B坐标轴：{degrees}°',27)
        body+=label(620,224,'p_A 始终 = (0.400, 0.200) m',23)
        body+=label(620,279,f'p_B = ({pb[0]:.3f}, {pb[1]:.3f}) m',23,BLUE)
        body+=label(620,339,'p_A = R_AB p_B + t_AB',24)
        body+=label(620,394,'t_AB = (0.200, 0.100) m',23)
        frames.append(frame('换坐标描述：杯子没动，数字为什么会变',body,'黑点固定；B原点处的红绿轴转动，蓝虚线是分量。',
            f'B转到{degrees}°，p_B变成({pb[0]:.3f}, {pb[1]:.3f}) m。',
            '坐标是相对原点和轴的描述；用新坐标回代仍得到同一个p_A。','二维平面示意；采用右手方向、列向量，未移动被测物体。'))
    return frames

def order_frames():
    frames=[]
    for degrees in range(0,91,5):
        t=math.radians(degrees);a=(1+math.cos(t),math.sin(t));b=(2*math.cos(t),2*math.sin(t));body=''
        for left,title,end,color in [(130,'S R p：先转再移',a,BLUE),(670,'R S p：先移再转',b,RED)]:
            def xy(p):return (left+p[0]*110,435-p[1]*110)
            body+=axes(xy((0,0)),0,105)+circle(xy((1,0)),5,'#111827')
            body+=circle(xy(end),7,color)+label(left-30,148,title,25,color)
            body+=polyline([xy((1+math.cos(math.radians(d)),math.sin(math.radians(d))) if color==BLUE else (2*math.cos(math.radians(d)),2*math.sin(math.radians(d)))) for d in range(degrees+1)],color,3)
            body+=label(left-25,188,f'终点 ({end[0]:.2f}, {end[1]:.2f}) m',22,color)
        frames.append(frame('交换顺序：相同的旋转和平移，终点不同',body,'黑点为共同起点；左右图使用相同刻度。',f'转角{degrees}°；沿x平移1 m；蓝点与红点可能不重合。',
            '列向量约定下，右边的操作先作用于点；矩阵乘法一般不交换。','S/R数值相同而物理操作顺序不同；并非一种写法永远错误。'))
    return frames

def fk_frames():
    frames=[];q1=math.pi/6;q2=math.pi/3;elbow=(.3*math.cos(q1),.3*math.sin(q1));tip=(elbow[0],elbow[1]+.2)
    def xy(p):return (140+p[0]*700,440-p[1]*700)
    names=['Rz(30°)：确定第一杆方向','Tx(.3)：沿局部x走到肘部','Rz(60°)：第二杆世界角90°','Tx(.2)：到达工具尖端']
    for step in range(4):
        body=axes(xy((0,0)),q1,75)+circle(xy((0,0)),6,GRAY)
        if step>=1:body+=line(xy((0,0)),xy(elbow),BLUE,7)+circle(xy(elbow),6,BLUE)
        if step>=2:body+=axes(xy(elbow),q1+q2,72)
        if step>=3:body+=line(xy(elbow),xy(tip),GREEN,7)+circle(xy(tip),7,GREEN)
        body+=label(560,155,'逐节积累变换：',26)
        for i,name in enumerate(names):body+=label(560,205+i*56,name,23,BLUE if i==step else GRAY)
        frames.append(frame('正运动学：沿每节自己的方向走到末端',body,'局部x轴跟着关节转；杆长沿局部x延伸。',names[step],
            '工具点最终为(.2598, .3500) m；姿态角为30°+60°=90°。','二维两杆教学链；URDF一般还含任意轴、零位与工具固定变换。'))
    return frames

def uart_frames():
    bits=[0,1,0,1,0,0,1,0,1,1];names=['起始']+[f'd{i}' for i in range(8)]+['停止'];frames=[]
    for k in range(10):
        body=rect(60,130,225,80,'#e0e7ff')+rect(795,130,245,80,'#dcfce7')
        body+=label(80,162,'MCU A：TX',24)+label(815,162,'MCU B：RX',24)
        body+=line((285,165),(795,165),BLUE,4)+label(418,151,'兼容的逻辑电平',20,BLUE)
        body+=label(81,199,'参考 GND',19)+label(816,199,'参考 GND',19)+line((285,199),(795,199),GRAY,2)
        points=[]
        for i,b in enumerate(bits):points.extend([(75+i*93,365-b*90),(75+(i+1)*93,365-b*90)])
        body+=polyline(points,BLUE,3)
        x=75+(k+.5)*93;body+=line((x,245),(x,390),RED,3,'5 3')+circle((x,365-bits[k]*90),6,RED)
        for i,name in enumerate(names):body+=label(81+i*93,425,name,19,RED if i==k else GRAY)
        body+=label(90,462,'115200 bit/s：每位约8.68微秒；红线为本位中间采样示意',21)
        frames.append(frame('UART：先看接线，再看接收器在哪采样',body,'TX连RX；红色采样位置沿电平波形前进。',f'当前{names[k]}，逻辑值={bits[k]}；数据0xA5，最低位先发。',
            '8N1一字节占起始1位、数据8位、停止1位，共10个位时间。','逻辑波形，不是RS-232实际电压；不模拟波特率误差与电气边沿。'))
    return frames

def can_frames():
    frames=[]
    for bit,noise in [(1,0),(0,0),(0,.4),(0,-.3),(1,0),(1,.4),(1,-.3),(0,0)]:
        high=2.5+(1 if bit==0 else 0)+noise;low=2.5-(1 if bit==0 else 0)+noise
        body=rect(50,155,210,140,'#e0e7ff')+rect(840,155,210,140,'#dcfce7')
        body+=label(67,189,'收发器A',25)+label(856,189,'收发器B',25)
        body+=line((260,225),(840,225),RED,4)+line((260,270),(840,270),BLUE,4)
        body+=label(380,216,'CAN_H',22,RED)+label(380,301,'CAN_L',22,BLUE)
        for x in (290,810):
            body+=line((x,225),(x,270),GRAY,3)+rect(x-9,235,18,24,'white',GRAY)+label(x-30,330,'120 Ω',18)
        body+=label(65,380,f'H={high:.1f} V；L={low:.1f} V；差值={high-low:.1f} V',26)
        body+=label(65,426,f'共同扰动={noise:+.1f} V；当前'+('显性0' if bit==0 else '隐性1'),26)
        frames.append(frame('CAN差分：两根线都变化，差值可以不变',body,'双线、两端终端以及下面的H−L数值。',f'本步差分={high-low:.1f} V；理想共同扰动在相减中抵消。',
            'CAN控制器先经过收发器再接总线；终端位于设计的总线两端。','典型电压教学示意；仍受器件共模范围限制，未给出实际接头针脚。'))
    return frames

def spi_frames():
    bits=[int(x) for x in '10100101'];frames=[]
    for k in range(8):
        body=rect(50,135,220,265,'#e0e7ff')+rect(835,135,215,265,'#dcfce7')
        body+=label(70,169,'主设备',26)+label(852,169,'从设备',26)
        for row,(name,color) in enumerate([('SCK →',BLUE),('MOSI →',GREEN),('MISO ←',RED),('CS  →',GRAY)]):
            y=210+row*52;body+=line((270,y),(835,y),color,3)+label(390,y-12,name,22,color)
        body+=label(77,443,f'Mode 0，上升沿采样；第{k+1}位MOSI={bits[k]}；CS保持选中',23)
        x=330+k*58;body+=circle((x,262),7,GREEN)
        frames.append(frame('SPI：四类信号各自承担什么任务',body,'SCK由主设备提供；两个数据方向不同；CS负责选中。',f'教学字节0xA5按最高位先发；当前第{k+1}位={bits[k]}。',
            '在此Mode 0示例，上升沿采样；位序和CPOL/CPHA需两端约定一致。','连线示意不模拟边沿时序；实际还需参考地、建立/保持时间和器件电平。'))
    return frames

def extra_scenes():
    return [('矩阵逐格相乘',matrix_frames()),('同一点不同坐标',coordinates_frames()),('左右乘与顺序',order_frames()),
            ('FK逐节变换',fk_frames()),('UART接线与采样',uart_frames()),('CAN双线与终端',can_frames()),('SPI四线分工',spi_frames())]