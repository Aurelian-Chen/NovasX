import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import numpy as np
from typing import Dict, List, Optional
from pricing_module import get_categories, get_platforms, get_follower_breakpoints, get_price

def format_large_number(num: float, is_english: bool = False) -> str:
    """将大数格式化为易读形式，保留两位小数，支持中英文格式
    
    Args:
        num: 要格式化的数字
        is_english: 是否使用英文格式 (True 使用K/M/B, False 使用万/亿)
    """
    # 保留两位小数
    def clean_decimal(n: float) -> str:
        # 判断是否为整数
        if n == int(n):
            return f"{int(n)}"
        else:
            return f"{n:.2f}"
    
    if is_english:
        if num >= 1_000_000_000:  # Billion
            return f"{clean_decimal(num/1_000_000_000)}B"
        elif num >= 1_000_000:  # Million
            return f"{clean_decimal(num/1_000_000)}M"
        elif num >= 1_000:  # Thousand
            return f"{clean_decimal(num/1_000)}K"
        else:
            return clean_decimal(num)
    else:
        if num >= 100_000_000:  # 亿
            return f"{clean_decimal(num/100_000_000)}亿"
        elif num >= 10_000:  # 万
            return f"{clean_decimal(num/10_000)}万"
        elif num >= 1_000:  # 千
            return f"{clean_decimal(num/1_000)}千"
        else:
            return clean_decimal(num)

def format_price(price: float, is_english: bool = False) -> str:
    """将价格格式化为易读形式，保留两位小数，支持中英文格式
    
    Args:
        price: 要格式化的价格
        is_english: 是否使用英文格式 (True 使用$, False 使用¥)
    """
    # 保留两位小数
    def clean_decimal(n: float) -> str:
        # 判断是否为整数
        if n == int(n):
            return f"{int(n)}"
        else:
            return f"{n:.2f}"
    
    if is_english:
        if price >= 1_000_000:
            return f"${clean_decimal(price/1_000_000)}M"
        elif price >= 1_000:
            return f"${clean_decimal(price/1_000)}K"
        else:
            return f"${clean_decimal(price)}"
    else:
        if price >= 10_000:
            return f"¥{clean_decimal(price/10_000)}万"
        else:
            return f"¥{clean_decimal(price)}"

def create_platform_comparison_chart(prices: Dict[str, float], title: str = "各平台报价对比") -> go.Figure:
    """创建平台报价对比柱状图"""
    platforms = list(prices.keys())
    values = list(prices.values())
    
    # 使用更饱和的蓝色系配色方案创建柱状图，提高对比度
    colors = ['rgba(65, 105, 225, 0.95)', 'rgba(100, 149, 237, 0.95)', 
              'rgba(30, 144, 255, 0.95)', 'rgba(70, 130, 180, 0.95)']
    
    fig = go.Figure()
    for i, (platform, value) in enumerate(zip(platforms, values)):
        # 确保价格显示为两位小数
        formatted_price = format_price(value)
        fig.add_trace(go.Bar(
            x=[platform], 
            y=[value],
            name=platform,
            marker_color=colors[i % len(colors)],
            text=[formatted_price],
            textposition='outside',  # 将文本放在柱状图外部，提高可见性
            textfont=dict(
                color='white',  # 确保文本为白色
                size=14,        # 增大字体大小
                family="Arial, sans-serif",  # 使用清晰的字体
            ),
            marker=dict(
                line=dict(
                    width=1,
                    color='rgba(255, 255, 255, 0.5)'  # 添加白色边框增强对比度
                )
            ),
            hovertemplate='%{x}: %{y:.2f}元<extra></extra>'  # 确保悬停时显示两位小数
        ))
    
    fig.update_layout(
        title={
            'text': title,
            'font': {'size': 18, 'color': 'white'},  # 增大标题字体
            'y': 0.95,  # 调整标题位置
        },
        plot_bgcolor='rgba(0,0,0,0.1)',  # 轻微的黑色背景，增强对比度
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white',
            size=14,  # 增大整体字体大小
            family="Arial, sans-serif"  # 使用清晰的字体
        ),
        showlegend=False,
        height=400,  # 适当增加高度，使内容更清晰
        autosize=True,  # 启用自动大小调整
        yaxis=dict(
            title='报价 (元)',
            title_font={'size': 15, 'color': 'white'},  # 轴标题字体大小和颜色
            gridcolor='rgba(255,255,255,0.2)',  # 增加网格线对比度
            tickfont={'size': 13, 'color': 'white'},  # 轴刻度字体大小和颜色
            tickmode='auto',
            nticks=6,  # 控制Y轴刻度数量
            showgrid=True,
            zeroline=True,
            zerolinecolor='rgba(255,255,255,0.3)',  # 零线颜色
            zerolinewidth=1
        ),
        xaxis=dict(
            title='社交媒体平台',
            title_font={'size': 15, 'color': 'white'},  # 轴标题字体大小和颜色
            tickfont={'size': 13, 'color': 'white'},  # 轴刻度字体大小和颜色
            tickangle=0,  # 保持刻度标签水平
        ),
        margin=dict(l=20, r=20, t=80, b=20),  # 增加顶部边距，给标题更多空间
    )
    
    return fig

def create_follower_price_curve(category: str, max_followers: float = 2000000, 
                               steps: int = 50) -> go.Figure:
    """创建粉丝量-价格曲线图"""
    platforms = get_platforms()
    follower_range = np.linspace(0, max_followers, steps)
    
    fig = go.Figure()
    
    # 使用更明亮的颜色以提高对比度
    colors = ['#4169E1', '#9370DB', '#6A5ACD', '#20B2AA']
    
    for i, platform in enumerate(platforms):
        prices = [get_price(platform, category, followers) for followers in follower_range]
        
        fig.add_trace(go.Scatter(
            x=follower_range,
            y=prices,
            mode='lines+markers',  # 添加标记点，增强可读性
            name=platform,
            line=dict(color=colors[i % len(colors)], width=4),  # 增加线宽
            marker=dict(size=6, opacity=0.7),  # 添加小标记点
            hovertemplate="粉丝数: %{x:,.0f}<br>价格: %{y:.2f}元<extra></extra>",
        ))
    
    # 添加粉丝基准点标记
    breakpoints = get_follower_breakpoints()
    if len(breakpoints) > 0:
        for bp in breakpoints:
            if bp <= max_followers:
                fig.add_vline(
                    x=bp, 
                    line=dict(color='rgba(255,255,255,0.4)', dash='dash', width=1.5),  # 增加线的可见度
                    annotation_text=format_large_number(bp),
                    annotation_position="top right",
                    annotation_font=dict(color="white", size=12)  # 确保标注文字清晰
                )
    
    fig.update_layout(
        title={
            'text': f'{category}类别不同粉丝量的价格曲线',
            'font': {'size': 18, 'color': 'white'}  # 增大标题字体
        },
        xaxis_title={
            'text': '粉丝数量',
            'font': {'size': 14, 'color': 'white'}  # 轴标题字体
        },
        yaxis_title={
            'text': '价格 (元)',
            'font': {'size': 14, 'color': 'white'}  # 轴标题字体
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white',
            size=13,  # 增大整体字体大小
            family="Arial, sans-serif"  # 使用清晰的字体
        ),
        height=450,  # 减少高度，更适合移动端
        autosize=True,  # 启用自动大小调整
        xaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',  # 增加网格线对比度
            tickvals=breakpoints,
            ticktext=[format_large_number(bp) for bp in breakpoints],
            tickfont={'size': 12, 'color': 'white'}  # 确保刻度标签清晰
        ),
        yaxis=dict(
            gridcolor='rgba(255,255,255,0.2)',  # 增加网格线对比度
            tickfont={'size': 12, 'color': 'white'}  # 确保刻度标签清晰
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=13, color="white"),  # 增加图例字体大小
            bgcolor="rgba(0,0,0,0.4)",  # 添加半透明背景提高对比度
            bordercolor="rgba(255,255,255,0.3)",
            borderwidth=1
        ),
        margin=dict(l=20, r=20, t=100, b=40),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
    )
    
    return fig

def create_category_comparison_radar(followers: float, platform: Optional[str] = None) -> go.Figure:
    """创建不同类别的价格雷达图"""
    categories = get_categories()
    
    if platform:
        # 单一平台的所有类别
        values = [get_price(platform, category, followers) for category in categories]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name=platform,
            line=dict(
                color='rgba(65, 105, 225, 0.9)',  # 增加颜色饱和度
                width=3  # 增加线宽
            ),
            fillcolor='rgba(65, 105, 225, 0.3)',  # 增加填充透明度
            hovertemplate='%{theta}: %{r:.2f}元<extra></extra>'  # 添加悬浮提示
        ))
        
        title = f'{platform}平台在{format_large_number(followers)}粉丝量下各类别价格'
    else:
        # 所有平台的所有类别
        platforms = get_platforms()
        
        fig = go.Figure()
        # 使用更饱和的颜色
        colors = ['rgba(65, 105, 225, 0.9)', 'rgba(138, 43, 226, 0.9)', 
                 'rgba(72, 61, 139, 0.9)', 'rgba(106, 90, 205, 0.9)']
        
        for i, platform in enumerate(platforms):
            values = [get_price(platform, category, followers) for category in categories]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=platform,
                line=dict(
                    color=colors[i % len(colors)],
                    width=3  # 增加线宽
                ),
                fillcolor=colors[i % len(colors)].replace('0.9', '0.3'),  # 调整填充透明度
                hovertemplate='%{theta}: %{r:.2f}元<extra></extra>'  # 添加悬浮提示
            ))
        
        title = f'各平台在{format_large_number(followers)}粉丝量下不同类别价格对比'
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                gridcolor='rgba(255,255,255,0.25)',  # 增加网格线对比度
                linecolor='rgba(255,255,255,0.5)',   # 增加轴线对比度
                angle=45,  # 调整径向轴标签角度
                tickfont=dict(size=12, color='white')  # 径向轴刻度标签
            ),
            angularaxis=dict(
                gridcolor='rgba(255,255,255,0.25)',  # 增加网格线对比度
                linecolor='rgba(255,255,255,0.5)',   # 增加轴线对比度
                tickfont=dict(size=11, color='white', family="Arial, sans-serif")  # 角度轴刻度标签
            ),
            bgcolor='rgba(0,0,0,0)',
        ),
        title={
            'text': title,
            'font': {'size': 18, 'color': 'white'}  # 增大标题字体
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white',
            size=13,
            family="Arial, sans-serif"
        ),
        height=500,  # 减少高度，更适合移动端
        autosize=True,  # 启用自动大小调整
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5,
            font=dict(size=13, color="white"),  # 增加图例字体大小
            bgcolor="rgba(0,0,0,0.4)",  # 添加半透明背景提高对比度
            bordercolor="rgba(255,255,255,0.3)",
            borderwidth=1
        ),
        margin=dict(l=40, r=40, t=100, b=50),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
    )
    
    return fig

def create_platform_coefficient_heatmap(selected_categories: Optional[List[str]] = None) -> go.Figure:
    """创建平台系数热力图"""
    from pricing_module import COEFF_MATRIX
    
    platforms = get_platforms()
    
    if not selected_categories:
        categories = get_categories()
    else:
        categories = selected_categories
    
    # 准备热力图数据
    data = []
    for category in categories:
        row = [COEFF_MATRIX[category].get(platform, 1.0) for platform in platforms]
        data.append(row)
    
    df = pd.DataFrame(data, index=categories, columns=platforms)
    
    # 创建热力图 - 使用更适合深色背景的配色方案
    fig = px.imshow(
        df, 
        labels=dict(x="平台", y="内容类别", color="系数"),
        x=platforms,
        y=categories,
        color_continuous_scale='Plasma',  # 改用Plasma配色方案，在黑色背景上更加清晰
        aspect="auto",
        zmin=0.5,  # 设置最小值使颜色对比更明显
        zmax=2.0,  # 设置最大值
    )
    
    fig.update_layout(
        title={
            'text': '内容类别在不同平台的系数热力图',
            'font': {'size': 18, 'color': 'white'}  # 增大标题字体
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white',
            size=13,
            family="Arial, sans-serif"
        ),
        height=max(350, len(categories) * 18),  # 减少高度，更适合移动端
        autosize=True,  # 启用自动大小调整
        xaxis=dict(
            title={
                'text': '平台',
                'font': {'size': 14, 'color': 'white'}
            },
            side='top',
            tickfont={'size': 12, 'color': 'white'}
        ),
        yaxis=dict(
            title={
                'text': '内容类别',
                'font': {'size': 14, 'color': 'white'}
            },
            tickfont={'size': 12, 'color': 'white'}
        ),
        margin=dict(l=20, r=40, t=100, b=40),  # 显著增加顶部和底部边距，为颜色条提供更多空间
        coloraxis=dict(
            colorbar=dict(
                title={
                    'text': '系数值',
                    'font': {'size': 12, 'color': 'white'}
                },
                tickfont={'color': 'white', 'size': 12},
                outlinecolor='rgba(255,255,255,0.3)',
                outlinewidth=1
            )
        )
    )
    
    # 添加文本标注
    for i in range(len(categories)):
        for j in range(len(platforms)):
            # 根据系数值确定文本颜色，确保在各种背景下都清晰可见
            value = df.iloc[i, j]
            if value <= 0.8:
                text_color = "white"  # 低值区域用白色文本
            elif value <= 1.2:
                text_color = "yellow"  # 中值区域用黄色文本
            else:
                text_color = "black"  # 高值区域用黑色文本
            
            fig.add_annotation(
                x=j,
                y=i,
                text=f"{value:.2f}",
                showarrow=False,
                font=dict(
                    color=text_color,
                    size=12,
                    family="Arial, sans-serif"
                )
            )
    
    return fig

def create_top_categories_chart(followers: float, platform: str, n: int = 10) -> go.Figure:
    """创建指定平台下报价最高的前N个类别图表"""
    categories = get_categories()
    
    prices = []
    for category in categories:
        price = get_price(platform, category, followers)
        prices.append((category, price))
    
    # 按价格降序排序
    prices.sort(key=lambda x: x[1], reverse=True)
    
    # 取前N个
    top_categories = [p[0] for p in prices[:n]]
    top_prices = [p[1] for p in prices[:n]]
    
    # 创建水平条形图 - 使用渐变色使图表更加美观
    color_scale = px.colors.sequential.Blues_r  # 使用反转的蓝色渐变色
    # 生成一个颜色梯度，让排名靠前的类别颜色更深
    colors = [color_scale[int(i * (len(color_scale)-1) / (n-1) if n > 1 else 0)] for i in range(n)]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_categories,
        x=top_prices,
        orientation='h',
        marker=dict(
            color=colors,
            opacity=0.9,  # 增加不透明度
            line=dict(width=1, color='rgba(255,255,255,0.3)')  # 添加细微边框
        ),
        text=[format_price(p) for p in top_prices],
        textposition='auto',
        textfont=dict(
            color='white',  # 确保文本为白色
            size=13,        # 增大字体大小
            family="Arial, sans-serif"  # 使用清晰的字体
        ),
        hovertemplate='%{y}: %{x:.2f}元<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': f'{platform}平台{format_large_number(followers)}粉丝量下报价最高的{n}个类别',
            'font': {'size': 18, 'color': 'white'}  # 增大标题字体
        },
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(
            color='white',
            size=13,
            family="Arial, sans-serif"
        ),
        height=max(400, n * 28),  # 减少高度，更适合移动端，但仍保持动态调整
        autosize=True,  # 启用自动大小调整
        xaxis=dict(
            title={
                'text': '报价 (元)',
                'font': {'size': 14, 'color': 'white'}
            },
            gridcolor='rgba(255,255,255,0.2)',  # 增加网格线对比度
            tickfont={'size': 12, 'color': 'white'},  # 确保刻度标签清晰
            showgrid=True
        ),
        yaxis=dict(
            title={
                'text': '内容类别',
                'font': {'size': 14, 'color': 'white'}
            },
            categoryorder='total ascending',
            tickfont={'size': 12, 'color': 'white'}  # 确保刻度标签清晰
        ),
        margin=dict(l=20, r=20, t=100, b=40),  # 显著增加顶部和底部边距，解决移动端标题重叠问题
    )
    
    return fig
