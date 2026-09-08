# %% [markdown]
# # 通信专题｜从封装到分帧，再到仲裁
#
# [历史与协议栈全文](../handbook/10_communication_stack_history.md) · [深度地图](../DEPTH_MAP.md)
# 本页全部读内存或合成PCAP，不发送网络或电机命令。先分清“哪一层做什么”，再检查字节。
# 动画请在文件夹中用浏览器打开 `assets/interactive/concept_player.html`，选择协议栈或CAN仲裁；它可离线运行。

# %% [markdown]
# ## 1. 从抓包文件逐层拆出同一个8字节载荷
# 本课合成PCAP记录Ethernet头14B、IPv4基本头20B、UDP头8B、载荷8B，共50B。真实线上最小填充/FCS等没有全部记录；文件长度不能直接当线上总开销。
# UDP长度字段是大端，应用角度字段是小端。每层各有自己的格式约定。

# %%
import struct
capture = (ROOT / "labs" / "data" / "teaching_udp.pcap").read_bytes()
assert capture[:4] == b"\xd4\xc3\xb2\xa1"  # 本文件为小端PCAP
seconds, micros, captured_length, original_length = struct.unpack_from("<IIII", capture, 24)
packet = capture[40:40+captured_length]
assert packet[12:14] == b"\x08\x00"  # Ethernet中的IPv4类型
ip_header_length = (packet[14] & 15)*4
udp_offset = 14 + ip_header_length
udp_length = int.from_bytes(packet[udp_offset+4:udp_offset+6], "big")
application = packet[udp_offset+8:udp_offset+udp_length]
print("捕获长度:", captured_length, "IPv4头:", ip_header_length, "UDP总长:", udp_length)
print("应用载荷:", application.hex(" "), decode_frame(application))
assert (captured_length, ip_header_length, udp_length, len(application)) == (50,20,16,8)
assert decode_frame(application)["angle_rad"] == .25

# %% [markdown]
# ## 2. TCP只给字节流：消息可能分几次到
# 下面用两字节大端长度前缀。把stream切成任意块，解析结果应该仍为ABC、DE。
# 缓冲区不是错误；它表示当前尚未拿到完整消息。修改cuts后重跑，比较每一步缓冲长度。

# %%
from expanded_lab import LengthPrefixedDecoder, framed, arbitration_trace
stream = framed(b"ABC") + framed(b"DE")
cuts = [1, 4, 7, len(stream)]
decoder = LengthPrefixedDecoder()
messages, start = [], 0
for end in cuts:
    chunk = stream[start:end]
    obtained = decoder.feed(chunk)
    messages.extend(obtained)
    print("收到:", chunk.hex(" "), "提取:", obtained, "还在缓冲:", bytes(decoder.buffer).hex(" "))
    start = end
assert messages == [b"ABC", b"DE"]

# %% [markdown]
# ## 3. 错误长度不能被当成正常等待
# 本示例拒绝超过8B的消息，并进入失败态；知道新会话/流边界后才能reset。
# 这是教学解析器，没有实现网络重连、校验和、版本协商或完整资源控制。

# %%
decoder = LengthPrefixedDecoder(max_length=8)
try:
    decoder.feed(b"\x00\x09")
except ValueError as error:
    print("预期拒绝:", error)
else:
    raise AssertionError("9B长度应被拒绝")
assert decoder.failed

# %% [markdown]
# ## 4. CAN仲裁逐位计算
# 标准数据帧的11位ID从高位开始。0显性、1隐性；同时发时0覆盖1。这里没有模拟扩展帧、远程帧或其他字段。

# %%
trace = arbitration_trace((0x120, 0x100))
for row in trace:
    print("bit", row["bit"], "发送", {hex(i):bit for i,bit in row["sent"].items()},
          "总线", row["bus"], "退出", [hex(i) for i in row["lost"]])
assert trace[-1]["active"] == [0x100]
assert next(r["bit"] for r in trace if r["lost"]) == 5

# %% [markdown]
# **自检：** 把两个ID改为0x321、0x300，先手工找第一个不同的位，再运行。解释为什么UART、RS-485和应用私有协议不是同一层。把载荷长度8B误当50B字段长度会出现什么？
# **答案方向：** 在本限定条件下0x300优先；先比较二进制高位，不用猜。RS-485描述电气，UART组织串行收发，应用定义含义；载荷与各层总长度混淆会造成越界、截断或错误等待。
