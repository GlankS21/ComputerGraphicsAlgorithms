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