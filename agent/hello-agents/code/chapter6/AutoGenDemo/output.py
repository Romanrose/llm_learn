import streamlit as st
import requests
import json

# 数据获取函数
def get_bitcoin_price():
    try:
        # 获取 Bitcoin 的价格数据
        response = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_24hr_change=true')
        data = response.json()
        # 获取当前价格和24小时变化
        current_price = data['bitcoin']['usd']
        price_change_percentage = data['bitcoin']['usd_24h_change']

        return current_price, price_change_percentage
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return None, None

# 初始化 Streamlit 应用
st.title('实时比特币价格')
st.subheader('获取最新的比特币价格信息及其24小时价格变化趋势')

# 添加刷新按钮
if st.button('刷新价格'):
    st.experimental_rerun()

# 显示加载状态
with st.spinner('加载中...'):
    current_price, price_change_percentage = get_bitcoin_price()

# 显示数据
if current_price is not None:
    st.metric(label="当前比特币价格 (USD)", value=f"${current_price}")

    if price_change_percentage is not None:
        st.metric(label="24小时变化 (%)", value=f"{price_change_percentage:.2f}%")
else:
    st.error("无法获取数据，请稍后重试。")