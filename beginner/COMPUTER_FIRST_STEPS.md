# 从零操作卡：文件、终端、程序和数据

不熟悉电脑开发工具时，按顺序完成。每步都有能看见的检查结果。例子按Windows写；其他系统替换路径和Python命令即可。

## 1. 找到文件，不要先安装一大堆工具

打开trainning_materials文件夹，应该看到README.md、lessons、labs、assets。文件夹把资料分类；`.md`是可用编辑器预览的文字，`.py`是Python程序，`.csv`是数据表，`.gif`是动画。

先打开README.md。VS Code中可右键选择预览，或使用Markdown预览命令；如果看到`#`和方括号，说明正在看源文本，不是文件坏了。无法播放GIF时，打开同名_steps.png看分镜。

## 2. 终端在哪里运行命令

终端是输入文字命令的窗口。Windows可以在项目文件夹打开PowerShell；也可在VS Code打开终端。先输入`Get-Location`，确认显示的是trainning_materials的目录。

目录不对时用`cd`切换，例如`cd D:\code_agent\trainning_materials`。这里D盘路径只是我们当前工作区示例，你的电脑按实际位置填写。路径有空格时用引号包起来。

输入`Get-ChildItem`列出文件。看到labs才继续。找不到文件的错误经常只是当前位置不对。

## 3. 先确认Python，再跑一行代码

输入`python --version`，应该看到版本号。本课程计算脚本使用Python 3.10及以上。命令不存在时，先按团队工具环境说明安装或请教同事；不要从错误弹窗随意下载不明软件。

输入`python -c "print(30 / 100)"`，应显示0.3。`-c`表示执行引号里的短程序。再运行`python labs/course_lab.py units`。程序输出结果后，终端回到等待输入状态。

看到`>>>`说明进入了Python交互环境，不是在PowerShell里。这时可输入`exit()`退出，再运行带python开头的终端命令。

## 4. 改一小段程序

新建`my_first.py`，写入：

```python
length_cm = 30
length_m = length_cm / 100
print(length_m)
```

保存，再运行`python my_first.py`。将30改20，保存后再运行。若结果不变，先确认保存了文件，以及运行的是同一个文件。只改一个值，练习观察因果。

## 5. 错误怎么读

把`length_cm`故意写成不存在的`lenght_cm`，会出现NameError。读最后一行了解错误类型，再向上看文件名与行号。修复后重新运行。

如果文件不存在，查路径；找不到模块，查解释器和安装；数字不对，查单位与输入；窗口打不开，查看Tcl/Tk或图形环境提示。不要将所有错误都理解为“程序算法错了”。

## 6. 打开CSV并画图

用表格软件打开 [trajectory_reference.csv](../references/data/trajectory_reference.csv)，第一行是列名。t_s代表秒，q_rad代表角度弧度，v_rad_s代表角速度。

选t_s与v_rad_s两列，插入XY散点连线图，让t_s作横轴。不要把时间当成任意分类标签。应看到先上升、再平、再下降的速度线。若全挤在一个单元格，导入时选择逗号分隔。

## 7. 保存版本与差异

有Git时，在正确仓库运行`git status`，看哪些文件改变；运行`git diff`看具体内容。先练习只改自己创建的一行注释，再观察差异。

想提交时只暂存你的文件，例如`git add my_first.py`，再用`git diff --cached`检查。提交不是运行程序，也不是把程序发给机器人。没有Git也能完成纸笔和计算主线，版本练习可以随后补。

## 8. 不会时怎样问同事

发送实际命令、工作目录、完整错误和你期望的结果。例如：“我在trainning_materials目录运行units，Python版本3.10，出现以下错误，我确认labs文件夹存在。”这比只说“打不开”更容易得到帮助。

完整模板见 [自学说明](../SELF_STUDY.md)。不要发设备密钥；教学数据已经足以复现多数入门问题。
