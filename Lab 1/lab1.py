import tkinter
from PIL import Image, ImageTk
from collections import Counter

# --- CẤU HÌNH GIAO DIỆN VÀ HẰNG SỐ ---
CANVAS_WIDTH = 700          # Tổng chiều rộng cửa sổ
IMAGE_DISPLAY_WIDTH = 480   # Chiều rộng cố định cho ảnh chính (Theo yêu cầu: 480)
IMAGE_DISPLAY_HEIGHT = 320  # Chiều cao cố định cho ảnh chính (Theo yêu cầu: 320)
HISTOGRAM_FRAME_WIDTH = 200 # Chiều rộng dành cho 3 biểu đồ RGB kênh (700 - 480 - padding)
CANVAS_HEIGHT = 400         # Chiều cao của vùng hiển thị (để chứa ảnh 320px + margin)
HISTOGRAM_HEIGHT = 100      # Chiều cao cho mỗi histogram kênh màu (R, G, B)
AVG_HISTOGRAM_HEIGHT = 100  # Chiều cao cho biểu đồ trung bình

root = tkinter.Tk()
root.title("Graphical user interface - Хоанг Ван Куан - Р3468")

# Canvas chính để hiển thị ảnh (chiều rộng 480px)
canvas = tkinter.Canvas(root, height=CANVAS_HEIGHT, width=IMAGE_DISPLAY_WIDTH, bg="#f0f0f0")

# Khung chứa 3 canvas cho 3 kênh màu (chiều rộng 200px)
histogram_frame = tkinter.Frame(root)

# Tạo 3 Canvas riêng biệt cho R, G, B (chiều rộng 200px)
r_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, bg="#ffe0e0", bd=1, relief="ridge")
g_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, bg="#e0ffe0", bd=1, relief="ridge")
b_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, bg="#e0e0ff", bd=1, relief="ridge")

# Canvas mới cho biểu đồ trung bình (chiều rộng 700px)
avg_canvas = tkinter.Canvas(root, height=AVG_HISTOGRAM_HEIGHT, width=CANVAS_WIDTH, bg="#f8f8f8", bd=1, relief="ridge")

info_label = tkinter.Label(root, text="Нажмите на картинку для анализа RGB каналов", font=("Arial", 11, "bold"))

# Biến toàn cục để lưu trữ trạng thái
photo = None
current_image_path = None
current_pil_image = None # Lưu trữ đối tượng PIL Image gốc

# --- HÀM PHÂN TÍCH VÀ VẼ BIỂU ĐỒ ---

def draw_average_histogram(avg_data):
    """Vẽ biểu đồ thanh thể hiện giá trị cường độ trung bình (0-255) của RGB."""
    avg_canvas.delete("all")
    
    max_avg = 255 # Cường độ tối đa
    bar_width = 150
    bar_gap = 50
    
    # Tính toán vị trí căn giữa
    total_bar_width = 3 * bar_width + 2 * bar_gap
    start_x = (CANVAS_WIDTH - total_bar_width) / 2
    
    drawing_area_height = AVG_HISTOGRAM_HEIGHT - 35
    base_y = AVG_HISTOGRAM_HEIGHT - 5

    avg_canvas.create_text(CANVAS_WIDTH / 2, 10, 
                             text="Средняя интенсивность каналов RGB (0-255)", 
                             font=("Arial", 9, "bold"), 
                             fill="#333")
    
    for i, (channel, avg_val, color) in enumerate(avg_data):
        # Chiều cao cột được chuẩn hóa theo giá trị 255
        bar_height = (avg_val / max_avg) * drawing_area_height
        
        x1 = start_x + i * (bar_width + bar_gap)
        y1 = base_y - bar_height
        x2 = x1 + bar_width
        y2 = base_y
        
        # Vẽ cột
        avg_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#333")
        
        # Nhãn giá trị
        avg_canvas.create_text(x1 + bar_width / 2, y1 - 10, 
                               text=f"{avg_val:.2f}", 
                               font=("Arial", 9, "bold"), fill="#000")
        
        # Nhãn kênh màu (R/G/B)
        avg_canvas.create_text(x1 + bar_width / 2, base_y + 10, 
                               text=channel, 
                               font=("Arial", 9, "bold"), fill=color)

def analyze_and_draw_channels(pil_image):
    """
    Tách ảnh thành 3 kênh RGB, tính toán tần suất pixel (histogram) 
    và vẽ biểu đồ cho từng kênh, đồng thời tính và vẽ giá trị trung bình.
    """
    # Đảm bảo ảnh được chuyển sang chế độ RGB để tách kênh
    rgb_image = pil_image.convert("RGB")
    
    # Tách 3 kênh
    r_channel, g_channel, b_channel = rgb_image.split()
    
    # Tính toán tần suất giá trị (0-255) cho mỗi kênh
    r_data = r_channel.getdata()
    g_data = g_channel.getdata()
    b_data = b_channel.getdata()

    # Sử dụng Counter để đếm tần suất
    r_counts = Counter(r_data)
    g_counts = Counter(g_data)
    b_counts = Counter(b_data)

    # Tìm giá trị count lớn nhất trên cả 3 kênh để chuẩn hóa chiều cao biểu đồ
    all_counts = list(r_counts.values()) + list(g_counts.values()) + list(b_counts.values())
    max_count = max(all_counts) if all_counts else 1

    # Dữ liệu cho từng kênh (tần suất, canvas, màu hiển thị)
    channels_data = [
        (r_counts, r_canvas, "#ff0000", "Красный (R)"),
        (g_counts, g_canvas, "#00ff00", "Зеленый (G)"),
        (b_counts, b_canvas, "#0000ff", "Синий (B)"),
    ]

    # Vẽ từng histogram
    for counts, target_canvas, bar_color, channel_name in channels_data:
        draw_single_histogram(counts, target_canvas, max_count, bar_color, channel_name)
        
    # NEW: Tính toán và vẽ biểu đồ trung bình
    img_size = pil_image.width * pil_image.height
    
    # Tính tổng cường độ
    sum_r = sum(intensity * count for intensity, count in r_counts.items())
    sum_g = sum(intensity * count for intensity, count in g_counts.items())
    sum_b = sum(intensity * count for intensity, count in b_counts.items())
    
    # Tính giá trị trung bình
    avg_r = sum_r / img_size
    avg_g = sum_g / img_size
    avg_b = sum_b / img_size
    
    avg_data = [
        ("R", avg_r, "#ff0000"),
        ("G", avg_g, "#00ff00"),
        ("B", avg_b, "#0000ff")
    ]
    
    draw_average_histogram(avg_data)


def draw_single_histogram(counts, target_canvas, max_count, bar_color, channel_name):
    """Vẽ một histogram duy nhất cho một kênh màu."""
    target_canvas.delete("all")
    
    # Vùng vẽ biểu đồ (chừa chỗ cho tiêu đề)
    drawing_area_height = HISTOGRAM_HEIGHT - 25
    base_y = HISTOGRAM_HEIGHT - 5
    
    # Tiêu đề được căn giữa trong HISTOGRAM_FRAME_WIDTH
    target_canvas.create_text(HISTOGRAM_FRAME_WIDTH / 2, 10, 
                             text=f"Канал {channel_name}: Распределение интенсивности (0-255)", 
                             font=("Arial", 9, "bold"), 
                             fill=bar_color)
    
    # Vẽ 256 cột (mỗi cột tương ứng 1 giá trị cường độ)
    bar_width_total = HISTOGRAM_FRAME_WIDTH / 256 # Tính chiều rộng thực tế của mỗi cột (200/256)
    
    for intensity in range(256):
        count = counts.get(intensity, 0) # Lấy tần suất, mặc định là 0
        
        # Chuẩn hóa chiều cao cột theo max_count
        bar_height = (count / max_count) * drawing_area_height
        
        x1 = intensity * bar_width_total
        y1 = base_y - bar_height
        x2 = x1 + bar_width_total
        y2 = base_y
        
        target_canvas.create_rectangle(x1, y1, x2, y2, fill=bar_color, outline="")

# --- HÀM HIỂN THỊ ẢNH ---

def display(image_path):
    """Tải, đổi kích thước và hiển thị hình ảnh."""
    global photo
    global current_image_path
    global current_pil_image
    
    try:
        pil_image = Image.open(image_path)
        
        # Resize ảnh CỐ ĐỊNH sang 480x320 theo yêu cầu
        resized_image = pil_image.resize((IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(resized_image)
        
        canvas.delete("all")
        center_x = IMAGE_DISPLAY_WIDTH / 2 # Sử dụng chiều rộng mới
        center_y = CANVAS_HEIGHT / 2
        
        canvas.create_image(center_x, center_y, anchor='center', image=photo)
        
        # Lưu trữ ảnh gốc (chưa resize) để phân tích chính xác
        current_pil_image = pil_image
        current_image_path = image_path
        
        # Xóa các biểu đồ cũ và reset nhãn thông tin
        r_canvas.delete("all")
        g_canvas.delete("all")
        b_canvas.delete("all")
        avg_canvas.delete("all") # Xóa canvas trung bình
        info_label.config(text=f"Изображение загружено: {image_path.split('/')[-1]}. Нажмите для анализа RGB.")
        
    except FileNotFoundError:
        canvas.delete("all")
        canvas.create_text(IMAGE_DISPLAY_WIDTH / 2, CANVAS_HEIGHT / 2, text="Изображение не найдено!", fill="red")
        current_image_path = None
        current_pil_image = None
        info_label.config(text="Изображение не найдено!")
        r_canvas.delete("all")
        g_canvas.delete("all")
        b_canvas.delete("all")
        avg_canvas.delete("all")
    except Exception as e:
        canvas.delete("all")
        canvas.create_text(IMAGE_DISPLAY_WIDTH / 2, CANVAS_HEIGHT / 2, text=f"Ошибка обработки: {e}", fill="red")
        current_image_path = None
        current_pil_image = None
        info_label.config(text=f"Ошибка обработки: {e}")
        r_canvas.delete("all")
        g_canvas.delete("all")
        b_canvas.delete("all")
        avg_canvas.delete("all")


def display_image(): display("Lab 1/image_1.png")

def change_image():
    """Chuyển đổi giữa hai hình ảnh."""
    global current_image_path
    # Đặt giá trị mặc định nếu chưa có ảnh nào được hiển thị
    current_path = current_image_path if current_image_path else "Lab 1/image_1.png"

    if current_path == "Lab 1/image_1.png": 
        display("Lab 1/image_2.png")
    else: 
        display("Lab 1/image_1.png")

def on_image_click(event):
    """Xử lý sự kiện click để phân tích các kênh màu."""
    if current_pil_image:
        info_label.config(text="Анализ RGB каналов завершен.")
        analyze_and_draw_channels(current_pil_image)
    else:
        info_label.config(text="Нет картинки для анализа!")
        avg_canvas.delete("all")

# --- BỐ CỤC GIAO DIỆN MỚI ---

# Khung chứa các nút điều khiển (Row 0, Column 0, columnspan 2)
frame = tkinter.Frame(root)
frame.grid(row=0, column=0, columnspan=2, pady=10) 
# Cấu hình cân nặng cột để căn giữa khung chứa ảnh và histogram
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)

but_display = tkinter.Button(frame, text="Показать картику (1)", command=display_image, font=("Arial", 10))
but_display.grid(row=0, column=0, padx=10, pady=10) 

but_change = tkinter.Button(frame, text="Сменить картику (2)", command=change_image, font=("Arial", 10))
but_change.grid(row=0, column=1, padx=10, pady=10)


# ROW 1: MAIN IMAGE (LEFT) VÀ RGB HISTOGRAMS (RIGHT)

# 1. Canvas ảnh chính (Row 1, Column 0) -> LEFT
canvas.grid(row=1, column=0, padx=10, pady=5) 

# 2. Đặt các Canvas histogram vào khung (Row 1, Column 1) -> RIGHT
histogram_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n") # sticky="n" để căn trên
r_canvas.pack(side=tkinter.TOP, pady=2)
g_canvas.pack(side=tkinter.TOP, pady=2)
b_canvas.pack(side=tkinter.TOP, pady=2)

# ROW 2: INFO LABEL (FULL WIDTH)
info_label.grid(row=2, column=0, columnspan=2, pady=5)

# ROW 3: AVERAGE RGB HISTOGRAM (FULL WIDTH)
avg_canvas.grid(row=3, column=0, columnspan=2, pady=5) 

# Gắn sự kiện click vào canvas
canvas.bind("<Button-1>", on_image_click)

root.mainloop()
