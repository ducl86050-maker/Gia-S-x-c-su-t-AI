import streamlit as st
import google.generativeai as genai

# Cấu hình giao diện trang
st.set_page_config(page_title="Gia sư Xác suất", page_icon="🎲")

# CSS để trang trí giao diện
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    h1 { color: #2e86c1; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎲 Gia sư Xác suất Soleil")
st.subheader("Chuyên gia giải bài tập Xác suất thống kê (⁀ᗢ⁀)")

# Cấu hình API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("Chưa cấu hình API Key!")
    st.stop()

# Bộ lọc để AI chỉ trả lời xác suất
SYSTEM_INSTRUCTION = """
Bạn là một chuyên gia về Xác suất Thống kê. 
Nhiệm vụ của bạn là giải các bài tập về xác suất.
Nếu người dùng hỏi về bất kỳ chủ đề nào khác (toán đại số, văn học, đời sống...), 
bạn hãy trả lời lịch sự: 'chị hơi bị khó tính đó nha , chị chỉ giúp em xác suất thôi!'
"""

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("em có thắc mắc gì đang cần chị giải đáp không nè (´｡• ω •｡`) ♡"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Kết hợp hướng dẫn vào prompt
        final_prompt = SYSTEM_INSTRUCTION + "\n\nBài tập: " + prompt
        response = model.generate_content(final_prompt)
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})