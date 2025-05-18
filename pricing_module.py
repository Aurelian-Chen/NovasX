import numpy as np
from typing import List, Tuple, Dict

# ====================== 连续分段线性函数生成器 ======================
class ContinuousPiecewiseFunction:
    """保证连续的分段线性函数生成器"""
    def __init__(self, breakpoints: List[Tuple[float, float]]):
        """
        :param breakpoints: [(粉丝数, 价格), ...] 按粉丝数升序排列
        """
        self.segments = []
        for i in range(len(breakpoints)-1):
            x1, y1 = breakpoints[i]
            x2, y2 = breakpoints[i+1]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y1 - slope * x1
            self.segments.append((x1, x2, slope, intercept))
    
    def __call__(self, x: float) -> float:
        for start, end, slope, intercept in self.segments:
            if start <= x < end:
                return slope * x + intercept
        # 超出最后一个区间，则用最后一段计算
        start, end, slope, intercept = self.segments[-1]
        return slope * x + intercept

# ====================== 构建抖音平台的32个标签分段函数 ======================
def build_douyin_functions() -> Dict[str, ContinuousPiecewiseFunction]:
    functions = {}
    
    # 1. 三农 (连续保证: 各断点误差 < 0.1元)
    functions["三农"] = ContinuousPiecewiseFunction([
        (0, 200),
        (6e4, 6800),
        (30e4, 15200),
        (75e4, 32000),
        (300e4, 68000),
        (750e4, 250000),
        (2000e4, 420000)
    ])
    
    # 2. 二次元
    functions["二次元"] = ContinuousPiecewiseFunction([
        (0, 300),
        (6e4, 5500),
        (30e4, 11200),
        (75e4, 26000),
        (300e4, 45000),
        (750e4, 180000),
        (2000e4, 260000)
    ])
    
    # 3. 健康
    functions["健康"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8000),
        (30e4, 18000),
        (75e4, 38000),
        (300e4, 110000),
        (750e4, 220000),
        (2000e4, 350000)
    ])
    
    # 4. 兴趣爱好
    functions["兴趣爱好"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 6000),
        (30e4, 15000),
        (75e4, 35000),
        (300e4, 70000),
        (750e4, 150000),
        (2000e4, 300000)
    ])
    
    # 5. 其他
    functions["其他"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7500),
        (30e4, 16000),
        (75e4, 30000),
        (300e4, 60000),
        (750e4, 140000),
        (2000e4, 280000)
    ])
    
    # 6. 医疗健康
    functions["医疗健康"] = ContinuousPiecewiseFunction([
        (0, 1000),
        (6e4, 8500),
        (30e4, 20000),
        (75e4, 45000),
        (300e4, 95000),
        (750e4, 200000),
        (2000e4, 400000)
    ])
    
    # 7. 娱乐
    functions["娱乐"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 5000),
        (30e4, 12000),
        (75e4, 25000),
        (300e4, 50000),
        (750e4, 100000),
        (2000e4, 200000)
    ])
    
    # 8. 家居家装
    functions["家居家装"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 10000),
        (30e4, 21000),
        (75e4, 52000),
        (300e4, 78000),
        (750e4, 120000),
        (2000e4, 220000)
    ])
    
    # 9. 幽默搞笑
    functions["幽默搞笑"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7000),
        (30e4, 19000),
        (75e4, 45000),
        (300e4, 90000),
        (750e4, 200000),
        (2000e4, 400000)
    ])
    
    # 10. 影视综艺（基础函数，特殊处理在报价时考虑明星账号）
    functions["影视综艺"] = ContinuousPiecewiseFunction([
        (0, 2500),
        (6e4, 7000),
        (30e4, 23500),
        (75e4, 52500),
        (300e4, 126000),
        (750e4, 220000),
        (2000e4, 400000)
    ])
    
    # 11. 情感心理
    functions["情感心理"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8500),
        (30e4, 22000),
        (75e4, 60000),
        (300e4, 110000),
        (750e4, 210000),
        (2000e4, 450000)
    ])
    
    # 12. 才艺技能
    functions["才艺技能"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 9500),
        (30e4, 25000),
        (75e4, 50000),
        (300e4, 90000),
        (750e4, 160000),
        (2000e4, 300000)
    ])
    
    # 13. 教育培训
    functions["教育培训"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 8000),
        (30e4, 22000),
        (75e4, 45000),
        (300e4, 85000),
        (750e4, 180000),
        (2000e4, 380000)
    ])
    
    # 14. 文化
    functions["文化"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 6000),
        (30e4, 18000),
        (75e4, 40000),
        (300e4, 80000),
        (750e4, 160000),
        (2000e4, 300000)
    ])
    
    # 15. 旅游
    functions["旅游"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 6500),
        (30e4, 20000),
        (75e4, 50000),
        (300e4, 95000),
        (750e4, 180000),
        (2000e4, 450000)
    ])
    
    # 16. 时事资讯
    functions["时事资讯"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7000),
        (30e4, 18000),
        (75e4, 40000),
        (300e4, 75000),
        (750e4, 140000),
        (2000e4, 280000)
    ])
    
    # 17. 时尚
    functions["时尚"] = ContinuousPiecewiseFunction([
        (0, 1000),
        (6e4, 9500),
        (30e4, 35000),
        (75e4, 75000),
        (300e4, 130000),
        (750e4, 250000),
        (2000e4, 1000000)
    ])
    
    # 18. 母婴育儿
    functions["母婴育儿"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 9000),
        (30e4, 22000),
        (75e4, 60000),
        (300e4, 95000),
        (750e4, 180000),
        (2000e4, 360000)
    ])
    
    # 19. 汽车
    functions["汽车"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8000),
        (30e4, 32000),
        (75e4, 98000),
        (300e4, 150000),
        (750e4, 220000),
        (2000e4, 720000)
    ])
    
    # 20. 游戏
    functions["游戏"] = ContinuousPiecewiseFunction([
        (0, 200),
        (6e4, 6500),
        (30e4, 18000),
        (75e4, 42000),
        (300e4, 75000),
        (750e4, 120000),
        (2000e4, 220000)
    ])
    
    # 21. 生活
    functions["生活"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8500),
        (30e4, 22000),
        (75e4, 50000),
        (300e4, 95000),
        (750e4, 180000),
        (2000e4, 400000)
    ])
    
    # 22. 科学科普
    functions["科学科普"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 8000),
        (30e4, 20000),
        (75e4, 45000),
        (300e4, 85000),
        (750e4, 160000),
        (2000e4, 320000)
    ])
    
    # 23. 科技
    functions["科技"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8500),
        (30e4, 22000),
        (75e4, 50000),
        (300e4, 95000),
        (750e4, 180000),
        (2000e4, 400000)
    ])
    
    # 24. 美妆
    functions["美妆"] = ContinuousPiecewiseFunction([
        (0, 2000),
        (6e4, 9500),
        (30e4, 38000),
        (75e4, 95000),
        (300e4, 145000),
        (750e4, 240000),
        (2000e4, 880000)
    ])
    
    # 25. 美容个护
    functions["美容个护"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 9000),
        (30e4, 25000),
        (75e4, 55000),
        (300e4, 100000),
        (750e4, 180000),
        (2000e4, 380000)
    ])
    
    # 26. 美食
    functions["美食"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7500),
        (30e4, 20000),
        (75e4, 45000),
        (300e4, 85000),
        (750e4, 150000),
        (2000e4, 350000)
    ])
    
    # 27. 职场
    functions["职场"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7000),
        (30e4, 18000),
        (75e4, 40000),
        (300e4, 75000),
        (750e4, 140000),
        (2000e4, 280000)
    ])
    
    # 28. 萌宠
    functions["萌宠"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 8500),
        (30e4, 18000),
        (75e4, 35000),
        (300e4, 65000),
        (750e4, 120000),
        (2000e4, 240000)
    ])
    
    # 29. 财经
    functions["财经"] = ContinuousPiecewiseFunction([
        (0, 500),
        (6e4, 9500),
        (30e4, 35000),
        (75e4, 75000),
        (300e4, 160000),
        (750e4, 300000),
        (2000e4, 1800000)
    ])
    
    # 30. 运动健身
    functions["运动健身"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7000),
        (30e4, 20000),
        (75e4, 55000),
        (300e4, 95000),
        (750e4, 170000),
        (2000e4, 350000)
    ])
    
    # 31. 音乐
    functions["音乐"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 7500),
        (30e4, 18000),
        (75e4, 40000),
        (300e4, 80000),
        (750e4, 150000),
        (2000e4, 300000)
    ])
    
    # 32. 颜值
    functions["颜值"] = ContinuousPiecewiseFunction([
        (0, 0),
        (6e4, 8000),
        (30e4, 20000),
        (75e4, 45000),
        (300e4, 85000),
        (750e4, 160000),
        (2000e4, 320000)
    ])
    
    return functions

# ====================== 定义各平台相对系数矩阵 ======================
COEFF_MATRIX = {
    "三农": {"小红书": 0.5, "B站": 0.3, "快手": 1.8, "抖音": 1},
    "二次元": {"小红书": 0.7, "B站": 2.2, "快手": 0.4, "抖音": 1},
    "健康": {"小红书": 1.3, "B站": 0.8, "快手": 1.1, "抖音": 1},
    "兴趣爱好": {"小红书": 1.2, "B站": 1.4, "快手": 0.9, "抖音": 1},
    "其他": {"小红书": 0.8, "B站": 0.9, "快手": 1.0, "抖音": 1},
    "医疗健康": {"小红书": 1.0, "B站": 0.6, "快手": 1.3, "抖音": 1},
    "娱乐": {"小红书": 0.9, "B站": 1.1, "快手": 1.4, "抖音": 1},
    "家居家装": {"小红书": 1.8, "B站": 0.5, "快手": 1.0, "抖音": 1},
    "幽默搞笑": {"小红书": 0.7, "B站": 1.0, "快手": 1.6, "抖音": 1},
    "影视综艺": {"小红书": 0.8, "B站": 1.7, "快手": 0.9, "抖音": 1},
    "情感心理": {"小红书": 1.6, "B站": 0.7, "快手": 1.0, "抖音": 1},
    "才艺技能": {"小红书": 1.1, "B站": 1.5, "快手": 0.8, "抖音": 1},
    "教育培训": {"小红书": 1.0, "B站": 1.6, "快手": 0.6, "抖音": 1},
    "文化": {"小红书": 1.1, "B站": 1.8, "快手": 0.5, "抖音": 1},
    "旅游": {"小红书": 1.6, "B站": 0.9, "快手": 1.1, "抖音": 1},
    "时事资讯": {"小红书": 0.6, "B站": 1.3, "快手": 1.1, "抖音": 1},
    "时尚": {"小红书": 1.9, "B站": 0.8, "快手": 1.2, "抖音": 1},
    "母婴育儿": {"小红书": 1.5, "B站": 0.4, "快手": 1.5, "抖音": 1},
    "汽车": {"小红书": 0.7, "B站": 1.1, "快手": 0.9, "抖音": 1},
    "游戏": {"小红书": 0.5, "B站": 2.0, "快手": 0.7, "抖音": 1},
    "生活": {"小红书": 1.3, "B站": 1.0, "快手": 1.5, "抖音": 1},
    "科学科普": {"小红书": 0.9, "B站": 1.7, "快手": 0.6, "抖音": 1},
    "科技": {"小红书": 0.6, "B站": 1.8, "快手": 0.8, "抖音": 1},
    "美妆": {"小红书": 2.0, "B站": 0.6, "快手": 1.0, "抖音": 1},
    "美容个护": {"小红书": 1.7, "B站": 0.5, "快手": 0.9, "抖音": 1},
    "美食": {"小红书": 1.5, "B站": 1.0, "快手": 1.4, "抖音": 1},
    "职场": {"小红书": 1.1, "B站": 1.4, "快手": 0.7, "抖音": 1},
    "萌宠": {"小红书": 1.2, "B站": 1.1, "快手": 1.4, "抖音": 1},
    "财经": {"小红书": 0.8, "B站": 1.0, "快手": 0.5, "抖音": 1},
    "运动健身": {"小红书": 1.1, "B站": 0.9, "快手": 1.0, "抖音": 1},
    "音乐": {"小红书": 1.0, "B站": 1.5, "快手": 1.1, "抖音": 1},
    "颜值": {"小红书": 1.4, "B站": 1.0, "快手": 1.3, "抖音": 1},
}

# ====================== 构建抖音基准函数 ======================
DOUYIN_FUNCTIONS = build_douyin_functions()

# ====================== 获取报价接口 ======================
def get_price(platform: str, category: str, followers: float, **kwargs) -> float:
    """
    获取单条广告报价
    :param platform: 平台名称，选项包括：抖音, 小红书, B站, 快手
    :param category: 标签名称（32个标准标签之一）
    :param followers: 粉丝数量
    :param kwargs: 特殊参数，比如影视综艺的 is_celebrity
    :return: 单条广告报价
    """
    if category not in DOUYIN_FUNCTIONS:
        raise ValueError(f"不支持的标签：{category}")
    if category not in COEFF_MATRIX:
        raise ValueError(f"未配置标签系数：{category}")
    
    # 获取抖音基准价格
    base_func = DOUYIN_FUNCTIONS[category]
    base_price = base_func(followers)
    
    # 特殊处理：影视综艺标签的明星账号
    if category == "影视综艺" and kwargs.get("is_celebrity", False):
        # 明星账号价格翻倍
        base_price *= 2
    
    # 应用平台系数
    platform_coeff = COEFF_MATRIX[category].get(platform, 1.0)
    final_price = base_price * platform_coeff
    
    return final_price

def get_all_platforms_prices(category: str, followers: float, **kwargs) -> Dict[str, float]:
    """
    获取所有平台的广告报价
    :param category: 标签名称
    :param followers: 粉丝数量
    :param kwargs: 特殊参数
    :return: 包含所有平台报价的字典
    """
    platforms = ["抖音", "小红书", "B站", "快手"]
    prices = {}
    
    for platform in platforms:
        prices[platform] = get_price(platform, category, followers, **kwargs)
    
    return prices

def get_categories() -> List[str]:
    """
    获取所有支持的标签类别，按照拼音排序
    :return: 标签列表
    """
    # 所有标签的拼音映射（按首字母）
    pinyin_mapping = {
        "三农": "sannong",
        "二次元": "erciyan",
        "健康": "jiankang",
        "兴趣爱好": "xingquaihao",
        "其他": "qita",
        "医疗健康": "yiliaojiankang",
        "娱乐": "yule",
        "家居家装": "jiajujiazhuang",
        "幽默搞笑": "youmogaoxiao",
        "影视综艺": "yingshizongyi",
        "情感心理": "qingganxinli",
        "才艺技能": "caiyijineng",
        "教育培训": "jiaoyupeixun",
        "文化": "wenhua",
        "旅游": "lvyou",
        "时事资讯": "shishizixun",
        "时尚": "shishang",
        "母婴育儿": "muyingyuer",
        "汽车": "qiche",
        "游戏": "youxi",
        "生活": "shenghuo",
        "科学科普": "kexueKepu",
        "科技": "keji",
        "美妆": "meizhuang",
        "美容个护": "meironggenghu",
        "美食": "meishi",
        "职场": "zhichang",
        "萌宠": "mengchong",
        "财经": "caijing",
        "运动健身": "yundongjianshen",
        "音乐": "yinyue",
        "颜值": "yanzhi"
    }
    
    # 获取所有有效的类别
    valid_categories = list(DOUYIN_FUNCTIONS.keys())
    
    # 按拼音排序
    valid_categories.sort(key=lambda x: pinyin_mapping.get(x, x))
    
    return valid_categories

def get_platforms() -> List[str]:
    """
    获取所有支持的平台
    :return: 平台列表
    """
    return ["抖音", "小红书", "B站", "快手"]

def get_follower_breakpoints() -> List[float]:
    """
    获取所有标签的粉丝数断点
    :return: 粉丝数列表
    """
    # 提取第一个函数的断点作为示例
    first_category = list(DOUYIN_FUNCTIONS.keys())[0]
    segments = DOUYIN_FUNCTIONS[first_category].segments
    
    # 只提取粉丝数断点
    breakpoints = [segments[0][0]]  # 第一个区间的起点
    for segment in segments:
        breakpoints.append(segment[1])  # 每个区间的终点
    
    return breakpoints
