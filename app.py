import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from typing import Dict, List, Tuple
import re
import base64
from pathlib import Path

# 导入自定义模块
from pricing_module import (
    get_price, get_all_platforms_prices, get_categories, 
    get_platforms, get_follower_breakpoints
)
from visualization import (
    create_platform_comparison_chart, create_follower_price_curve, 
    create_category_comparison_radar, create_platform_coefficient_heatmap,
    create_top_categories_chart, format_price, format_large_number
)
from value_predictor import BloggerValuePredictor, AdMatrixGenerator

# 保留平台映射字典以防内部代码引用
PLATFORM_MAP = {
    "抖音": "Douyin",
    "小红书": "Xiaohongshu",
    "B站": "Bilibili",
    "快手": "Kuaishou"
}

# 配置页面基本信息
st.set_page_config(
    page_title="潜星云集 - 达人广告自动估价系统",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 添加背景图片和响应式样式
def add_bg_from_url(url):
    st.markdown(
         f"""
         <style>
         /* 基本背景样式 */
         .stApp {{
             background-image: url({url});
             background-size: cover;
             background-position: center;
             background-repeat: no-repeat;
             background-attachment: fixed;
             color: white !important;
         }}
         
         /* 强制应用深色样式到所有元素 */
         .stApp, .main, .block-container, [data-testid="stAppViewContainer"], 
         [data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stSidebar"] {{
             background-color: rgba(17, 17, 17, 0.8) !important;
             color: white !important;
         }}
         
         /* 所有文本强制使用白色 */
         p, span, div, h1, h2, h3, h4, h5, h6, label {{
             color: white !important;
         }}
         
         /* 表格样式增强 */
         table, th, td {{
             color: white !important;
             border-color: rgba(255, 255, 255, 0.2) !important;
         }}
         
         th {{
             background-color: rgba(65, 105, 225, 0.7) !important;
         }}
         
         td {{
             background-color: rgba(30, 30, 30, 0.8) !important;
         }}
         
         /* 移动端优化样式 */
         @media (max-width: 768px) {{
             /* 减小移动端的元素间距 */
             .stButton, .stSelectbox, .stNumberInput {{
                 margin-bottom: 10px !important;
             }}
             
             /* 移动端改进卡片和容器样式 */
             div.stCard, [data-testid="stExpander"] > div:first-child {{
                 padding: 10px !important;
                 background-color: rgba(17, 17, 17, 0.9) !important;
                 color: white !important;
             }}
             
             /* 优化移动端文本大小 */
             h1 {{
                 font-size: 1.8rem !important;
             }}
             h2 {{
                 font-size: 1.5rem !important;
             }}
             h3 {{
                 font-size: 1.2rem !important;
             }}
             
             /* 确保图表在移动端不会被切断 */
             [data-testid="stVerticalBlock"] {{
                 gap: 10px !important;
             }}
             
             /* 改进移动端侧边栏 */
             .sidebar .sidebar-content {{
                 padding-top: 2rem;
                 padding-bottom: 2rem;
                 background-color: rgba(17, 17, 17, 0.9) !important;
                 color: white !important;
             }}
         }}
         
         /* 全局改进：使文本在各种背景上更清晰 */
         .stMarkdown, .stText, [data-testid="stMarkdownContainer"] {{
             color: rgba(255, 255, 255, 0.95) !important; 
             text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
         }}
         
         /* 确保所有容器使用深色背景 */
         [data-testid="stBlock"], [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {{
             background-color: rgba(17, 17, 17, 0.8) !important;
             color: white !important;
         }}
         
         /* 改进输入控件在深色背景上的可见度 */
         input, select, textarea, [data-baseweb="input"], [data-baseweb="select"] {{
             background-color: rgba(255, 255, 255, 0.1) !important;
             color: white !important;
             border-color: rgba(255, 255, 255, 0.3) !important;
         }}
         
         /* 标签页文字颜色加强对比度 */
         button[data-baseweb="tab"] {{
             color: white !important;
             font-weight: 500 !important;
         }}
         
         /* 确保所有按钮文本清晰可见 */
         button {{
             color: white !important;
         }}
         
         /* 确保图表标题和标签使用白色 */
         .js-plotly-plot .plotly .gtitle, .js-plotly-plot .plotly .xtitle, 
         .js-plotly-plot .plotly .ytitle, .js-plotly-plot .plotly .legend .legendtext {{
             fill: white !important;
             color: white !important;
         }}
         
         /* 图表轴标签颜色修复 */
         .js-plotly-plot .plotly .xtick text, .js-plotly-plot .plotly .ytick text {{
             fill: white !important;
         }}
         </style>
         """,
         unsafe_allow_html=True
     )

# 函数：将图片转换为base64编码
def img_to_base64(img_path):
    img_path = Path(img_path)
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 自定义CSS，增强移动端响应式设计
st.markdown("""
<style>
    /* 基础样式 */
    .logo-text {
        font-weight: bold;
        font-size: 28px;
        color: white;
        vertical-align: middle;
        margin-left: 15px;
    }
    .logo-container {
        display: flex;
        align-items: center;
    }
    .logo-img {
        width: 60px;
        height: 60px;
    }
    
    /* 响应式设计优化 */
    /* 提高数据表格在移动设备上的可见性 */
    .dataframe {
        font-size: 12px !important;
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: white !important;
    }
    .dataframe th {
        background-color: rgba(65, 105, 225, 0.7) !important;
        color: white !important;
    }
    .dataframe td {
        background-color: rgba(30, 30, 30, 0.8) !important;
        color: white !important;
    }
    
    /* 优化移动设备上的文本显示 */
    @media (max-width: 768px) {
        .logo-text {
            font-size: 20px;
        }
        .logo-img {
            width: 40px;
            height: 40px;
        }
        /* 调整表格字体大小 */
        .dataframe {
            font-size: 10px !important;
        }
        /* 确保图表不会溢出屏幕 */
        .stPlotlyChart {
            max-width: 100%;
            height: auto !important;
        }
        /* 改善移动设备上的卡片显示 */
        div[data-testid="stExpander"] {
            padding: 10px 5px !important;
        }
        /* 调整标签页在移动设备上的显示 */
        button[data-baseweb="tab"] {
            font-size: 12px !important;
            padding: 5px !important;
        }
    }
    
    /* 确保所有图表背景透明并使用白色文本 */
    .stPlotlyChart {
        background-color: transparent !important;
    }
    
    /* 统一黑底白字的主题 */
    .stMarkdown, .stTextInput label, .stSelectbox label, .stSlider label, 
    .stNumberInput label, .stRadio label, .stCheckbox label, 
    .stDateInput label, .stMultiselect label, .stTextArea label, 
    span.st-emotion-cache-*, [class*="st-emotion-cache-"] {
        color: white !important;
    }
    
    /* 强制所有文字元素使用白色 */
    div.element-container div.stMarkdown p, 
    div.stMarkdown h1, div.stMarkdown h2, div.stMarkdown h3, 
    div.stMarkdown h4, div.stMarkdown h5, div.stMarkdown h6, 
    div.stMarkdown span, div.stMarkdown a, div.stMarkdown label,
    div.stMarkdown text, div.stMarkdown li, div.stMarkdown button {
        color: white !important;
    }
    
    /* 改善间距，避免内容拥挤 */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# 使用简约大气的深色科技背景
add_bg_from_url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80")

# 获取logo的base64编码
try:
    # 尝试多个可能的路径
    logo_paths = ["static/logo.png", "attached_assets/logo- white_1743183316407.png"]
    logo_base64 = None
    
    for path in logo_paths:
        try:
            logo_base64 = img_to_base64(path)
            break
        except:
            continue
    
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" class="logo-img"/>'
    else:
        logo_html = "<span style='font-size: 36px;'>📊</span>"  # 使用emoji作为备选
except Exception as e:
    logo_html = "<span style='font-size: 36px;'>📊</span>"  # 使用emoji作为备选

# 移除语言切换功能，固定使用中文
language = "中文"
if 'language' not in st.session_state:
    st.session_state.language = language

# 设置公司名称和UI文本
company_name = "潜星云集"
title_text = "达人广告自动估价与价值预测系统 🚀"
subtitle_text = "基于大数据的社交媒体广告价格与价值预测工具"
description_text = "本系统根据平台特性、内容类别和粉丝数量，精准计算社交媒体达人的广告报价，预测商业价值，提供数据可视化和优化建议。"

# 应用标题和简介 - 带logo，改进对比度和可读性
st.markdown(f"""
<div style="background-color: rgba(0,0,0,0.7); padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
    <div class="logo-container">
        {logo_html} 
        <span class="logo-text">{company_name}</span>
    </div>
    <h1 style="margin-top:10px; color: white; font-weight: 600;">{title_text}</h1>
    <h3 style="color: #6495ED; margin-top: 5px; margin-bottom: 15px;">{subtitle_text}</h3>
    <p style="color: rgba(255,255,255,0.9); line-height: 1.5; font-size: 1.05em;">
        {description_text}
    </p>
</div>
""", unsafe_allow_html=True)

# 创建侧边栏输入区域 - 改进视觉对比度
with st.sidebar:
    # 去除语言选择部分
    
    # 设置标题和参数配置标签
    param_title = "参数配置"
    company_name = "潜星云集"
    
    st.markdown(f"""
    <h2 style="color:white; margin-bottom:15px;">
        <span style="vertical-align:middle;">⚙️</span>
        <span style="vertical-align:middle; margin-left:8px;">{param_title}</span>
    </h2>
    """, unsafe_allow_html=True)
    
    # 添加装饰性图片，并添加圆角和边框
    st.markdown("""
    <div style="border-radius:10px; overflow:hidden; margin-bottom:15px; border:1px solid rgba(255,255,255,0.1);">
    """, unsafe_allow_html=True)
    st.image("https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?q=80", 
             caption="社交媒体数据分析", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 创建参数表单容器
    st.markdown("""
    <div style="background-color:rgba(0,0,0,0.3); padding:15px; border-radius:10px; margin-bottom:15px;">
    """, unsafe_allow_html=True)
    
    # 设置UI标签
    platform_label = "选择平台"
    platform_help = "选择要计算广告报价的社交媒体平台"
    category_label = "选择内容类别"
    category_help = "选择创作者的内容类别/标签"
    followers_label = "粉丝数量"
    followers_help = "输入创作者的粉丝数量，可以使用科学计数法(例如: 1e6 表示100万)"
    
    # 平台选择
    # 获取可用平台列表
    platform_options = get_platforms()
    
    # 平台选择
    platform = st.selectbox(
        platform_label, 
        options=platform_options,
        help=platform_help
    )
    
    # 内容类别选择
    category = st.selectbox(
        category_label, 
        get_categories(),
        help=category_help
    )
    
    # 粉丝数量输入 - 使用科学计数法通用表示
    followers_input = st.text_input(
        followers_label, 
        "100000",
        help=followers_help
    )
    
    # 验证并转换粉丝数输入
    try:
        # 支持科学计数法和普通数字
        if "e" in followers_input.lower() or "^" in followers_input:
            followers_input = followers_input.replace("^", "e")
            followers = float(followers_input)
        else:
            # 移除逗号和空格
            cleaned_input = re.sub(r'[,\s]', '', followers_input)
            followers = float(cleaned_input)
        
        if followers < 0:
            st.error("粉丝数量不能为负数")
            followers = 0
    except ValueError:
        st.error("请输入有效的数字")
        followers = 0
    
    # 设置更多UI标签
    followers_display = "当前粉丝数"
    celebrity_label = "是否为明星账号"
    celebrity_help = "明星账号将有额外的价格加成"
    calculate_btn_text = "计算价格 💰"
    
    # 显示格式化的粉丝数 - 更好的视觉呈现
    st.markdown(f"""
    <div style="background-color:rgba(51, 153, 255, 0.2); border-left:3px solid #39f; padding:10px; border-radius:5px; margin:10px 0;">
        <p style="margin:0; color:white;">{followers_display}: <b>{format_large_number(followers)}</b></p>
    </div>
    """, unsafe_allow_html=True)
    
    # 特殊选项：影视综艺类别的明星标志
    is_celebrity = False
    if category == "影视综艺":
        is_celebrity = st.checkbox(celebrity_label, value=False, 
                                  help=celebrity_help)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # 计算按钮 - 更突出的设计
    st.markdown("""
    <style>
    div[data-testid="stButton"] button {
        background-color: #4169E1 !important;
        color: white !important;
        font-weight: bold !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 5px !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2) !important;
        transition: all 0.3s ease !important;
    }
    div[data-testid="stButton"] button:hover {
        background-color: #2E4CC9 !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    calculate_btn = st.button(calculate_btn_text, use_container_width=True)
    
    # 底部信息 - 更美观的设计
    footer_text = f"© 2025 {company_name} - 达人广告估价系统"
        
    st.markdown("---")
    st.markdown(f"""
    <div style="text-align:center; margin-top:20px;">
        <p style="color:rgba(255,255,255,0.7); font-size:0.8em; margin:0;">
            {footer_text}
        </p>
    </div>
    """, unsafe_allow_html=True)

# 主界面内容区
if calculate_btn or 'last_calculation' in st.session_state:
    # 存储上次计算结果，以便在页面刷新时保持
    if calculate_btn:
        st.session_state.last_calculation = {
            'platform': platform,
            'category': category,
            'followers': followers,
            'is_celebrity': is_celebrity
        }
    else:
        # 使用上次计算的值
        platform = st.session_state.last_calculation['platform']
        category = st.session_state.last_calculation['category']
        followers = st.session_state.last_calculation['followers']
        is_celebrity = st.session_state.last_calculation['is_celebrity']
    
    # 计算当前参数下的报价
    try:
        current_price = get_price(platform, category, followers, is_celebrity=is_celebrity)
        
        # 计算所有平台的报价
        all_prices = get_all_platforms_prices(category, followers, is_celebrity=is_celebrity)
        
        # 设置中文文本和标签
        price_title = f"{platform} 平台下「{category}」类别的广告报价:"
        follower_text = "粉丝数:"
        celebrity_text = "✨ 明星账号加成已应用 ✨"
        
        # 显示价格结果 - 改进显示效果和对比度
        st.markdown(
            f"""
            <div style="background-color: rgba(65, 105, 225, 0.5); 
                        padding: 25px; border-radius: 10px; 
                        border-left: 5px solid #4169E1; margin-bottom: 20px;
                        box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h2 style="margin-top:0; color: white;">{price_title}</h2>
                <h1 style="color: white; font-weight: 600; margin-bottom:0; font-size: 2.5em;">
                    {format_price(current_price, is_english=False)}
                </h1>
                <p style="color: rgba(255,255,255,0.9); margin-top: 10px;">
                    {follower_text} <b>{format_large_number(followers, is_english=False)}</b>
                </p>
                {"<p style='color: #FFD700; margin-bottom:0; font-weight: 600;'>" + celebrity_text + "</p>" if is_celebrity else ""}
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # 创建标签页来组织不同的图表 - 价值预测放在最前面，根据语言设置标签
        if language == "中文":
            tab_labels = ["价值预测", "平台对比", "粉丝曲线", "类别分析", "高级分析"]
        else:
            tab_labels = ["Value Prediction", "Platform Comparison", "Follower Curve", "Category Analysis", "Advanced Analysis"]
            
        tab5, tab1, tab2, tab3, tab4 = st.tabs(tab_labels)
        
        with tab1:
            # 根据语言设置标题和标签
            if language == "中文":
                platform_title = "各平台报价对比"
                chart_title = f"「{category}」内容在各平台的报价对比 ({format_large_number(followers)}粉丝)"
                details_title = "详细报价数据"
                df_columns = {
                    "平台": list(all_prices.keys()),
                    "报价(元)": ["{:.2f}".format(p) for p in all_prices.values()],  # 强制保留两位小数
                    "格式化报价": [format_price(p, is_english=False) for p in all_prices.values()],
                    "相对抖音比例": ["{:.2f}".format(p/all_prices["抖音"]) for p in all_prices.values()]  # 强制保留两位小数
                }
                highlight_col = "报价(元)"
            else:
                platform_title = "Platform Price Comparison"
                chart_title = f"Price Comparison for '{category}' across Platforms ({format_large_number(followers)} followers)"
                details_title = "Detailed Price Data"
                # 英文界面需要将平台名称转换为英文
                platform_keys = list(all_prices.keys())
                platform_names = [PLATFORM_MAP.get(p, p) for p in platform_keys]
                df_columns = {
                    "Platform": platform_names,
                    "Price(CNY)": ["{:.2f}".format(p) for p in all_prices.values()],  # 强制保留两位小数
                    "Formatted Price": [format_price(p) for p in all_prices.values()],
                    "Relative to Douyin": ["{:.2f}".format(p/all_prices["抖音"]) for p in all_prices.values()]  # 强制保留两位小数
                }
                highlight_col = "Price(CNY)"
            
            st.subheader(platform_title)
            
            # 平台对比柱状图
            if language == "中文":
                # 中文模式直接使用原平台名称
                platform_comparison_fig = create_platform_comparison_chart(
                    all_prices, 
                    title=chart_title
                )
            else:
                # 英文模式需要将平台名称转换为英文显示
                # 创建一个新的字典，键为英文平台名
                english_prices = {}
                for p, price in all_prices.items():
                    english_platform = PLATFORM_MAP.get(p, p)
                    english_prices[english_platform] = price
                
                # 英文模式下，更新坐标轴标签
                platform_comparison_fig = create_platform_comparison_chart(
                    english_prices, 
                    title=chart_title
                )
                
                # 修改英文模式的坐标轴标签
                platform_comparison_fig.update_layout(
                    yaxis=dict(
                        title='Price (CNY)',
                        title_font={'size': 14},
                        gridcolor='rgba(255,255,255,0.2)',
                        tickfont={'size': 12}
                    ),
                    xaxis=dict(
                        title='Social Media Platform',
                        title_font={'size': 14},
                        tickfont={'size': 12}
                    )
                )
            st.plotly_chart(platform_comparison_fig, use_container_width=True)
            
            # 平台报价数据表格
            st.subheader(details_title)
            comparison_df = pd.DataFrame(df_columns)
            st.dataframe(comparison_df.style.highlight_max(subset=[highlight_col]), use_container_width=True)
        
        with tab2:
            # 根据语言设置标题和标签
            if language == "中文":
                curve_title = "粉丝数-价格曲线"
                max_followers_label = "最大粉丝数（单位：人）"
                expander_title = "📘 粉丝曲线解读"
                explanation = """
                **曲线代表什么?**
                - 每条曲线显示了特定平台下粉丝数量与广告报价之间的关系
                - 垂直虚线代表关键粉丝数量节点，这些是价格的断点
                
                **如何使用这个图?**
                - 通过比较不同平台在各粉丝量区间的斜率，可以评估哪个平台在特定粉丝量范围内增长更快
                - 寻找曲线交叉点，确定在哪个粉丝数量下平台优势发生变化
                """
            else:
                curve_title = "Followers-Price Curve"
                max_followers_label = "Maximum Followers (people)"
                expander_title = "📘 Curve Interpretation"
                explanation = """
                **What do the curves represent?**
                - Each curve shows the relationship between follower count and ad pricing for a specific platform
                - Vertical dotted lines represent key follower thresholds, which are price breakpoints
                
                **How to use this chart?**
                - Compare the slopes across different follower ranges to evaluate which platform grows faster in specific ranges
                - Look for curve intersection points to identify where platform advantages change
                """
            
            st.subheader(curve_title)
            
            # 粉丝数量滑动条，用于设置曲线图的最大粉丝数
            max_followers = st.slider(
                max_followers_label, 
                min_value=1_000, 
                max_value=20_000_000, 
                value=min(2_000_000, int(followers * 5) if followers > 0 else 2_000_000),
                step=1_000,
                format="%d"
            )
            
            # 粉丝数-价格曲线图
            follower_curve_fig = create_follower_price_curve(
                category, 
                max_followers=max_followers
            )
            st.plotly_chart(follower_curve_fig, use_container_width=True)
            
            # 解释说明
            with st.expander(expander_title):
                st.markdown(explanation)
        
        with tab3:
            # 根据语言设置标题和标签
            if language == "中文":
                category_title = "内容类别分析"
                view_option_label = "查看方式"
                view_options = ["当前平台的类别比较", "所有平台的类别比较"]
            else:
                category_title = "Content Category Analysis"
                view_option_label = "View Mode"
                view_options = ["Categories on Current Platform", "Categories Across All Platforms"]
            
            st.subheader(category_title)
            
            # 类别雷达图
            view_option = st.radio(
                view_option_label, 
                view_options,
                horizontal=True
            )
            
            if view_option == view_options[0]:  # 当前平台的类别比较 / Categories on Current Platform
                # 单一平台下的所有类别
                category_radar_fig = create_category_comparison_radar(
                    followers,
                    platform=platform
                )
            else:
                # 所有平台的所有类别比较
                category_radar_fig = create_category_comparison_radar(
                    followers
                )
            
            st.plotly_chart(category_radar_fig, use_container_width=True)
            
            # 报价最高的类别排行
            top_fig = create_top_categories_chart(
                followers, 
                platform, 
                n=10
            )
            st.plotly_chart(top_fig, use_container_width=True)
        
        with tab4:
            # 根据语言设置标题和标签
            if language == "中文":
                advanced_title = "高级平台特性分析"
                slider_label = "显示的类别数量（个）"
                expander_title = "🔍 平台系数解读"
                explanation = """
                **系数表示什么?**
                - 系数代表相对于抖音平台的价格倍率
                - 高于1的值表示该平台在特定类别上比抖音更加昂贵
                - 低于1的值表示该平台在特定类别上比抖音更加经济
                
                **如何利用这些信息?**
                - 寻找深色区域，这些是特定平台对特定内容类别高度重视的区域
                - 系数高的组合意味着市场对这类内容在该平台上的需求高
                - 系数低的组合可能代表性价比高的投放机会
                """
            else:
                advanced_title = "Advanced Platform Analysis"
                slider_label = "Number of Categories to Display"
                expander_title = "🔍 Platform Coefficient Interpretation"
                explanation = """
                **What do the coefficients represent?**
                - Coefficients show the price multiplier relative to Douyin platform
                - Values above 1 indicate the platform is more expensive for that category than Douyin
                - Values below 1 indicate the platform is more economical for that category than Douyin
                
                **How to use this information?**
                - Look for darker areas, which represent categories that specific platforms value highly
                - High coefficient combinations indicate high market demand for that content on that platform
                - Low coefficient combinations may represent cost-effective advertising opportunities
                """
            
            st.subheader(advanced_title)
            
            # 平台系数热力图的类别筛选
            num_categories = st.slider(
                slider_label, 
                min_value=5, 
                max_value=len(get_categories()), 
                value=10
            )
            
            # 根据当前粉丝数下的价格选择前N个类别
            prices_for_all = []
            for cat in get_categories():
                price = get_price(platform, cat, followers)
                prices_for_all.append((cat, price))
            
            # 按价格排序
            prices_for_all.sort(key=lambda x: x[1], reverse=True)
            selected_categories = [p[0] for p in prices_for_all[:num_categories]]
            
            # 创建热力图
            heatmap_fig = create_platform_coefficient_heatmap(selected_categories)
            st.plotly_chart(heatmap_fig, use_container_width=True)
            
            # 解释说明
            with st.expander(expander_title):
                st.markdown(explanation)
                
        with tab5:
            # 根据语言设置标题和标签
            if language == "中文":
                prediction_title = "✨ 达人商业价值预测 ✨"
                params_title = "📋 分析参数概览"
                platform_label = "平台"
                category_label = "内容类别"
                followers_label = "当前粉丝数"
                ad_price_label = "单条广告报价"
                growth_rate_title = "📊 粉丝增长率设置"
                growth_rate_desc = "您可以选择使用系统默认的智能增长算法，或设置自定义的年度粉丝增长率。"
                custom_growth_checkbox = "使用自定义粉丝增长率"
                custom_growth_help = "启用后可以手动设置年度粉丝增长百分比，替代默认的智能算法"
                growth_rate_slider = "年度粉丝增长率 (%)"
                growth_rate_help = "设置每年粉丝数的百分比增长率，例如20表示每年增长20%"
                growth_rate_set = "设定增长率"
                unit_year = "年"
            else:
                prediction_title = "✨ Influencer Commercial Value Prediction ✨"
                params_title = "📋 Analysis Parameters"
                platform_label = "Platform"
                category_label = "Content Category"
                followers_label = "Current Followers"
                ad_price_label = "Single Ad Price"
                growth_rate_title = "📊 Follower Growth Rate Settings"
                growth_rate_desc = "You can choose to use the system's default intelligent growth algorithm or set a custom annual follower growth rate."
                custom_growth_checkbox = "Use Custom Growth Rate"
                custom_growth_help = "When enabled, you can manually set the annual percentage growth rate, replacing the default intelligent algorithm"
                growth_rate_slider = "Annual Follower Growth Rate (%)"
                growth_rate_help = "Set the percentage growth rate of followers per year, e.g., 20 means 20% annual growth"
                growth_rate_set = "Growth Rate Set"
                unit_year = "year"
                
            # 使用更突出的标题样式
            st.markdown(f"""
            <h2 style="color: white; text-align: center; 
                       background: linear-gradient(90deg, rgba(72, 61, 139, 0.7), rgba(72, 61, 139, 0.3)); 
                       padding: 10px; border-radius: 5px; margin-bottom: 20px;">
                {prediction_title}
            </h2>
            """, unsafe_allow_html=True)
            
            # 初始化预测器和广告矩阵生成器
            predictor = BloggerValuePredictor()
            ad_matrix = AdMatrixGenerator()
            
            # 单条广告价格（万元）
            single_ad_price = current_price / 10000  # 转换为万元
            
            # 显示当前参数和单条广告价格 - 使用卡片式设计
            st.markdown(
                f"""
                <div style="background-color: rgba(72, 61, 139, 0.5); 
                            padding: 20px; border-radius: 10px; 
                            margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h4 style="margin-top:0; color: white; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 8px;">
                        {params_title}
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 15px;">
                        <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                            <p style="margin:0; color: rgba(255,255,255,0.7); font-size: 0.85em;">{platform_label}</p>
                            <p style="margin:5px 0 0 0; color: white; font-weight: bold;">
                                {platform if language == "中文" else PLATFORM_MAP.get(platform, platform)}
                            </p>
                        </div>
                        <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                            <p style="margin:0; color: rgba(255,255,255,0.7); font-size: 0.85em;">{category_label}</p>
                            <p style="margin:5px 0 0 0; color: white; font-weight: bold;">{category}</p>
                        </div>
                        <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                            <p style="margin:0; color: rgba(255,255,255,0.7); font-size: 0.85em;">{followers_label}</p>
                            <p style="margin:5px 0 0 0; color: white; font-weight: bold;">{format_large_number(followers, is_english=False)}</p>
                        </div>
                        <div style="background-color: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px;">
                            <p style="margin:0; color: rgba(255,255,255,0.7); font-size: 0.85em;">{ad_price_label}</p>
                            <p style="margin:5px 0 0 0; color: white; font-weight: bold;">
                                {format_price(current_price, is_english=False)} ({single_ad_price:.2f}万元)
                            </p>
                        </div>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # 自适应布局 - 使用垂直布局而非列布局，优化移动端体验
            
            # 粉丝增长率自定义滑动条
            st.markdown(f"""
            <h5 style="margin-bottom:0px;">{growth_rate_title}</h5>
            <p style="color: rgba(255,255,255,0.7); font-size: 0.9em; margin-top:5px;">
                {growth_rate_desc}
            </p>
            """, unsafe_allow_html=True)
            
            use_custom_growth = st.checkbox(custom_growth_checkbox, value=False, 
                                          help=custom_growth_help)
            
            growth_rate = None
            if use_custom_growth:
                growth_rate = st.slider(
                    growth_rate_slider, 
                    min_value=0.0, 
                    max_value=1000.0, 
                    value=20.0, 
                    step=1.0,
                    help=growth_rate_help
                )
                
                # 显示选择的增长率
                st.markdown(f"""
                <div style="background-color:rgba(65, 105, 225, 0.2); border-left:3px solid #4169E1; 
                           padding:10px; border-radius:5px; margin:10px 0;">
                    <p style="margin:0; color:white;">{growth_rate_set}: <b>{growth_rate:.0f}%/{unit_year}</b></p>
                </div>
                """, unsafe_allow_html=True)
            
            # 初始化变量，防止错误引用
            # 创建初始空结构，后续会被真实数据替换
            result_data = {
                'years': [],
                'fans': [],
                'ad_counts': [],
                'income': []
            }
            
            # 增长趋势图
            if language == "中文":
                trend_title = "##### 粉丝和收益增长趋势"
                summary_title = "##### 价值预测汇总"
                expander_title = "📈 价值预测说明"
                explanation = """
                **预测模型考虑因素:**
                - 粉丝自然增长率（平台和内容类别差异）
                - 内容变现能力（广告条数和价格增长）
                - 平台特性对变现的影响
                - 粉丝数量上限（平台天花板）
                - 自定义粉丝增长率（如启用）
                
                **收入包括:**
                - 广告收入（主要收入来源）
                - 其他收入（电商、会员等附加收益，按广告收入的20%估算）
                
                **自定义增长率说明:**
                - 默认情况下，系统使用基于平台和类别特性的智能增长算法
                - 启用自定义增长率后，可以根据历史数据或市场预期设置具体的年度百分比增长率
                - 增长率影响粉丝数量，进而影响广告量和单价，最终影响总收益预测
                """
            else:
                trend_title = "##### Follower and Revenue Growth Trends"
                summary_title = "##### Value Prediction Summary"
                expander_title = "📈 Prediction Explanation"
                explanation = """
                **Prediction Model Factors:**
                - Natural follower growth rate (differences between platforms and content categories)
                - Content monetization capability (number of ads and price growth)
                - Platform-specific impact on monetization
                - Follower count ceiling (platform limits)
                - Custom follower growth rate (if enabled)
                
                **Income Includes:**
                - Ad revenue (primary income source)
                - Other income (e-commerce, memberships, etc., estimated at 20% of ad revenue)
                
                **Custom Growth Rate Notes:**
                - By default, the system uses an intelligent growth algorithm based on platform and category characteristics
                - When custom growth rate is enabled, you can set a specific annual percentage growth rate based on historical data or market expectations
                - Growth rate affects follower count, which impacts ad volume and pricing, ultimately affecting total revenue predictions
                """
            
            st.markdown(trend_title)
            growth_fig = predictor.create_growth_visualization(
                fans=followers,
                platform=platform,
                label=category,
                single_ad_value=single_ad_price,
                growth_rate=growth_rate if use_custom_growth else None
            )
            st.plotly_chart(growth_fig, use_container_width=True)
            
            # 价值预测结果表格
            st.markdown(summary_title)
            
            # 获取预测结果
            results = predictor.predict_value(
                fans=followers,
                platform=platform,
                label=category,
                single_ad_value=single_ad_price,
                growth_rate=growth_rate if use_custom_growth else None
            )
            
            # 创建数据表格
            result_data = predictor.create_summary_table(
                fans=followers,
                platform=platform,
                label=category,
                single_ad_value=single_ad_price,
                growth_rate=growth_rate if use_custom_growth else None
            )
            
            # 更新数据表列
            if language == "中文":
                df_columns = {
                    "预测周期": result_data['years'],
                    "粉丝规模": result_data['fans'],
                    "广告量": result_data['ad_counts'],
                    "年收入": result_data['income']
                }
            else:
                df_columns = {
                    "Year": result_data['years'],
                    "Followers": result_data['fans'],
                    "Ad Count": result_data['ad_counts'],
                    "Annual Income": result_data['income']
                }
            
            # 创建DataFrame并显示
            result_df = pd.DataFrame(df_columns)
            st.dataframe(result_df, use_container_width=True)
            
            # 增加一些解释说明
            with st.expander(expander_title):
                st.markdown(explanation)
            
            # 添加商业开发程度分析
            st.markdown("---")
            
            # 根据语言设置标题和标签
            if language == "中文":
                dev_analysis_title = "### 商业开发程度分析"
                ad_count_label = "当前年广告承接数量（条）"
                ad_count_help = "输入您目前一年能够承接的广告数量，将与同量级博主进行比较分析"
            else:
                dev_analysis_title = "### Commercial Development Analysis"
                ad_count_label = "Current Annual Ad Count"
                ad_count_help = "Enter the number of ads you accept annually to compare with similar influencers in your category"
                
            st.markdown(dev_analysis_title)
            
            # 添加输入当前年广告承接量的选项
            fans_in_wan = followers / 10000  # 转换为万
            
            # 获取同量级平均广告条数作为默认值
            expected_ads = ad_matrix.get_expected_ad_count(
                platform=platform, 
                label=category, 
                fans=fans_in_wan
            )
            
            ad_count = st.number_input(
                ad_count_label,
                min_value=0,
                max_value=1000,
                value=expected_ads,
                step=1,
                help=ad_count_help
            )
            
            # 仅在输入有效广告数时显示分析
            if ad_count >= 0:
                # 计算商业开发程度
                ratio = ad_matrix.calculate_development_ratio(
                    platform=platform,
                    label=category,
                    fans=fans_in_wan,
                    actual_ads=ad_count
                )
                # 限制小数点后2位
                ratio = round(ratio, 2)
                
                # 计算差异值
                diff = expected_ads - ad_count if expected_ads > ad_count else 0
                extra = ad_count - expected_ads if ad_count > expected_ads else 0
                
                # 设置标题和详情标签
                if language == "中文":
                    details_title = "#### 开发程度分析详情"
                    underdeveloped_title = "📊 开发不足"
                    underdeveloped_text1 = f"您当前年广告承接量为 <b>{ad_count}</b> 条，低于同量级的 {platform} 平台 {category} 类博主平均承接 <b>{expected_ads}</b> 条。"
                    underdeveloped_text2 = f"您还有 <b>{diff}</b> 条的增长空间。"
                    normal_title = "🎯 正常水平"
                    normal_text = f"您当前年广告承接量为 <b>{ad_count}</b> 条，与同量级的 {platform} 平台 {category} 类博主平均承接量 <b>{expected_ads}</b> 条相当，处于合理范围。"
                    overdeveloped_title = "⚠️ 充分开发"
                    overdeveloped_text = f"您当前年广告承接量为 <b>{ad_count}</b> 条，超过同量级的 {platform} 平台 {category} 类博主平均承接量 <b>{expected_ads}</b> 条，高出 <b>{extra}</b> 条。"
                    suggestion_title = "💡 建议："
                    
                    underdeveloped_suggestions = [
                        "提高内容质量与互动率，增加与品牌方的曝光机会",
                        "拓展合作渠道，主动联系潜在广告主",
                        "适当降低广告报价或提供组合套餐增加吸引力"
                    ]
                    
                    normal_suggestions = [
                        "维持现有的内容与广告平衡策略",
                        "适度提升单条广告价格，提高收益质量",
                        "向核心粉丝提供更多增值服务，提升商业价值"
                    ]
                    
                    overdeveloped_suggestions = [
                        "注意控制广告频率，避免影响用户体验和掉粉",
                        "提高广告选择标准，优先选择与粉丝匹配度高的品牌",
                        "大幅提升单条广告价格，降低数量但提高总收益"
                    ]
                else:
                    details_title = "#### Development Analysis Details"
                    underdeveloped_title = "📊 Underdeveloped"
                    underdeveloped_text1 = f"Your current annual ad count is <b>{ad_count}</b>, which is lower than the average of <b>{expected_ads}</b> for similar {category} content creators on {platform}."
                    underdeveloped_text2 = f"You have room to grow by <b>{diff}</b> more ads."
                    normal_title = "🎯 Normal Level"
                    normal_text = f"Your current annual ad count is <b>{ad_count}</b>, which is comparable to the average of <b>{expected_ads}</b> for similar {category} content creators on {platform}."
                    overdeveloped_title = "⚠️ Fully Developed"
                    overdeveloped_text = f"Your current annual ad count is <b>{ad_count}</b>, which exceeds the average of <b>{expected_ads}</b> for similar {category} content creators on {platform} by <b>{extra}</b> ads."
                    suggestion_title = "💡 Suggestions:"
                    
                    underdeveloped_suggestions = [
                        "Improve content quality and engagement to increase brand exposure opportunities",
                        "Expand cooperation channels and proactively contact potential advertisers",
                        "Consider lowering ad prices or offering package deals to increase attractiveness"
                    ]
                    
                    normal_suggestions = [
                        "Maintain your current content and advertising balance strategy",
                        "Moderately increase single ad prices to improve revenue quality",
                        "Offer more value-added services to core followers to enhance commercial value"
                    ]
                    
                    overdeveloped_suggestions = [
                        "Control ad frequency to avoid affecting user experience and losing followers",
                        "Raise standards for ad selection, prioritizing brands that match your audience",
                        "Significantly increase single ad prices while decreasing volume to improve total revenue"
                    ]
                
                # 布局：移动优先的垂直布局
                if language == "中文":
                    layout_title = "### 商业开发程度分析"
                else:
                    layout_title = "### Commercial Development Analysis"
                    
                st.markdown(layout_title)
                
                # 检测是否是手机访问
                is_mobile = """
                <script>
                    if (window.innerWidth < 768) {
                        document.getElementById('is_mobile').value = 'true';
                    } else {
                        document.getElementById('is_mobile').value = 'false';
                    }
                </script>
                <input type="hidden" id="is_mobile" value="false">
                """
                st.markdown(is_mobile, unsafe_allow_html=True)
                
                # 根据屏幕宽度决定布局
                # 移动设备使用垂直堆叠布局
                if st.session_state.get('mobile_view', True):  # 默认假设为移动设备
                    # 生成商业开发度分析图表
                    dev_fig = ad_matrix.create_development_visualization(
                        platform=platform,
                        label=category,
                        fans=fans_in_wan,
                        actual_ads=ad_count
                    )
                    st.plotly_chart(dev_fig, use_container_width=True)
                    
                    # 生成广告数量对比图表
                    ad_comp_fig = ad_matrix.create_ad_comparison_chart(
                        platform=platform,
                        label=category,
                        fans=fans_in_wan,
                        actual_ads=ad_count
                    )
                    st.plotly_chart(ad_comp_fig, use_container_width=True)
                # 桌面设备使用两列布局
                else:
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # 生成广告数量对比图表
                        ad_comp_fig = ad_matrix.create_ad_comparison_chart(
                            platform=platform,
                            label=category,
                            fans=fans_in_wan,
                            actual_ads=ad_count
                        )
                        st.plotly_chart(ad_comp_fig, use_container_width=True)
                    
                    with col2:
                        # 生成商业开发度分析图表
                        dev_fig = ad_matrix.create_development_visualization(
                            platform=platform,
                            label=category,
                            fans=fans_in_wan,
                            actual_ads=ad_count
                        )
                        st.plotly_chart(dev_fig, use_container_width=True)
                
                # 创建开发程度分析详情
                st.markdown(details_title)
                
                # 创建一个美观的分析详情卡片
                if ratio < 0.8:
                    # 使用已经计算好的diff值
                    analysis_html = f"""
                    <div style="background-color: rgba(38, 39, 48, 0.8); padding: 20px; border-radius: 10px; border-left: 5px solid #FF6347;">
                        <h4 style="color: #FF6347;">{underdeveloped_title} ({ratio:.2f}x)</h4>
                        <p>{underdeveloped_text1}</p>
                        <p>{underdeveloped_text2}</p>
                        <h5>{suggestion_title}</h5>
                        <ul>
                            <li>{underdeveloped_suggestions[0]}</li>
                            <li>{underdeveloped_suggestions[1]}</li>
                            <li>{underdeveloped_suggestions[2]}</li>
                        </ul>
                    </div>
                    """
                elif ratio <= 1.2:
                    analysis_html = f"""
                    <div style="background-color: rgba(38, 39, 48, 0.8); padding: 20px; border-radius: 10px; border-left: 5px solid #2ECC71;">
                        <h4 style="color: #2ECC71;">{normal_title} ({ratio:.2f}x)</h4>
                        <p>{normal_text}</p>
                        <h5>{suggestion_title}</h5>
                        <ul>
                            <li>{normal_suggestions[0]}</li>
                            <li>{normal_suggestions[1]}</li>
                            <li>{normal_suggestions[2]}</li>
                        </ul>
                    </div>
                    """
                else:
                    # 使用已经计算好的extra值
                    analysis_html = f"""
                    <div style="background-color: rgba(38, 39, 48, 0.8); padding: 20px; border-radius: 10px; border-left: 5px solid #3498DB;">
                        <h4 style="color: #3498DB;">{overdeveloped_title} ({ratio:.2f}x)</h4>
                        <p>{overdeveloped_text}</p>
                        <h5>{suggestion_title}</h5>
                        <ul>
                            <li>{overdeveloped_suggestions[0]}</li>
                            <li>{overdeveloped_suggestions[1]}</li>
                            <li>{overdeveloped_suggestions[2]}</li>
                        </ul>
                    </div>
                    """
                
                st.markdown(analysis_html, unsafe_allow_html=True)
            
            # 增加一些操作建议
            st.markdown("---")
            
            # 根据语言调整标题
            if language == "中文":
                suggestions_title = "### 商业价值优化建议"
                no_suggestions_message = "当前设置已经是最优配置，继续保持内容质量稳定增长。"
            else:
                suggestions_title = "### Commercial Value Optimization Tips"
                no_suggestions_message = "Your current setup is already optimal. Continue maintaining content quality for steady growth."
                
            st.markdown(suggestions_title)
            
            # 提供一些基于当前数据的建议
            suggestions = []
            
            # 平台建议
            platform_prices = {p: get_price(p, category, followers) for p in get_platforms()}
            best_platform = max(platform_prices.items(), key=lambda x: x[1])[0]
            
            if best_platform != platform:
                if language == "中文":
                    suggestions.append(f"考虑将内容向「{best_platform}」平台扩展，该平台对「{category}」类内容估值更高")
                else:
                    suggestions.append(f"Consider expanding content to the {best_platform} platform, which values '{category}' content higher")
            
            # 内容类别建议
            category_prices = {cat: get_price(platform, cat, followers) for cat in get_categories()[:5]}  # 只取前5个类别，避免计算太多
            better_categories = [cat for cat, price in category_prices.items() if price > current_price * 1.2]  # 找出比当前高20%的类别
            
            if better_categories:
                if language == "中文":
                    suggestions.append(f"尝试融入「{better_categories[0]}」元素，可能会提高单条内容的商业价值")
                else:
                    suggestions.append(f"Try incorporating '{better_categories[0]}' elements into your content, which may increase commercial value per post")
            
            # 粉丝量级建议
            next_milestone = 0
            breakpoints = get_follower_breakpoints()
            for bp in breakpoints:
                if bp > followers:
                    next_milestone = bp
                    break
            
            if next_milestone > 0:
                next_price = get_price(platform, category, next_milestone)
                price_increase = (next_price - current_price) / current_price * 100
                
                if language == "中文":
                    suggestions.append(f"冲刺下一个粉丝量级 {format_large_number(next_milestone)}，有望增加约 {price_increase:.0f}% 的单条广告报价")
                else:
                    suggestions.append(f"Aim for the next follower milestone of {format_large_number(next_milestone)}, which could increase your ad price by approximately {price_increase:.0f}%")
            
            # 显示建议列表
            if suggestions:
                for i, sugg in enumerate(suggestions):
                    st.markdown(f"#### {i+1}. {sugg}")
            else:
                st.info(no_suggestions_message)
    
    except Exception as e:
        st.error(f"计算报价时发生错误: {e}")

# 如果是首次访问，显示使用指南
else:
    # 特性介绍 - 移动优先响应式布局
    # 检测屏幕宽度决定布局
    if st.session_state.get('mobile_view', True):  # 默认为移动设备
        # 移动设备使用单列布局
        st.markdown(
            """
            <div style="background-color: rgba(65, 105, 225, 0.5); padding: 15px; 
                      border-radius: 10px; text-align: center; margin-bottom: 10px;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: white; margin-top:0; font-size: 1.3rem;">多平台分析</h3>
                <p style="color: white; font-size: 0.9rem;">支持抖音、小红书、B站、快手四大平台</p>
                <p style="font-size: 24px; margin-bottom:0;">📊</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background-color: rgba(138, 43, 226, 0.5); padding: 15px; 
                      border-radius: 10px; text-align: center; margin-bottom: 10px;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: white; margin-top:0; font-size: 1.3rem;">32个内容标签</h3>
                <p style="color: white; font-size: 0.9rem;">覆盖主流内容类别的精准报价</p>
                <p style="font-size: 24px; margin-bottom:0;">🏷️</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background-color: rgba(72, 61, 139, 0.5); padding: 15px; 
                      border-radius: 10px; text-align: center; margin-bottom: 10px;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: white; margin-top:0; font-size: 1.3rem;">可视化分析</h3>
                <p style="color: white; font-size: 0.9rem;">直观图表展示报价和平台对比</p>
                <p style="font-size: 24px; margin-bottom:0;">📈</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.markdown(
            """
            <div style="background-color: rgba(0, 128, 128, 0.5); padding: 15px; 
                      border-radius: 10px; text-align: center; margin-bottom: 10px;
                      box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <h3 style="color: white; margin-top:0; font-size: 1.3rem;">价值预测</h3>
                <p style="color: white; font-size: 0.9rem;">预测达人未来商业价值走势</p>
                <p style="font-size: 24px; margin-bottom:0;">💎</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # 桌面设备使用两列布局
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(
                """
                <div style="background-color: rgba(65, 105, 225, 0.5); padding: 20px; 
                          border-radius: 10px; height: 150px; text-align: center;
                          box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin-top:0;">多平台分析</h3>
                    <p style="color: white;">支持抖音、小红书、B站、快手四大平台</p>
                    <p style="font-size: 30px; margin-bottom:0;">📊</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div style="background-color: rgba(138, 43, 226, 0.5); padding: 20px; 
                          border-radius: 10px; height: 150px; text-align: center;
                          box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin-top:0;">32个内容标签</h3>
                    <p style="color: white;">覆盖主流内容类别的精准报价</p>
                    <p style="font-size: 30px; margin-bottom:0;">🏷️</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        # 第二行两列
        col3, col4 = st.columns(2)
        
        with col3:
            st.markdown(
                """
                <div style="background-color: rgba(72, 61, 139, 0.5); padding: 20px; 
                          border-radius: 10px; height: 150px; text-align: center;
                          box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin-top:0;">可视化分析</h3>
                    <p style="color: white;">直观图表展示报价和平台对比</p>
                    <p style="font-size: 30px; margin-bottom:0;">📈</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col4:
            st.markdown(
                """
                <div style="background-color: rgba(0, 128, 128, 0.5); padding: 20px; 
                          border-radius: 10px; height: 150px; text-align: center;
                          box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <h3 style="color: white; margin-top:0;">价值预测</h3>
                    <p style="color: white;">预测达人未来商业价值走势</p>
                    <p style="font-size: 30px; margin-bottom:0;">💎</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
    
    # 使用指南 - 移动优先响应式设计
    st.markdown("---")
    st.subheader("🚀 快速开始")
    
    # 根据设备调整步骤布局
    if st.session_state.get('mobile_view', True):  # 默认为移动设备
        # 移动设备使用垂直单列步骤
        st.markdown(
            """
            <div style="margin-bottom:15px;">
                <div style="background-color: rgba(0,0,0,0.3); padding: 12px; border-radius: 10px; text-align:center; margin-bottom:10px;">
                    <h4 style="color:white; margin-top:0; font-size:1.1rem;">步骤 1</h4>
                    <p style="color:white; margin-bottom:0; font-size:0.9rem;">选择平台和内容类别</p>
                </div>
                <div style="background-color: rgba(0,0,0,0.3); padding: 12px; border-radius: 10px; text-align:center; margin-bottom:10px;">
                    <h4 style="color:white; margin-top:0; font-size:1.1rem;">步骤 2</h4>
                    <p style="color:white; margin-bottom:0; font-size:0.9rem;">输入粉丝数量并计算</p>
                </div>
                <div style="background-color: rgba(0,0,0,0.3); padding: 12px; border-radius: 10px; text-align:center;">
                    <h4 style="color:white; margin-top:0; font-size:1.1rem;">步骤 3</h4>
                    <p style="color:white; margin-bottom:0; font-size:0.9rem;">浏览分析和预测结果</p>
                </div>
            </div>
            """, 
            unsafe_allow_html=True
        )
    else:
        # 桌面设备使用三列布局
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                """
                <div style="background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; text-align:center; height:100px;">
                    <h4 style="color:white; margin-top:0;">步骤 1</h4>
                    <p style="color:white; margin-bottom:0;">选择平台和内容类别</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div style="background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; text-align:center; height:100px;">
                    <h4 style="color:white; margin-top:0;">步骤 2</h4>
                    <p style="color:white; margin-bottom:0;">输入粉丝数量并计算</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                """
                <div style="background-color: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; text-align:center; height:100px;">
                    <h4 style="color:white; margin-top:0;">步骤 3</h4>
                    <p style="color:white; margin-bottom:0;">浏览分析和预测结果</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
    # 示例图片
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?q=80", 
             caption="达人营销价值分析", use_container_width=True)
    
    # 支持的平台和类别预览 - 移动优先响应式设计
    with st.expander("查看支持的平台和内容类别"):
        # 平台部分 - 使用更明显的样式
        st.markdown("""
        <div style="background-color: rgba(65, 105, 225, 0.2); padding: 10px; border-radius: 5px; margin-bottom: 15px;">
            <h3 style="color: white; text-align: center; margin-top: 0;">支持的平台</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 获取平台列表
        platforms = get_platforms()
        
        # 根据设备调整平台展示布局
        if st.session_state.get('mobile_view', True):  # 默认为移动设备
            # 移动设备使用2列布局
            platform_cols = st.columns(2)
            for i, p in enumerate(platforms):
                with platform_cols[i % 2]:
                    st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.1); padding: 10px; 
                              border-radius: 5px; text-align: center; margin-bottom: 10px;">
                        <p style="color: white; font-weight: bold; margin: 0; font-size: 0.95rem;">{p}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # 桌面设备使用4列布局
            platform_cols = st.columns(4)
            for i, p in enumerate(platforms):
                with platform_cols[i]:
                    st.markdown(f"""
                    <div style="background-color: rgba(255,255,255,0.1); padding: 10px; 
                              border-radius: 5px; text-align: center;">
                        <p style="color: white; font-weight: bold; margin: 0;">{p}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        # 类别部分
        st.markdown("""
        <div style="background-color: rgba(138, 43, 226, 0.2); padding: 10px; border-radius: 5px; margin: 15px 0;">
            <h3 style="color: white; text-align: center; margin-top: 0;">支持的内容类别</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # 获取所有类别
        categories = get_categories()
        
        # 根据设备调整类别展示布局
        if st.session_state.get('mobile_view', True):  # 默认为移动设备
            # 移动设备使用2列布局
            for i in range(0, len(categories), 2):
                cols = st.columns(2)
                for j in range(2):
                    if i + j < len(categories):
                        with cols[j]:
                            st.markdown(f"""
                            <div style="background-color: rgba(255,255,255,0.1); padding: 8px; 
                                      border-radius: 5px; text-align: center; margin-bottom: 8px;">
                                <p style="color: white; margin: 0; font-size: 0.9rem;">{categories[i+j]}</p>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            # 桌面设备使用4列布局
            for i in range(0, len(categories), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(categories):
                        with cols[j]:
                            st.markdown(f"""
                            <div style="background-color: rgba(255,255,255,0.1); padding: 5px; 
                                      border-radius: 5px; text-align: center; margin-bottom: 5px;">
                                <p style="color: white; margin: 0;">{categories[i+j]}</p>
                            </div>
                            """, unsafe_allow_html=True)
            
    # 数据来源说明
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p style="color: rgba(255,255,255,0.7); font-size: 0.8em;">
            数据来源: 基于行业报告与实际广告投放数据建模
        </p>
    </div>
    """, unsafe_allow_html=True)
