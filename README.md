# 从纸条机械臂开始：机器人开发自学

这套资料按中学生可起步的顺序编写：先用生活例子、纸笔和动画理解问题，再学几个数字怎样计算，最后运行代码。不会矩阵、微积分或编程也可以从第一天开始。需要深入时，再进入技术手册和新增的工程细节。

**第一周目标：看懂机器人各部分如何配合，完成一个自己能解释的小工具。** 每天的末尾都有自检和答案，遇到具体问题可以请教同事，无需讲师。

**现在可以边读边改Python并运行：** 打开[交互课堂说明](INTERACTIVE.md)，安装一次后双击 `start_classroom.cmd`。8本Notebook包含代码编辑、关节/控制/滤波滑块、实际训练过程播放和工具调用。浏览器显示教材，本机Python负责计算；尚未部署公共网址。

## 先走这条线

1. [七天路线](WEEK_PLAN.md)：每天学什么，哪些暂时不用学。
2. [第一天：让机器人听懂一句话](lessons/day01_system_and_code.md)：从任务、单位和位置开始。
3. 看不懂符号时查 [数学小台阶](beginner/MATH_STEPS.md)；不会运行命令时查 [从零操作卡](beginner/COMPUTER_FIRST_STEPS.md)。
4. 每天先猜动画结果，再播放，再做纸笔题和代码实验。参考 [自学方法](SELF_STUDY.md)。

## 这次可直接使用的材料

| 材料 | 入口 |
|---|---|
| 可编辑运行的8本Python交互教材 | [安装与使用](INTERACTIVE.md)、[课堂首页](notebooks/00_start_here.ipynb) |
| 从通俗解释接到工程实现：推导、参数、接口与失败原因 | [工程细节](handbook/09_engineering_details.md) |
| 重写后的七天正文：生活例子→分步计算→代码→自检 | [第一天](lessons/day01_system_and_code.md) |
| 12段离线动画、12张四步分镜 | [动画索引](assets/animations/README.md) |
| 14组进一步理解算法的PNG/SVG图 | [技术图示](assets/README.md) |
| 原生Python动画播放器，可暂停、逐帧和慢放 | [播放说明](assets/animations/README.md) |
| 从通俗比喻过渡到算法 | [算法故事](beginner/ALGORITHM_STORIES.md) |
| 9类教学数值表与可核对的预期结果 | [参考数据说明](references/DATA_GUIDE.md) |
| 4套团队模型、24个关节的文件声明快照 | [来源与范围](references/DATA_GUIDE.md) |
| 10条分级阅读卡、8条BibTeX与外部数据集卡 | [文献阅读路线](references/READING_GUIDE.md) |
| 深入原理、推导与方法比较 | [技术手册及算法地图](handbook/ALGORITHMS.md) |
| 基础与算法实验、离线通信数据 | [基础实验](labs/README.md)、[算法实验](labs/ALGORITHMS.md) |
| 自检与结业 | 每篇正文3题含答案；[原题库](assessments/QUESTIONS.md)、[算法题](assessments/ALGORITHM_EXERCISES.md)作为进阶 |
| 团队项目与工具文档 | [项目地图](PROJECT_MAP.md)、[工具说明](TOOLS.md)、[来源索引](SOURCES.md) |

## 能运行程序后再用这些命令

在本仓库根目录运行，计算实验只需Python 3.10+标准库：

```powershell
python labs/course_lab.py all
python labs/algorithm_lab.py all
python -m unittest discover -s tests -v
```

想调角度：`python labs/kinematics_explorer.py`。想逐帧看动画：`python labs/animation_player.py`。这两个窗口需要可用Tcl/Tk与桌面；打不开时用已保存的GIF、PNG与CSV继续学习。

教学数值、文件声明与外部数据来源已分开标注。它们不能直接作为电机额定参数或真机控制参数。交互课程更新于2026-09-08，实际检查范围见 [验证记录](VALIDATION.md)。
