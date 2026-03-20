#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri March 20 11:43 2026

@author: adele
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import folium_static

# ---------------------- 1. 页面配置（与原代码风格统一） ----------------------
st.set_page_config(page_title="Internet Slang Dashboard", page_icon="🛜", layout="wide")
st.title("🛜 Internet Slang Analysis Dashboard 🛜")

# ---------------------- 2. 加载数据（缓存优化，适配你的CSV） ----------------------
@st.cache_data
def load_data():
    # 读取你的CSV文件（本地运行时替换为你的文件路径）
    df = pd.read_csv("internet_slang.csv", encoding='utf-8-sig')
    
    # 数据预处理：处理#1-#7 @1-@7列（转为数值型，缺失值填0）
    num_cols = [col for col in df.columns if col.startswith(('#', '@')) and col not in ['#']]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 计算#1-#7 @1-@7的总和列
    df['#_Total'] = df[[col for col in num_cols if col.startswith('#')]].sum(axis=1)
    df['@_Total'] = df[[col for col in num_cols if col.startswith('@')]].sum(axis=1)
    
    return df

df = load_data()

# ---------------------- 3. 数据预览（原代码风格） ----------------------
st.header("📊 Sample of Processed Data")
st.dataframe(df[['Gender', 'Age', 'Residence', 'Acquisition_Channel', 'Using_Scene', '#_Total', '@_Total']].head(10))

# ---------------------- 4. 侧边栏过滤器（按核心维度筛选） ----------------------
st.sidebar.header("Filter Data 🔍")

# 性别筛选
selected_gender = st.sidebar.multiselect(
    "Select Gender:", df['Gender'].unique(), default=df['Gender'].unique())

# 年龄筛选
selected_age = st.sidebar.multiselect(
    "Select Age Group:", df['Age'].unique(), default=df['Age'].unique())

# 常住地筛选
selected_residence = st.sidebar.multiselect(
    "Select Residence:", df['Residence'].unique(), default=df['Residence'].unique())

# 应用筛选条件
filtered_df = df[
    df['Gender'].isin(selected_gender) & 
    df['Age'].isin(selected_age) & 
    df['Residence'].isin(selected_residence)
]

st.sidebar.markdown(f"**Filtered Samples**: {len(filtered_df)}/{len(df)}")

# ---------------------- 5. 核心指标卡片（原代码风格） ----------------------
st.header("📈 Key Metrics")
col1, col2, col3, col4 = st.columns(4)

# #1-#7总和均值
avg_hash_total = filtered_df['#_Total'].mean()
col1.metric(label="Avg #1-#7 Total", value=f"{avg_hash_total:.1f}")

# @1-@7总和均值
avg_at_total = filtered_df['@_Total'].mean()
col2.metric(label="Avg @1-@7 Total", value=f"{avg_at_total:.1f}")

# 男女比例（计算占比）
male_ratio = (filtered_df['Gender'] == 1).sum() / len(filtered_df) * 100
col3.metric(label="Male Ratio", value=f"{male_ratio:.1f}%")

# 主要常住地占比（取最多的常住地）
top_residence = filtered_df['Residence'].value_counts().index[0]
top_residence_ratio = filtered_df['Residence'].value_counts().iloc[0] / len(filtered_df) * 100
col4.metric(label=f"Top Residence ({top_residence})", value=f"{top_residence_ratio:.1f}%")

# ---------------------- 6. 需求1：#1-#7 @1-@7与年龄/性别的关系（散点图） ----------------------
st.header("🔗 #1-#7 / @1-@7 vs Gender/Age")
col1, col2 = st.columns(2)

# #1-#7总和与性别的关系（箱线图）
fig_hash_gender = px.box(
    filtered_df, x='Gender', y='#_Total', 
    title="#1-#7 Total vs Gender (0=Female, 1=Male)",
    labels={'#_Total': '#1-#7 Sum', 'Gender': 'Gender (0=Female, 1=Male)'},
    color='Gender', color_discrete_sequence=px.colors.qualitative.Prism
)
col1.plotly_chart(fig_hash_gender, use_container_width=True)

# @1-@7总和与年龄的关系（箱线图）
fig_at_age = px.box(
    filtered_df, x='Age', y='@_Total', 
    title="@1-@7 Total vs Age Group",
    labels={'@_Total': '@1-@7 Sum', 'Age': 'Age Group'},
    color='Age', color_discrete_sequence=px.colors.qualitative.Prism
)
col2.plotly_chart(fig_at_age, use_container_width=True)

# ---------------------- 7. 需求2-4：饼图（性别、常住地、年龄） ----------------------
st.header("🥧 Distribution Analysis")
col1, col2, col3 = st.columns(3)

# 需求2：男女比例饼图
gender_counts = filtered_df['Gender'].value_counts().reset_index()
gender_counts['Gender_Label'] = gender_counts['Gender'].map({0: 'Female', 1: 'Male'})
fig_gender_pie = px.pie(
    gender_counts, names='Gender_Label', values='count',
    title="Gender Distribution", hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Prism
)
col1.plotly_chart(fig_gender_pie, use_container_width=True)

# 需求3：常住地饼图
residence_counts = filtered_df['Residence'].value_counts().reset_index()
fig_residence_pie = px.pie(
    residence_counts, names='Residence', values='count',
    title="Residence Distribution", hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Prism
)
col2.plotly_chart(fig_residence_pie, use_container_width=True)

# 需求4：年龄饼图
age_counts = filtered_df['Age'].value_counts().reset_index()
fig_age_pie = px.pie(
    age_counts, names='Age', values='count',
    title="Age Group Distribution", hole=0.4,
    color_discrete_sequence=px.colors.qualitative.Prism
)
col3.plotly_chart(fig_age_pie, use_container_width=True)

# ---------------------- 8. 需求5：IP定位地图（带标记点） ----------------------


# ---------------------- 9. 需求6：获取渠道柱状图对比 ----------------------
st.header("📊 Acquisition Channel Comparison")

# 处理多选项（按┋拆分，统计每个渠道的频次）
@st.cache_data
def count_multi_options(df_col):
    channel_counts = {}
    for val in df_col.dropna():
        channels = str(val).split('┋')
        for ch in channels:
            if ch.strip() != '':
                channel_counts[ch.strip()] = channel_counts.get(ch.strip(), 0) + 1
    return pd.DataFrame(list(channel_counts.items()), columns=['Channel', 'Count'])

# 统计获取渠道频次
channel_df = count_multi_options(filtered_df['Acquisition_Channel'])

# 绘制柱状图
fig_channel_bar = px.bar(
    channel_df.sort_values('Count', ascending=False),
    x='Channel', y='Count',
    title="Frequency of Internet Slang Acquisition Channels",
    labels={'Count': 'Number of Users', 'Channel': 'Acquisition Channel'},
    color='Channel', color_discrete_sequence=px.colors.qualitative.Prism
)
st.plotly_chart(fig_channel_bar, use_container_width=True)

# ---------------------- 10. 需求7：使用场景柱状图对比 ----------------------
st.header("📊 Usage Scene Comparison")

# 统计使用场景频次
scene_df = count_multi_options(filtered_df['Using_Scene'])

# 绘制柱状图
fig_scene_bar = px.bar(
    scene_df.sort_values('Count', ascending=False),
    x='Scene', y='Count',
    title="Frequency of Internet Slang Usage Scenes",
    labels={'Count': 'Number of Users', 'Scene': 'Usage Scene'},
    color='Scene', color_discrete_sequence=px.colors.qualitative.Prism
)
st.plotly_chart(fig_scene_bar, use_container_width=True)

# ---------------------- 11. 特殊发现报告 ----------------------
st.header("🔍 Key Insights & Findings")

# 发现1：#1-#7 @1-#7与性别的关联
male_hash_avg = filtered_df[filtered_df['Gender'] == 1]['#_Total'].mean()
female_hash_avg = filtered_df[filtered_df['Gender'] == 0]['#_Total'].mean()
gender_insight = f"1. Male users have a higher average #1-#7 total ({male_hash_avg:.1f}) than female users ({female_hash_avg:.1f})."

# 发现2：主要获取渠道
top_channel = channel_df.sort_values('Count', ascending=False).iloc[0]['Channel']
top_channel_count = channel_df.sort_values('Count', ascending=False).iloc[0]['Count']
channel_insight = f"2. The most popular acquisition channel is '{top_channel}' (used by {top_channel_count} users, {top_channel_count/len(filtered_df)*100:.1f}% of samples)."

# 发现3：主要使用场景
top_scene = scene_df.sort_values('Count', ascending=False).iloc[0]['Scene']
top_scene_count = scene_df.sort_values('Count', ascending=False).iloc[0]['Count']
scene_insight = f"3. The most common usage scene is '{top_scene}' (used by {top_scene_count} users, {top_scene_count/len(filtered_df)*100:.1f}% of samples)."

# 发现4：常住地分布
top_res = filtered_df['Residence'].value_counts().index[0]
top_res_pct = filtered_df['Residence'].value_counts().iloc[0]/len(filtered_df)*100
residence_insight = f"4. {top_res} is the most common residence ({top_res_pct:.1f}% of samples)."

# 显示发现
st.markdown(f"- {gender_insight}")
st.markdown(f"- {channel_insight}")
st.markdown(f"- {scene_insight}")
st.markdown(f"- {residence_insight}")
