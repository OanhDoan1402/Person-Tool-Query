import streamlit as st
import pandas as pd
import os
import sqlite3
import requests
# Đường dẫn tới thư mục chứa các file CSV đã tải xuống
folder_path = "/tmp/download_drive"
db_path = "/tmp/combined_data.db"  # Sử dụng thư mục tạm thời cho Streamlit Cloud

# URLs của các file trên Google Drive
file_urls = [
   'https://drive.google.com/uc?id=106Lxh2NUpgT6IFL2KaXY9UnFzlvQd7ol',
   # Các URL còn lại...
]

# Sử dụng cache để tải dữ liệu vào SQLite nếu chưa tồn tại
@st.cache_data
def load_data_to_sqlite():
    st.write("Bắt đầu tải dữ liệu...")
    # Nếu file database đã tồn tại, không cần tải lại dữ liệu
    if not os.path.exists(db_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            st.write(f"Đã tạo thư mục {folder_path}")

        # Tải các file CSV từ Google Drive về thư mục cục bộ
        for idx, url in enumerate(file_urls):
            output_file = os.path.join(folder_path, f'file_{idx + 1}.csv')
            if not os.path.exists(output_file):
                st.write(f"Đang tải file {output_file} từ URL...")
                response = requests.get(url)
                if response.status_code == 200:
                    if "<html" not in response.text.lower():
                        with open(output_file, 'wb') as f:
                            f.write(response.content)
                        st.write(f"Tải thành công file: {output_file}")
                    else:
                        st.write(f"Lỗi: File tải về có nội dung HTML, có thể là yêu cầu xác nhận quyền. URL: {url}")
                else:
                    st.write(f"Lỗi tải file từ URL: {url} - Mã lỗi: {response.status_code}")
            else:
                st.write(f"File đã tồn tại: {output_file}")

            if os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                st.write(f"Dung lượng của file {output_file}: {file_size} bytes")
                if file_size == 0:
                    st.write(f"File {output_file} không có dữ liệu (rỗng).")

        # Đọc các file CSV và kết hợp chúng lại
        header = ["PersonCode", "IdentityNo", "en_LastName", "en_MiddleName", "en_FirstName", "Address", "BirthDate", "Status", "Version", "STT"]
        dfs = []

        # Đọc tất cả các file CSV trong thư mục và lưu vào danh sách
        for f in os.listdir(folder_path):
            if f.endswith('.csv'):
                st.write(f"Đang đọc file {f}...")
                try:
                    df = pd.read_csv(os.path.join(folder_path, f), names=header, low_memory=False)
                    if not df.empty:
                        dfs.append(df)
                        st.write(f"Đã đọc thành công file {f} với {len(df)} dòng.")
                    else:
                        st.write(f"File {f} trống hoặc không đọc được.")
                except Exception as e:
                    st.write(f"Lỗi khi đọc file {f}: {e}")

        # Gộp tất cả các DataFrame lại thành một DataFrame duy nhất bằng concat
        if dfs:
            st.write("Bắt đầu gộp các DataFrame lại thành một...")
            combined_df = pd.concat(dfs, ignore_index=True)
            st.write(f"Tổng số dòng sau khi gộp: {combined_df.shape[0]}")

            # Lưu vào SQLite
            conn = sqlite3.connect(db_path)
            combined_df.to_sql('PersonData', conn, if_exists='replace', index=False)
            st.write("Đã lưu dữ liệu vào SQLite thành công.")
            conn.close()
        else:
            st.write("Không có file nào được gộp. Danh sách dfs trống.")
    else:
        st.write(f"Database đã được tạo trong bộ nhớ. Không cần tải lại dữ liệu.")

# Tải dữ liệu vào SQLite (chỉ khi cần)
try:
    load_data_to_sqlite()
except Exception as e:
    st.error(f"Đã xảy ra lỗi khi tải dữ liệu vào SQLite: {e}")

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")
st.write("Đã khởi tạo giao diện Streamlit.")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

if st.button("Tìm kiếm nèoo"):
    if identity_number:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM PersonData WHERE IdentityNo = ? ORDER BY en_FirstName"
        try:
            filtered_df = pd.read_sql_query(query, conn, params=(identity_number,))
            st.write("Đã thực hiện truy vấn với SQLite.")
        except Exception as e:
            st.error("Lỗi khi truy vấn dữ liệu từ SQLite: " + str(e))
        finally:
            conn.close()

        if 'filtered_df' in locals() and not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
# Chạy Streamlit
# streamlit run Query_PersonRawCombine.py
