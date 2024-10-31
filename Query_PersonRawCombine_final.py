import streamlit as st
import pandas as pd
import pyodbc

# Thông tin kết nối tới SQL Server
server = '192.168.1.39,63839'  # Thường là IP hoặc tên server
database = 'BiinForm_Data_Ingestion'  # Tên database bạn muốn kết nối tới
username = 'BI.BA.Select'  # Tên đăng nhập SQL Server của bạn
password = 'lsdlwiEkmNDF09)(DNFNk87'  # Mật khẩu đăng nhập

# Kết nối tới SQL Server
def get_connection():
    connection = pyodbc.connect(
        f'DRIVER={{ODBC Driver 17 for SQL Server}};'
        f'SERVER={server};DATABASE={database};'
        f'UID={username};PWD={password}'
    )
    return connection

# Sử dụng cache để giữ kết nối (nếu cần thiết)
@st.cache_data
def load_data():
    conn = get_connection()
    query = "SELECT * FROM PersonCodeRaw_combine"  # Thay thế bằng câu lệnh SQL phù hợp
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# Tải dữ liệu
combined_df = load_data()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Thực hiện tìm kiếm khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    if identity_number:
        # Lọc kết quả theo IdentityNo
        filtered_df = combined_df[combined_df['IdentityNo'].str.strip().str.lower() == identity_number.strip().lower()]
        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìaa")

# Hiển thị số lượng kết quả tìm kiếm / tổng số bản ghi
if 'filtered_df' in locals() and not filtered_df.empty:
    st.write(f"Số lượng kết quả tìm kiếm: {len(filtered_df)} / {len(combined_df)}")
