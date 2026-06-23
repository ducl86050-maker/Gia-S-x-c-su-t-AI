import streamlit as st
import google.generativeai as genai
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="Gia sư Xác suất", page_icon="🎲")
st.title("🎲 Gia sư Xác suất Soleil")

# Cấu hình API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key!")
    st.stop()

# Khởi tạo trạng thái
if "messages" not in st.session_state: st.session_state.messages = []
if "warning_count" not in st.session_state: st.session_state.warning_count = 0
if "ban_time" not in st.session_state: st.session_state.ban_time = None

# Hàm kiểm tra "cơn giận" và "lệnh cấm"
def get_ai_response(prompt):
    # Kiểm tra xem có đang bị cấm không
    if st.session_state.ban_time:
        elapsed = datetime.now() - st.session_state.ban_time
        if elapsed < timedelta(minutes=5):
            remaining = 5 - int(elapsed.total_seconds() / 60)
            return f"🚫 Em vẫn đang giận và cấm chat! Còn {remaining} phút nữa mới được hỏi tiếp nhé!"
        else:
            st.session_state.ban_time = None # Hết thời gian cấm
            st.session_state.warning_count = 0 # Reset lại từ đầu

    # Kiểm tra chủ đề
    is_probability = any(word in prompt.lower() for word in ["xác suất", "thống kê", "biến cố", "tính toán", "p("])
    
    if is_probability:
        return model.generate_content(f"Giải bài tập xác suất: {prompt}").text
    else:
        st.session_state.warning_count += 1
        count = st.session_state.warning_count
        
        if count == 1:
            return "Chị chỉ giải bài tập xác suất thôi nha!!"
        elif count == 2:
            return "nhắc lại là chị chỉ giải bài tập thôi , hỏi ngoài nữa là chị giận em đó!"
        elif count == 3:
            return " GIẬN RỒI! Hỏi nữa là chị cấm chat em đấy!"
        else:
            st.session_state.ban_time = datetime.now()
            return "🚫 ĐỦ RỒI! chị sẽ cấm chat em trong 5 phút vì không nghe lời! (╯°□°）╯︵ ┻━┻"

# Giao diện chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Em có thắc mắc gì cần chị giải đáp không nè(´｡• ω •｡`) ♡ "):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = get_ai_response(prompt)
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})