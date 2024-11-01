import streamlit as st
import pandas as pd
import requests
from io import StringIO

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

# Sử dụng cache để tải dữ liệu nếu chưa tồn tại
@st.cache_data
def load_data():
    st.write("Bắt đầu tải dữ liệu...")
    dfs = []

    # Tải các file CSV từ Google Drive về và đọc vào DataFrame
    for idx, url in enumerate(file_urls):
        try:
            st.write(f"Đang tải file {idx + 1} từ URL...")
            response = requests.get(url)
            response.raise_for_status()  # Kiểm tra phản hồi có thành công không
            if "<html" not in response.text.lower():
                df = pd.read_csv(StringIO(response.text))
                dfs.append(df)
                st.write(f"Tải thành công file {idx + 1}")
            else:
                st.error(f"Lỗi: File tải về có nội dung HTML, có thể là yêu cầu xác nhận quyền. URL: {url}")
        except requests.exceptions.RequestException as e:
            st.error(f"Lỗi tải file từ URL: {url} - Lỗi: {e}")

    # Gộp tất cả các DataFrame lại thành một DataFrame duy nhất bằng concat
    if dfs:
        st.write("Bắt đầu gộp các DataFrame lại thành một...")
        combined_df = pd.concat(dfs, ignore_index=True)
        st.write(f"Tổng số dòng sau khi gộp: {combined_df.shape[0]}")
        return combined_df
    else:
        st.write("Không có file nào được gộp. Danh sách dfs trống.")
        return pd.DataFrame()

# Tải dữ liệu vào DataFrame (chỉ khi cần)
try:
    combined_df = load_data()
except Exception as e:
    st.error(f"Đã xảy ra lỗi khi tải dữ liệu: {e}")
    combined_df = pd.DataFrame()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")
st.write("Đã khởi tạo giao diện Streamlit.")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Tìm kiếm dữ liệu khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    st.write("Người dùng nhấn nút tìm kiếm.")
    if identity_number and not combined_df.empty:
        filtered_df = combined_df[combined_df['IdentityNo'] == identity_number]
        
        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
            st.write("Đã hiển thị kết quả tìm kiếm.")
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
            st.write("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìa" if not identity_number else "Dữ liệu chưa sẵn sàng.")
        st.write("Người dùng quên không nhập IdentityNo." if not identity_number else "Dữ liệu chưa sẵn sàng.")

st.write("Sẵn sàng chạy lệnh stream")
