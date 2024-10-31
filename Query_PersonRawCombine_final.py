import streamlit as st
import pandas as pd
import requests
import os

# Đường dẫn tới thư mục để lưu file CSV đã tải xuống
folder_path = "download_drive"
db_path = "combined_data.db"

# URL của file CSV đã được gộp sẵn trên Google Drive (sửa lại để tải trực tiếp)
combined_file_url = 'https://drive.google.com/uc?id=YOUR_COMBINED_FILE_ID&export=download'

# Sử dụng cache để tải dữ liệu vào DataFrame nếu chưa tồn tại
@st.cache_data
def load_combined_data():
    # Nếu file database đã tồn tại, không cần tải lại dữ liệu
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Đường dẫn để lưu file đã tải xuống
    combined_file_path = os.path.join(folder_path, 'combine_df.csv')

    # Tải file CSV đã được gộp từ Google Drive
    response = requests.get(combined_file_url)
    if response.status_code == 200:
        with open(combined_file_path, 'wb') as f:
            f.write(response.content)
    else:
        st.error(f"Lỗi tải file từ URL: {combined_file_url}")
    
    # Đọc file CSV và trả về DataFrame
    combined_df = pd.read_csv(combined_file_path, low_memory=False)
    
    return combined_df

# Tải dữ liệu vào DataFrame (chỉ khi cần)
combined_df = load_combined_data()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Thực hiện truy vấn khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    if identity_number:
        identity_number = identity_number.strip().lower()
        # Truy vấn dữ liệu
        filtered_df = combined_df[combined_df['IdentityNo'].str.lower() == identity_number]
        
        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìaa")

# Thêm thông tin về số lượng kết quả tìm kiếm và tổng số lượng bản ghi
if 'filtered_df' in locals() and not filtered_df.empty:
    st.write(f"Số lượng kết quả tìm kiếm: {len(filtered_df)} / {len(combined_df)}")
