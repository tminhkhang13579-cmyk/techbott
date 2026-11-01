import streamlit as st
import os
import json
from pathlib import Path
import pandas as pd
import re
import unicodedata
from google import genai
from google.genai import types

# Cấu hình trang Streamlit
st.set_page_config(
    page_title="TechBot Store - Trợ lý AI Sản Phẩm Công Nghệ",
    page_icon="🤖",
    layout="centered"
)

# --- 1. KHỞI TẠO DỮ LIỆU VÀ CẤU HÌNH ---
@st.cache_resource
def load_data_and_config():
    # Catalog sản phẩm
    catalog_path = Path("techbot_products_catalog_300_filled.csv")
    if not catalog_path.exists():
        sample_products = [
            {
                "product_id": "0251",
                "product_name": "PlayStation 5",
                "brand": "Sony",
                "category": "Thiết bị chơi game",
                "release_year": "2020",
                "launch_price": "499",
                "currency": "USD",
                "specifications": "CPU AMD Zen 2 8 nhân 3.5GHz; GPU RDNA 2 10.28 TFLOPS; RAM 16GB GDDR6; SSD 825GB; ổ UHD Blu-ray; hỗ trợ 4K 120Hz, ray tracing",
                "advantages": "SSD siêu nhanh; DualSense có haptic và trigger thích ứng; thư viện game độc quyền mạnh",
                "disadvantages": "Dung lượng SSD hạn chế; thiếu nguồn hàng giai đoạn đầu",
                "successor_model": "PlayStation 5 Pro",
                "official_source_url": "https://www.sony.com",
                "data_status": "Điền từ kiến thức nền, cần đối chiếu nguồn hãng; giá là giá niêm yết khởi điểm tại Mỹ (USD)"
            },
            {
                "product_id": "0132",
                "product_name": "WH-1000XM5",
                "brand": "Sony",
                "category": "Tai nghe và âm thanh",
                "release_year": "2022",
                "launch_price": "399.99",
                "currency": "USD",
                "specifications": "Tai nghe over-ear không dây; ANC với 8 mic; Bluetooth 5.2; pin khoảng 30 giờ; kết nối đa điểm",
                "advantages": "ANC rất tốt; thoải mái; âm thanh chi tiết",
                "disadvantages": "Không gập phẳng; giá cao",
                "successor_model": "WH-1000XM6",
                "official_source_url": "https://www.sony.com",
                "data_status": "Điền từ kiến thức nền, cần đối chiếu nguồn hãng"
            },
            {
                "product_id": "0064",
                "product_name": "G Pro X Superlight 2",
                "brand": "Logitech",
                "category": "Chuột máy tính",
                "release_year": "2023",
                "launch_price": "159.99",
                "currency": "USD",
                "specifications": "Cảm biến HERO 2 32K; trọng lượng 60g; pin khoảng 95 giờ; tần số quét tới 2000Hz; cổng USB-C; công tắc lai LIGHTFORCE",
                "advantages": "Nhẹ 60g; pin 95 giờ; USB-C; tần số quét cao",
                "disadvantages": "Giá cao; kiểu dáng chỉ phù hợp tay trung và lớn",
                "successor_model": "Chưa xác định",
                "official_source_url": "https://www.logitech.com",
                "data_status": "Điền từ kiến thức nền, cần đối chiếu nguồn hãng"
            },
            {
                "product_id": "0039",
                "product_name": "MacBook Air M3 (2024)",
                "brand": "Apple",
                "category": "Laptop",
                "release_year": "2024",
                "launch_price": "1099",
                "currency": "USD",
                "specifications": "Chip M3 (CPU 8 nhân, GPU 8/10 nhân); RAM 8/16/24GB; SSD 256GB-2TB; màn hình 13.6\" Liquid Retina",
                "advantages": "Hỗ trợ hai màn hình ngoài khi gập; chip M3 mạnh",
                "disadvantages": "RAM khởi điểm vẫn 8GB; chỉ 2 cổng",
                "successor_model": "MacBook Air M4 (2025)",
                "official_source_url": "https://www.apple.com",
                "data_status": "Điền từ kiến thức nền, cần đối chiếu nguồn hãng"
            },
            {
                "product_id": "0013",
                "product_name": "iPhone 17",
                "brand": "Apple",
                "category": "Điện thoại",
                "release_year": "2025",
                "launch_price": "799",
                "currency": "USD",
                "specifications": "Màn hình 6.3\" OLED ProMotion 120Hz; chip A19; bộ nhớ khởi điểm 256GB; camera sau kép 48MP",
                "advantages": "Màn hình 120Hz; dung lượng khởi điểm 256GB",
                "disadvantages": "Không có camera tele",
                "successor_model": "iPhone 18",
                "official_source_url": "https://www.apple.com",
                "data_status": "Độ tin cậy thấp: năm, giá hoặc thông số cần xác minh từ nguồn hãng"
            }
        ]
        pd.DataFrame(sample_products).to_csv(catalog_path, index=False, encoding="utf-8")
    
    df = pd.read_csv(catalog_path, dtype=str).fillna("")

    # Cấu hình cửa hàng
    config_path = Path("config.json")
    if not config_path.exists():
        sample_config = {
            "store_name": "TechBot Store",
            "store_address": "123 Đường Công Nghệ, Quận 1, TP.HCM",
            "hotline": "1900-0000",
            "functions": ["giới thiệu cửa hàng", "giới thiệu sản phẩm công nghệ", "giải đáp thông số và so sánh sản phẩm"],
            "out_of_scope_message": "Tôi đang không hỗ trợ chức năng này. Xin vui lòng liên hệ nhân viên cửa hàng qua hotline 1900-0000 để được trợ giúp."
        }
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(sample_config, f, ensure_ascii=False, indent=2)
            
    with open(config_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    return df, cfg

catalog_df, config = load_data_and_config()
MODEL_NAME = "gemini-3.1-flash-lite"

# --- 2. CÁC HÀM XỬ LÝ TÌM KIẾM VÀ GỌI AI ---
def normalize(text) -> str:
    text = unicodedata.normalize("NFD", str(text).lower())
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()

CATEGORY_KEYWORDS = {
    "Điện thoại": ["dien thoai", "smartphone", "phone"],
    "Laptop": ["laptop", "may tinh xach tay", "notebook"],
    "Chuột máy tính": ["chuot", "mouse"],
    "Bàn phím": ["ban phim", "keyboard"],
    "Tai nghe và âm thanh": ["tai nghe", "loa", "am thanh", "headphone", "earbuds"],
    "Màn hình": ["man hinh", "monitor"],
    "Đồng hồ và vòng đeo": ["dong ho", "vong deo", "smartwatch", "watch", "band"],
    "Máy tính bảng và e-reader": ["may tinh bang", "tablet", "e reader", "ereader", "ebook"],
    "Thiết bị chơi game": ["choi game", "may choi game", "console", "game"],
    "Mạng và lưu trữ": ["mang", "luu tru", "router", "wifi", "ssd", "nas", "usb", "o cung"],
}

STOPWORDS = set("co la cua cho va nhung cac mot nao gi nhu the bao nhieu gia may thong so so sanh khac nhau ra mat nam khi tu den nay do hay voi ve thi nen o mau loai hang cua hang nhe nhat tot nhat".split())

def search_products(df: pd.DataFrame, question: str):
    q_norm = normalize(question)
    q_tokens = {t for t in q_norm.split() if t not in STOPWORDS}
    scored = []
    for idx, row in df.iterrows():
        name_tokens = normalize(row["product_name"]).split()
        core = [t for t in name_tokens if not re.fullmatch(r"(19|20)\d{2}", t)]
        brand_norm = normalize(row["brand"])
        matched = [t for t in core if t in q_tokens]
        score = 3.0 * len(matched)
        if core and len(matched) == len(core):
            score += 10
        brand_hit = brand_norm in q_tokens or any(t in q_tokens for t in brand_norm.split())
        if brand_hit:
            score += 2
        cat_hit = any(kw in f" {q_norm} " if " " in kw else kw in q_tokens for kw in CATEGORY_KEYWORDS.get(row["category"], []))
        if cat_hit:
            score += 1.5
        if brand_hit and cat_hit:
            score += 3
        if str(row["release_year"]) in q_tokens:
            score += 1
        if score > 0:
            scored.append((score, idx))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [idx for _, idx in scored]

def reliability_text(status: str) -> str:
    status = str(status)
    note = ""
    if "Ghi chú:" in status:
        note = " Ghi chú: " + status.split("Ghi chú:", 1)[1].strip()
    if status.startswith("Độ tin cậy thấp"):
        return "thấp, cần xác minh từ nguồn hãng." + note
    return "trung bình, cần đối chiếu nguồn hãng." + note

def format_product(row) -> str:
    year = row["release_year"] or "chưa rõ"
    price = f"{row['launch_price']} {row['currency']}".strip() if row["launch_price"] else "chưa có dữ liệu giá"
    successor = row["successor_model"] or "chưa rõ"
    return (
        f"- {row['product_name']} ({row['brand']} | {row['category']} | ra mắt: {year}). "
        f"Giá khởi điểm: {price}. "
        f"Thông số: {row['specifications']}. "
        f"Ưu điểm: {row['advantages']}. "
        f"Nhược điểm: {row['disadvantages']}. "
        f"Đời kế nhiệm: {successor}. "
        f"Độ tin cậy dữ liệu: {reliability_text(row['data_status'])}"
    )

def catalog_overview(df: pd.DataFrame) -> str:
    parts = [f"{cat}: {n} sản phẩm" for cat, n in df["category"].value_counts().items()]
    return f"Catalog có {len(df)} sản phẩm. Các nhóm: " + "; ".join(parts) + "."

def build_catalog_context(df: pd.DataFrame, question: str, top_k: int = 8, extra_names: int = 25) -> str:
    matches = search_products(df, question)
    lines = [catalog_overview(df)]
    if not matches:
        lines.append("Không tìm thấy sản phẩm nào trong catalog khớp với câu hỏi này.")
        return "\n".join(lines)
    lines.append("Các sản phẩm liên quan nhất:")
    for idx in matches[:top_k]:
        lines.append(format_product(df.loc[idx]))
    rest = matches[top_k:top_k + extra_names]
    if rest:
        short = ", ".join(f"{df.loc[i, 'product_name']} ({df.loc[i, 'release_year'] or '?'})" for i in rest)
        lines.append(f"Các sản phẩm liên quan khác: {short}.")
    return "\n".join(lines)

def build_system_instruction(cfg: dict) -> str:
    store_name = cfg.get("store_name", "TechBot Store")
    store_address = cfg.get("store_address", "")
    functions = ", ".join(cfg.get("functions", ["tư vấn sản phẩm công nghệ"]))
    out_of_scope_message = cfg.get(
        "out_of_scope_message",
        "Tôi đang không hỗ trợ chức năng này. Xin vui lòng liên hệ nhân viên cửa hàng qua hotline để được trợ giúp."
    )
    return f"""
Bạn tên là TechBot, trợ lý AI thông minh, nhiệt tình và lịch sự của cửa hàng {store_name}.
Địa chỉ cửa hàng: {store_address}.
Các nhiệm vụ hỗ trợ: {functions}.

Quy tắc trả lời BẮT BUỘC:
1. Luôn trả lời bằng tiếng Việt, giọng điệu thân thiện, rõ ràng, chuyên nghiệp.
2. Chỉ tư vấn dựa trên dữ liệu sản phẩm cung cấp. Tuyệt đối KHÔNG tự bịa sản phẩm, thông số hay giá.
3. Nếu dữ liệu ghi "chưa có dữ liệu giá", hãy nói rõ là chưa có dữ liệu.
4. Khi giới thiệu sản phẩm, nêu thông số chính, ưu điểm, nhược điểm, năm ra mắt, đời kế nhiệm. Nhắc khách đối chiếu nguồn hãng nếu độ tin cậy thấp/trung bình. Giá là giá khởi điểm.
5. So sánh đối chiếu từng tiêu chí dựa trên dữ liệu cung cấp.
6. Nếu hỏi sản phẩm không có trong dữ liệu nhưng thuộc lĩnh vực công nghệ, nói rõ sản phẩm hiện chưa có trong catalog.
7. Nếu hỏi ngoài phạm vi công nghệ (thời tiết, món ăn, toán học...), trả lời ĐÚNG câu sau:
   "{out_of_scope_message}"
8. Giữ câu trả lời súc tích, mạch lạc, dễ đọc.
""".strip()

def generate_text(prompt: str, system_instruction: str, api_key: str, use_mock: bool) -> str:
    if use_mock or not api_key:
        return "[Mock Mode]: Chào bạn! Đây là câu trả lời giả lập. Hãy nhập API Key thực tế vào thanh bên trái để kết nối Gemini AI chính thức."
    try:
        client = genai.Client(api_key=api_key)
        config_ai = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.3
        )
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config_ai,
        )
        return response.text
    except Exception as e:
        return f"⚠️ Lỗi khi gọi Gemini API ({e}). Đang dùng chế độ giả lập phản hồi."

def ask_bot(question: str, api_key: str, use_mock: bool) -> str:
    catalog_context = build_catalog_context(catalog_df, question)
    system_instruction = build_system_instruction(config)
    user_prompt = f"""
Dưới đây là thông tin sản phẩm liên quan trong catalog của cửa hàng:
{catalog_context}

Khách hàng hỏi:
"{question}"

Hãy trả lời khách hàng theo đúng vai trò TechBot và các quy tắc đã được hướng dẫn.
"""
    return generate_text(user_prompt, system_instruction, api_key, use_mock)

# --- 3. GIAO DIỆN STREAMLIT (UI) ---
st.sidebar.title("⚙️ Cấu hình TechBot")
api_key_input = st.sidebar.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
use_mock_mode = st.sidebar.checkbox("Bật Mock Mode (Chế độ giả lập)", value=not bool(api_key_input))

st.sidebar.markdown("---")
st.sidebar.subheader(f"🏪 {config['store_name']}")
st.sidebar.write(f"📍 **Địa chỉ:** {config['store_address']}")
st.sidebar.write(f"☎️ **Hotline:** {config['hotline']}")
st.sidebar.write(f"📊 **Sản phẩm trong kho:** {len(catalog_df)}")

st.sidebar.markdown("---")
st.sidebar.subheader("💡 Câu hỏi gợi ý nhanh:")
sample_q1 = "Cửa hàng có những mẫu iPhone nào?"
sample_q2 = "MacBook Air M3 có thông số gì và giá bao nhiêu?"
sample_q3 = "Hôm nay thời tiết thế nào?"

if st.sidebar.button(sample_q1):
    st.session_state.selected_question = sample_q1
if st.sidebar.button(sample_q2):
    st.session_state.selected_question = sample_q2
if st.sidebar.button(sample_q3):
    st.session_state.selected_question = sample_q3

# Giao diện chính
st.title("🤖 TechBot Store Assistant")
st.markdown(f"Chào mừng bạn đến với **{config['store_name']}**! Tôi có thể giúp gì cho bạn về các sản phẩm công nghệ hôm nay?")

# Khởi tạo lịch sử chat trong session_state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Lấy câu hỏi từ nút gợi ý hoặc ô nhập chat
user_input = st.chat_input("Nhập câu hỏi của bạn về sản phẩm công nghệ...")

if "selected_question" in st.session_state and st.session_state.selected_question:
    user_input = st.session_state.selected_question
    st.session_state.selected_question = None

if user_input:
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Sinh phản hồi từ bot
    with st.chat_message("assistant"):
        with st.spinner("TechBot đang tra cứu catalog và soạn câu trả lời..."):
            response = ask_bot(user_input, api_key_input, use_mock_mode)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})