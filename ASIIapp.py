import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import numpy as np

GSCALE_SIMPLE = "@%#*+=-:. "
GSCALE_EXTENDED = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~i!lI;:,\"^`'. "

def avg_brightness(tile):
    return np.array(tile).mean()

def map_brightness_to_char(brightness, gradient):
    idx = int(brightness * (len(gradient) - 1) / 255)
    return gradient[idx]

def image_to_ascii(image, cols=80, scale=0.43, gradient=GSCALE_SIMPLE, html=False):
    W, H = image.size
    tile_w = W / cols
    tile_h = tile_w / scale
    rows = int(H / tile_h)
    ascii_art = []
    image_gray = image.convert('L')

    for row in range(rows):
        y1 = int(row * tile_h)
        y2 = int((row + 1) * tile_h if row < rows - 1 else H)
        line = ""
        for col in range(cols):
            x1 = int(col * tile_w)
            x2 = int((col + 1) * tile_w if col < cols - 1 else W)

            tile_gray = image_gray.crop((x1, y1, x2, y2))
            brightness = avg_brightness(tile_gray)
            char = map_brightness_to_char(brightness, gradient)

            if html:
                tile_color = image.crop((x1, y1, x2, y2)).resize((1, 1))
                r, g, b = tile_color.getpixel((0, 0))
                line += f'<span style="color: rgb({r},{g},{b})">{char}</span>'
            else:
                line += char
        ascii_art.append(line)
    return ascii_art

def save_html(ascii_art, filepath):
    content = "<!DOCTYPE html><html><head><meta charset='UTF-8'><style>" \
              "body { background: black; color: white; font-family: monospace; white-space: pre; }" \
              "</style></head><body>" + "\n".join(ascii_art) + "</body></html>"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def save_txt(ascii_art, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(ascii_art))

class ASCIIApp:
    def __init__(self, master):
        self.master = master
        self.master.title("🎨 ASCII Art Generator")
        self.image = None
        self.gradient = tk.StringVar(value="simple")
        self.html_mode = tk.BooleanVar(value=False)
        self.width = tk.IntVar(value=80)
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.master, padx=10, pady=10)
        frame.pack()

        self.img_label = tk.Label(frame, text="Нет изображения", width=40, height=10, relief="sunken")
        self.img_label.grid(row=0, column=0, columnspan=3, pady=10)

        btn_load = tk.Button(frame, text="📂 Открыть изображение", command=self.load_image)
        btn_load.grid(row=1, column=0, columnspan=3)

        tk.Label(frame, text="Ширина (в символах):").grid(row=2, column=0)
        tk.Entry(frame, textvariable=self.width, width=6).grid(row=2, column=1)

        tk.Checkbutton(frame, text="HTML (цветной)", variable=self.html_mode).grid(row=2, column=2)

        tk.Label(frame, text="Градиент:").grid(row=3, column=0)
        ttk.Combobox(frame, textvariable=self.gradient, values=["simple", "extended"]).grid(row=3, column=1, columnspan=2)

        btn_generate = tk.Button(frame, text="🎨 Генерировать ASCII", command=self.generate_ascii)
        btn_generate.grid(row=4, column=0, columnspan=3, pady=10)

        self.output = tk.Text(self.master, height=25, width=100, font=("Courier", 8))
        self.output.pack(padx=10, pady=10)

        btn_save = tk.Button(self.master, text="💾 Сохранить", command=self.save_output)
        btn_save.pack(pady=5)

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Изображения", "*.jpg *.png *.jpeg *.webp")])
        if not file_path:
            return
        self.image = Image.open(file_path)
        img_thumb = self.image.copy()
        img_thumb.thumbnail((300, 200))
        tk_img = ImageTk.PhotoImage(img_thumb)
        self.img_label.configure(image=tk_img, text="")
        self.img_label.image = tk_img

    def generate_ascii(self):
        if self.image is None:
            messagebox.showwarning("Нет изображения", "Сначала загрузите изображение.")
            return

        gradient = GSCALE_SIMPLE if self.gradient.get() == "simple" else GSCALE_EXTENDED
        ascii_art = image_to_ascii(
            self.image,
            cols=self.width.get(),
            gradient=gradient,
            html=self.html_mode.get()
        )

        self.output.delete('1.0', tk.END)
        if self.html_mode.get():
            self.output.insert(tk.END, "[HTML] Предпросмотр невозможно отобразить здесь.\nСохраните как HTML.")
        else:
            self.output.insert(tk.END, "\n".join(ascii_art))

    def save_output(self):
        if self.image is None:
            messagebox.showwarning("Нет изображения", "Сначала загрузите изображение.")
            return

        gradient = GSCALE_SIMPLE if self.gradient.get() == "simple" else GSCALE_EXTENDED
        html = self.html_mode.get()

        if html:
            f = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML файл", "*.html")])
            if f:
                ascii_art = image_to_ascii(self.image, cols=self.width.get(), gradient=gradient, html=True)
                save_html(ascii_art, f)
                messagebox.showinfo("Готово", f"HTML сохранён: {f}")
        else:
            f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Текстовый файл", "*.txt")])
            if f:
                ascii_art = image_to_ascii(self.image, cols=self.width.get(), gradient=gradient, html=False)
                save_txt(ascii_art, f)
                messagebox.showinfo("Готово", f"Текст сохранён: {f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ASCIIApp(root)
    root.mainloop()
