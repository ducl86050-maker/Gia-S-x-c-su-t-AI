import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta # Đã thêm đầy đủ thư viện cần thiết

st.set_page_config(page_title="Gia sư Xác suất", page_icon="🎲")
st.title("🎲 Gia sư Xác suất Soleil")

# Cấu hình API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Chưa cấu hình API Key trong Secrets!")
    st.stop()

# Khởi tạo các trạng thái
if "messages" not in st.session_state: st.session_state.messages = []
if "warning_count" not in st.session_state: st.session_state.warning_count = 0
if "ban_time" not in st.session_state: st.session_state.ban_time = None
if "forgiven_today" not in st.session_state: st.session_state.forgiven_today = None

def get_ai_response(prompt):
    # 1. Tính năng xin lỗi và tha lỗi
    if "em xin lỗi" in prompt.lower() or "tha lỗi" in prompt.lower():
        if st.session_state.forgiven_today == date.today():
            return "Anh/chị đã dùng quyền được tha lỗi hôm nay rồi! Em không tha nữa đâu nhé! 😤"
        else:
            st.session_state.warning_count = 0
            st.session_state.ban_time = None
            st.session_state.forgiven_today = date.today()
            return "Thôi được rồi, thấy anh/chị thành khẩn nên em tha cho lần này đấy. Lần sau chú ý nhé! 😊"

    # 2. Kiểm tra lệnh cấm
    if st.session_state.ban_time:
        elapsed = datetime.now() - st.session_state.ban_time
        if elapsed < timedelta(minutes=5):
            remaining = 5 - int(elapsed.total_seconds() / 60)
            return f"🚫 Em vẫn đang giận và cấm chat! Còn {remaining} phút nữa mới được hỏi tiếp nhé!"
        else:
            st.session_state.ban_time = None
            st.session_state.warning_count = 0

    # 3. Logic xác suất
    is_probability = any(word in prompt.lower() for word in ["xác suất", "thống kê", "biến cố", "tính toán", "p("])
    
    if is_probability:
        return model.generate_content(f"Giải bài tập xác suất: {prompt}").text
    else:
        st.session_state.warning_count += 1
        count = st.session_state.warning_count
        if count >= 4:
            st.session_state.ban_time = datetime.now()
            return "🚫 ĐỦ RỒI! Em cấm chat 5 phút! Nếu muốn em tha lỗi thì hãy ghi 'Em xin lỗi' nhé!"
        elif count == 3: return "😡 GIẬN RỒI! Hỏi nữa là em cấm chat đấy!"
        elif count == 2: return "⚠️ Cảnh báo lần 2: Đừng hỏi ngoài lề nữa!"
        else: return "Dạ, em chỉ giải bài tập Xác suất thôi ạ."

# Giao diện chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Gửi bài tập xác suất cho mình nhé..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = get_ai_response(prompt)
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})