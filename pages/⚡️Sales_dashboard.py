import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import altair as alt
from datetime import date
from streamlit_extras.dataframe_explorer import dataframe_explorer
from streamlit_extras.metric_cards import style_metric_cards
from matplotlib import pyplot as plt

# Cấu hình trang
st.set_page_config(page_title="Doanh Số", page_icon="🔆", layout="wide")

st.header("PHÂN TÍCH KPI & TRENDS DOANH SỐ | PHÂN TÍCH MÔ TẢ")
st.write("Chọn khoảng thời gian thành lập từ thanh bên để xem xu hướng doanh số")

# Tải CSS tùy chỉnh
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Tải dữ liệu
df = pd.read_csv('sales_data.csv')

# Bộ lọc năm để xem doanh số
with st.sidebar:
    st.title("Chọn Khoảng Thời Gian")
    start_year = st.number_input("Năm Bắt Đầu", min_value=int(df['Outlet_Establishment_Year'].min()), max_value=int(df['Outlet_Establishment_Year'].max()), value=date.today().year - 4)
    end_year = st.number_input("Năm Kết Thúc", min_value=int(df['Outlet_Establishment_Year'].min()), max_value=int(df['Outlet_Establishment_Year'].max()), value=date.today().year)

st.error(f"Các chỉ số kinh doanh giữa [{start_year}] và [{end_year}]")

# So sánh năm
df2 = df[(df['Outlet_Establishment_Year'] >= start_year) & (df['Outlet_Establishment_Year'] <= end_year)]

# Hiển thị dataframe
with st.expander("Lọc Dữ Liệu CSV"):
    filtered_df = dataframe_explorer(df2, case=False)
    st.dataframe(filtered_df, use_container_width=True)



st.subheader('Thêm Bản Ghi Mới vào Tệp CSV')
# Hàm này được gọi từ một tệp khác tên là 'new_data.py'
from new_data import add_data
add_data()


st.subheader('Các Chỉ Số Dữ Liệu')
col1, col2 = st.columns(2)
col1.metric(label="Tất Cả Các Sản Phẩm Trong Các Cửa Hàng", value=df2['Item_Identifier'].count(), delta="Số Lượng Mặt Hàng Trong Cửa Hàng")
col2.metric(label="Tổng Giá Sản Phẩm (USD):", value=f"{df2['Item_MRP'].sum():,.0f}", delta=df2['Item_MRP'].median())

col11, col22, col33 = st.columns(3)
col11.metric(label="Giá Cao Nhất (USD):", value=f"{df2['Item_MRP'].max():,.0f}", delta="Giá Cao")
col22.metric(label="Giá Thấp Nhất (USD):", value=f"{df2['Item_MRP'].min():,.0f}", delta="Giá Thấp")
col33.metric(label="Khoảng Giá Tổng (USD):", value=f"{df2['Item_MRP'].max() - df2['Item_MRP'].min():,.0f}", delta="Khoảng Giá Chênh Lệch")

# Cấu hình thẻ chỉ số
style_metric_cards(background_color="#FFFFFF", border_left_color="#686664", border_color="#000000", box_shadow="#F71938")

# Biểu đồ điểm
a1, a2 = st.columns(2)
with a1:
    st.subheader('Sản Phẩm & Giá Tổng')
    source = df2
    chart = alt.Chart(source).mark_circle().encode(
        x='Item_Type',
        y='Item_MRP',
        color='Item_Fat_Content',
    ).interactive()
    st.altair_chart(chart, use_container_width=True)

with a2:
    st.subheader('Sản Phẩm & Giá Đơn Vị')
    
    # Nhóm dữ liệu theo Item_Type và tính tổng giá
    energy_source = df2.groupby('Item_Type').agg({'Item_MRP': 'sum'}).reset_index()
    energy_source.rename(columns={'Item_MRP': 'Total Price (USD)'}, inplace=True)

    # Biểu đồ cột
    bar_chart = alt.Chart(energy_source).mark_bar().encode(
        x='Item_Type:N',  # Thêm trục x để hiển thị loại mặt hàng
        y='Total Price (USD):Q',
        color='Item_Type:N'
    )
    st.altair_chart(bar_chart, use_container_width=True)

# Chọn chỉ số số học hoặc dữ liệu số
p1, p2 = st.columns(2)


# Assuming df2 is your DataFrame
with p1:
    

    # Tạo biểu đồ cột để so sánh tổng doanh thu theo loại cửa hàng
    st.subheader("Tổng Doanh Thu Bán Hàng Theo Loại Cửa Hàng")
    total_sales = df2.groupby(['Outlet_Location_Type', 'Outlet_Type']).agg({'Item_Outlet_Sales': 'sum'}).reset_index()

    bar_chart = alt.Chart(total_sales).mark_bar().encode(
        x='Outlet_Type:N',
        y='Item_Outlet_Sales:Q',
        color='Outlet_Location_Type:N'
    ).properties(
        title="Tổng Doanh Thu Bán Hàng theo Loại Cửa Hàng"
    )

    st.altair_chart(bar_chart, use_container_width=True)
with p2:
    st.subheader('Sản Phẩm & Số Lượng')
    source = pd.DataFrame({
        "Quantity": df2["Item_Outlet_Sales"],
        "Item_Type": df2["Item_Type"]
    })

    bar_chart = alt.Chart(source).mark_bar().encode(
        x="sum(Quantity):Q",
        y=alt.Y("Item_Type:N", sort="-x")
    )
    st.altair_chart(bar_chart, use_container_width=True)
df2_encoded = df2.copy()
for col in df2_encoded.select_dtypes(include=['object']).columns:
    df2_encoded[col] = pd.factorize(df2_encoded[col])[0] + 1

# Lựa chọn tính năng cho dữ liệu định tính và định lượng
feature_x_options = df2.select_dtypes(include=['object']).columns.tolist()
feature_y_options = df2.select_dtypes(include=['number']).columns.tolist()

# Loại bỏ các cột không cần thiết
unwanted_cols = ['Item_Fat_Content', 'Item_Identifier']
feature_x_options = [col for col in feature_x_options if col not in unwanted_cols]

# Streamlit selectbox để chọn tính năng
feature_x = st.selectbox('Chọn tính năng cho dữ liệu định tính', feature_x_options)
feature_y = st.selectbox('Chọn tính năng cho dữ liệu định lượng', feature_y_options)

if feature_x and feature_y:
    # Vẽ biểu đồ phân tán
    fig, ax = plt.subplots()
    sns.scatterplot(data=df2_encoded, x=feature_x, y=feature_y, ax=ax)
    
    # Thêm chú thích các giá trị của cột đối tượng gốc
    labels = pd.factorize(df2[feature_x])[1]  # Lấy các giá trị gốc của cột đối tượng
    for index, label in enumerate(labels):
        ax.text(index+1, df2_encoded[feature_y].max(), str(index +1), ha='center', va='bottom')
    
    ax.set_xlabel(feature_x)
    ax.set_ylabel(feature_y)
    
    # Hiển thị bản chú thích lên màn hình
    st.write("Bản chú thích các giá trị của", feature_x)
    for index, label in enumerate(labels):
        st.write(f"{index + 1}: {label}")
    
    st.pyplot(fig)
st.sidebar.image("img/logo.png")
