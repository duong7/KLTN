import streamlit as st
import pandas as pd

def add_data(key_suffix=""):
    # Đọc dữ liệu từ file train1.csv
    df = pd.read_csv("sales_data.csv")
    
    # Tạo form nhập liệu với khóa duy nhất
    form_key = f"unique_form_key_{key_suffix}"  # Tạo khóa duy nhất cho form
    with st.form(key=form_key, clear_on_submit=True):
        col1, col2 = st.columns(2)
        item_identifier = col1.text_input("Mã hàng hóa")
        item_weight = col2.number_input("Trọng lượng hàng hóa")
        
        col11, col22 = st.columns(2)
        item_fat_content = col11.selectbox("Nội dung chất béo", df["Item_Fat_Content"].unique())
        item_visibility = col22.number_input("Tỷ lệ hiển thị hàng hóa")
        
        col111, col222 = st.columns(2)
        item_type = col111.selectbox("Loại hàng hóa", df["Item_Type"].unique())
        item_mrp = col222.number_input("Giá bán lẻ tối đa")
        
        col333, col444 = st.columns(2)
        outlet_identifier = col333.selectbox("Mã cửa hàng", df["Outlet_Identifier"].unique())
        outlet_establishment_year = col444.number_input("Năm thành lập cửa hàng", min_value=1900, max_value=2100, step=1)
        
        col555, col666 = st.columns(2)
        outlet_size = col555.selectbox("Kích thước cửa hàng", df["Outlet_Size"].unique())
        outlet_location_type = col666.selectbox("Loại vị trí cửa hàng", df["Outlet_Location_Type"].unique())
        
        col777, col888 = st.columns(2)
        outlet_type = col777.selectbox("Loại cửa hàng", df["Outlet_Type"].unique())
        item_outlet_sales = col888.number_input("Doanh số cửa hàng")
        
        # Nút lưu dữ liệu
        btn = st.form_submit_button("Lưu dữ liệu vào Excel", type="primary")

        # Nếu nút được nhấn
        if btn:
            # Kiểm tra dữ liệu
            if (item_identifier == "" or item_weight == 0 or item_visibility == 0 or 
                item_mrp == 0 or outlet_establishment_year == 0 or item_outlet_sales == 0):
                st.warning("Tất cả các trường là bắt buộc và phải lớn hơn 0")
                return False
            else:
                # Thêm dữ liệu mới vào DataFrame
                new_data = pd.DataFrame([{
                    'Item_Identifier': item_identifier,
                    'Item_Weight': item_weight,
                    'Item_Fat_Content': item_fat_content,
                    'Item_Visibility': item_visibility,
                    'Item_Type': item_type,
                    'Item_MRP': item_mrp,
                    'Outlet_Identifier': outlet_identifier,
                    'Outlet_Establishment_Year': outlet_establishment_year,
                    'Outlet_Size': outlet_size,
                    'Outlet_Location_Type': outlet_location_type,
                    'Outlet_Type': outlet_type,
                    'Item_Outlet_Sales': item_outlet_sales
                }])
                
                # Ghi dữ liệu vào file CSV
                try:
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv("train1_updated.csv", index=False)
                    st.success("Dữ liệu mới đã được thêm thành công!")
                    return True
                except:
                    st.warning("Không thể ghi dữ liệu, vui lòng đóng file dữ liệu!!")
                    return False

# Gọi hàm với khóa khác nhau nếu cần
add_data(key_suffix="1")
