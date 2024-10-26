import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium
import plotly.graph_objs as go
import plotly.express as px
from folium.plugins import MarkerCluster, HeatMap, Fullscreen, Draw
import pandas as pd
from streamlit_extras.metric_cards import style_metric_cards

# Thiết lập chiều rộng
st.set_page_config(page_title="Phân Tích Kinh Doanh", page_icon="🔆", layout="wide")  

# Tải CSS Style
with open('style.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.markdown(
 """
 <style>
    [data-testid=stSidebar] {
         color: white;
         text-size:24px;
    }
</style>
""", unsafe_allow_html=True
)

# Tải dữ liệu mới
load_df = pd.read_csv('sales_data_group.csv')

# Logo
st.sidebar.image("img/logo.png", caption="")

# Multi-select để lọc theo Outlet Identifier
name = st.sidebar.multiselect(
    "CHỌN OUTLET",
    options=load_df["Outlet_Identifier"].unique(),
    default=load_df["Outlet_Identifier"].unique(),
)
df = load_df.query("Outlet_Identifier == @name")

# Phần phân tích
try:
    st.header("XU HƯỚNG KINH DOANH THEO GEO-REFERENCING")
    items = df['Outlet_Identifier'].count()
    total_sales = float(df['Item_Outlet_Sales'].sum())
    total_mrp = df['Item_MRP'].sum()  # Tổng giá trị Item_MRP
    unique_item_types = df['Item_Type_Count'].unique()  # Số lượng loại sản phẩm duy nhất
    with st.expander("PHÂN TÍCH"):
        a1, a2 = st.columns(2)
        a1.metric(label="Số Lượng Outlet", value=items, help=f"Tổng Doanh Thu: {total_sales}", delta=total_sales)
        a2.metric(label="Số Loại sản phẩm", value=unique_item_types, help=f"Tổng Item_MRP: {total_mrp}", delta=total_mrp)
        style_metric_cards(background_color="#FFFFFF", border_left_color="#00462F", border_color="#070505", box_shadow="#F71938")

    # Tạo bản đồ
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=4)

    marker_cluster = MarkerCluster().add_to(m)
    for i, row in df.iterrows():
        popup_content = f"""
          <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
          <ul class="list-group">
          <h3>Thông tin của {row['Outlet_Identifier']}</h3>
          <hr class='bg-danger text-primary'>
          <div style='width:400px;height:200px;margin:10px;color:gray;text-size:18px;'>
          <li class="list-group-item"><b>Loại Outlet:</b> {row['Outlet_Type']}</li>
          <li class="list-group-item"><b>Loại Địa Điểm:</b> {row['Outlet_Location_Type']}<br></li>
          <li class="list-group-item"><b>Kích Thước:</b> {row['Outlet_Size']}<br></li>
          <li class="list-group-item"><b>MRP:</b> {row['Item_MRP']}<br></li>
          <li class="list-group-item"><b>Doanh Thu:</b> {row['Item_Outlet_Sales']}<br></li>
          <li class="list-group-item"><h4>Kinh Độ: {row['Longitude']}</h4></li>
          <li class="list-group-item"><h4>Vĩ Độ: {row['Latitude']}</h4></li>"""
        folium.Marker(
            location=[row['Latitude'], row['Longitude']],
            tooltip=row['Outlet_Identifier'],
            icon=folium.Icon(color='red', icon='fa-dollar-sign', prefix='fa'),
        ).add_to(marker_cluster).add_child(folium.Popup(popup_content, max_width=600))  

    # Lớp Heatmap
    heat_data = [[row['Latitude'], row['Longitude']] for i, row in df.iterrows()]
    HeatMap(heat_data).add_to(m)

    # Điều khiển Toàn Màn Hình
    Fullscreen(position='topright', title='Toàn Màn Hình', title_cancel='Thoát Toàn Màn Hình').add_to(m)

    # Công cụ Vẽ
    draw = Draw(export=True)
    draw.add_to(m)

    def add_google_maps(m):
        tiles = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
        attr = "Google Digital Satellite"
        folium.TileLayer(tiles=tiles, attr=attr, name=attr, overlay=True, control=True).add_to(m)
        # Thêm nhãn cho đường phố và các đối tượng
        label_tiles = "https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}"
        label_attr = "Google Labels"
        folium.TileLayer(tiles=label_tiles, attr=label_attr, name=label_attr, overlay=True, control=True).add_to(m)
       
        return m

    with st.expander("XEM BẢN ĐỒ VÀ PHÂN TÍCH"):
        m = add_google_maps(m)
        m.add_child(folium.LayerControl(collapsed=False))
        folium_static(m, width=1350, height=600)
        folium.LayerControl().add_to(m)  # Thêm điều khiển lớp để chuyển đổi các lớp khác nhau

    # Hiển thị dữ liệu bảng khi di chuột qua một đánh dấu
    with st.expander("CHỌN DỮ LIỆU"):
        selected_outlet = st.selectbox("Chọn một Outlet", df['Outlet_Identifier'])
        selected_row = df[df['Outlet_Identifier'] == selected_outlet].squeeze()
        # Hiển thị thông tin bổ sung trong bảng
        st.table(selected_row)

    # Biểu đồ
    col1, col2 = st.columns(2)
    with col1:
        fig2 = go.Figure(
            data=[go.Bar(x=df['Outlet_Identifier'], y=df['Item_MRP'])],
            layout=go.Layout(
                title=go.layout.Title(text="Tổng Item_MRP Theo Outlet"),
                plot_bgcolor='rgba(0, 0, 0, 0)',  # Đặt màu nền biểu đồ thành trong suốt
                paper_bgcolor='rgba(0, 0, 0, 0)',  # Đặt màu nền giấy thành trong suốt
                xaxis=dict(showgrid=True, gridcolor='#AED6F1'),  # Hiển thị lưới trục x và đặt màu của nó
                yaxis=dict(showgrid=True, gridcolor='#cecdcd'),  # Hiển thị lưới trục y và đặt màu của nó
                font=dict(color='#cecdcd'),  # Đặt màu chữ thành đen
             )
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        # Tạo biểu đồ donut
        fig = px.pie(df, values='Item_Outlet_Sales', names='Outlet_Identifier', title='Phân Phối Doanh Thu Theo Outlet')
        fig.update_traces(hole=0.4)  # Đặt kích thước lỗ ở giữa cho biểu đồ donut
        fig.update_layout(width=800)
        st.plotly_chart(fig, use_container_width=True)
  
except Exception as e:
    st.error(f"Không thể hiển thị dữ liệu: {e}")
