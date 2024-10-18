import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu
from numerize.numerize import numerize
import time
from streamlit_extras.metric_cards import style_metric_cards
st.set_option('deprecation.showPyplotGlobalUse', False)
import plotly.graph_objs as go

# Cấu hình trang
st.set_page_config(page_title="Bảng điều khiển", page_icon="🔆", layout="wide")
st.header("XỬ LÝ PHÂN TÍCH, KPI, XU HƯỚNG & DỰ ĐOÁN")

# Tải CSS tùy chỉnh
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Tải dữ liệu mới
df = pd.read_csv('sales_data.csv')

# Các bộ lọc bên thanh bên
item_type = st.sidebar.multiselect(
    "CHỌN LOẠI MẶT HÀNG",
    options=df["Item_Type"].unique(),
    default=df["Item_Type"].unique(),
)
outlet_location_type = st.sidebar.multiselect(
    "CHỌN LOẠI ĐỊA ĐIỂM BÁN HÀNG",
    options=df["Outlet_Location_Type"].unique(),
    default=df["Outlet_Location_Type"].unique(),
)
outlet_type = st.sidebar.multiselect(
    "CHỌN LOẠI CỬA HÀNG",
    options=df["Outlet_Type"].unique(),
    default=df["Outlet_Type"].unique(),
)

df_selection = df.query(
    "Item_Type == @item_type & Outlet_Location_Type == @outlet_location_type & Outlet_Type == @outlet_type"
)

# Trang chính với phân tích mô tả
def Home():
    with st.expander("XEM DỮ LIỆU CSV"):
        showData = st.multiselect('Lọc: ', df_selection.columns, default=df_selection.columns.tolist())
        st.dataframe(df_selection[showData], use_container_width=True)
        
    # Tính toán các chỉ số chính
    total_sales = float(pd.Series(df_selection['Item_Outlet_Sales']).sum())
    # Assuming df_selection is your DataFrame
    sales_mode = float(pd.Series(df_selection['Item_Outlet_Sales']).max())

    sales_mean = float(pd.Series(df_selection['Item_Outlet_Sales']).mean())
    sales_median = float(pd.Series(df_selection['Item_Outlet_Sales']).median())

    total1, total2, total3, total4 = st.columns(4, gap='small')
    with total1:
        st.info('Tổng Doanh Thu', icon="💰")
        st.metric(label="Tổng Doanh Thu", value=f"{total_sales:,.0f}")

    with total2:
        st.info('Doanh Thu Cao Nhất', icon="💰")
        st.metric(label="Doanh Thu Cao Nhất", value=f"{sales_mode:,.0f}")

    with total3:
        st.info('Doanh Thu Trung Bình', icon="💰")
        st.metric(label="Trung Bình Doanh Thu", value=f"{sales_mean:,.0f}")

    with total4:
        st.info('Doanh Thu Trung Tâm', icon="💰")
        st.metric(label="Doanh Thu Trung Tâm", value=f"{sales_median:,.0f}")
    
    style_metric_cards(background_color="#FFFFFF", border_left_color="#686664", border_color="#000000", box_shadow="#F71938")

    # Biểu đồ phân phối
    with st.expander("PHÂN PHỐI THEO TẦN SUẤT"):
        df_selection.hist(figsize=(16, 8), color='#898784', zorder=2, rwidth=0.9)
        st.pyplot()

# Các biểu đồ
def graphs():
    # Doanh thu theo loại mặt hàng
    sales_by_item_type = df_selection.groupby(by=["Item_Type"]).sum()[["Item_Outlet_Sales"]].sort_values(by="Item_Outlet_Sales")
    fig_sales_item_type = px.bar(
        sales_by_item_type,
        x="Item_Outlet_Sales",
        y=sales_by_item_type.index,
        orientation="h",
        title="<b> DOANH THU THEO LOẠI MẶT HÀNG </b>",
        color_discrete_sequence=["#0083B8"]*len(sales_by_item_type),
        template="plotly_white",
    )
    fig_sales_item_type.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="black"),
        yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
    )

    # Doanh thu theo loại địa điểm bán hàng
    sales_outlet_location = df_selection.groupby(by=["Outlet_Location_Type"]).sum()[["Item_Outlet_Sales"]]
    fig_sales_outlet_location = px.line(
        sales_outlet_location,
        x=sales_outlet_location.index,
        y="Item_Outlet_Sales",
        orientation="v",
        title="<b> DOANH THU THEO LOẠI ĐỊA ĐIỂM BÁN HÀNG </b>",
        color_discrete_sequence=["#0083b8"]*len(sales_outlet_location),
        template="plotly_white",
    )
    fig_sales_outlet_location.update_layout(
        xaxis=dict(tickmode="linear"),
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(showgrid=False)
    )

    left, right, center = st.columns(3)
    left.plotly_chart(fig_sales_outlet_location, use_container_width=True)
    right.plotly_chart(fig_sales_item_type, use_container_width=True)
    
    with center:
        # Biểu đồ hình tròn
        fig = px.pie(df_selection, values='Item_Outlet_Sales', names='Outlet_Type', title='DOANH THU THEO LOẠI CỬA HÀNG')
        fig.update_layout(legend_title="Loại Cửa Hàng", legend_y=0.9)
        fig.update_traces(textinfo='percent+label', textposition='inside')
        st.plotly_chart(fig, use_container_width=True)


    st.subheader('CHỌN TÍNH NĂNG ĐỂ KHÁM PHÁ XU HƯỚNG PHÂN PHỐI THEO QUARTILES')
    feature_y = st.selectbox('Chọn tính năng cho dữ liệu số', df_selection.select_dtypes("number").columns)
    fig2 = go.Figure(
        data=[go.Box(x=df_selection['Item_Type'], y=df_selection[feature_y])],
        layout=go.Layout(
            title=go.layout.Title(text="LOẠI MẶT HÀNG THEO PHÂN VỊ QUARTILES CỦA DOANH THU"),
            plot_bgcolor='rgba(0, 0, 0, 0)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            xaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            yaxis=dict(showgrid=True, gridcolor='#cecdcd'),
            font=dict(color='#cecdcd'),
        )
    )
    st.plotly_chart(fig2, use_container_width=True)
# Hàm để hiển thị doanh thu hiện tại so với mục tiêu dự kiến     
def Progressbar():
    st.markdown("""<style>.stProgress > div > div > div > div { background-image: linear-gradient(to right, #99ff99 , #FFFF00)}</style>""", unsafe_allow_html=True)
    target = 30000000  # Cập nhật mục tiêu theo nhu cầu
    current = df_selection["Item_Outlet_Sales"].sum()
    percent = round((current / target * 100))
    mybar = st.progress(0)

    if percent > 100:
        st.subheader("Đã hoàn thành mục tiêu!")
    else:
        st.write("Bạn đã đạt ", percent, "% của ", format(target, 'd'), " Doanh Thu")
        for percent_complete in range(percent):
            time.sleep(0.1)
            mybar.progress(percent_complete + 1, text=" Phần Trăm Đạt Được")

# Thanh bên menu
def sideBar():
    with st.sidebar:
        selected = option_menu(
            menu_title="Menu Chính",
            options=["Trang Chính", "Tiến Độ"],
            icons=["house", "eye"],
            menu_icon="cast",
            default_index=0
        )
    if selected == "Trang Chính":
        Home()
        graphs()
    if selected == "Tiến Độ":
        Progressbar()
       

sideBar()
st.sidebar.image("img/logo.png", caption="")


# Ẩn các phần tử của Streamlit
hide_st_style = """ 
<style>
#MainMenu {visibility:hidden;}
footer {visibility:hidden;}
header {visibility:hidden;}
</style>
"""
st.markdown(hide_st_style, unsafe_allow_html=True)
