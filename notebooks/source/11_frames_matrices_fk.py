# %% [markdown]
# # 坐标、矩阵与正运动学：每一行都能解释
# 先读[逐步讲义](../handbook/15_frames_matrices_fk.md)。采用列向量，T_AB把B坐标转成A坐标；长度用米，函数角度用弧度。先预测，再运行；函数实现可在labs/spatial_lab.py中阅读。

# %%
from spatial_lab import matmul, homogeneous, rz, rotation_z, translation, transform, inverse_rigid, fk_matrix
A=[[1,2],[3,4]];B=[[2,0],[1,2]]
for i in range(2):
    for j in range(2):
        terms=[A[i][k]*B[k][j] for k in range(2)]
        print(f'C[{i},{j}] = {terms[0]} + {terms[1]} = {sum(terms)}')
assert matmul(A,B)==[[4,4],[10,8]]
print('AB:',matmul(A,B),'BA:',matmul(B,A))

# %% [markdown]
# ## 同一个变换：点会平移，方向不会
# B原点在A里为[.3,.1,0]，B相对A绕z转90°。手算p_B=[.2,.1,0]先转成[−.1,.2,0]，再加平移得到[.2,.3,0]。

# %%
T=homogeneous(rz(math.pi/2),[.3,.1,0])
p=[.2,.1,0]
assert np.allclose(transform(T,p),[.2,.3,0])
assert np.allclose(transform(T,p,direction=True),[-.1,.2,0])
print('point:',transform(T,p),'direction:',transform(T,p,True))
invT=inverse_rigid(T)
assert np.allclose(np.array(invT)[:3,3],[-.1,.3,0])
assert np.allclose(transform(invT,transform(T,p)),p)
print('Inverse:\n',np.array(invT))

# %% [markdown]
# ## 顺序反例：图上的两个终点为什么不同
# 黑点是共同起点，蓝点为先转再移，红点为先移再转。把角度调到0°时两种结果重合；一般角度下不重合。

# %%
def compare_order(degrees=90):
    r=rotation_z(math.radians(degrees));s=translation(1)
    a=transform(matmul(s,r),[1,0,0]);b=transform(matmul(r,s),[1,0,0])
    fig,ax=plt.subplots()
    ax.scatter([1],[0],c='black',label='start')
    ax.scatter([a[0]],[a[1]],c='royalblue',label='S @ R @ p')
    ax.scatter([b[0]],[b[1]],c='crimson',marker='x',label='R @ S @ p')
    ax.set(xlim=(-2.2,2.2),ylim=(-2.2,2.2),aspect='equal',xlabel='x / m',ylabel='y / m')
    ax.legend();plt.show()
    return a,b
assert np.allclose(compare_order(90),[[1,1,0],[0,2,0]])
display(widgets.interactive(compare_order,degrees=widgets.IntSlider(value=90,min=-180,max=180)))

# %% [markdown]
# ## FK用两种独立方法核对
# 30°与60°是关节相对角度，第二杆世界角为90°。齐次矩阵还给出末端姿态，不只位置。

# %%
q1,q2=math.radians(30),math.radians(60)
chain=fk_matrix(q1,q2)
endpoint=transform(chain,[0,0,0])
assert np.allclose(endpoint,[.3*math.sqrt(3)/2,.35,0])
assert np.allclose(endpoint[:2],fk(q1,q2))
assert np.allclose(np.array(chain)[:3,:3],rz(math.pi/2))
print('FK matrix:\n',np.array(chain),'\nEndpoint:',endpoint)

# %% [markdown]
# ## 同一物理点，换坐标系描述
# A系黑点固定为[.4,.2,0]；B原点固定为[.2,.1,0]，只转动B的轴。观察p_B的数字变化，回代p_A始终不变。

# %%
def frame_coordinates(degrees=45):
    t=homogeneous(rz(math.radians(degrees)),[.2,.1,0])
    fixed=[.4,.2,0];local=transform(inverse_rigid(t),fixed)
    assert np.allclose(transform(t,local),fixed)
    print('p_A fixed:',fixed,'p_B:',[round(x,5) for x in local])
    fig,ax=plt.subplots()
    ax.scatter([.4],[.2],c='black',label='fixed point')
    for endpoint,color in [([.15,0,0],'red'),([0,.15,0],'green')]:
        end=transform(t,endpoint);ax.arrow(.2,.1,end[0]-.2,end[1]-.1,color=color,head_width=.01,length_includes_head=True)
    ax.set(xlim=(-.1,.6),ylim=(-.15,.45),aspect='equal',xlabel='x_A / m',ylabel='y_A / m');plt.show()
frame_coordinates(90)
display(widgets.interactive(frame_coordinates,degrees=widgets.IntSlider(value=45,min=-180,max=180)))

# %% [markdown]
# 实验完成后解释：矩阵维度正确为何仍可能用错框架？逆变换为何要用−Rᵀt？FK位置正确为何还需要看姿态、工具与碰撞？不会的部分回到[前置路线](../handbook/16_prerequisites_and_deeper_topics.md)。
