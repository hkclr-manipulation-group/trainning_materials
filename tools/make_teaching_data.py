"""Create synthetic CSV and Ethernet/IPv4/UDP pcap files without sending traffic."""
import csv
from pathlib import Path
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/"labs"))
from course_lab import encode_frame


def ipv4_checksum(data):
    if len(data) % 2:
        data += b"\0"
    total = sum(struct.unpack("!"+"H"*(len(data)//2), data))
    while total >> 16:
        total = (total & 65535)+(total >> 16)
    return (~total) & 65535


def make_packet(payload, reverse=False):
    # Documentation addresses (RFC 5737); no network calls are made.
    src, dst = bytes([192,0,2,1]), bytes([192,0,2,2])
    sport, dport = 40000, 5000
    if reverse:
        src, dst, sport, dport = dst, src, dport, sport
    udp = struct.pack("!HHHH", sport, dport, 8+len(payload), 0)+payload
    # UDP checksum zero is allowed for IPv4. IPv4 header checksum is computed.
    header = struct.pack("!BBHHHBBH4s4s", 0x45, 0, 20+len(udp), 1, 0, 64, 17, 0, src, dst)
    header = header[:10]+struct.pack("!H", ipv4_checksum(header))+header[12:]
    ethernet = bytes.fromhex("0200000000020200000000010800")
    return ethernet+header+udp


def main():
    out = ROOT/"labs"/"data"
    out.mkdir(parents=True, exist_ok=True)
    events = [(0.0,"TX",7,.25,"new command"),(.02,"RX",7,.25,"fresh feedback"),
              (.04,"RX",7,.25,"duplicate; does not refresh freshness in this exercise"),
              (.06,"TX",8,.30,"next command"),(.181,"CHECK",8,None,"last fresh RX at .020; age .161s")]
    with (out/"protocol_events.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f); writer.writerow(["time_s","direction","sequence","angle_rad","note"]); writer.writerows(events)
    with (out/"teaching_udp.pcap").open("wb") as f:
        f.write(struct.pack("<IHHIIII",0xa1b2c3d4,2,4,0,0,65535,1))
        for t,direction,seq,angle,_ in events:
            if direction == "CHECK": continue
            packet=make_packet(encode_frame(1,seq,angle),direction=="RX")
            f.write(struct.pack("<IIII",0,round(t*1e6),len(packet),len(packet)))
            f.write(packet)
    with (out/"spi_mode0.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.writer(f); writer.writerow(["time_us","CS","CLK","MOSI"])
        writer.writerow([0,1,0,0])
        for i,bit in enumerate("10100101"):
            writer.writerow([1+2*i,0,0,int(bit)])
            writer.writerow([2+2*i,0,1,int(bit)])
        writer.writerow([17,0,0,1]); writer.writerow([18,1,0,1])
    print("Created synthetic events, SPI samples, and four-packet pcap in",out)


if __name__ == "__main__":
    main()
