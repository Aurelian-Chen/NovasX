import streamlit as st
import pandas as pd
import numpy as np
import base64
import plotly.graph_objects as go
from pathlib import Path

# 函数：将图片转换为base64编码
def img_to_base64(img_path):
    img_path = Path(img_path)
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# 配置页面基本信息
st.set_page_config(
    page_title="潜星云集 - 简化版测试",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 获取logo的base64编码
try:
    # 尝试多个可能的路径
    logo_paths = ["static/logo.png", "attached_assets/logo- white_1743183316407.png"]
    logo_base64 = None
    
    for path in logo_paths:
        try:
            logo_base64 = img_to_base64(path)
            st.write(f"成功加载logo: {path}")
            break
        except Exception as e:
            st.write(f"加载失败 {path}: {str(e)}")
    
    if logo_base64:
        # 使用HTML显示logo
        st.markdown(f'<img src="data:image/png;base64,{logo_base64}" width="100">', unsafe_allow_html=True)
    else:
        st.write("所有logo路径加载失败")
except Exception as e:
    st.write(f"整体logo加载失败: {str(e)}")

# 应用标题和简介
st.title("潜星云集 - 测试版")
st.subheader("这是一个简化版的测试应用")

# 侧边栏
with st.sidebar:
    st.header("测试功能")
    option = st.selectbox("选择平台", ["抖音", "小红书", "B站", "快手"])
    followers = st.number_input("粉丝数量", value=100000)
    st.button("测试按钮")

# 主内容区
st.write(f"选择的平台: {option}")
st.write(f"输入的粉丝数: {followers:,}")

# 创建简单图表
data = pd.DataFrame({
    "平台": ["抖音", "小红书", "B站", "快手"],
    "价格": [10000, 8000, 7000, 6000]
})

fig = go.Figure(go.Bar(
    x=data["平台"],
    y=data["价格"],
    marker_color=["#FF6347", "#4169E1", "#32CD32", "#FFD700"]
))

fig.update_layout(
    title="示例图表",
    xaxis_title="平台",
    yaxis_title="价格（元）",
)

st.plotly_chart(fig, use_container_width=True)

# 显示环境信息
st.subheader("环境信息")
st.write("Python版本:", st.version_info)
st.write("服务器地址:", "0.0.0.0")
st.write("服务器端口:", 5000)