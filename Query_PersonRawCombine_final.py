import streamlit as st
import pandas as pd
import os
import sqlite3
import gdown

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
                gdown.download(url, output_file, quiet=False)

        # Đọc các file CSV và kết hợp chúng lại
        header = ["PersonCode", "IdentityNo", "en_LastName", "en_MiddleName", "en_FirstName", "Address", "BirthDate", "Status", "Version", "STT"]
        dfs = []
        for f in os.listdir(folder_path):
            if f.endswith('.csv'):
                df = pd.read_csv(os.path.join(folder_path, f), names=header, low_memory=False)
                dfs.append(df)

        combined_df = pd.concat(dfs, ignore_index=True)
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
        query = "SELECT * FROM PersonData WHERE IdentityNo = ?"
        filtered_df = pd.read_sql_query(query, conn, params=(identity_number,))
        conn.close()

        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìa")

# Phân trang kết quả nếu cần thiết
def paginate_dataframe(df, page_size=20):
    total_rows = df.shape[0]
    current_page = st.number_input("Trang", min_value=1, max_value=(total_rows // page_size) + 1, step=1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]

# Tìm kiếm phân trang khi có kết quả lớn
if 'filtered_df' in locals() and not filtered_df.empty:
    paginated_df = paginate_dataframe(filtered_df)
    st.write("Hiển thị kết quả phân trang:")
    st.dataframe(paginated_df)
