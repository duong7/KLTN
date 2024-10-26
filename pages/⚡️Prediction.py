import streamlit as st
import numpy as np
import pandas as pd  # Ensure pandas is imported
import folium
from folium.plugins import HeatMap, Draw, Fullscreen
from streamlit_folium import folium_static
import pickle
import matplotlib.pyplot as plt

def load_model():
    """Load the saved model and label encoders from a pickle file."""
    with open('saved_steps.pkl', 'rb') as file:
        data = pickle.load(file)
    return data

# Load model and encoders
data = load_model()
regressor_loaded = data["model"]
le_item_identifier = data["le_item_identifier"]
le_outlet_size = data["le_outlet_size"]
le_outlet_identifier = data["le_outlet_identifier"]
le_outlet_location_type = data["le_outlet_location_type"]
le_outlet_type = data["le_outlet_type"]

def show_predict_page():
    """Render the Streamlit page for making predictions and showing results."""
    st.title("Dự đoán doanh số bán hàng cho một mặt hàng mới")

    st.write("""### Chúng ta cần thông tin để dự đoán""")

    cacloaithanhpho = ("Tier 1", "Tier 2", "Tier 3")
    cactheloaicuahang = ("Supermarket Type1", "Supermarket Type2","Supermarket Type3","Grocery Store")
    cacsizecuahang = ("Medium","Small","High")
    masanpham = st.text_input("Mã sản phẩm", value="")  
    macuahang = st.text_input("Mã cửa hàng", value="")
    sizecuahang = st.selectbox("Size cửa hàng", cacsizecuahang)
    giabanle = st.text_input("Giá bán lẻ của sản phẩm", value="")
    loaithanhpho = st.selectbox("Loại thành phố", cacloaithanhpho)
    theloaicuahang = st.selectbox("Thể loại cửa hàng", cactheloaicuahang)
    giacaonhat = st.text_input("Giá cao nhất của Item_MRP", value="")
    ok = st.button("Dự đoán doanh số bán hàng")
    
    if ok:
        # Prepare input features for prediction
        x = np.array([[masanpham, macuahang,sizecuahang, giabanle, loaithanhpho, theloaicuahang]])
        
        # Transform categorical features
        x[:, 0] = le_item_identifier.transform(x[:, 0])
        x[:, 1] = le_outlet_identifier.transform(x[:, 1])
        x[:, 2] = le_outlet_size.transform(x[:, 2])
        x[:, 4] = le_outlet_location_type.transform(x[:, 4])
        x[:, 5] = le_outlet_type.transform(x[:, 5])

        # Create DataFrame for prediction
        x_df = pd.DataFrame(x, columns=["Item_Identifier","Outlet_Identifier","Outlet_Size", "Item_MRP", "Outlet_Location_Type", "Outlet_Type"])
        x_df['Item_Visibility'] = -1.092117e-16  # Placeholder value
        

        # Predict sales
        salary = regressor_loaded.predict(x_df)
        formatted_salary = "{:,.2f}".format(salary[0]).replace(",", ".")

        st.subheader(f"Doanh số mặt hàng là ${formatted_salary}")

        # Vẽ đồ thị Partial Dependence Plot
        item_mrp_max = float(giacaonhat) if giacaonhat else 300  # Giá cao nhất của Item_MRP
        item_mrp_values = np.linspace(30, item_mrp_max, 100)  # Thay đổi khoảng giá trị tùy theo nhu cầu
        predicted_sales = []

        for mrp in item_mrp_values:
            x_new = np.array([masanpham, macuahang,sizecuahang, mrp, loaithanhpho, theloaicuahang]).reshape(1, -1)
            x_new[:, 0] = le_item_identifier.transform(x_new[:, 0])
            x_new[:, 1] = le_outlet_identifier.transform(x_new[:, 1])
            x_new[:, 2] = le_outlet_size.transform(x_new[:, 2])
            x_new[:, 4] = le_outlet_location_type.transform(x_new[:, 4])
            x_new[:, 5] = le_outlet_type.transform(x_new[:, 5])
          
            x_new_df = pd.DataFrame(x_new, columns=["Item_Identifier", "Outlet_Identifier","Outlet_Size", "Item_MRP", "Outlet_Location_Type", "Outlet_Type"])
            x_new_df['Item_Visibility'] = -1.092117e-16
            
            y_pred_new = regressor_loaded.predict(x_new_df)
            predicted_sales.append(y_pred_new[0])

        # Plot the Partial Dependence Plot
        plt.figure(figsize=(10, 6))
        plt.plot(item_mrp_values, predicted_sales, color='blue')
        plt.xlabel('Item_MRP')
        plt.ylabel('Dự đoán Doanh Thu')
        plt.title('Sơ đồ phụ thuộc một phần cho Item_MRP')
        st.pyplot(plt)

        # Process and filter data for the map
        df = pd.read_csv('sales_data.csv')
        columns = [
            'Outlet_Identifier', 'Item_Identifier', 'Item_Type', 'Outlet_Location_Type', 'Outlet_Type', 
            'Outlet_Size', 'Item_MRP', 'Item_Outlet_Sales', 'Longitude', 'Latitude'
        ]
        df = df[columns]

        # Group by both Outlet_Identifier and Item_Identifier
        def unique_values(series):
            return ', '.join(series.dropna().astype(str).unique())

        df_grouped = df.groupby(['Outlet_Identifier', 'Item_Identifier']).agg({
            'Item_Type': unique_values,
            'Outlet_Location_Type': unique_values,
            'Outlet_Type': unique_values,
            'Outlet_Size': unique_values,
            'Item_MRP': 'sum',
            'Item_Outlet_Sales': 'sum',
            'Longitude': 'mean',
            'Latitude': 'mean'
        }).reset_index()

        # Filter for the selected outlet and item
        selected_outlet = df_grouped[
            (df_grouped['Outlet_Identifier'] == macuahang) &
            (df_grouped['Item_Identifier'] == masanpham)
        ]

        if not selected_outlet.empty:
            row = selected_outlet.iloc[0]
            m = folium.Map(location=[row['Latitude'], row['Longitude']], zoom_start=10)

            # Popup content with actual values
            popup_content = f"""
              <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
              <ul class="list-group">
              <h3>Thông tin của {row['Outlet_Identifier']}</h3>
              <hr class='bg-danger text-primary'>
              <div style='width:400px;height:300px;margin:10px;color:gray;text-size:18px;'>
              <li class="list-group-item"><b>Mã cửa hàng:</b> {row['Outlet_Identifier']}</li>
              <li class="list-group-item"><b>Mã sản phẩm:</b> {row['Item_Identifier']}</li>
              <li class="list-group-item"><b>Loại sản phẩm:</b> {row['Item_Type']}</li>
              <li class="list-group-item"><b>Loại Outlet:</b> {row['Outlet_Type']}</li>
              <li class="list-group-item"><b>Loại Địa Điểm:</b> {row['Outlet_Location_Type']}<br></li>
              <li class="list-group-item"><b>Kích Thước:</b> {row['Outlet_Size']}<br></li>
              <li class="list-group-item"><b>MRP Tổng:</b> {row['Item_MRP']}<br></li>
              <li class="list-group-item"><b>Doanh Thu Tổng:</b> {row['Item_Outlet_Sales']}<br></li>
              <li class="list-group-item"><h4>Kinh Độ: {row['Longitude']}</h4></li>
              <li class="list-group-item"><h4>Vĩ Độ: {row['Latitude']}</h4></li>
              </div>
              </ul>
            """
            folium.Marker(
                location=[row['Latitude'], row['Longitude']],
                tooltip=row['Outlet_Identifier'],
                icon=folium.Icon(color='red', icon='fa-dollar-sign', prefix='fa'),
            ).add_to(m).add_child(folium.Popup(popup_content, max_width=600))

            Fullscreen(position='topright', title='Toàn Màn Hình', title_cancel='Thoát Toàn Màn Hình').add_to(m)
            draw = Draw(export=True)
            draw.add_to(m)

            def add_google_maps(m):
                tiles = "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
                attr = "Google Digital Satellite"
                folium.TileLayer(tiles=tiles, attr=attr, name=attr, overlay=True, control=True).add_to(m)
                label_tiles = "https://mt1.google.com/vt/lyrs=h&x={x}&y={y}&z={z}"
                label_attr = "Google Labels"
                folium.TileLayer(tiles=label_tiles, attr=label_attr, name=label_attr, overlay=False, control=True).add_to(m)
                folium.LayerControl().add_to(m)

            add_google_maps(m)
            folium_static(m)
        else:
            st.error("Mã cửa hàng hoặc mã sản phẩm không tồn tại trong dữ liệu.")
        
        with st.expander("Bảng dự đoán"):
            st.write("Dưới đây là bảng dự đoán doanh số bán hàng.")
            # Create DataFrame for predictions
            predictions_df = pd.DataFrame({
                'Item_MRP': item_mrp_values,
                'Dự đoán Doanh Thu': predicted_sales
            })
            st.write(predictions_df)

            # Convert DataFrame to CSV and provide download link
            csv = predictions_df.to_csv(index=False)
            st.download_button(
                label="Tải xuống CSV",
                data=csv,
                file_name='predictions.csv',
                mime='text/csv')

show_predict_page()
st.sidebar.image("img/logo.png")
