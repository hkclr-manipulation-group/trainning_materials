# %% [markdown]
# # 物理链路的算例：接线、位时间与吞吐
# 配合[接线与链路讲义](../handbook/14_physical_connections.md)。全部是离线计算，不打开串口、CAN或USB，不是电路仿真。电压、接头引脚和器件容限需要具体硬件资料。

# %%
from spatial_lab import uart_8n1,uart_payload_rate,spi_transfer_seconds,parallel_resistance
bits=uart_8n1(0xA5)
assert bits==[0,1,0,1,0,0,1,0,1,1]
baud=115200
print('Start / data LSB first / stop:',bits)
print('Bit duration us:',1e6/baud,'ideal payload byte/s:',uart_payload_rate(baud))
fig,ax=plt.subplots();ax.step(range(len(bits)+1),bits+[bits[-1]],where='post')
ax.scatter(np.arange(10)+.5,bits,color='red');ax.set(xlabel='bit slot',ylabel='logic level',yticks=[0,1]);plt.show()

# %% [markdown]
# ## 同一个“速度”为什么有三种数字
# 总线时钟、纯移位时间与完整事务延迟不同。76字节是本地F446 README描述的快照长度；本例1MHz仅为教学时钟。

# %%
seconds=spi_transfer_seconds(76,1e6)
assert abs(seconds-.000608)<1e-12
print('SPI shift only:',seconds*1e6,'us')
print('If extra waiting is 200 us, transaction:',(seconds+.0002)*1e6,'us')
print('Two 120 ohm in parallel:',parallel_resistance([120,120]))
assert parallel_resistance([120,120])==60

# %% [markdown]
# ## 差分与共模：两条线都变了，差值却没变
# 本例用典型示意电压，不验证任何芯片的阈值。加共同扰动只演示代数相减，实际接收器仍受共模范围限制。

# %%
for disturbance in [0,.4,-.3]:
    high,low=3.5+disturbance,1.5+disturbance
    assert abs(high-low-2)<1e-12
    print('H/L:',high,low,'differential:',high-low,'common mode:',(high+low)/2)
resistance=4700;capacitance=100e-12
rise=.8473*resistance*capacitance
assert abs(rise*1e9-398.231)<1e-6
print('I2C approximate rise:',rise*1e9,'ns; compare with selected mode specification')

# %% [markdown]
# 自检：接头相同是否保证协议相同？CAN_TX可以直接接CAN_H吗？增加波特率是否总能降低整个控制闭环延迟？答案要分别说明电气、链路和应用条件。
