import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
from matplotlib import pyplot as plt
import plotly.graph_objs as go
from datetime import date

st.set_option('deprecation.showPyplotGlobalUse', False)

# Cấu hình trang
st.set_page_config(page_title="Bảng điều khiển", page_icon="🔆", layout="wide")
st.header("XỬ LÝ PHÂN TÍCH, KPI, XU HƯỚNG & DỰ ĐOÁN")

# Tải CSS tùy chỉnh
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Tải dữ liệu
df = pd.read_csv('sales_data.csv')

# ---------------- Sidebar Menu + Bộ lọc ----------------
def sideBar():
    with st.sidebar:
        # Menu chính
        selected = option_menu(
            menu_title="Menu Chính",
            options=["Trang Chính", "Tiến Độ"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )

        st.markdown("---")

        # Bộ lọc năm
        st.subheader("Chọn Khoảng Thời Gian")
        min_year = int(df['Outlet_Establishment_Year'].min())
        max_year = int(df['Outlet_Establishment_Year'].max())

        start_year_default = max(min_year, date.today().year - 4)
        end_year_default = min(max_year, date.today().year)

        start_year = st.number_input(
            "Năm Bắt Đầu",
            min_value=min_year,
            max_value=max_year,
            value=start_year_default
        )
        end_year = st.number_input(
            "Năm Kết Thúc",
            min_value=min_year,
            max_value=max_year,
            value=end_year_default
        )

        st.markdown("---")

        # Bộ lọc loại mặt hàng và cửa hàng
        item_type = st.multiselect(
            "CHỌN LOẠI MẶT HÀNG",
            options=df["Item_Type"].unique(),
            default=df["Item_Type"].unique(),
        )
        outlet_location_type = st.multiselect(
            "CHỌN LOẠI ĐỊA ĐIỂM BÁN HÀNG",
            options=df["Outlet_Location_Type"].unique(),
            default=df["Outlet_Location_Type"].unique(),
        )
        outlet_type = st.multiselect(
            "CHỌN LOẠI CỬA HÀNG",
            options=df["Outlet_Type"].unique(),
            default=df["Outlet_Type"].unique(),
        )

    return selected, start_year, end_year, item_type, outlet_location_type, outlet_type

# ---------------- Lọc dữ liệu theo sidebar ----------------
selected, start_year, end_year, item_type, outlet_location_type, outlet_type = sideBar()

df_selection = df.query(
    "Item_Type == @item_type & Outlet_Location_Type == @outlet_location_type & Outlet_Type == @outlet_type & Outlet_Establishment_Year >= @start_year & Outlet_Establishment_Year <= @end_year"
)

st.sidebar.image("img/logo.png", caption="")

# ---------------- Trang Chính ----------------
def Home():
    with st.expander("XEM DỮ LIỆU CSV"):
        showData = st.multiselect('Lọc: ', df_selection.columns, default=df_selection.columns.tolist())
        st.dataframe(df_selection[showData], use_container_width=True)

    # Tính toán KPI
    total_sales = df_selection['Item_Outlet_Sales'].sum()
    sales_max = df_selection['Item_Outlet_Sales'].max()
    sales_mean = df_selection['Item_Outlet_Sales'].mean()
    sales_median = df_selection['Item_Outlet_Sales'].median()

    col1, col2, col3, col4 = st.columns(4, gap='small')
    col1.metric("Tổng Doanh Thu", f"{total_sales:,.0f}")
    col2.metric("Doanh Thu Cao Nhất", f"{sales_max:,.0f}")
    col3.metric("Doanh Thu Trung Bình", f"{sales_mean:,.0f}")
    col4.metric("Doanh Thu Trung Tâm", f"{sales_median:,.0f}")

    style_metric_cards(background_color="#FFFFFF", border_left_color="#686664",
                       border_color="#000000", box_shadow="#F71938")

    # Biểu đồ phân phối
    with st.expander("PHÂN PHỐI THEO TẦN SUẤT"):
        df_selection.hist(figsize=(16, 8), color='#898784', zorder=2, rwidth=0.9)
        st.pyplot()

# ---------------- Biểu đồ ----------------
def graphs():
    # Doanh thu theo loại mặt hàng
    sales_by_item_type = df_selection.groupby("Item_Type")['Item_Outlet_Sales'].sum().sort_values()
    fig_sales_item_type = px.bar(
        sales_by_item_type,
        x=sales_by_item_type.values,
        y=sales_by_item_type.index,
        orientation="h",
        title="<b> DOANH THU THEO LOẠI MẶT HÀNG </b>",
        color_discrete_sequence=["#0083B8"]*len(sales_by_item_type),
        template="plotly_white"
    )
    fig_sales_item_type.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor='rgba(0,0,0,0)',
                                      yaxis=dict(showgrid=True, gridcolor='#cecdcd'))

    # Doanh thu theo loại địa điểm
    sales_outlet_location = df_selection.groupby("Outlet_Location_Type")['Item_Outlet_Sales'].sum()
    fig_sales_outlet_location = px.line(
        sales_outlet_location,
        x=sales_outlet_location.index,
        y=sales_outlet_location.values,
        title="<b> DOANH THU THEO LOẠI ĐỊA ĐIỂM BÁN HÀNG </b>",
        color_discrete_sequence=["#0083b8"]*len(sales_outlet_location),
        template="plotly_white"
    )
    fig_sales_outlet_location.update_layout(plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(showgrid=True))

    left, right, center = st.columns(3)
    left.plotly_chart(fig_sales_outlet_location, use_container_width=True)
    right.plotly_chart(fig_sales_item_type, use_container_width=True)
    
    with center:
        fig_pie = px.pie(df_selection, values='Item_Outlet_Sales', names='Outlet_Type',
                         title='DOANH THU THEO LOẠI CỬA HÀNG')
        fig_pie.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Boxplot theo Item_Type
    st.subheader('PHÂN PHỐI QUARTILES')
    feature_y = st.selectbox('Chọn tính năng số', df_selection.select_dtypes("number").columns)
    fig2 = go.Figure(
        data=[go.Box(x=df_selection['Item_Type'], y=df_selection[feature_y])],
        layout=go.Layout(
            title=go.layout.Title(text="LOẠI MẶT HÀNG THEO PHÂN VỊ QUARTILES CỦA DOANH THU"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            font=dict(color='#cecdcd'),
        )
    )
    st.plotly_chart(fig2, use_container_width=True)

# ---------------- Tiến Độ ----------------
def Progressbar():
    st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""", unsafe_allow_html=True)
    target = 30000000
    current = df_selection["Item_Outlet_Sales"].sum()
    percent = round((current / target * 100))
    mybar = st.progress(0)

    if percent > 100:
        st.subheader("Đã hoàn thành mục tiêu!")
    else:
        st.write("Bạn đã đạt ", percent, "% của ", format(target, 'd'), " Doanh Thu")
        for percent_complete in range(percent):
            time.sleep(0.05)
            mybar.progress(percent_complete + 1)

# ---------------- Xử lý menu ----------------
if selected := selected:  # dùng giá trị trả về từ sidebar
    if selected == "Trang Chính":
        Home()
        graphs()
    elif selected == "Tiến Độ":
        Progressbar()

# Ẩn các phần tử của Streamlit
hide_st_style = """ 
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
