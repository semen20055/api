import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from PIL import Image, ImageTk
from io import BytesIO


class GiftCardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор подарочных карт")
        self.root.geometry("800x700")

        input_frame = ttk.LabelFrame(root, text="Параметры карты", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(input_frame, text="Основной цвет:").grid(row=0, column=0, sticky=tk.W)
        self.primary_color = ttk.Entry(input_frame, width=10)
        self.primary_color.grid(row=0, column=1, sticky=tk.W)
        self.primary_color.insert(0, "#FF5733")

        ttk.Label(input_frame, text="Вторичный цвет:").grid(row=1, column=0, sticky=tk.W)
        self.secondary_color = ttk.Entry(input_frame, width=10)
        self.secondary_color.grid(row=1, column=1, sticky=tk.W)
        self.secondary_color.insert(0, "#33FF57")

        ttk.Label(input_frame, text="Цена в USD:").grid(row=2, column=0, sticky=tk.W)
        self.price_usd = ttk.Entry(input_frame, width=10)
        self.price_usd.grid(row=2, column=1, sticky=tk.W)
        self.price_usd.insert(0, "100")

        ttk.Label(input_frame, text="Цена в звездах:").grid(row=3, column=0, sticky=tk.W)
        self.price_star = ttk.Entry(input_frame, width=10)
        self.price_star.grid(row=3, column=1, sticky=tk.W)
        self.price_star.insert(0, "500")

        ttk.Label(input_frame, text="Цена в TON:").grid(row=4, column=0, sticky=tk.W)
        self.price_ton = ttk.Entry(input_frame, width=10)
        self.price_ton.grid(row=4, column=1, sticky=tk.W)
        self.price_ton.insert(0, "10")

        ttk.Label(input_frame, text="Название подарка:").grid(row=5, column=0, sticky=tk.W)
        self.gift_name = ttk.Entry(input_frame, width=30)
        self.gift_name.grid(row=5, column=1, sticky=tk.W)
        self.gift_name.insert(0, "Premium Box")

        ttk.Label(input_frame, text="URL изображения:").grid(row=6, column=0, sticky=tk.W)
        self.gift_image = ttk.Entry(input_frame, width=40)
        self.gift_image.grid(row=6, column=1, sticky=tk.W)
        self.gift_image.insert(0, "https://i.postimg.cc/jR6TNBW5/Plush-Pepe-Gift.png?dl=1")

        ttk.Label(input_frame, text="Количество:").grid(row=7, column=0, sticky=tk.W)
        self.gift_quantity = ttk.Entry(input_frame, width=10)
        self.gift_quantity.grid(row=7, column=1, sticky=tk.W)
        self.gift_quantity.insert(0, "1")

        ttk.Label(input_frame, text="Время:").grid(row=8, column=0, sticky=tk.W)
        self.time_display = ttk.Entry(input_frame, width=10)
        self.time_display.grid(row=8, column=1, sticky=tk.W)
        self.time_display.insert(0, "24h")

        generate_btn = ttk.Button(root, text="Сгенерировать карту", command=self.generate_card)
        generate_btn.pack(pady=10)

        self.image_frame = ttk.LabelFrame(root, text="Результат", padding=10)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.image_label = ttk.Label(self.image_frame)
        self.image_label.pack(expand=True)

    def generate_card(self):
        try:
            data = {
                "background_gradient": {
                    "primary_color": self.primary_color.get(),
                    "secondary_color": self.secondary_color.get()
                },
                "price": {
                    "usd": int(self.price_usd.get()),
                    "star": int(self.price_star.get()),
                    "ton": int(self.price_ton.get())
                },
                "gift": {
                    "name": self.gift_name.get(),
                    "image": self.gift_image.get(),
                    "quantity": int(self.gift_quantity.get())
                },
                "time_display": self.time_display.get()
            }

            url = "http://31.129.110.168:8001/generate_gift_card"

            response = requests.post(url, json=data)

            if response.status_code == 200:
                img_data = BytesIO(response.content)
                img = Image.open(img_data)

                img.thumbnail((500, 700))

                photo = ImageTk.PhotoImage(img)

                self.image_label.config(image=photo)
                self.image_label.image = photo
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.status_code}\n{response.text}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")



root = tk.Tk()
app = GiftCardApp(root)
root.mainloop()