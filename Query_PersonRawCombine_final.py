import streamlit as st
import pandas as pd
import os
import sqlite3
import requests

# Đường dẫn tới thư mục chứa các file CSV đã tải xuống
folder_path = "download_drive"
db_path = ":memory:"  # Sử dụng bộ nhớ để tránh lỗi ghi đĩa trên Streamlit Cloud

# URLs của các file trên Google Drive
file_urls = [
   'https://drive.google.com/uc?id=106Lxh2NUpgT6IFL2KaXY9UnFzlvQd7ol',
   'https://drive.google.com/uc?id=1EzEWTq_L0Qu_du9rJltW4vhFrFbzuCJL',
   'https://drive.google.com/uc?id=13BgFJhVfRdaHS9zv3rPOqPqLPKM7c3AY',
   'https://drive.google.com/uc?id=1Zrp232Ufy_16bKgj7DCboFMe9wu5TPGy',
   'https://drive.google.com/uc?id=1FgN_JcLzE1swa1hI3WG1Ys7BsKmMiZ3F',
   'https://drive.google.com/uc?id=1PTAb56aEQ6WAW62WLTnyYE0bJgPVEPjJ',
   'https://drive.google.com/uc?id=1BHGtkzHbPg8IgM5DURGP3_n9ZVN7fI0l',
   'https://drive.google.com/uc?id=1tkTOrlnq7Dv7Smcbg6L2VMbMHPaFsEiG',
   'https://drive.google.com/uc?id=1GQrTA1H5ozW8A4xhen0CiTFM8IIUTfai',
   'https://drive.google.com/uc?id=1HaJNmziUpoEOuFkQpZ5aUAlYxFTS1N61',
   'https://drive.google.com/uc?id=1wmT1xQElJqD4BaWgW3gWHGOjcVYXsF0Y',
   'https://drive.google.com/uc?id=1LQve3Rnj4bVtb_xg2PUyOmHZgOd-FG2_',
   'https://drive.google.com/uc?id=1RRFT_u7hIc6sLIFArf_erhdzvWM2gNWj',
   'https://drive.google.com/uc?id=1Uk-tZYLfgS7PdxCGMPIpAH7TB2PtoSaL',
   'https://drive.google.com/uc?id=1AY9pCiaYnTYh6bMKGkdrTyatkiW7Mnzs'
]

# Sử dụng cache để tải dữ liệu vào SQLite nếu chưa tồn tại
@st.cache_data
def load_data_to_sqlite():
    st.write("Bắt đầu tải dữ liệu...")
    # Nếu thư mục không tồn tại thì tạo thư mục
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
                # Kiểm tra xem nội dung của file có phải HTML hay không (có thể là thông báo lỗi)
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

        # Kiểm tra dung lượng file sau khi tải
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

        # In ra số lượng dòng của DataFrame sau khi gộp
        st.write(f"Tổng số dòng sau khi gộp: {combined_df.shape[0]}")

        # Lưu vào SQLite
        conn = sqlite3.connect(db_path)
        combined_df.to_sql('PersonData', conn, if_exists='replace', index=False)
        st.write("Đã lưu dữ liệu vào SQLite thành công.")
        conn.close()
    else:
        st.write("Không có file nào được gộp. Danh sách dfs trống.")

# Tải dữ liệu vào SQLite (chỉ khi cần)
load_data_to_sqlite()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")
st.write("Đã khởi tạo giao diện Streamlit.")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Kết nối đến SQLite và thực hiện truy vấn khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    st.write("Người dùng nhấn nút tìm kiếm.")
    if identity_number:
        conn = sqlite3.connect(db_path)
        query = "SELECT * FROM PersonData WHERE IdentityNo = ? ORDER BY en_FirstName"
        try:
            filtered_df = pd.read_sql_query(query, conn, params=(identity_number,))
            st.write("Đã thực hiện truy vấn với SQLite.")
        except Exception as e:
            st.error("Lỗi khi truy vấn dữ liệu từ SQLite: " + str(e))
            st.write(f"Lỗi khi truy vấn dữ liệu: {e}")
        finally:
            conn.close()

        if 'filtered_df' in locals() and not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
            st.write("Đã hiển thị kết quả tìm kiếm.")
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
            st.write("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìa")
        st.write("Người dùng quên không nhập IdentityNo.")


# Phân trang kết quả nếu cần thiết
def paginate_dataframe(df, page_size=20):
    total_rows = df.shape[0]
    current_page = st.number_input("Trang", min_value=1, max_value=(total_rows // page_size) + 1, step=1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]


# Chạy Streamlit
# streamlit run Query_PersonRawCombine.py
