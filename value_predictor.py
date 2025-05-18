import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Optional
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class BloggerValuePredictor:
    def __init__(self):
        # 平台参数配置：增速系数k, 广告条数系数beta, 粉丝上限fan_limit(万)
        self.platform_params = {
            "抖音": {"k": 0.75, "beta": 1.2, "fan_limit": 500},
            "小红书": {"k": 0.65, "beta": 1.0, "fan_limit": 300},
            "B站": {"k": 0.55, "beta": 0.8, "fan_limit": 200},
            "快手": {"k": 0.45, "beta": 0.6, "fan_limit": 400}
        }
        
        # 完整32个标签参数：[增速修正α, 广告条数系数γ, 单价增长系数δ]
        self.label_params = {
            "三农": [0.45, 1.2, 0.6],
            "二次元": [0.50, 1.4, 0.7],
            "健康": [0.30, 0.8, 0.4],
            "兴趣爱好": [0.35, 0.9, 0.5],
            "其他": [0.25, 0.6, 0.3],
            "医疗健康": [0.32, 0.7, 0.5],
            "娱乐": [0.40, 1.1, 0.6],
            "家居家装": [0.38, 1.3, 0.7],
            "幽默搞笑": [0.42, 1.0, 0.5],
            "影视综艺": [0.35, 1.1, 0.6],
            "情感心理": [0.36, 1.0, 0.6],
            "才艺技能": [0.37, 1.1, 0.6],
            "教育培训": [0.33, 0.9, 0.5],
            "文化": [0.34, 0.9, 0.5],
            "旅游": [0.39, 1.2, 0.7],
            "时事资讯": [0.30, 0.7, 0.4],
            "时尚": [0.43, 1.5, 0.8],
            "母婴育儿": [0.40, 1.4, 0.7],
            "汽车": [0.38, 1.3, 0.8],
            "游戏": [0.45, 1.3, 0.7],
            "生活": [0.36, 1.0, 0.6],
            "科学科普": [0.35, 1.1, 0.6],
            "科技": [0.42, 1.4, 0.9],
            "美妆": [0.48, 1.6, 0.9],
            "美容个护": [0.45, 1.5, 0.8],
            "美食": [0.44, 1.4, 0.7],
            "职场": [0.37, 1.0, 0.6],
            "萌宠": [0.41, 1.2, 0.6],
            "财经": [0.39, 1.3, 0.8],
            "运动健身": [0.40, 1.2, 0.7],
            "音乐": [0.38, 1.1, 0.6],
            "颜值": [0.46, 1.3, 0.8]
        }
        
        # 标签颜色映射（用于可视化）
        self.label_colors = {
            "美妆": "#FF69B4", "科技": "#4169E1", "三农": "#228B22",
            "时尚": "#FF1493", "母婴育儿": "#FFA07A", "其他": "#808080",
            "二次元": "#9370DB", "游戏": "#20B2AA", "财经": "#DAA520"
        }

    def get_single_ad_value(self, platform: str, label: str, fans: float) -> float:
        """估算单条广告报价（单位：万元）"""
        if label not in self.label_params:
            raise ValueError(f"无效标签！可选: {list(self.label_params.keys())}")
        gamma = self.label_params[label][1]
        base_value = 0.1 * np.sqrt(fans) * gamma  # 基础报价公式，用万为单位
        return round(base_value, 2)

    def predict_value(
        self,
        fans: float,
        platform: str,
        label: str,
        single_ad_value: Optional[float] = None,
        years: List[int] = [1, 2, 3, 4, 5],
        growth_rate: Optional[float] = None  # 新增粉丝增长率参数（年度百分比）
    ) -> List[Tuple[int, float, int, float]]:
        """
        预测商业价值
        参数:
            fans: 当前粉丝数（万）
            platform: 平台名称
            label: 内容标签
            single_ad_value: 单条广告报价（万元，可选）
            years: 预测年份列表
            growth_rate: 自定义年度粉丝增长率（百分比，如20表示20%），默认为None使用模型内置增长算法
        返回:
            [(年份, 粉丝数(万), 年广告条数, 年收益(万元))]
        """
        # 参数校验
        if platform not in self.platform_params:
            raise ValueError(f"无效平台！可选: {list(self.platform_params.keys())}")
        if label not in self.label_params:
            raise ValueError(f"无效标签！可选: {list(self.label_params.keys())}")

        # 获取参数
        k = self.platform_params[platform]["k"]
        beta = self.platform_params[platform]["beta"]
        fan_limit = self.platform_params[platform]["fan_limit"]
        alpha, gamma, delta = self.label_params[label]
        
        # 处理广告报价
        if single_ad_value is None:
            # 将粉丝数转换为万为单位
            fans_in_wan = fans / 10000
            single_ad_value = self.get_single_ad_value(platform, label, fans_in_wan)
        
        # 确保fans是以万为单位进行计算
        fans_in_wan = fans / 10000

        results = []
        current_fans = fans_in_wan  # 当前粉丝数，用于自定义增长率计算
        
        for year in years:
            if growth_rate is not None:
                # 使用用户自定义增长率 - 使用复合指数计算
                # 公式: 初始粉丝数 * (1 + 增长率/100)^年数
                ft = current_fans * ((1 + growth_rate/100) ** year)
            else:
                # 使用默认的粉丝增长模型（无上限）
                ft = fans_in_wan + k * np.log(year + 1) * (1 + alpha)
            
            # 使用硬编码的矩阵数据获取广告条数
            # 创建一个临时矩阵生成器
            temp_matrix = AdMatrixGenerator()
            nt = temp_matrix.get_expected_ad_count(platform, label, ft)
            
            # 广告单价增长
            pt = single_ad_value * (1 + (ft - fans_in_wan) / fans_in_wan * delta)
            
            # 总收益（广告+20%其他收入）
            vt = nt * pt * 1.2  # 单位：万元
            
            results.append((year, round(ft, 2), nt, round(vt, 2)))
        
        return results

    def create_growth_visualization(
        self,
        fans: float,
        platform: str,
        label: str,
        single_ad_value: float,
        growth_rate: Optional[float] = None
    ) -> go.Figure:
        """生成plotly可视化图表 - 优化版，显示1-5年完整数据，针对移动设备优化"""
        # 将粉丝数转换为万人
        fans_in_wan = fans / 10000
        
        # 统一获取1-5年的预测数据
        data = self.predict_value(fans, platform, label, single_ad_value, years=[1, 2, 3, 4, 5], growth_rate=growth_rate)
        years = [x[0] for x in data]
        fan_growth = [x[1] for x in data]
        ad_counts = [x[2] for x in data]
        income_growth = [x[3] for x in data]
        
        # 计算5年总价值
        total_value = sum(x[3] for x in data)
        
        # 获取对应的颜色，默认为蓝色
        color = self.label_colors.get(label, "#1E90FF")
        
        # 创建子图 - 移动端友好的纵向排列，进一步简化标题，减少重叠
        fig = make_subplots(
            rows=4, cols=1,
            subplot_titles=(
                "粉丝趋势(万)", 
                "年收益(万元)",
                "广告条数",
                "五年总价值"
            ),
            specs=[
                [{"type": "scatter"}],
                [{"type": "bar"}],
                [{"type": "bar"}],
                [{"type": "indicator"}]
            ],
            row_heights=[0.22, 0.22, 0.22, 0.34],
            vertical_spacing=0.15,  # 进一步增加间距避免重叠
        )
        
        # 1. 粉丝增长曲线 (第一行)
        fig.add_trace(
            go.Scatter(
                x=years, 
                y=fan_growth, 
                mode="lines+markers",
                name="粉丝数(万)",
                line=dict(color=color, width=3),
                marker=dict(size=8),
                hovertemplate="第%{x}年: %{y:.2f}万粉丝<extra></extra>"  # 强制保留两位小数
            ),
            row=1, col=1
        )
        
        # 添加起始粉丝数标记点 - 调整位置，避免重叠
        # 格式化粉丝数显示
        start_fans_display = f"{int(fan_growth[0])}" if fan_growth[0] == int(fan_growth[0]) else f"{fan_growth[0]:.2f}".rstrip('0').rstrip('.')
        
        fig.add_annotation(
            x=1, y=fan_growth[0],
            text=f"起始: {start_fans_display}万",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color,
            arrowwidth=1.5,
            ax=-40, ay=-40,  # 调整箭头位置
            font=dict(color="white", size=10),
            row=1, col=1
        )
        
        # 添加最终粉丝数标记点 - 调整位置，避免重叠
        # 格式化粉丝数显示
        end_fans_display = f"{int(fan_growth[-1])}" if fan_growth[-1] == int(fan_growth[-1]) else f"{fan_growth[-1]:.2f}".rstrip('0').rstrip('.')
        
        fig.add_annotation(
            x=5, y=fan_growth[-1],
            text=f"第5年: {end_fans_display}万",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color,
            arrowwidth=1.5,
            ax=40, ay=-40,  # 调整箭头位置
            font=dict(color="white", size=10),
            row=1, col=1
        )
        
        # 2. 收益增长条形图 (第二行)
        # 格式化收入显示
        income_text = []
        for v in income_growth:
            if v == int(v):
                income_text.append(f"{int(v)}万")
            else:
                income_text.append(f"{v:.2f}".rstrip('0').rstrip('.') + "万")
                
        fig.add_trace(
            go.Bar(
                x=[str(y) for y in years], 
                y=income_growth,
                name="年收益(万元)",
                marker_color=color,
                text=income_text,
                textposition="auto",  # 改为auto，让plotly自动调整文本位置
                textangle=0,  # 水平文本
                textfont=dict(size=12),  # 调整文本大小
                hovertemplate="第%{x}年: %{y:.2f}万元<extra></extra>"
            ),
            row=2, col=1
        )
        
        # 3. 广告条数图表 (第三行)
        fig.add_trace(
            go.Bar(
                x=[str(y) for y in years], 
                y=ad_counts,
                name="年广告条数",
                marker_color="rgba(255, 193, 7, 0.8)",
                text=[f"{v}条" for v in ad_counts],
                textposition="auto",  # 改为auto，让plotly自动调整文本位置
                textangle=0,  # 水平文本
                textfont=dict(size=12),  # 调整文本大小
                hovertemplate="第%{x}年: %{y}条广告<extra></extra>"
            ),
            row=3, col=1
        )
        
        # 4. 累计商业价值指示器 (第四行)
        fig.add_trace(
            go.Indicator(
                mode="number+delta",
                value=total_value,
                number={"prefix": "¥", "suffix": "万元", "font": {"size": 48, "color": "white"}},
                title={"text": "5年总商业价值", "font": {"size": 16, "color": "white"}},
                delta={"reference": income_growth[0] * 5, "relative": True, "valueformat": ".1%"},
                domain={"row": 3, "column": 0}
            ),
            row=4, col=1
        )
        
        # 更新布局
        # 标题根据是否有自定义增长率而变化 - 简化标题内容，减少重叠可能性
        
        # 格式化粉丝数
        fans_formatted = f"{int(fans_in_wan)}" if fans_in_wan == int(fans_in_wan) else f"{fans_in_wan:.2f}".rstrip('0').rstrip('.')
        # 格式化单价
        price_formatted = f"{int(single_ad_value)}" if single_ad_value == int(single_ad_value) else f"{single_ad_value:.2f}".rstrip('0').rstrip('.')
        
        title_text = f"{platform}·{label} 达人价值预测<br><span style='font-size:14px'>初始粉丝: {fans_formatted}万 | 单价: {price_formatted}万元"
        if growth_rate is not None:
            title_text += f" | 年增长率: {int(growth_rate)}%</span>"
        else:
            title_text += "</span>"
            
        fig.update_layout(
            title={
                'text': title_text,
                'font': {'size': 20},
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', family="Arial, sans-serif"),
            height=980,  # 进一步增加高度，确保子图之间有充足间距
            showlegend=False,
            autosize=True,  # 自动调整大小
            margin=dict(l=10, r=10, t=100, b=40),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
            grid=dict(rows=4, columns=1, pattern='independent', roworder='top to bottom', ygap=0.15)  # 增加子图间距
        )
        
        # 更新X轴和Y轴 - 针对纵向布局调整
        for i in range(1, 4):  # 1,2,3行（第4行是指示器）
            fig.update_xaxes(
                title_text="预测年份",
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
            fig.update_yaxes(
                gridcolor='rgba(255,255,255,0.1)',
                row=i, col=1
            )
        
        return fig
    
    def create_summary_table(
        self,
        fans: float,
        platform: str,
        label: str,
        single_ad_value: float,
        growth_rate: Optional[float] = None
    ) -> Dict:
        """创建预测结果汇总表 - 优化版，显示1-5年完整数据和总价值"""
        # 将粉丝数转换为万人单位
        fans_in_wan = fans / 10000
        
        # 统一获取1-5年的预测数据
        results = self.predict_value(fans, platform, label, single_ad_value, years=[1, 2, 3, 4, 5], growth_rate=growth_rate)
        
        # 计算5年总价值
        total_value = sum(r[3] for r in results)
        
        # 格式化为表格数据
        years = [f"第{r[0]}年" for r in results]
        
        # 格式化粉丝数，保留两位小数
        fans_data = []
        for r in results:
            if r[1] == int(r[1]):
                fans_data.append(f"{int(r[1])}万")  # 整数显示
            else:
                fans_data.append(f"{r[1]:.2f}万")  # 强制保留两位小数
        
        # 广告条数
        ad_counts = [f"{r[2]}条" for r in results]
        
        # 格式化收入，保留两位小数
        income_data = []
        for r in results:
            if r[3] == int(r[3]):
                income_data.append(f"{int(r[3])}万元")  # 整数显示
            else:
                income_data.append(f"{r[3]:.2f}万元")  # 强制保留两位小数
        
        # 添加总计行
        years.append("五年总计")
        
        # 格式化最终粉丝数
        if results[-1][1] == int(results[-1][1]):
            fans_data.append(f"{int(results[-1][1])}万")  # 整数显示
        else:
            fans_data.append(f"{results[-1][1]:.2f}万")  # 强制保留两位小数
            
        total_ads = sum(r[2] for r in results)
        ad_counts.append(f"{total_ads}条")
        
        # 格式化总价值
        if total_value == int(total_value):
            income_data.append(f"{int(total_value)}万元")  # 整数显示
        else:
            income_data.append(f"{total_value:.2f}万元")  # 强制保留两位小数
        
        return {
            "years": years,
            "fans": fans_data,
            "ad_counts": ad_counts,
            "income": income_data,
            "total_value": round(total_value, 2)  # 单独返回总价值，方便其他地方调用
        }


class AdMatrixGenerator:
    """广告条数矩阵生成器"""
    def __init__(self):
        # 粉丝量级划分
        self.fan_ranges = [
            "1-10万", "10-50万", "50-100万", 
            "100-500万", "500-1000万", "1000万+"
        ]
        
        # 平台列表
        self.platforms = ["抖音", "小红书", "B站", "快手"]
        
        # 完整32标签列表
        self.labels = [
            "三农", "二次元", "健康", "兴趣爱好", "其他",
            "医疗健康", "娱乐", "家居家装", "幽默搞笑", "影视综艺",
            "情感心理", "才艺技能", "教育培训", "文化", "旅游",
            "时事资讯", "时尚", "母婴育儿", "汽车", "游戏",
            "生活", "科学科普", "科技", "美妆", "美容个护",
            "美食", "职场", "萌宠", "财经", "运动健身",
            "音乐", "颜值"
        ]
        
        # 生成矩阵并缓存
        self._matrix = self.generate_matrix()

    def generate_matrix(self) -> pd.DataFrame:
        """生成完整广告条数矩阵"""
        # 使用2023年行业数据定义的硬编码矩阵值
        
        # 抖音矩阵
        douyin_matrix = {
            "1-10万": {
                "三农": 8, "二次元": 5, "健康": 6, "兴趣爱好": 7, "其他": 4,
                "医疗健康": 5, "娱乐": 12, "家居家装": 8, "幽默搞笑": 15, "影视综艺": 9,
                "情感心理": 12, "才艺技能": 9, "教育培训": 5, "文化": 6, "旅游": 9,
                "时事资讯": 5, "时尚": 20, "母婴育儿": 12, "汽车": 6, "游戏": 8,
                "生活": 15, "科学科普": 5, "科技": 8, "美妆": 22, "美容个护": 18,
                "美食": 15, "职场": 6, "萌宠": 12, "财经": 5, "运动健身": 9,
                "音乐": 10, "颜值": 15
            },
            "10-50万": {
                "三农": 12, "二次元": 8, "健康": 9, "兴趣爱好": 10, "其他": 6,
                "医疗健康": 8, "娱乐": 22, "家居家装": 12, "幽默搞笑": 30, "影视综艺": 15,
                "情感心理": 18, "才艺技能": 15, "教育培训": 8, "文化": 9, "旅游": 15,
                "时事资讯": 8, "时尚": 38, "母婴育儿": 18, "汽车": 9, "游戏": 12,
                "生活": 30, "科学科普": 8, "科技": 12, "美妆": 45, "美容个护": 38,
                "美食": 30, "职场": 9, "萌宠": 18, "财经": 8, "运动健身": 15,
                "音乐": 18, "颜值": 30
            },
            "50-100万": {
                "三农": 18, "二次元": 13, "健康": 15, "兴趣爱好": 16, "其他": 10,
                "医疗健康": 12, "娱乐": 45, "家居家装": 18, "幽默搞笑": 60, "影视综艺": 30,
                "情感心理": 38, "才艺技能": 22, "教育培训": 12, "文化": 15, "旅游": 30,
                "时事资讯": 12, "时尚": 75, "母婴育儿": 38, "汽车": 15, "游戏": 18,
                "生活": 60, "科学科普": 12, "科技": 18, "美妆": 90, "美容个护": 75,
                "美食": 60, "职场": 15, "萌宠": 38, "财经": 12, "运动健身": 30,
                "音乐": 38, "颜值": 60
            },
            "100-500万": {
                "三农": 35, "二次元": 20, "健康": 22, "兴趣爱好": 25, "其他": 15,
                "医疗健康": 20, "娱乐": 90, "家居家装": 35, "幽默搞笑": 120, "影视综艺": 60,
                "情感心理": 75, "才艺技能": 38, "教育培训": 22, "文化": 22, "旅游": 60,
                "时事资讯": 20, "时尚": 150, "母婴育儿": 75, "汽车": 22, "游戏": 35,
                "生活": 120, "科学科普": 18, "科技": 35, "美妆": 180, "美容个护": 150,
                "美食": 120, "职场": 22, "萌宠": 75, "财经": 18, "运动健身": 60,
                "音乐": 75, "颜值": 120
            },
            "500-1000万": {
                "三农": 55, "二次元": 35, "健康": 38, "兴趣爱好": 40, "其他": 25,
                "医疗健康": 35, "娱乐": 150, "家居家装": 55, "幽默搞笑": 230, "影视综艺": 120,
                "情感心理": 150, "才艺技能": 75, "教育培训": 38, "文化": 38, "旅游": 120,
                "时事资讯": 35, "时尚": 300, "母婴育儿": 150, "汽车": 38, "游戏": 55,
                "生活": 230, "科学科普": 35, "科技": 55, "美妆": 370, "美容个护": 300,
                "美食": 230, "职场": 38, "萌宠": 150, "财经": 35, "运动健身": 120,
                "音乐": 150, "颜值": 230
            },
            "1000万+": {
                "三农": 80, "二次元": 50, "健康": 60, "兴趣爱好": 65, "其他": 40,
                "医疗健康": 55, "娱乐": 220, "家居家装": 80, "幽默搞笑": 300, "影视综艺": 180,
                "情感心理": 200, "才艺技能": 110, "教育培训": 50, "文化": 60, "旅游": 150,
                "时事资讯": 50, "时尚": 400, "母婴育儿": 200, "汽车": 50, "游戏": 80,
                "生活": 280, "科学科普": 50, "科技": 80, "美妆": 500, "美容个护": 450,
                "美食": 350, "职场": 50, "萌宠": 200, "财经": 50, "运动健身": 150,
                "音乐": 200, "颜值": 300
            }
        }
        
        # 小红书矩阵
        xiaohongshu_matrix = {
            "1-10万": {
                "三农": 5, "二次元": 3, "健康": 6, "兴趣爱好": 5, "其他": 3,
                "医疗健康": 5, "娱乐": 8, "家居家装": 9, "幽默搞笑": 6, "影视综艺": 5,
                "情感心理": 9, "才艺技能": 6, "教育培训": 5, "文化": 5, "旅游": 12,
                "时事资讯": 4, "时尚": 22, "母婴育儿": 15, "汽车": 5, "游戏": 4,
                "生活": 12, "科学科普": 4, "科技": 6, "美妆": 30, "美容个护": 22,
                "美食": 18, "职场": 5, "萌宠": 9, "财经": 4, "运动健身": 12,
                "音乐": 8, "颜值": 18
            },
            "10-50万": {
                "三农": 9, "二次元": 6, "健康": 12, "兴趣爱好": 8, "其他": 5,
                "医疗健康": 9, "娱乐": 15, "家居家装": 18, "幽默搞笑": 12, "影视综艺": 9,
                "情感心理": 18, "才艺技能": 12, "教育培训": 9, "文化": 9, "旅游": 22,
                "时事资讯": 6, "时尚": 45, "母婴育儿": 30, "汽车": 9, "游戏": 6,
                "生活": 22, "科学科普": 6, "科技": 12, "美妆": 60, "美容个护": 45,
                "美食": 38, "职场": 9, "萌宠": 18, "财经": 6, "运动健身": 22,
                "音乐": 15, "颜值": 38
            },
            "50-100万": {
                "三农": 15, "二次元": 10, "健康": 20, "兴趣爱好": 12, "其他": 8,
                "医疗健康": 15, "娱乐": 25, "家居家装": 30, "幽默搞笑": 20, "影视综艺": 15,
                "情感心理": 30, "才艺技能": 20, "教育培训": 15, "文化": 15, "旅游": 38,
                "时事资讯": 10, "时尚": 75, "母婴育儿": 55, "汽车": 15, "游戏": 10,
                "生活": 38, "科学科普": 10, "科技": 20, "美妆": 100, "美容个护": 75,
                "美食": 60, "职场": 15, "萌宠": 30, "财经": 10, "运动健身": 38,
                "音乐": 25, "颜值": 60
            },
            "100-500万": {
                "三农": 25, "二次元": 15, "健康": 35, "兴趣爱好": 20, "其他": 12,
                "医疗健康": 25, "娱乐": 45, "家居家装": 55, "幽默搞笑": 35, "影视综艺": 25,
                "情感心理": 55, "才艺技能": 35, "教育培训": 25, "文化": 25, "旅游": 75,
                "时事资讯": 15, "时尚": 150, "母婴育儿": 90, "汽车": 25, "游戏": 15,
                "生活": 75, "科学科普": 15, "科技": 35, "美妆": 200, "美容个护": 150,
                "美食": 120, "职场": 25, "萌宠": 55, "财经": 15, "运动健身": 75,
                "音乐": 45, "颜值": 120
            },
            "500-1000万": {
                "三农": 40, "二次元": 25, "健康": 60, "兴趣爱好": 35, "其他": 20,
                "医疗健康": 40, "娱乐": 80, "家居家装": 90, "幽默搞笑": 60, "影视综艺": 40,
                "情感心理": 90, "才艺技能": 60, "教育培训": 40, "文化": 40, "旅游": 120,
                "时事资讯": 25, "时尚": 250, "母婴育儿": 150, "汽车": 40, "游戏": 25,
                "生活": 120, "科学科普": 25, "科技": 60, "美妆": 350, "美容个护": 250,
                "美食": 200, "职场": 40, "萌宠": 90, "财经": 25, "运动健身": 120,
                "音乐": 80, "颜值": 200
            },
            "1000万+": {
                "三农": 60, "二次元": 40, "健康": 90, "兴趣爱好": 55, "其他": 30,
                "医疗健康": 60, "娱乐": 120, "家居家装": 130, "幽默搞笑": 90, "影视综艺": 60,
                "情感心理": 130, "才艺技能": 90, "教育培训": 60, "文化": 60, "旅游": 180,
                "时事资讯": 40, "时尚": 350, "母婴育儿": 220, "汽车": 60, "游戏": 40,
                "生活": 180, "科学科普": 40, "科技": 90, "美妆": 500, "美容个护": 380,
                "美食": 300, "职场": 60, "萌宠": 130, "财经": 40, "运动健身": 180,
                "音乐": 120, "颜值": 300
            }
        }
        
        # B站矩阵
        bilibili_matrix = {
            "1-10万": {
                "三农": 4, "二次元": 8, "健康": 5, "兴趣爱好": 6, "其他": 3,
                "医疗健康": 5, "娱乐": 6, "家居家装": 5, "幽默搞笑": 7, "影视综艺": 6,
                "情感心理": 5, "才艺技能": 6, "教育培训": 5, "文化": 6, "旅游": 8,
                "时事资讯": 4, "时尚": 12, "母婴育儿": 6, "汽车": 5, "游戏": 10,
                "生活": 7, "科学科普": 6, "科技": 8, "美妆": 15, "美容个护": 12,
                "美食": 10, "职场": 5, "萌宠": 7, "财经": 5, "运动健身": 8,
                "音乐": 7, "颜值": 10
            },
            "10-50万": {
                "三农": 7, "二次元": 15, "健康": 9, "兴趣爱好": 10, "其他": 5,
                "医疗健康": 8, "娱乐": 12, "家居家装": 9, "幽默搞笑": 12, "影视综艺": 12,
                "情感心理": 9, "才艺技能": 12, "教育培训": 9, "文化": 12, "旅游": 15,
                "时事资讯": 6, "时尚": 22, "母婴育儿": 12, "汽车": 9, "游戏": 18,
                "生活": 12, "科学科普": 12, "科技": 15, "美妆": 30, "美容个护": 22,
                "美食": 18, "职场": 9, "萌宠": 12, "财经": 9, "运动健身": 15,
                "音乐": 12, "颜值": 18
            },
            "50-100万": {
                "三农": 12, "二次元": 25, "健康": 15, "兴趣爱好": 16, "其他": 8,
                "医疗健康": 12, "娱乐": 20, "家居家装": 15, "幽默搞笑": 20, "影视综艺": 20,
                "情感心理": 15, "才艺技能": 20, "教育培训": 15, "文化": 20, "旅游": 25,
                "时事资讯": 10, "时尚": 38, "母婴育儿": 20, "汽车": 15, "游戏": 30,
                "生活": 20, "科学科普": 20, "科技": 25, "美妆": 55, "美容个护": 38,
                "美食": 30, "职场": 15, "萌宠": 20, "财经": 15, "运动健身": 25,
                "音乐": 20, "颜值": 30
            },
            "100-500万": {
                "三农": 20, "二次元": 45, "健康": 25, "兴趣爱好": 25, "其他": 12,
                "医疗健康": 20, "娱乐": 35, "家居家装": 25, "幽默搞笑": 35, "影视综艺": 35,
                "情感心理": 25, "才艺技能": 35, "教育培训": 25, "文化": 35, "旅游": 45,
                "时事资讯": 15, "时尚": 75, "母婴育儿": 35, "汽车": 25, "游戏": 55,
                "生活": 35, "科学科普": 35, "科技": 45, "美妆": 90, "美容个护": 75,
                "美食": 55, "职场": 25, "萌宠": 35, "财经": 25, "运动健身": 45,
                "音乐": 35, "颜值": 55
            },
            "500-1000万": {
                "三农": 30, "二次元": 70, "健康": 40, "兴趣爱好": 40, "其他": 20,
                "医疗健康": 35, "娱乐": 60, "家居家装": 40, "幽默搞笑": 60, "影视综艺": 60,
                "情感心理": 40, "才艺技能": 60, "教育培训": 40, "文化": 60, "旅游": 70,
                "时事资讯": 25, "时尚": 120, "母婴育儿": 60, "汽车": 40, "游戏": 90,
                "生活": 60, "科学科普": 60, "科技": 70, "美妆": 150, "美容个护": 120,
                "美食": 90, "职场": 40, "萌宠": 60, "财经": 40, "运动健身": 70,
                "音乐": 60, "颜值": 90
            },
            "1000万+": {
                "三农": 50, "二次元": 100, "健康": 60, "兴趣爱好": 65, "其他": 30,
                "医疗健康": 55, "娱乐": 90, "家居家装": 60, "幽默搞笑": 90, "影视综艺": 90,
                "情感心理": 60, "才艺技能": 90, "教育培训": 60, "文化": 90, "旅游": 100,
                "时事资讯": 40, "时尚": 180, "母婴育儿": 90, "汽车": 60, "游戏": 130,
                "生活": 90, "科学科普": 90, "科技": 100, "美妆": 220, "美容个护": 180,
                "美食": 130, "职场": 60, "萌宠": 90, "财经": 60, "运动健身": 100,
                "音乐": 90, "颜值": 130
            }
        }
        
        # 快手矩阵
        kuaishou_matrix = {
            "1-10万": {
                "三农": 10, "二次元": 6, "健康": 8, "兴趣爱好": 7, "其他": 5,
                "医疗健康": 6, "娱乐": 15, "家居家装": 8, "幽默搞笑": 18, "影视综艺": 10,
                "情感心理": 12, "才艺技能": 10, "教育培训": 6, "文化": 8, "旅游": 12,
                "时事资讯": 5, "时尚": 22, "母婴育儿": 15, "汽车": 8, "游戏": 10,
                "生活": 15, "科学科普": 6, "科技": 8, "美妆": 25, "美容个护": 20,
                "美食": 18, "职场": 8, "萌宠": 12, "财经": 6, "运动健身": 12,
                "音乐": 10, "颜值": 18
            },
            "10-50万": {
                "三农": 18, "二次元": 12, "健康": 15, "兴趣爱好": 12, "其他": 8,
                "医疗健康": 10, "娱乐": 30, "家居家装": 15, "幽默搞笑": 38, "影视综艺": 18,
                "情感心理": 22, "才艺技能": 18, "教育培训": 12, "文化": 15, "旅游": 22,
                "时事资讯": 8, "时尚": 45, "母婴育儿": 30, "汽车": 15, "游戏": 18,
                "生活": 30, "科学科普": 12, "科技": 15, "美妆": 50, "美容个护": 40,
                "美食": 38, "职场": 15, "萌宠": 22, "财经": 12, "运动健身": 22,
                "音乐": 18, "颜值": 38
            },
            "50-100万": {
                "三农": 30, "二次元": 20, "健康": 25, "兴趣爱好": 20, "其他": 12,
                "医疗健康": 16, "娱乐": 55, "家居家装": 25, "幽默搞笑": 60, "影视综艺": 30,
                "情感心理": 38, "才艺技能": 30, "教育培训": 20, "文化": 25, "旅游": 38,
                "时事资讯": 12, "时尚": 75, "母婴育儿": 55, "汽车": 25, "游戏": 30,
                "生活": 55, "科学科普": 20, "科技": 25, "美妆": 90, "美容个护": 75,
                "美食": 60, "职场": 25, "萌宠": 38, "财经": 20, "运动健身": 38,
                "音乐": 30, "颜值": 60
            },
            "100-500万": {
                "三农": 60, "二次元": 35, "健康": 45, "兴趣爱好": 35, "其他": 20,
                "医疗健康": 25, "娱乐": 90, "家居家装": 45, "幽默搞笑": 120, "影视综艺": 60,
                "情感心理": 75, "才艺技能": 60, "教育培训": 35, "文化": 45, "旅游": 75,
                "时事资讯": 20, "时尚": 150, "母婴育儿": 90, "汽车": 45, "游戏": 60,
                "生活": 90, "科学科普": 35, "科技": 45, "美妆": 180, "美容个护": 150,
                "美食": 120, "职场": 45, "萌宠": 75, "财经": 35, "运动健身": 75,
                "音乐": 60, "颜值": 120
            },
            "500-1000万": {
                "三农": 100, "二次元": 60, "健康": 80, "兴趣爱好": 60, "其他": 35,
                "医疗健康": 40, "娱乐": 150, "家居家装": 80, "幽默搞笑": 200, "影视综艺": 100,
                "情感心理": 120, "才艺技能": 100, "教育培训": 60, "文化": 80, "旅游": 120,
                "时事资讯": 35, "时尚": 250, "母婴育儿": 150, "汽车": 80, "游戏": 100,
                "生活": 150, "科学科普": 60, "科技": 80, "美妆": 300, "美容个护": 250,
                "美食": 200, "职场": 80, "萌宠": 120, "财经": 60, "运动健身": 120,
                "音乐": 100, "颜值": 200
            },
            "1000万+": {
                "三农": 150, "二次元": 90, "健康": 120, "兴趣爱好": 90, "其他": 55,
                "医疗健康": 65, "娱乐": 220, "家居家装": 120, "幽默搞笑": 300, "影视综艺": 150,
                "情感心理": 180, "才艺技能": 150, "教育培训": 90, "文化": 120, "旅游": 180,
                "时事资讯": 55, "时尚": 350, "母婴育儿": 220, "汽车": 120, "游戏": 150,
                "生活": 220, "科学科普": 90, "科技": 120, "美妆": 450, "美容个护": 380,
                "美食": 300, "职场": 120, "萌宠": 180, "财经": 90, "运动健身": 180,
                "音乐": 150, "颜值": 300
            }
        }
        
        # 创建数据列表
        data = []
        
        # 抖音数据
        for fan_range, fan_data in douyin_matrix.items():
            row = {"粉丝量级": fan_range, "平台": "抖音"}
            for label, value in fan_data.items():
                row[label] = str(value)
            data.append(row)
        
        # 小红书数据
        for fan_range, fan_data in xiaohongshu_matrix.items():
            row = {"粉丝量级": fan_range, "平台": "小红书"}
            for label, value in fan_data.items():
                row[label] = str(value)
            data.append(row)
            
        # B站数据
        for fan_range, fan_data in bilibili_matrix.items():
            row = {"粉丝量级": fan_range, "平台": "B站"}
            for label, value in fan_data.items():
                row[label] = str(value)
            data.append(row)
            
        # 快手数据
        for fan_range, fan_data in kuaishou_matrix.items():
            row = {"粉丝量级": fan_range, "平台": "快手"}
            for label, value in fan_data.items():
                row[label] = str(value)
            data.append(row)
        
        return pd.DataFrame(data)
    
    def get_fan_range(self, fans: float) -> str:
        """根据粉丝数（万）获取对应的范围区间"""
        if fans < 10:
            return "1-10万"
        elif fans < 50:
            return "10-50万"
        elif fans < 100:
            return "50-100万"
        elif fans < 500:
            return "100-500万"
        elif fans < 1000:
            return "500-1000万"
        else:
            return "1000万+"
    
    def get_expected_ad_count(self, platform: str, label: str, fans: float) -> int:
        """获取同量级平均广告条数"""
        fan_range = self.get_fan_range(fans)
        
        # 从矩阵中查询
        query_result = self._matrix[
            (self._matrix["粉丝量级"] == fan_range) & 
            (self._matrix["平台"] == platform)
        ]
        
        if query_result.empty:
            return 0
        
        # 获取对应标签的广告条数
        if label in query_result.columns:
            return int(query_result[label].iloc[0])
        else:
            return 0
    
    def calculate_development_ratio(self, platform: str, label: str, fans: float, actual_ads: int) -> float:
        """
        计算商业开发程度（比率）
        
        参数:
            platform: 平台名称
            label: 标签
            fans: 粉丝数（万）
            actual_ads: 实际广告条数
            
        返回:
            开发程度比率（实际广告数/预期广告数）
        """
        expected_ads = self.get_expected_ad_count(platform, label, fans)
        
        if expected_ads == 0:
            return 0
        
        return round(actual_ads / expected_ads, 2)
    
    def create_development_visualization(self, platform: str, label: str, fans: float, actual_ads: int) -> go.Figure:
        """创建商业开发程度可视化 - 完全重构版，只保留仪表盘"""
        # 获取粉丝范围
        fan_range = self.get_fan_range(fans)
        
        # 计算开发程度
        ratio = self.calculate_development_ratio(platform, label, fans, actual_ads)
        # 限制小数点后2位
        ratio_display = round(ratio, 2)
        
        # 根据比率设置颜色和文本
        if ratio < 0.8:
            color = "rgba(255, 87, 51, 0.8)"  # 红色 - 开发不足
            text = "开发不足"
        elif ratio <= 1.2:
            color = "rgba(46, 204, 113, 0.8)"  # 绿色 - 正常水平
            text = "正常水平"
        else:
            color = "rgba(52, 152, 219, 0.8)"  # 蓝色 - 充分开发
            text = "充分开发"
        
        # 只创建单个指示器图表，没有子图
        fig = go.Figure()
        
        # 添加指示器
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=ratio_display,  # 使用保留两位小数的值
                title={
                    "text": f"<b>{platform}·{label}</b><br>商业开发程度<br><span style='font-size:14px'>粉丝量级: {fan_range}</span><br><span style='font-size:14px; color:{color}'>开发状态: {text}</span>",
                    "font": {"size": 18, "color": "white", "family": "Arial, sans-serif"}
                },
                gauge={
                    "axis": {
                        "range": [0, 2], 
                        "tickvals": [0, 0.5, 1, 1.5, 2],
                        "ticktext": ["0", "0.5", "1.0", "1.5", "2.0"],
                        "tickfont": {"size": 12, "color": "white"},
                        "tickwidth": 1,
                        "tickcolor": "white",
                    },
                    "steps": [
                        {"range": [0, 0.8], "color": "rgba(255, 87, 51, 0.4)"},  # 增加透明度
                        {"range": [0.8, 1.2], "color": "rgba(46, 204, 113, 0.4)"},  # 增加透明度
                        {"range": [1.2, 2], "color": "rgba(52, 152, 219, 0.4)"}  # 增加透明度
                    ],
                    "threshold": {
                        "line": {"color": "white", "width": 2},
                        "thickness": 0.75,
                        "value": ratio_display
                    },
                    "bar": {"color": color},
                    "borderwidth": 2,
                    "bordercolor": "white",
                },
                number={
                    "font": {"size": 40, "color": "white", "family": "Arial, sans-serif"}, 
                    "valueformat": ".2f",
                    "prefix": "",
                    "suffix": "x"
                },
                # 通过调整domain，移动数字位置，使其更靠上
                domain={"x": [0, 1], "y": [0.15, 1]}
            )
        )
        
        # 更新布局
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='white',
                family="Arial, sans-serif"  # 设置默认字体
            ),
            height=320,  # 略微增加高度，为标题提供更多空间
            margin=dict(l=20, r=20, t=110, b=40),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
            annotations=[
                dict(
                    text=f"预期广告数: {self.get_expected_ad_count(platform, label, fans)}条 | 实际广告数: {actual_ads}条",
                    x=0.5,
                    y=0.1,  # 将y值从0调整为0.1，向上移动，避免与底部数字重叠
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=13, color="rgba(255,255,255,0.8)")
                )
            ]
        )
        
        return fig
        
    def create_ad_comparison_chart(self, platform: str, label: str, fans: float, actual_ads: int) -> go.Figure:
        """创建广告条数对比图表 - 分离出来的单独图表"""
        # 计算期望广告数
        expected_ads = self.get_expected_ad_count(platform, label, fans)
        
        # 计算开发程度
        ratio = self.calculate_development_ratio(platform, label, fans, actual_ads)
        
        # 根据比率设置颜色
        if ratio < 0.8:
            color = "rgba(255, 87, 51, 0.8)"  # 红色
        elif ratio <= 1.2:
            color = "rgba(46, 204, 113, 0.8)"  # 绿色
        else:
            color = "rgba(52, 152, 219, 0.8)"  # 蓝色
            
        # 创建柱状图
        fig = go.Figure()
        
        # 添加预期广告条数
        fig.add_trace(
            go.Bar(
                x=["行业平均"],
                y=[expected_ads],
                name="行业平均水平",
                marker=dict(
                    color="rgba(189, 195, 199, 0.9)",  # 增加不透明度
                    line=dict(width=1, color='rgba(255,255,255,0.3)')  # 添加细微边框
                ),
                text=[f"{expected_ads}条"],
                textposition="auto",
                textfont=dict(
                    color='white',  # 确保文本为白色
                    size=14,        # 增大字体大小
                    family="Arial, sans-serif"  # 使用清晰的字体
                ),
                width=0.4,
                hovertemplate="行业平均: %{y}条<extra></extra>"
            )
        )
        
        # 添加实际广告条数
        fig.add_trace(
            go.Bar(
                x=["实际承接"],
                y=[actual_ads],
                name="实际承接数量",
                marker=dict(
                    color=color,
                    line=dict(width=1, color='rgba(255,255,255,0.3)')  # 添加细微边框
                ),
                text=[f"{actual_ads}条"],
                textposition="auto",
                textfont=dict(
                    color='white',  # 确保文本为白色
                    size=14,        # 增大字体大小
                    family="Arial, sans-serif"  # 使用清晰的字体
                ),
                width=0.4,
                hovertemplate="实际承接: %{y}条<extra></extra>"
            )
        )
        
        # 更新布局
        fig.update_layout(
            title={
                'text': f"广告承接数量对比",
                'font': {'size': 18, 'color': 'white', 'family': "Arial, sans-serif"},
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                color='white',
                size=13,
                family="Arial, sans-serif"  # 设置默认字体
            ),
            height=280,  # 略微增加高度，提高可读性
            bargap=0.15,
            margin=dict(l=20, r=20, t=100, b=50),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
            showlegend=False,
            yaxis=dict(
                gridcolor='rgba(255,255,255,0.2)',  # 增加网格线对比度
                tickfont={'size': 12, 'color': 'white'}  # 确保刻度标签清晰
            ),
            xaxis=dict(
                tickfont={'size': 13, 'color': 'white'}  # 确保刻度标签清晰
            ),
            # 添加开发状态注释
            annotations=[
                dict(
                    text=f"开发比率: {ratio:.2f}x",
                    x=0.5,
                    y=-0.2,
                    xref="paper",
                    yref="paper",
                    showarrow=False,
                    font=dict(size=13, color=color)
                )
            ]
        )
        
        return fig