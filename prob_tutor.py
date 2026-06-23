from datetime import date # Thêm thư viện này ở đầu file

# ... (các phần cũ giữ nguyên)

# Thêm biến lưu trạng thái tha lỗi
if "forgiven_today" not in st.session_state: st.session_state.forgiven_today = None

def get_ai_response(prompt):
    # 1. Kiểm tra "Lời xin lỗi"
    if "em xin lỗi" in prompt.lower() or "tha lỗi" in prompt.lower():
        if st.session_state.forgiven_today == date.today():
            return "Anh/chị đã dùng quyền được tha lỗi hôm nay rồi! Em không tha nữa đâu nhé! 😤"
        else:
            st.session_state.warning_count = 0
            st.session_state.ban_time = None
            st.session_state.forgiven_today = date.today() # Ghi lại ngày đã tha
            return "Thôi được rồi, thấy anh/chị thành khẩn nên em tha cho lần này đấy. Lần sau chú ý nhé! 😊"

    # 2. Kiểm tra cấm chat (giữ nguyên logic cũ)
    if st.session_state.ban_time:
        elapsed = datetime.now() - st.session_state.ban_time
        if elapsed < timedelta(minutes=5):
            remaining = 5 - int(elapsed.total_seconds() / 60)
            return f"🚫 Em vẫn đang giận! Còn {remaining} phút nữa mới được hỏi tiếp!"
        else:
            st.session_state.ban_time = None
            st.session_state.warning_count = 0

    # 3. Kiểm tra chủ đề (giữ nguyên logic cũ)
    is_probability = any(word in prompt.lower() for word in ["xác suất", "thống kê", "biến cố", "tính toán", "p("])
    
    if is_probability:
        return model.generate_content(f"Giải bài tập xác suất: {prompt}").text
    else:
        st.session_state.warning_count += 1
        count = st.session_state.warning_count
        if count >= 4:
            st.session_state.ban_time = datetime.now()
            return "🚫 CẤM CHAT! Nếu muốn em tha lỗi thì hãy ghi 'Em xin lỗi' nhé!"
        elif count == 3: return "😡 GIẬN RỒI! Hỏi nữa là em cấm chat đấy!"
        elif count == 2: return "⚠️ Cảnh báo lần 2: Đừng hỏi ngoài lề nữa!"
        else: return "Dạ, em chỉ giải bài tập Xác suất thôi ạ."