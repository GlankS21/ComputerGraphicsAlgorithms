import tkinter
from PIL import Image, ImageTk
from collections import Counter

CANVAS_WIDTH = 700
CANVAS_HEIGHT = 400
TARGET_WIDTH = 480 
TARGET_HEIGHT = 320
HISTOGRAM_HEIGHT = 100 
HISTOGRAM_BAR_WIDTH = 20 

root = tkinter.Tk()
root.title("Graphical user interface - Хоанг Ван Куан - Р3468")


canvas = tkinter.Canvas(root, height=CANVAS_HEIGHT, width=CANVAS_WIDTH)
histogram_canvas = tkinter.Canvas(root, height=HISTOGRAM_HEIGHT, width=CANVAS_WIDTH, bg="lightgray")
info_label = tkinter.Label(root, text="Нажмите на картинку для анализа цвета", font=("Arial", 12))

photo = None
current_image_path = None
current_pil_image = None 

def get_image_colors(pil_image, num_colors=10):
    pil_image = pil_image.convert("RGB")
    colors = pil_image.getdata()
    color_counts = Counter(colors)
    most_common_colors = color_counts.most_common(num_colors)
    return most_common_colors, len(color_counts)

def draw_histogram(colors_data, total_unique_colors):
    histogram_canvas.delete("all")
    
    if not colors_data:
        histogram_canvas.create_text(CANVAS_WIDTH / 2, HISTOGRAM_HEIGHT / 2, text="Нет данных для гистограммы.", fill="black")
        return

    max_count = max([count for color, count in colors_data])
    if max_count == 0: return

    x_offset = (CANVAS_WIDTH - len(colors_data) * (HISTOGRAM_BAR_WIDTH + 5)) / 2
    histogram_canvas.create_text(CANVAS_WIDTH / 2, 15, text=f"Всего уникальных цветов: {total_unique_colors}", font=("Arial", 10, "bold"))

    for i, (color_rgb, count) in enumerate(colors_data):
        hex_color = '#%02x%02x%02x' % color_rgb
        bar_height = (count / max_count) * (HISTOGRAM_HEIGHT - 40)
        
        x1 = x_offset + i * (HISTOGRAM_BAR_WIDTH + 5)
        y1 = HISTOGRAM_HEIGHT - bar_height - 5
        x2 = x1 + HISTOGRAM_BAR_WIDTH
        y2 = HISTOGRAM_HEIGHT - 5
        
        histogram_canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline="black")
        
        if bar_height > 20: 
            histogram_canvas.create_text(x1 + HISTOGRAM_BAR_WIDTH / 2, y1 - 10, text=str(count), font=("Arial", 8))
        
        histogram_canvas.create_rectangle(x1, y2 + 2, x2, y2 + 12, fill=hex_color, outline="gray")


def display(image_path):
    global photo
    global current_image_path
    global current_pil_image
    
    try:
        pil_image = Image.open(image_path)
        resized_image = pil_image.resize((TARGET_WIDTH, TARGET_HEIGHT), Image.Resampling.LANCZOS)
        current_pil_image = resized_image
        photo = ImageTk.PhotoImage(resized_image)
        canvas.delete("all")
        center_x = CANVAS_WIDTH / 2
        center_y = CANVAS_HEIGHT / 2
        canvas.create_image(center_x, center_y, anchor='center', image=photo)
        current_image_path = image_path
        histogram_canvas.delete("all")
        info_label.config(text="Нажмите на картинку для анализа цвета")
        
    except FileNotFoundError:
        canvas.delete("all")
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, text="Изображение не найдено!", fill="red")
        current_image_path = None
        current_pil_image = None
        histogram_canvas.delete("all")
        info_label.config(text="Изображение не найдено!")
    except Exception as e:
        canvas.delete("all")
        canvas.create_text(CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2, text=f"Ошибка обработки: {e}", fill="red")
        current_image_path = None
        current_pil_image = None
        histogram_canvas.delete("all")
        info_label.config(text=f"Ошибка обработки: {e}")

def display_image(): display("image_1.png")

def change_image():
    global current_image_path
    if current_image_path == "image_1.png": display("image_2.png")
    else: display("image_1.png")

def on_image_click(event):
    if current_pil_image:
        most_common_colors, total_unique_colors = get_image_colors(current_pil_image, num_colors=10)
        draw_histogram(most_common_colors, total_unique_colors)
        info_label.config(text=f"Анализ цвета: {len(most_common_colors)} самых частых цветов")
    else:
        info_label.config(text="Нет картинки для анализа!")
        histogram_canvas.delete("all")

frame = tkinter.Frame(root)
frame.grid(row=0, column=0, columnspan=2, pady=10) 

but_display = tkinter.Button(frame, text="Показать картику", command=display_image)
but_display.grid(row=0, column=0, padx=10, pady=10) 

but_change = tkinter.Button(frame, text="Сменить картику", command=change_image)
but_change.grid(row=0, column=1, padx=10, pady=10)

canvas.grid(row=1, column=0, columnspan=2) 
info_label.grid(row=2, column=0, columnspan=2, pady=5)
histogram_canvas.grid(row=3, column=0, columnspan=2, pady=5)

canvas.bind("<Button-1>", on_image_click)

root.mainloop()