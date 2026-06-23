import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta

# Cấu hình giao diện
st.set_page_config(page_title="Gia sư Xác suất", page_icon="🎲")
st.title("🎲 Gia sư Xác suất Soleil")

# Cấu hình API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key trong Secrets!")
    st.stop()

# Khởi tạo trạng thái
if "messages" not in st.session_state: st.session_state.messages = []
if "warning_count" not in st.session_state: st.session_state.warning_count = 0
if "ban_time" not in st.session_state: st.session_state.ban_time = None
if "forgiven_today" not in st.session_state: st.session_state.forgiven_today = None

def check_forgiveness(prompt):
    try:
        evaluation_prompt = f"Người dùng vừa chat: '{prompt}'. Họ có đang thành khẩn xin lỗi hoặc hối hận không? Chỉ trả lời YES hoặc NO."
        response = model.generate_content(evaluation_prompt)
        return "YES" in response.text.upper()
    except:
        return False

def get_ai_response(prompt):
    # 1. Logic Tha thứ
    if check_forgiveness(prompt):
        if st.session_state.forgiven_today == date.today():
            return "Chị chỉ rộng lượng một lần với em thôi! 🙄"
        else:
            st.session_state.warning_count = 0
            st.session_state.ban_time = None
            st.session_state.forgiven_today = date.today()
            return "Thôi được rồi, thấy thành khẩn nên chị tha! Lần sau mà lì nữa thì xác định nhé nhé! 😊"

    # 2. Logic Cấm chat
    if st.session_state.ban_time:
        elapsed = datetime.now() - st.session_state.ban_time
        if elapsed < timedelta(minutes=5):
            remaining = 5 - int(elapsed.total_seconds() / 60)
            return f"🚫 Chị vẫn đang giận! Còn {remaining} phút chị mới hết dỗi!"
        else:
            st.session_state.ban_time = None
            st.session_state.warning_count = 0

    # 3. Logic Xác suất
    is_probability = any(word in prompt.lower() for word in ["xác suất", "thống kê", "biến cố", "tính toán", "p("])
    
    if is_probability:
        return model.generate_content(f"Giải bài tập xác suất: {prompt}").text
    else:
        st.session_state.warning_count += 1
        if st.session_state.warning_count >= 4:
            st.session_state.ban_time = datetime.now()
            return "🚫 ĐỦ RỒI! Chị cấm chat 5 phút! ai bảo lì quá "
        elif st.session_state.warning_count == 3: return "😡 GIẬN RỒI! Hỏi nữa là chị cấm đấy!"
        elif st.session_state.warning_count == 2: return "⚠️ nhắc lại là chị chỉ giải bài tập xác suất thôi (-_-)"
        else: return "chị chỉ giải bài tập Xác suất thôi nha! "

# Giao diện hiển thị
for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

if prompt := st.chat_input("Gửi bài tập xác suất cho mình nhé..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response_text = get_ai_response(prompt)
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})