import streamlit as st
import google.generativeai as genai
from datetime import datetime, date, timedelta

st.set_page_config(page_title="Gia sư Xác suất", page_icon="🎲")
st.title("🎲 Gia sư Xác suất Soleil")

# Cấu hình API
if "GOOGLE_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
    model = genai.GenerativeModel('gemini-2.5-flash')
else:
    st.error("Chưa cấu hình API Key!")
    st.stop()

# Khởi tạo session
if "messages" not in st.session_state: st.session_state.messages = []
if "warning_count" not in st.session_state: st.session_state.warning_count = 0
if "ban_time" not in st.session_state: st.session_state.ban_time = None

def get_ai_response(prompt):
    prompt_lower = prompt.lower()
    
    # --- TẦNG 1: BỘ LỌC CỤC BỘ (Không tốn API) ---
    # Kiểm tra xin lỗi
    if any(k in prompt_lower for k in ["xin lỗi", "tha lỗi", "sorry", "tha cho"]):
        st.session_state.warning_count = 0
        st.session_state.ban_time = None
        return "Thôi được rồi, thấy thành khẩn nên chị tha đấy! 😊"
    
    # Kiểm tra chào hỏi/linh tinh
    if any(greet in prompt_lower for greet in ["chào", "hello", "hi", "bạn là ai"]):
        return "Chị là gia sư Xác suất, đừng hỏi linh tinh, tập trung học đi! 📚"

    # --- TẦNG 2: GỌI API (Chỉ khi cần thiết) ---
    is_probability = any(word in prompt_lower for word in ["xác suất", "thống kê", "biến cố", "tính toán", "p("])
    
    if is_probability:
        # Kiểm tra cấm chat
        if st.session_state.ban_time:
            if datetime.now() - st.session_state.ban_time < timedelta(minutes=5):
                return "🚫 Đang bị cấm chat, 5 phút nữa mới được hỏi nhé!"
            else:
                st.session_state.ban_time = None
                st.session_state.warning_count = 0
        
        try:
            return model.generate_content(f"Giải bài tập xác suất: {prompt}").text
        except:
            return "hồi nãy giải bài cho bạn kia mệt quá! em cho chị chút thời gian nghỉ ngơi nhé!"
            
    else:
        st.session_state.warning_count += 1
        if st.session_state.warning_count >= 4:
            st.session_state.ban_time = datetime.now()
            return "🚫 ĐỦ RỒI! Chị cấm chat 5 phút! ai bảo lì quá!"
        return f"⚠️ Chị chỉ giải bài tập Xác suất thôi (Lần {st.session_state.warning_count}/4)!"

# Giao diện
for message in st.session_state.messages:
    with st.chat_message(message["role"]): st.markdown(message["content"])

if prompt := st.chat_input("Gửi bài tập xác suất cho chị nhé..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)
    with st.chat_message("assistant"):
        response_text = get_ai_response(prompt)
        st.markdown(response_text)
        st.session_state.messages.append({"role": "assistant", "content": response_text})