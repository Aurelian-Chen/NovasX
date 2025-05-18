import streamlit as st

st.set_page_config(
    page_title="潜星云集 - 基础测试",
    page_icon="📊",
)

st.title("潜星云集 - 网红广告自动估价系统")
st.write("这是一个基础版本，用于测试应用程序是否能正常运行")

st.sidebar.title("测试功能")
option = st.sidebar.selectbox("选择平台", ["抖音", "小红书", "B站", "快手"])
followers = st.sidebar.number_input("粉丝数量", value=100000)

st.write(f"选择的平台: {option}")
st.write(f"输入的粉丝数: {followers:,}")

if st.button("计算价格"):
    st.success(f"示例价格: ¥{followers * 0.01:.2f}")