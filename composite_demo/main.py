import streamlit as st
import pandas as pd
import os

# 设置页面配置
st.set_page_config(
    page_title="PlotAgent Demo",
    page_icon=":hammer_and_wrench:",
    layout='centered',
    initial_sidebar_state='expanded',
)

import demo_tool

# 设置标题
st.title("PlotAgent Demo")

# 侧边栏参数配置
with st.sidebar:
    top_p = st.slider('top_p', 0.0, 1.0, 0.8, step=0.01)
    temperature = st.slider('temperature', 0.0, 1.5, 0.95, step=0.01)
    repetition_penalty = st.slider('repetition_penalty', 0.0, 2.0, 1.1, step=0.01)
    max_new_token = st.slider('Output length', 5, 32000, 256, step=1)

    # 重试和清除历史记录按钮
    cols = st.columns(2)
    export_btn = cols[0]
    clear_history = cols[1].button("Clear History", use_container_width=True)
    retry = export_btn.button("Retry", use_container_width=True)

# 工具模式下的输入框
prompt_text = st.chat_input('Enter your input for the tool!', key='tool_input')

# 清除历史记录或重试的逻辑
if clear_history or retry:
    prompt_text = ""

# 运行工具主函数
demo_tool.main(
    retry=retry,
    top_p=top_p,
    temperature=temperature,
    prompt_text=prompt_text,
    repetition_penalty=repetition_penalty,
    max_new_tokens=max_new_token,
    truncate_length=1024
)

# CSV 文件路径
csv_file_path = "extracted_table.csv"

# 定期检查 CSV 文件是否存在并可视化表格
if os.path.exists(csv_file_path) and os.path.getsize(csv_file_path) > 0:
    # 读取并可视化表格
    df = pd.read_csv(csv_file_path)
    st.subheader("Generated Table:")
    st.dataframe(df)
else:
    st.write("No table data available yet.")

# 图片文件路径
pie_chart_file = "pie_chart.png"  # 假设饼图文件名为此
line_chart_file = "line_chart.png"  # 假设折线图文件名为此

# 检查饼状图是否存在
if os.path.exists(pie_chart_file) and os.path.getsize(pie_chart_file) > 0:
    st.subheader("Generated Pie Chart:")
    st.image(pie_chart_file)
else:
    st.write("No pie chart available yet.")

# 检查折线图是否存在
if os.path.exists(line_chart_file) and os.path.getsize(line_chart_file) > 0:
    st.subheader("Generated Line Chart:")
    st.image(line_chart_file)
else:
    st.write("No line chart available yet.")
