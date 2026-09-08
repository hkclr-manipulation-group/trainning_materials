"""Small, explicit column-vector matrix and wiring calculations; no hardware I/O."""
import math

def _matrix(a):
    if not a or not a[0] or any(len(row)!=len(a[0]) for row in a):
        raise ValueError('Expected a nonempty rectangular matrix')
    if not all(math.isfinite(v) for row in a for v in row): raise ValueError('Nonfinite matrix')
    return len(a),len(a[0])

def matmul(a,b):
    m,n=_matrix(a); k,p=_matrix(b)
    if n!=k: raise ValueError('Inner dimensions must match')
    return [[sum(a[i][z]*b[z][j] for z in range(n)) for j in range(p)] for i in range(m)]

def identity(n=4): return [[float(i==j) for j in range(n)] for i in range(n)]

def rz(angle):
    if not math.isfinite(angle): raise ValueError('Nonfinite angle')
    c,s=math.cos(angle),math.sin(angle)
    return [[c,-s,0.],[s,c,0.],[0.,0.,1.]]

def homogeneous(rotation,translation):
    if _matrix(rotation)!=(3,3) or len(translation)!=3: raise ValueError('Expected 3D R,t')
    if not all(math.isfinite(v) for v in translation): raise ValueError('Nonfinite translation')
    return [list(rotation[i])+[translation[i]] for i in range(3)]+[[0.,0.,0.,1.]]

def rotation_z(angle): return homogeneous(rz(angle),[0.,0.,0.])

def translation(x=0.,y=0.,z=0.): return homogeneous(identity(3),[x,y,z])

def transform(t,p,direction=False):
    if _matrix(t)!=(4,4) or len(p)!=3: raise ValueError('Expected 4x4 transform and 3D point')
    result=matmul(t,[[v] for v in [*p,0. if direction else 1.]])
    return [row[0] for row in result[:3]]

def inverse_rigid(t):
    if _matrix(t)!=(4,4) or any(abs(a-b)>1e-9 for a,b in zip(t[3],[0,0,0,1])):
        raise ValueError('Not a homogeneous transform')
    r=[row[:3] for row in t[:3]]; rt=[list(col) for col in zip(*r)]
    test=matmul(rt,r)
    det=(r[0][0]*(r[1][1]*r[2][2]-r[1][2]*r[2][1])-r[0][1]*(r[1][0]*r[2][2]-r[1][2]*r[2][0])+r[0][2]*(r[1][0]*r[2][1]-r[1][1]*r[2][0]))
    if abs(det-1)>1e-8 or any(abs(test[i][j]-float(i==j))>1e-8 for i in range(3) for j in range(3)):
        raise ValueError('R must be a proper rotation')
    invt=[-sum(rt[i][j]*t[j][3] for j in range(3)) for i in range(3)]
    return homogeneous(rt,invt)

def fk_matrix(q1,q2,l1=.3,l2=.2):
    if not (math.isfinite(l1) and math.isfinite(l2) and l1>0 and l2>0): raise ValueError('Positive finite lengths required')
    t=identity()
    for step in [rotation_z(q1),translation(l1),rotation_z(q2),translation(l2)]: t=matmul(t,step)
    return t

def uart_8n1(value):
    if not isinstance(value,int) or isinstance(value,bool) or not 0<=value<=255: raise ValueError('Byte required')
    return [0]+[(value>>k)&1 for k in range(8)]+[1]

def uart_payload_rate(baud):
    if not math.isfinite(baud) or baud<=0: raise ValueError('Positive baud required')
    return baud/10.

def spi_transfer_seconds(byte_count,clock_hz):
    if not isinstance(byte_count,int) or isinstance(byte_count,bool) or byte_count<0: raise ValueError('Nonnegative integer bytes required')
    if not math.isfinite(clock_hz) or clock_hz<=0: raise ValueError('Positive clock required')
    return byte_count*8/clock_hz

def parallel_resistance(values):
    if not values or any(not math.isfinite(v) or v<=0 for v in values): raise ValueError('Positive resistances required')
    return 1/sum(1/v for v in values)
