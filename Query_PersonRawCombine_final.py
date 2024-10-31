
'''
pip install pandas gdown
pip install streamlit
pip install gdown
streamlit run your_script.py  -- chạy thử ứng dụng
'''


import streamlit as st
import pandas as pd
import os
import sqlite3
import requests


# Đường dẫn tới thư mục chứa các file CSV đã tải xuống
folder_path = "download_drive"
db_path = "combined_data.db"

# URLs của các file trên Google Drive
file_urls = [
    'https://drive.google.com/uc?id=1NCCXd9ei81ImegtIr5KdAPr0O1-A7J7F',
    'https://drive.google.com/uc?id=1kCa4qKFVGkePKM3ltP_Zw65-trgdy9X2',
    'https://drive.google.com/uc?id=1QmCwQl8aAutlBvDDYbi6jFaqWbwXA-j3',
    'https://drive.google.com/uc?id=1xp75FLWcwwRmDTlhfffzxuujgB1g3mZm',
    'https://drive.google.com/uc?id=1p2YRevYBlMsuFGx26rlnzAD-3ailTtPq',
    'https://drive.google.com/uc?id=1-HmYrP873kjFWM2yFFwJTLNsjFKwng4O',
    'https://drive.google.com/uc?id=1N6zQgTpocGEps9NuG0Pp08wOws2GthaY',
    'https://drive.google.com/uc?id=1pp_DA7VdrBptFtROxeixfDzq_jQW21V2',
    'https://drive.google.com/uc?id=1tifuC6Petn1Tpx9AKeeJr5k_pxR9548D'
]

# Sử dụng cache để tải dữ liệu vào SQLite nếu chưa tồn tại
@st.cache_data
def load_data_to_sqlite():
    # Nếu file database đã tồn tại, không cần tải lại dữ liệu
    if not os.path.exists(db_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Tải các file CSV từ Google Drive về thư mục cục bộ
        for idx, url in enumerate(file_urls):
            output_file = os.path.join(folder_path, f'file_{idx + 1}.csv')
            if not os.path.exists(output_file):
                response = requests.get(url)
                if response.status_code == 200:
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                else:
                    st.error(f"Lỗi tải file từ URL: {url}")

        # Đọc các file CSV và kết hợp chúng lại
        header = ["PersonCode", "IdentityNo", "en_LastName", "en_MiddleName", "en_FirstName", "Address", "BirthDate", "Status", "Version", "STT"]
        dfs = []

        # Đọc tất cả các file CSV trong thư mục và lưu vào danh sách
        for f in os.listdir(folder_path):
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(folder_path, f), names=header, low_memory=False)
                dfs.append(df)

        # Gộp tất cả các DataFrame lại thành một DataFrame duy nhất bằng concat
        combined_df = pd.concat(dfs, ignore_index=True)

        # Thêm cột mới để lấy năm từ BirthDate
        combined_df['BirthYear'] = pd.to_datetime(combined_df['BirthDate'], errors='coerce').dt.year

        # Lưu vào SQLite
        conn = sqlite3.connect(db_path)
        combined_df.to_sql('PersonData', conn, if_exists='replace', index=False)
        conn.close()

# Tải dữ liệu vào SQLite (chỉ khi cần)
load_data_to_sqlite()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Kết nối đến SQLite và thực hiện truy vấn khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    if identity_number:
        conn = sqlite3.connect(db_path)
        
        # Truy vấn tổng số lượng bản ghi trong toàn bộ DataFrame
        total_records_query = "SELECT COUNT(*) FROM PersonData"
        total_records = pd.read_sql_query(total_records_query, conn).iloc[0, 0]

        # Truy vấn kết quả theo IdentityNo
        query = "SELECT * FROM PersonData WHERE IdentityNo = ?"
        filtered_df = pd.read_sql_query(query, conn, params=(identity_number,))
        conn.close()

        # Hiển thị kết quả tìm kiếm
        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)

            # Hiển thị số lượng bản ghi tìm được / tổng số bản ghi
            st.write(f"Kết quả tìm kiếm: {len(filtered_df)} / {total_records} bản ghi")
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìa")




################## CHẠY CÂU LỆNH NÀY ĐỂ RA WEB QUERY 

#streamlit run Query_PersonRawCombine.py

