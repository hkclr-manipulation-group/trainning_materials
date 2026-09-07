# %% [markdown]
# # 第七天｜从在线改代码到可复现交付
#
# [正文](../lessons/day07_vibe_coding.md) · [操作说明](../INTERACTIVE.md) · [软件手册](../handbook/07_software.md)
#
# 今天把 Python 接到其他工具：读取 URDF/CSV、查看实现、调用本地命令、检查返回码、保存报告。Jupyter 内核运行在哪台电脑，工具就运行在哪台；远程服务器不能自动使用你电脑的 USB。
#
# 此处工具是已有 Python 模块、脚本和测试。CAD、Wireshark、CMake、ROS 和硬件驱动须在对应机器另行安装，不能因为 Notebook 能打开就视为可用。

# %% [markdown]
# ## 1. 查看正在使用的实现
# `inspect.getsource` 显示函数源码，帮助把推导与实现对应起来。在左侧文件树打开 `labs/course_lab.py` 可以修改源文件；保存后需重启内核再导入。
# 想保持原版，先复制函数为自己的版本，在实验文件中修改。不要只改一份与实际调用无关的副本。

# %%
import inspect
print(inspect.getsource(fk))

# %% [markdown]
# ## 2. 调用命令行工具：参数列表、工作目录、超时、返回码
# 下面真正启动一个子进程执行课程算法脚本。用 `sys.executable` 保证与当前内核同一个 Python；参数用列表分别传递，`cwd` 使相对路径明确。
# `timeout` 防止永久等待；`returncode=0` 表示进程正常结束，但业务结果还要读 JSON 的 success/reason。非零返回码要连同 stderr 保留，不能吞掉报错再说成功。

# %%
import subprocess
def run_python(arguments, timeout_s=60):
    result = subprocess.run([sys.executable, *arguments], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace",
                            timeout=timeout_s, check=False)
    print(result.stdout)
    if result.returncode:
        print(result.stderr)
        raise RuntimeError(f"工具失败，returncode={result.returncode}")
    return result

run_python(["labs/algorithm_lab.py", "ik"])
tool_result = json.loads((ROOT / "outputs" / "algorithms_ik.json").read_text(encoding="utf-8"))["ik"]
assert tool_result["success"] and tool_result["error_m"] <= 1e-6
print("业务状态:", tool_result["reason"])

# %% [markdown]
# ## 3. 跑独立测试并保留证据
# 命令是 `python -m unittest discover -s tests -v`。测试包括手算位置、固定报文字节、A*已知最短代价、雅可比差分和参考数据清单。
# 核心测试全过并不代表真机通过；测试范围要写清楚。下面将日志保存到 outputs，便于请同事定位问题。

# %%
checks = run_python(["-m", "unittest", "discover", "-s", "tests", "-v"])
output_dir = ROOT / "outputs" / "student"
output_dir.mkdir(parents=True, exist_ok=True)
(output_dir / "tests.log").write_text(checks.stdout + checks.stderr, encoding="utf-8")
print(checks.stderr[-500:])

# %% [markdown]
# ## 4. 把需求写给 AI，再用自己知道的答案验证
# 示例任务卡：
#
# > 写 endpoint_cm(q1_deg,q2_deg)，两杆30cm和20cm，输入度、输出(x,y)厘米。拒绝非有限数。保留关节2相对关节1的含义。验证(0,0)→(50,0)、(90,0)→(0,50)、(0,90)→(30,20)。不要接电机。
#
# 下面先给可运行版本。你可以请求自己常用的 AI 工具提出另一种写法，然后比较代码差异、独立预期和异常行为。此处没有自动调用收费模型 API，也无需账号。

# %%
def endpoint_cm(q1_deg, q2_deg):
    if not all(math.isfinite(v) for v in (q1_deg, q2_deg)):
        raise ValueError("angles must be finite")
    x, y = fk(math.radians(q1_deg), math.radians(q2_deg))
    return 100*x, 100*y

known = [((0,0),(50,0)), ((90,0),(0,50)), ((0,90),(30,20))]
for inputs, expected in known:
    assert np.allclose(endpoint_cm(*inputs), expected)
try:
    endpoint_cm(float("nan"),0)
except ValueError:
    pass
else:
    raise AssertionError("NaN should be rejected")
print("自己的工具通过3个独立数值预期和1个异常检查")

# %% [markdown]
# ## 5. 记录环境、输入、输出、来源和限制
# 记录源码 SHA-256 可发现文件是否改变，但哈希不能证明算法正确。Git 提交号还需要仓库中有实际提交；本页只探测工具是否安装，不自动提交或发布。

# %%
import hashlib, importlib.metadata, shutil, platform
report = {
    "python": platform.python_version(),
    "packages": {p: importlib.metadata.version(p) for p in ("numpy", "matplotlib", "jupyterlab", "ipywidgets")},
    "input": {"q_deg": [0,90], "link_lengths_cm": [30,20]},
    "output_cm": endpoint_cm(0,90),
    "source_sha256": hashlib.sha256((ROOT / "labs" / "course_lab.py").read_bytes()).hexdigest(),
    "external_tools_available": {tool: shutil.which(tool) is not None for tool in ("git", "cmake", "tshark", "ros2")},
    "checks": {"unit_test_returncode": checks.returncode, "known_positions": len(known)},
    "scope": "Planar position teaching; no hardware, dynamics or collision certification",
}
report_path = output_dir / "report.json"
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(report_path)
display(report)

# %% [markdown]
# ## 6. 自学结业与交接
# 另存自己的 Notebook；写一句需求，修改一个功能，增加一个实现之外的已知答案，执行 Restart Kernel and Run All，再保存报告。
# 若失败，请同事时带上：输入、预期、实际、完整报错、Python路径、依赖版本。不要只发“没有reachable”。
#
# **进阶任务：** 给 endpoint_cm 增加杆长参数并校验正数；用不同长度的直杆手算值测试。若把工具扩展为真实三维机器人，补齐关节顺序、参考系、限位、碰撞与工具偏移，再讨论控制接口。
#
# **自检：** 返回码0但IK返回success=false该怎么做？答案：命令运行完成，业务求解失败，读取reason并保留输入。Notebook在哪台电脑运行，子进程就在哪台启动。更多工具用法见[工程细节第9节](../handbook/09_engineering_details.md)。
