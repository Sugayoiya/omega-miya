import datetime
import random
import hashlib

basic = {
    '一元微积分',
    '多元微积分',
    '高等微积分',
    '几何与代数',
    '随机数学方法',
    '概率论与数理统计',
    '线性代数',
    '复变函数引论',
    '大学物理',
    '数理方程引',
    '数值分析',
    '离散数学',
    '离散数学（Ⅱ）',
    '随机过程',
    '应用随机过程',
    '泛函分析',
    '代数编码理论',
    '初等数论与多项式',
    '应用统计',
    '工程图学基础',
    '电路原理',
    '电子基础',
    '电子技术实验',
    '电路分析',
    'C语言程序设计',
    'C++程序设计',
    'Java程序设计',
    '编译原理',
    '操作系统',
    '计算机网络',
    '数据库原理   ',
    '软件工程',
    '软件系统设计',
    'Python',
    'Java面向对象程序设计',
    '计算机系统结构',
    '计算机网络及应用',
    '计算机组成原理',
    '计算机导论',
    '大学计算机基础实践',
    '数据结构',
    '计算机网络与通信',
    '微机原理及应用',
    '电子技术基础',
    '模拟电子技术基础',
    '数据库原理',
    '多媒体技术',
    '计算机接口技术',
    '电路与电子技术基础',
    'Linux系统及应用'
}
advance = {
    '微计算机技术',
    '数字系统设计自动化',
    'VLSI设计导论',
    '网络编程与计算技术',
    '通信电路',
    '通信原理课组',
    '网络安全',
    '网格计算',
    '高性能计算前沿技术',
    '模式识别',
    '数字图象处理',
    '多媒体技术基础及应用',
    '计算机图形学基础',
    '计算机实时图形和动画技术',
    '系统仿真与虚拟现实',
    '现代控制技术',
    '信息检索',
    '电子商务平台及核心技术',
    '数据挖掘',
    '机器学习概论',
    '人机交互理论与技术',
    '人工神经网络',
    '信号处理原理',
    '系统分析与控制',
    '媒体计算',
    '形式语言与自动机',
    '分布式数据库系统',
    '算法分析与设计基础',
    '面向对象技术及其应用',
    '软件项目管理',
    '信息检索技术',
    '人工智能导论',
    '高级数据结构',
    '计算机动画的算法与技术',
    '嵌入式系统',
    'C++高级编程',
    '单片机和嵌入式系统',
    '数字系统集成化设计与综合',
    '移动通信与卫星通信',
    '遥感原理',
    '图象处理系统',
    '图象压缩',
    'Windows操作系统原理与应用',
    '专业英语',
    '光纤应用技术A',
    '光电子技术及其应用',
    '微电子学概论',
    '付立叶光学',
    '激光与光电子技术实验',
    '信号处理实验与设计',
    '激光光谱',
    '光检测技术',
    '光传感技术',
    '光电子CAD与仿真',
    '量子电子学',
    '非线性光学',
    '真空技术',
    '光通信技术',
    '微电子新器件',
    '微电子系统集成概论',
    '量子信息学引论',
    '语音信号处理',
    '无线信号的光纤传输技术',
    '初等数论',
    '互联网信息处理',
    '机器人智能控制',
    '电子测量',
    '电力电子系统设计',
    '现代检测技术基础',
    '智能仪表设计',
    '生产系统计划与控制',
    '过程控制',
    '计算机图象处理与多媒体',
    '现代电子技术',
    '智能控制',
    '过程控制系统',
    'UNIX系统基础',
    '离散时间信号处理',
    '系统的可靠性及容错',
    '电力电子电路的微机控制',
    '非线性控制理论',
    '电子商务概论',
    '虚拟现实技术及其应用',
    '智能优化算法及其应用',
    '随机控制',
    '控制专题',
    '现场总线技术及其应用',
    '数字视频基础与应用',
    '嵌入式系统设计与应用',
    '多维空间分布系统控制及信号处理杂谈',
    '集成传感器',
    'RF-CMOS电路设计',
    '数/模混合集成电路',
    '分子生物电子学',
    '集成电路测试',
    '纳电子材料',
    '半导体材料与器件的表征和测量',
    '模式识别与机器学习导论',
    '自动控制原理',
    '调节器与执行器',
    '计算机控制系统',
    '电机及电力拖动基础',
    '集散控制系统实验',
    '过程控制综合实践',
    '电气控制技术',
    '系统工程导论',
    '先进控制理论与技术',
    '自动化工程设计',
    '企业供电',
    '自动化导论',
    '数字信号处理',
    '电子信息技术导论',
    '计算机图形学',
    '信息安全',
    '高级语言程序设计',
    'Android移动终端开发',
    '网页设计与网站建设',
    '信号与系统',
    '传感器与检测技术',
    '单片机课程设计',
    '数字电子技术基础',
    '大学计算机基础与实践',
    '大数据基础概论',
    'Web系统与技术',
    '强化学习',
    '智能计算导论',
    '并行程序设计',
    '数据结构与算法分析',
    '人工智能原理',
    '机器学习',
    '虚拟现实和数字孪生技术',
    '智能传感器与控制系统',
    '人工智能系统平台实训',
    '智能系统综合设计',
    '自动控制概论'
}


def course(user_id: int) -> str:
    # 用qq、日期生成随机种子
    # random_seed_str = str([user_id, datetime.date.today()])
    # md5 = hashlib.md5()
    # md5.update(random_seed_str.encode('utf-8'))
    # random_seed = md5.hexdigest()
    # random.seed(random_seed)
    course_day = random.sample(basic, k=1)
    course_day.extend(random.sample(advance, k=3))
    course_t = str.join('》\n《', course_day)
    result = f"今天要修行的课有:\n《{course_t}》"
    return result
