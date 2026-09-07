# 机器人开发一周入门

面向刚加入团队、需要理解机器人开发全流程的同事，按完全自学设计，遇到具体问题可以请教同事。沿用仓库名 `trainning_materials`，覆盖本体设计、通信、控制、软件工程、感知与AI。

**一周目标：能解释系统、运行离线实验、阅读项目入口、提交一个有测试证据的小改动。** 独立完成机械定型、驱动器调参或真机 AI 部署，需要后续专项训练。

## 从这里开始

1. 先读 [自学说明](SELF_STUDY.md)，再按 [一周路线](WEEK_PLAN.md) 开始，每天约6小时，共42小时。
2. 按 [环境与工具操作](TOOLS.md) 准备 Python 和编辑器。
3. 从 [第一天](lessons/day01_system_and_code.md) 开始，按天完成讲义、实验和测验。
4. 在 [每日测试题](assessments/QUESTIONS.md) 作答后，再看 [答案与评分](assessments/ANSWERS.md)。

基础实验只依赖 Python 3.10+ 标准库，不需要机器人、CUDA、ROS 或联网服务。在本仓库根目录运行：

```powershell
python labs/course_lab.py all
python labs/algorithm_lab.py all
python -m unittest discover -s tests -v
```

第一条命令生成 `outputs/course_report.json`，包含单位换算、运动学、通信编解码、模拟控制、碰撞和小型学习实验的结果。它是教学数据，不能作为 Spark2 的参数或性能报告。

## 资料导航

| 内容 | 入口 |
|---|---|
| 每天学什么、做到什么程度 | [WEEK_PLAN.md](WEEK_PLAN.md) |
| 七天中文讲义 | [第一天：系统与代码](lessons/day01_system_and_code.md) |
| 工具、安装层级、实际操作 | [TOOLS.md](TOOLS.md) |
| 团队仓库和阅读入口 | [PROJECT_MAP.md](PROJECT_MAP.md) |
| 官方资料与推荐阅读段落 | [SOURCES.md](SOURCES.md) |
| 离线实验步骤与预期结果 | [labs/README.md](labs/README.md) |
| 每日测验与综合考核 | [测试题](assessments/QUESTIONS.md)、[结业任务](assessments/CAPSTONE.md) |
| 术语查询 | [GLOSSARY.md](GLOSSARY.md) |
| AI 协作任务模板 | [templates/AI_TASK.md](templates/AI_TASK.md) |
| 实验与故障报告模板 | [templates/LAB_REPORT.md](templates/LAB_REPORT.md) |
| 自学、排错与请教同事 | [SELF_STUDY.md](SELF_STUDY.md) |
| 深入手册与算法比较 | [九章手册及算法地图](handbook/ALGORITHMS.md) |
| 14组图解与原生交互窗口 | [图示索引](assets/README.md) |
| 新增算法实验与离线通信数据 | [实验步骤](labs/ALGORITHMS.md) |
| 20道算法专项题及解答 | [专项自检](assessments/ALGORITHM_EXERCISES.md) |
| 实际运行结果与环境范围 | [验证记录](VALIDATION.md) |

资料整理日期：2026-09-07。团队案例按当前工作区文件整理；网络资料保留官方原文链接和阅读目的，不整篇搬运。部分项目文档与实现可能不同步，具体接口以对应版本代码为准。
