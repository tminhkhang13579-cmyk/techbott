# TechBot — Chatbot tư vấn sản phẩm công nghệ

TechBot tra cứu CSV trước khi sử dụng Gemini để diễn đạt câu trả lời. Dữ liệu trống không được tự suy đoán.

## Tệp dự án

- `TechBot_Chatbot.ipynb`: notebook chính chạy trên Google Colab.
- `techbot_products_catalog_300.csv`: danh sách sản phẩm khởi tạo (đặt cùng notebook hoặc tải lên khi notebook yêu cầu).
- `requirements.txt`: thư viện cần thiết.

## Chạy trên Google Colab

1. Tải `TechBot_Chatbot.ipynb` lên Google Colab.
2. Tải `techbot_products_catalog_300.csv` lên cùng phiên làm việc khi notebook yêu cầu.
3. Chạy từng cell từ trên xuống.
4. Để bật Gemini, tạo API key trong Google AI Studio và lưu dưới tên `GEMINI_API_KEY` trong Colab Secrets. Không đưa key lên GitHub.
5. Nếu không có API key, các chức năng tra cứu CSV vẫn có thể sử dụng.

## Cấu trúc CSV

`product_id`, `product_name`, `brand`, `category`, `release_year`, `launch_price`, `currency`, `specifications`, `advantages`, `disadvantages`, `successor_model`, `official_source_url`, `data_status`.

## Giới hạn dữ liệu

CSV khởi tạo chưa xác minh đầy đủ năm ra mắt, giá và thông số. Hãy bổ sung dữ liệu từ nguồn đáng tin cậy trước khi dùng để tư vấn thực tế. TechBot không tự điền giá trị chưa có.

## Chạy ngoài Colab

Notebook sử dụng tính năng tải file của Colab và widget. Để chạy ngoài Colab, cài thư viện bằng `pip install -r requirements.txt`, đặt biến môi trường `GEMINI_API_KEY`, và điều chỉnh phần tải file theo đường dẫn CSV trên máy.
