import tkinter
from PIL import Image, ImageTk
from collections import Counter

CANVAS_WIDTH = 900             
IMAGE_DISPLAY_WIDTH = 550      
IMAGE_DISPLAY_HEIGHT = 380     
HISTOGRAM_FRAME_WIDTH = 300    
CANVAS_HEIGHT = 450            
HISTOGRAM_HEIGHT = 120         
AVG_HISTOGRAM_HEIGHT = 120     

# Создание окно
root = tkinter.Tk()
root.title("Graphical user interface - Хоанг Ван Куан - Р3468")

# рамка для гистограмм (R, G, B)
canvas = tkinter.Canvas(root, height=CANVAS_HEIGHT, width=IMAGE_DISPLAY_WIDTH, bg="#f0f0f0")
histogram_frame = tkinter.Frame(root)

# подробные гистограммы, показывающие распределение интенсивности каждого цветового канала красного, зеленого и синего на изображении
r_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, relief="ridge")
g_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, relief="ridge")
b_canvas = tkinter.Canvas(histogram_frame, height=HISTOGRAM_HEIGHT, width=HISTOGRAM_FRAME_WIDTH, relief="ridge")
avg_canvas = tkinter.Canvas(root, height=AVG_HISTOGRAM_HEIGHT, width=CANVAS_WIDTH, relief="ridge")
info_label = tkinter.Label(root, text="Нажмите на картинку для анализа RGB", font=("Arial", 11, "bold"))

photo = None
current_image_path = None
current_pil_image = None 

def draw_average_histogram(avg_data):
    # Инициализация и расчет размера
    avg_canvas.delete("all")        
    Y_AXIS_WIDTH = 35 
    MAX_AVG = 255 
    bar_width = 100             
    bar_gap = 40
    total_bars_width = 3 * bar_width + 2 * bar_gap
    full_chart_width = Y_AXIS_WIDTH + 5 + total_bars_width 
    start_offset_x = (CANVAS_WIDTH - full_chart_width) / 2
    drawing_area_height = AVG_HISTOGRAM_HEIGHT - 45 
    base_y = AVG_HISTOGRAM_HEIGHT - 15 

    # Название и координаты оси (Y)
    avg_canvas.create_text(CANVAS_WIDTH / 2, 10, text="Средняя интенсивность RGB (0-255)", font=("Arial", 9, "bold"), fill="#333")
    axis_x = start_offset_x + Y_AXIS_WIDTH
    avg_canvas.create_line(axis_x, base_y, axis_x, base_y - drawing_area_height, fill="#555", width=1)
    avg_canvas.create_text(axis_x - 5, base_y, text="0", anchor="e", font=("Arial", 8, "bold"), fill="#555")
    avg_canvas.create_text(axis_x - 5, base_y - drawing_area_height, text=f"{MAX_AVG:.0f}", anchor="e", font=("Arial", 8, "bold"), fill="#555")
    # Линия сетки
    grid_levels = [0, MAX_AVG / 4, MAX_AVG / 2, MAX_AVG * 3 / 4, MAX_AVG]
    grid_end_x = axis_x + total_bars_width + 30 
    # Метка оси Y
    for level in grid_levels:
        y_pos = base_y - (level / MAX_AVG) * drawing_area_height
        avg_canvas.create_line(axis_x, y_pos, grid_end_x, y_pos, fill="#ccc", dash=(2, 2))
        if level > 0 and level < MAX_AVG: avg_canvas.create_text(axis_x - 5, y_pos, text=f"{level:.0f}", anchor="e", font=("Arial", 7), fill="#888")

    avg_canvas.create_text(axis_x - 40, base_y - drawing_area_height / 2, text="Интенсивность", font=("Arial", 9, "bold"), angle=90, fill="#555")
    
    # столбцы среднего значения
    start_bar_x = axis_x + 10     
    for i, (channel, avg_val, color) in enumerate(avg_data):
        bar_height = (avg_val / MAX_AVG) * drawing_area_height 
        x1 = start_bar_x + i * (bar_width + bar_gap)
        y1 = base_y - bar_height
        x2 = x1 + bar_width
        y2 = base_y
        avg_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#666", width=1)
        avg_canvas.create_text(x1 + bar_width / 2, y1 - 10, text=f"{avg_val:.2f}", font=("Arial", 9, "bold"), fill="#000")
        avg_canvas.create_text(x1 + bar_width / 2, base_y + 10, text=channel, font=("Arial", 9, "bold"), fill=color)

def analyze(pil_image):
    rgb_image = pil_image.convert("RGB")
    r_channel, g_channel, b_channel = rgb_image.split()
    
    r_data = r_channel.getdata()
    g_data = g_channel.getdata()
    b_data = b_channel.getdata()
    # Расчет частоты
    r_counts = Counter(r_data)
    g_counts = Counter(g_data)
    b_counts = Counter(b_data)
    # подробная гистограмма частот
    all_counts = list(r_counts.values()) + list(g_counts.values()) + list(b_counts.values())
    max_count = max(all_counts) if all_counts else 1

    channels_data = [(r_counts, r_canvas, "#ff0000", "(R)"), (g_counts, g_canvas, "#00ff00", "(G)"), (b_counts, b_canvas, "#0000ff", "(B)"),]

    for counts, target_canvas, bar_color, channel_name in channels_data:
        draw_histogram(counts, target_canvas, max_count, bar_color, channel_name)
    
    # среднее значение
    img_size = pil_image.width * pil_image.height
    sum_r = sum(intensity * count for intensity, count in r_counts.items())
    sum_g = sum(intensity * count for intensity, count in g_counts.items())
    sum_b = sum(intensity * count for intensity, count in b_counts.items())
    
    avg_r = sum_r / img_size
    avg_g = sum_g / img_size
    avg_b = sum_b / img_size
    avg_data = [("R", avg_r, "#ff0000"), ("G", avg_g, "#00ff00"), ("B", avg_b, "#0000ff")]
    draw_average_histogram(avg_data)

# распределение значений яркости в определенном цветовом канале (R, G или B)
def draw_histogram(counts, target_canvas, max_count, bar_color, channel_name):
    target_canvas.delete("all")
    Y_AXIS_MARGIN = 30 
    X_AXIS_PADDING = 5 
    drawing_area_width = HISTOGRAM_FRAME_WIDTH - Y_AXIS_MARGIN - X_AXIS_PADDING
    drawing_area_height = HISTOGRAM_HEIGHT - 25
    base_y = HISTOGRAM_HEIGHT - 5
    target_canvas.create_text(HISTOGRAM_FRAME_WIDTH / 2, 10, text=f"{channel_name}", font=("Arial", 9, "bold"), fill=bar_color)

    # ось координат (Y)
    bar_width_total = drawing_area_width / 256 
    axis_x = Y_AXIS_MARGIN - 5
    target_canvas.create_line(axis_x, base_y, axis_x, base_y - drawing_area_height, fill="#555", width=1)
    
    max_count_text = f"{max_count}" if max_count < 10000 else f"{max_count/1000:.1f}K"
    target_canvas.create_text(axis_x - 3, base_y, text="0", anchor="e",font=("Arial", 7), fill="#555")
    target_canvas.create_text(axis_x - 3, base_y - drawing_area_height, text=max_count_text, anchor="e",font=("Arial", 7), fill="#555")
    target_canvas.create_text(axis_x - 15, base_y - drawing_area_height / 2, text="Частота", font=("Arial", 8, "bold"), angle=90, fill="#555")
    # рисование столбцов диаграммы
    for intensity in range(256):
        count = counts.get(intensity, 0)
        bar_height = (count / max_count) * drawing_area_height
        x1 = Y_AXIS_MARGIN + intensity * bar_width_total
        y1 = base_y - bar_height
        x2 = x1 + bar_width_total
        y2 = base_y
        target_canvas.create_rectangle(x1, y1, x2, y2, fill=bar_color, outline="")

    target_canvas.create_line(Y_AXIS_MARGIN, base_y, HISTOGRAM_FRAME_WIDTH - X_AXIS_PADDING, base_y, fill="#555", width=1)
    target_canvas.create_text(Y_AXIS_MARGIN, base_y + 10, text="0", font=("Arial", 7), anchor="n",fill="#555")
    target_canvas.create_text(HISTOGRAM_FRAME_WIDTH - X_AXIS_PADDING, base_y + 10, text="255", font=("Arial", 7), anchor="ne",fill="#555")
    target_canvas.create_text(Y_AXIS_MARGIN + drawing_area_width / 2, base_y + 10, text="Интенсивность", font=("Arial", 8, "bold"), fill="#555")

def display(image_path):
    global photo
    global current_image_path
    global current_pil_image
    pil_image = Image.open(image_path)
    resized_image = pil_image.resize((IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT), Image.Resampling.LANCZOS)
    photo = ImageTk.PhotoImage(resized_image)
    canvas.delete("all")
    center_x = IMAGE_DISPLAY_WIDTH / 2
    center_y = IMAGE_DISPLAY_HEIGHT / 2 
    canvas.create_image(center_x, center_y, anchor='center', image=photo)

    current_pil_image = pil_image
    current_image_path = image_path
    
    r_canvas.delete("all")
    g_canvas.delete("all")
    b_canvas.delete("all")
    avg_canvas.delete("all") 
    info_label.config(text=f"Нажмите для анализа RGB")

def display_image(): display("Lab 1/image_1.png")

def change_image():
    global current_image_path
    current_path = current_image_path if current_image_path else "Lab 1/image_1.png"
    if current_path == "Lab 1/image_1.png": display("Lab 1/image_2.png")
    else: display("Lab 1/image_1.png")

def on_image_click(event):
    if current_pil_image:
        info_label.config(text="Анализ RGB каналов завершен.")
        analyze(current_pil_image)
    else:
        info_label.config(text="Нет картинки для анализа!")
        avg_canvas.delete("all")

# Область кнопок (строка 0)
frame = tkinter.Frame(root)
frame.grid(row=0, column=0, columnspan=2, pady=10) 
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=1)
# Кнопки в рамке
but_display = tkinter.Button(frame, text="Показать картику ", command=display_image, font=("Arial", 10))
but_display.grid(row=0, column=0, padx=10, pady=10) 
but_change = tkinter.Button(frame, text="Сменить картику", command=change_image, font=("Arial", 10))
but_change.grid(row=0, column=1, padx=10, pady=10)
# Основная зона (строка 1)
canvas.grid(row=1, column=0, padx=10, pady=(5, 2)) 
histogram_frame.grid(row=1, column=1, padx=10, pady=5, sticky="n")
# Макет гистограммы
r_canvas.pack(side=tkinter.TOP, pady=2)
g_canvas.pack(side=tkinter.TOP, pady=2)
b_canvas.pack(side=tkinter.TOP, pady=2)
# Область уведомлений и средняя диаграмма (строки 2 и 3)
info_label.grid(row=2, column=0, columnspan=2)
avg_canvas.grid(row=3, column=0, columnspan=2, pady=(0, 5)) 

canvas.bind("<Button-1>", on_image_click)
root.mainloop()