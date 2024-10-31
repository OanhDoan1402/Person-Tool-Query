import streamlit as st
import pandas as pd
import os
import requests

# Đường dẫn tới thư mục chứa các file CSV đã tải xuống
folder_path = "download_drive"

# URLs của các file trên Google Drive (sửa lại để tải trực tiếp)
file_urls = [
    'https://drive.google.com/uc?id=1mqN10fsClug7tUvDXE-t1-bPGfaJCTt9&export=download',
    'https://drive.google.com/uc?id=1vOXnGrOasv5srNgeOZ7n1n_InukBuuu5&export=download',
    'https://drive.google.com/uc?id=1baH_EJjmhURChp5T0S3fNvTQPzfqIva7&export=download',
    'https://drive.google.com/uc?id=1iI1GSghFI5BiyQ01M7FL_UE-EyPPD-oT&export=download',
    'https://drive.google.com/uc?id=14PixcanqWPB79Yc5ioKXuL3_uTqQLVUi&export=download',
    'https://drive.google.com/uc?id=1MzIPguxKci5QGg_T6i59bJEFnRsEwCHU&export=download',
    'https://drive.google.com/uc?id=1NTuinbRYKFfMWJIHomhE04KBFyiuTgp4&export=download',
    'https://drive.google.com/uc?id=11sW9RBOI3fNqxYUneJEH0DKhfSDVzcBQ&export=download',
    'https://drive.google.com/uc?id=1otcLQLUVz84qB3ROF4AEpjLa_Fqk3A57&export=download'
]

# Sử dụng cache để tải dữ liệu nếu chưa tồn tại
@st.cache_data
def load_data():
    # Tạo thư mục nếu chưa có
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Tải các file CSV từ Google Drive
    for i, url in enumerate(file_urls):
        response = requests.get(url)
        if response.status_code == 200:
            with open(os.path.join(folder_path, f'file_{i+1}.csv'), 'wb') as f:
                f.write(response.content)
        else:
            st.error(f"Lỗi tải file từ URL: {url}")

    # Đọc các file CSV và kết hợp chúng lại
    header = ["PersonCode", "IdentityNo", "en_LastName", "en_MiddleName", "en_FirstName", "Address", "BirthDate", "Status", "Version", "STT"]
    dfs = []
    output_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.csv')]
    for output in output_files:
        df = pd.read_csv(output, names=header, low_memory=False)
        dfs.append(df)

    # Gộp các DataFrame lại với nhau mà không có bất kỳ bước lọc nào
    combined_df = pd.concat(dfs, ignore_index=True)

    return combined_df

# Tải dữ liệu
combined_df = load_data()

# Giao diện người dùng bằng Streamlit
st.title("PersonRawCombine Query Tool")

# Nhập IdentityNo để tìm kiếm
identity_number = st.text_input("Nhập IdentityNo để tìm kiếm:")

# Thực hiện truy vấn khi người dùng nhấn nút "Tìm kiếm"
if st.button("Tìm kiếm nèoo"):
    if identity_number:
        # Không thay đổi bất kỳ định dạng nào của dữ liệu gốc
        filtered_df = combined_df[combined_df['IdentityNo'] == identity_number]

        if not filtered_df.empty:
            st.write("Kết quả tìm kiếm:")
            st.dataframe(filtered_df)
        else:
            st.warning("Không tìm thấy IdentityNo này trong dữ liệu.")
    else:
        st.warning("Quên không nhập IdentityNo kìaa")

# Phân trang kết quả nếu cần thiết
def paginate_dataframe(df, page_size=20):
    total_rows = df.shape[0]
    current_page = st.number_input("Trang", min_value=1, max_value=(total_rows // page_size) + 1, step=1)
    start_idx = (current_page - 1) * page_size
    end_idx = start_idx + page_size
    return df.iloc[start_idx:end_idx]

