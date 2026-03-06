import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

# 1. 금고(Secrets)에서 열쇠 정보를 가져와서 연결 준비
creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"]  # <--- 이게 아까 넣은 그 키입니다!
)

# 2. 구글 시트 열기
client = gspread.authorize(creds)
sheet = client.open("내_시트_이름").sheet1

# 3. 이제부터는 엑셀처럼 마음대로 쓰면 됩니다!
data = sheet.get_all_records()
st.write(data)