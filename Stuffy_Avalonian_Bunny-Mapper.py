import os, sys, json, re, difflib, threading, time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import pyautogui, pytesseract, cv2, numpy as np
from PIL import Image, ImageTk, ImageDraw
import keyboard
import pystray
import copy

# ---------- Настройки по умолчанию ----------
DEFAULT_SETTINGS = {
    'overlay_duration': 35000,  # мс
    'language': 'ru',
    'hotkey': 'f8'
}
SETTINGS_FILE = 'settings.json'

# ---------- Определение базовой папки ----------
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

JSON_PATH = os.path.join(BASE_DIR, 'maps.json')
ICONS_DIR = os.path.join(BASE_DIR, 'icons')

# ---------- Путь к Tesseract ----------
tesseract_path = os.path.join(BASE_DIR, 'Tesseract', 'tesseract.exe')
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
else:
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# ---------- Языковые строки ----------
LANG = {
    'ru': {
        'title': 'Stuffy Avalonian Bunny Mapper - Настройки',
        'overlay_time': 'Время показа окна (мс):',
        'language': 'Язык интерфейса:',
        'current_hotkey': 'Текущая комбинация:',
        'change_btn': 'Изменить',
        'listen_hotkey': 'Нажмите новую комбинацию клавиш...',
        'hotkey_set': 'Новая комбинация: {}',
        'hotkey_error': 'Не удалось записать комбинацию.',
        'howto': '\nПосле нажатия {} выделите курсором\nтолько название портала.\n\nДля выхода из режима скриншота - Esc',
        'tray_show': 'Показать',
        'tray_exit': 'Выход',
        'overlay_chests': 'Сундуки',
        'overlay_dungeons': 'Данжены',
        'overlay_resources': 'Ресурсы',
        'overlay_solo': 'Соло',
        'overlay_group': 'Группа',
        'scan_start': 'Захватываем экран...',
        'no_region': 'Область не выбрана.',
        'ocr_fail': 'Не удалось распознать текст.',
        'map_found': 'Найдена карта: {}',
        'map_not_found': 'Подходящая карта не найдена.',
        'invalid_duration': 'Введите целое число (1000 – 120000 мс).',
        'convert_btn': 'Заменить все данжи на групповые',
        'editor_btn': 'Редактор карт',
        'editor_title': 'Редактор карт',
        'editor_select': 'Выберите карту:',
        'add_object': 'Добавить объект',
        'edit_object_title': 'Редактировать объект',
        'confirm_delete_title': 'Подтверждение',
        'confirm_delete': 'Удалить этот объект?',
        'obj_type': 'Тип:',
        'size': 'Размер:',
        'count': 'Кол-во:',
        'save': 'Сохранить',
        'add_object_title': 'Добавить объект',
        'obj_category': 'Категория:',
        'add': 'Добавить',
        'err_save': 'Ошибка сохранения',
        'err_invalid_count': 'Количество должно быть целым положительным числом',
        'warn_size_change': 'Предупреждение',
        'warn_not_multiple4': 'При смене large на small количество должно быть кратно 4.',
        'search_placeholder': 'Поиск карты...',
        'help_btn': 'Справка',
        'help_title': 'О программе',
        'help_text': (
            "🔹 Чтобы просканировать портал, нажмите заданную комбинацию клавиш,\n"
            "   затем выделите мышью название карты на затемнённом экране.\n"
            "🔹 Для выхода из режима выделения нажмите Esc.\n\n"
            "🔹 В редакторе карт можно изменять состав объектов,\n"
            "   а также переключать тип подземелий и размер сундуков/ресурсов.\n\n"
            "🔹 Информация о типах объектов может быть неточной,\n"
            "   но количество объектов верно в 99% случаев.\n\n"
            "🔹 Создано гильдией Stuffy Bunny.\n"
            "   Наш Discord:"
        ),
    },
    'en': {
        'title': 'Stuffy Avalonian Bunny Mapper – Settings',
        'overlay_time': 'Overlay duration (ms):',
        'language': 'Interface language:',
        'current_hotkey': 'Current hotkey:',
        'change_btn': 'Change',
        'listen_hotkey': 'Press a new key combination...',
        'hotkey_set': 'New hotkey: {}',
        'hotkey_error': 'Failed to capture combination.',
        'howto': '\nAfter pressing {}, select the cursor\nonly the portal name.\n\nTo exit the screenshot mode, press Esc',
        'tray_show': 'Show',
        'tray_exit': 'Exit',
        'overlay_chests': 'Chests',
        'overlay_dungeons': 'Dungeons',
        'overlay_resources': 'Resources',
        'overlay_solo': 'Solo',
        'overlay_group': 'Group',
        'scan_start': 'Capturing screen...',
        'no_region': 'No region selected.',
        'ocr_fail': 'Failed to recognize text.',
        'map_found': 'Map found: {}',
        'map_not_found': 'No matching map found.',
        'invalid_duration': 'Enter an integer (1000–120000 ms).',
        'convert_btn': 'Convert all dungeons to group',
        'editor_btn': 'Map Editor',
        'editor_title': 'Map Editor',
        'editor_select': 'Select a map:',
        'add_object': 'Add object',
        'edit_object_title': 'Edit object',
        'confirm_delete_title': 'Confirm',
        'confirm_delete': 'Delete this object?',
        'obj_type': 'Type:',
        'size': 'Size:',
        'count': 'Count:',
        'save': 'Save',
        'add_object_title': 'Add object',
        'obj_category': 'Category:',
        'add': 'Add',
        'err_save': 'Save error',
        'err_invalid_count': 'Count must be a positive integer',
        'warn_size_change': 'Warning',
        'warn_not_multiple4': 'When changing large to small, count must be a multiple of 4.',
        'search_placeholder': 'Search map...',
        'help_btn': 'Help',
        'help_title': 'About',
        'help_text': (
            "🔹 To scan a portal, press the assigned hotkey,\n"
            "   then select the map name on the darkened screen.\n"
            "🔹 Press Esc to cancel the selection.\n\n"
            "🔹 In the Map Editor, you can modify objects,\n"
            "   toggle dungeon types, and change chest/resource sizes.\n\n"
            "🔹 Object types may be inaccurate,\n"
            "   but object counts are 99% correct.\n\n"
            "🔹 Created by Stuffy Bunny guild.\n"
            "   Discord:"
        ),
    }
}

import webbrowser

def show_help():
    help_win = tk.Toplevel(root)
    help_win.title(LANG[lang]['help_title'])
    help_win.geometry("570x400")
    help_win.resizable(True, True)

    text_frame = tk.Frame(help_win, padx=15, pady=15)
    text_frame.pack(fill='both', expand=True)

    tk.Label(text_frame, text=LANG[lang]['help_text'], justify='left',
             font=('Segoe UI', 9)).pack(anchor='w')

    # Ссылка кликабельная
    link = tk.Label(text_frame, text="https://discord.gg/D6C73tZcMn",
                    fg="blue", cursor="hand2", font=('Segoe UI', 9, 'underline'))
    link.pack(anchor='w', pady=(10, 0))
    link.bind("<Button-1>", lambda e: webbrowser.open_new("https://discord.gg/D6C73tZcMn"))

    tk.Button(help_win, text="OK", command=help_win.destroy, width=10).pack(pady=10)

# ---------- Загрузка/сохранение настроек ----------
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2)

settings = load_settings()
current_hotkey = settings['hotkey']
overlay_duration = settings['overlay_duration']
lang = settings['language']

root = None
last_scanned_map = None   # имя последней успешно найденной карты
overlay_win = None
hide_timer = None
tray_icon = None
listener_active = True   # флаг работы слушателя

# ---------- OCR и оверлей ----------
def clean_ocr_text(text):
    cleaned = re.sub(r'[^a-zA-Z-]', '', text)
    cleaned = re.sub(r'-+', '-', cleaned).strip('-')
    return cleaned

def find_best_map_name(ocr_text, threshold=0.7):
    if not ocr_text:
        return None
    best_score = 0
    best_name = None
    for name in map_names:
        score = difflib.SequenceMatcher(None, ocr_text.lower(), name.lower()).ratio()
        if score > best_score:
            best_score = score
            best_name = name
    return best_name if best_score >= threshold else None

def get_icon(category, obj_type):
    mapping = {
        ('chest', 'GREEN'): 'chest_green.png',
        ('chest', 'BLUE'): 'chest_blue.png',
        ('chest', 'GOLD'): 'chest_gold.png',
        ('dungeon', 'DUNGEON_SOLO'): 'dungeon_solo.png',
        ('dungeon', 'DUNGEON_GROUP'): 'dungeon_group.png',
        ('resource', 'STONE'): 'resource_stone.png',
        ('resource', 'WOOD'): 'resource_wood.png',
        ('resource', 'HIDE'): 'resource_hide.png',
        ('resource', 'FIBER'): 'resource_fiber.png',
        ('resource', 'ORE'): 'resource_ore.png',
    }
    filename = mapping.get((category, obj_type))
    if filename:
        path = os.path.join(ICONS_DIR, filename)
        if os.path.exists(path):
            return path
    return None

def create_overlay(map_info):
    global overlay_win, hide_timer
    if hide_timer is not None:
        root.after_cancel(hide_timer)
        hide_timer = None

    # Создание окна (если ещё не создано)
    if overlay_win is None or not overlay_win.winfo_exists():
        overlay_win = tk.Toplevel(root)
        overlay_win.overrideredirect(True)
        overlay_win.attributes('-topmost', True)
        overlay_win.attributes('-alpha', 0.85)
        overlay_win.configure(bg='#1e1e1e')

        main_frame = tk.Frame(overlay_win, bg='#1e1e1e')
        main_frame.pack(fill='both', expand=True, padx=8, pady=8)

        close_btn = tk.Label(overlay_win, text='✕', bg='#1e1e1e', fg='#888888',
                             font=('Segoe UI', 12, 'bold'), padx=6, pady=0, cursor='hand2')
        close_btn.place(relx=1.0, rely=0.0, x=-6, y=5, anchor='ne')
        close_btn.bind('<Button-1>', lambda e: hide_overlay())

        def on_enter(e): e.widget.configure(fg='#ff5555')
        def on_leave(e): e.widget.configure(fg='#888888')
        close_btn.bind('<Enter>', on_enter)
        close_btn.bind('<Leave>', on_leave)

        icons_frame = tk.Frame(main_frame, bg='#1e1e1e')
        icons_frame.pack(fill='both', expand=True)
        overlay_win.icons_frame = icons_frame
    else:
        # Очистка старых виджетов
        for child in overlay_win.icons_frame.winfo_children():
            child.destroy()

    # Заголовок: название + тир, для T8 золотой цвет
    header = f"{map_info['name']}  [T{map_info['tier']}]"
    tier = map_info.get('tier', 0)
    header_color = '#FFD700' if tier == 8 else '#ffffff'
    header_lbl = tk.Label(overlay_win.icons_frame, text=header, bg='#1e1e1e',
                          fg=header_color, font=('Segoe UI', 12, 'bold'))
    header_lbl.grid(row=0, column=0, columnspan=10, sticky='w', pady=(0, 6))

    # Компактные настройки
    icon_size = 32
    main_font = ('Segoe UI', 10)
    cat_font = ('Segoe UI', 8, 'italic')
    row_pad = 2
    col_pad_icon = (4, 4)
    col_pad_text = (4, 0)

    # Фиксируем ширину колонок, чтобы иконки не растягивались
    overlay_win.icons_frame.grid_columnconfigure(0, weight=0)
    overlay_win.icons_frame.grid_columnconfigure(1, weight=1)

    row = 1

    # --- Сундуки ---
    if map_info.get('chests'):
        tk.Label(overlay_win.icons_frame, text=LANG[lang]['overlay_chests'], bg='#1e1e1e',
                 fg='#aaaaaa', font=cat_font).grid(row=row, column=0, sticky='w', columnspan=10)
        row += 1
        for chest in map_info['chests']:
            icon_path = get_icon('chest', chest['type'])
            if icon_path:
                img = Image.open(icon_path).resize((icon_size, icon_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(overlay_win.icons_frame, image=photo, bg='#1e1e1e',
                               width=icon_size, height=icon_size)
                lbl.image = photo
                lbl.grid(row=row, column=0, padx=col_pad_icon, pady=row_pad, sticky='w')
            if chest.get('size'):
                size_text = chest['size']
                # Для зелёных large добавляем пояснение (4)
                if chest['type'] == 'GREEN' and chest['size'] == 'large':
                    size_text = 'large (4)'
                desc = f"{size_text} x{chest['count']}"
            else:
                desc = f"x{chest['count']}"
            tk.Label(overlay_win.icons_frame, text=desc, bg='#1e1e1e', fg='#ffffff',
                     font=main_font).grid(row=row, column=1, sticky='w', padx=col_pad_text, pady=row_pad)
            row += 1

    # --- Подземелья ---
    if map_info.get('dungeons'):
        tk.Label(overlay_win.icons_frame, text=LANG[lang]['overlay_dungeons'], bg='#1e1e1e',
                 fg='#aaaaaa', font=cat_font).grid(row=row, column=0, sticky='w', columnspan=10)
        row += 1
        for dung in map_info['dungeons']:
            icon_path = get_icon('dungeon', dung['type'])
            if icon_path:
                img = Image.open(icon_path).resize((icon_size, icon_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(overlay_win.icons_frame, image=photo, bg='#1e1e1e',
                               width=icon_size, height=icon_size)
                lbl.image = photo
                lbl.grid(row=row, column=0, padx=col_pad_icon, pady=row_pad, sticky='w')
            if dung['type'] == 'DUNGEON_SOLO':
                dung_name = LANG[lang]['overlay_solo']
            elif dung['type'] == 'DUNGEON_GROUP':
                dung_name = LANG[lang]['overlay_group']
            else:
                dung_name = dung['type']
            desc = f"{dung_name} x{dung['count']}"
            tk.Label(overlay_win.icons_frame, text=desc, bg='#1e1e1e', fg='#ffffff',
                     font=main_font).grid(row=row, column=1, sticky='w', padx=col_pad_text, pady=row_pad)
            row += 1

    # --- Ресурсы ---
    if map_info.get('resources'):
        tk.Label(overlay_win.icons_frame, text=LANG[lang]['overlay_resources'], bg='#1e1e1e',
                 fg='#aaaaaa', font=cat_font).grid(row=row, column=0, sticky='w', columnspan=10)
        row += 1
        for res in map_info['resources']:
            icon_path = get_icon('resource', res['type'])
            if icon_path:
                img = Image.open(icon_path).resize((icon_size, icon_size), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(overlay_win.icons_frame, image=photo, bg='#1e1e1e',
                               width=icon_size, height=icon_size)
                lbl.image = photo
                lbl.grid(row=row, column=0, padx=col_pad_icon, pady=row_pad, sticky='w')
            desc = f"{res['size']} x{res['count']}" if res.get('size') else f"x{res['count']}"
            tk.Label(overlay_win.icons_frame, text=desc, bg='#1e1e1e', fg='#ffffff',
                     font=main_font).grid(row=row, column=1, sticky='w', padx=col_pad_text, pady=row_pad)
            row += 1

    # --- Обеспечиваем достаточную ширину для заголовка ---
    overlay_win.update_idletasks()
    req_width = header_lbl.winfo_reqwidth() + 50
    overlay_win.minsize(width=max(req_width, 220), height=1)

    # Гильдейская плашка (отдельная строка в сетке, выровнена вправо)
    guild_frame = tk.Frame(overlay_win.icons_frame, bg='#1e1e1e')
    guild_frame.grid(row=row, column=0, columnspan=10, sticky='e', pady=(6, 0))

    # Текстовая подпись
    tk.Label(guild_frame, text="by Stuffy Bunny Guild", bg='#1e1e1e', fg='#888888',
             font=('Segoe UI', 7)).pack(side='left', padx=(0, 4))

    # Иконка
    guild_icon_path = os.path.join(ICONS_DIR, 'stuffy_bunny.png')
    if os.path.exists(guild_icon_path):
        try:
            guild_img = Image.open(guild_icon_path).resize((32, 32), Image.LANCZOS)
            guild_photo = ImageTk.PhotoImage(guild_img)
            icon_lbl = tk.Label(guild_frame, image=guild_photo, bg='#1e1e1e')
            icon_lbl.image = guild_photo
            icon_lbl.pack(side='left')
        except Exception:
            pass

    # Позиция – левый нижний угол
    win_height = overlay_win.winfo_height()
    screen_height = overlay_win.winfo_screenheight()
    x = 10
    y = screen_height - win_height - 30
    overlay_win.geometry(f'+{x}+{y}')
    overlay_win.deiconify()

    # Таймер автоскрытия
    hide_timer = overlay_win.after(overlay_duration, hide_overlay)

def hide_overlay():
    global overlay_win, hide_timer
    if overlay_win and overlay_win.winfo_exists():
        try:
            overlay_win.withdraw()
        except tk.TclError:
            pass
    if hide_timer is not None:
        try:
            root.after_cancel(hide_timer)
        except (ValueError, tk.TclError):
            pass
        hide_timer = None

# ---------- Интерактивное выделение ----------
class ScreenSelector:
    def __init__(self, root, screenshot):
        self.root = root
        self.screenshot = screenshot
        self.top = tk.Toplevel(root)
        self.top.attributes('-fullscreen', True)
        self.top.attributes('-topmost', True)
        self.top.configure(bg='black')
        self.canvas = tk.Canvas(self.top, highlightthickness=0)
        self.canvas.pack(fill='both', expand=True)
        self.tk_img = ImageTk.PhotoImage(screenshot)
        self.canvas.create_image(0, 0, image=self.tk_img, anchor='nw')
        self.start_x = self.start_y = None
        self.rect = None
        self.selected_region = None
        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)
        self.top.bind('<Escape>', lambda e: self.cancel())
        self.top.focus_force()
        self.top.wait_window()

    def cancel(self):
        self.selected_region = None
        try:
            self.top.destroy()
        except tk.TclError:
            pass

    def on_press(self, event):
        self.start_x, self.start_y = event.x, event.y
        if self.rect: self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=2)

    def on_drag(self, event):
        if self.rect: self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        end_x, end_y = event.x, event.y
        if self.start_x is None or self.start_y is None:
            self.top.destroy(); return
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        if x2 - x1 < 5 or y2 - y1 < 5:
            self.top.destroy(); return
        self.selected_region = (x1, y1, x2 - x1, y2 - y1)
        self.top.destroy()

def interactive_ocr():
    print(LANG[lang]['scan_start'])
    full_screenshot = pyautogui.screenshot().convert('RGB')
    from PIL import ImageEnhance
    enhancer = ImageEnhance.Brightness(full_screenshot)
    darkened = enhancer.enhance(0.6)

    selector = ScreenSelector(root, darkened)
    region = selector.selected_region
    if not region:
        print(LANG[lang]['no_region'])
        return None
    left, top, width, height = region
    cropped = full_screenshot.crop((left, top, left + width, top + height))
    img = cv2.cvtColor(np.array(cropped), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.bitwise_not(gray)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    thresh = cv2.resize(thresh, None, fx=20, fy=20, interpolation=cv2.INTER_CUBIC)
    config = r'--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-'
    text = pytesseract.image_to_string(thresh, lang='eng', config=config)
    return clean_ocr_text(text)

# ---------- Загрузка карт ----------
try:
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        maps_data = json.load(f)['maps']
    map_names = [m['name'] for m in maps_data]
    map_dict = {m['name']: m for m in maps_data}
except Exception as e:
    messagebox.showerror("Ошибка", f"Не удалось загрузить maps.json:\n{e}")
    sys.exit(1)

# ---------- Конвертация данжей ----------
def convert_dungeons_to_group():
    """Заменяет все DUNGEON_SOLO на DUNGEON_GROUP и сохраняет в maps.json."""
    if not messagebox.askyesno("Подтверждение",
                               "Заменить ВСЕ подземелья на групповые?\n"
                               "Изменения сохранятся в maps.json."):
        return
    try:
        with open(JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
        changed = 0
        for m in data['maps']:
            for d in m.get('dungeons', []):
                if d['type'] == 'DUNGEON_SOLO':
                    d['type'] = 'DUNGEON_GROUP'
                    changed += 1
        with open(JSON_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Обновляем глобальные переменные
        global maps_data, map_names, map_dict
        maps_data = data['maps']
        map_names = [m['name'] for m in maps_data]
        map_dict = {m['name']: m for m in maps_data}
        messagebox.showinfo("Готово", f"Обновлено подземелий: {changed}")
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))

# ---------- Редактор карт ----------
def open_map_editor():
    editor = tk.Toplevel(root)
    editor.title(LANG[lang]['editor_title'])
    editor.geometry("600x600")
    editor.resizable(True, True)

    # ---------- Поле поиска с автодополнением (всплывающее окно) ----------
    tk.Label(editor, text=LANG[lang]['editor_select']).pack(pady=(10,0))

    search_var = tk.StringVar()
    search_entry = tk.Entry(editor, textvariable=search_var, width=35)
    search_entry.pack(pady=(0,5))



    popup = None
    listbox = None

    # Основной фрейм для отображения информации о карте (создаём заранее)
    info_frame = tk.Frame(editor)
    info_frame.pack(fill='both', expand=True, pady=10)

    # ---------- Функции сохранения и отображения ----------
    def save_map_data(map_name, updated_map):
        try:
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for m in data['maps']:
                if m['name'] == map_name:
                    m.clear()
                    m.update(updated_map)
                    break
            with open(JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            global maps_data, map_dict
            maps_data = data['maps']
            map_dict[map_name] = updated_map
            show_map_info()
        except Exception as e:
            messagebox.showerror(LANG[lang]['err_save'], str(e))

    def show_map_info(event=None):
        for w in info_frame.winfo_children():
            w.destroy()
        name = search_var.get().strip()
        if not name or name not in map_dict:
            return
        map_info = map_dict[name]
        header = f"{name} [T{map_info['tier']}]"
        tk.Label(info_frame, text=header, font=('Arial', 11, 'bold')).pack(anchor='w')

        # Сундуки
        if map_info.get('chests'):
            tk.Label(info_frame, text=LANG[lang]['overlay_chests'], font=('Arial', 9, 'italic')).pack(anchor='w', pady=(5,0))
            for idx, chest in enumerate(map_info['chests']):
                row = tk.Frame(info_frame)
                row.pack(anchor='w', fill='x', padx=20, pady=1)
                tk.Label(row, text=f"{chest['type']} {chest['size']} x{chest['count']}").pack(side='left')
                tk.Button(row, text='✎', font=('Arial', 8), command=lambda i=idx: edit_object(name, 'chests', i)).pack(side='right', padx=2)
                tk.Button(row, text='✕', fg='red', font=('Arial', 8), command=lambda i=idx: delete_object(name, 'chests', i)).pack(side='right')

        # Ресурсы
        if map_info.get('resources'):
            tk.Label(info_frame, text=LANG[lang]['overlay_resources'], font=('Arial', 9, 'italic')).pack(anchor='w', pady=(5,0))
            for idx, res in enumerate(map_info['resources']):
                row = tk.Frame(info_frame)
                row.pack(anchor='w', fill='x', padx=20, pady=1)
                tk.Label(row, text=f"{res['type']} {res['size']} x{res['count']}").pack(side='left')
                tk.Button(row, text='✎', font=('Arial', 8), command=lambda i=idx: edit_object(name, 'resources', i)).pack(side='right', padx=2)
                tk.Button(row, text='✕', fg='red', font=('Arial', 8), command=lambda i=idx: delete_object(name, 'resources', i)).pack(side='right')

        # Подземелья
        if map_info.get('dungeons'):
            tk.Label(info_frame, text=LANG[lang]['overlay_dungeons'], font=('Arial', 9, 'italic')).pack(anchor='w', pady=(5,0))
            for idx, dung in enumerate(map_info['dungeons']):
                row = tk.Frame(info_frame)
                row.pack(anchor='w', fill='x', padx=20, pady=1)
                dung_type = dung['type']
                display = LANG[lang]['overlay_solo'] if dung_type == 'DUNGEON_SOLO' else LANG[lang]['overlay_group']
                tk.Button(row, text=f"{display} x{dung['count']}", command=lambda i=idx: toggle_dungeon_type(name, i)).pack(side='left')
                tk.Button(row, text='✎', font=('Arial', 8), command=lambda i=idx: edit_object(name, 'dungeons', i)).pack(side='right', padx=2)
                tk.Button(row, text='✕', fg='red', font=('Arial', 8), command=lambda i=idx: delete_object(name, 'dungeons', i)).pack(side='right')

        tk.Button(info_frame, text=LANG[lang]['add_object'], command=lambda: add_object_dialog(name)).pack(pady=10)

    # ---------- Удаление ----------
    def delete_object(map_name, category, index):
        map_info = map_dict[map_name]
        if not messagebox.askyesno(LANG[lang]['confirm_delete_title'], LANG[lang]['confirm_delete']):
            return
        del map_info[category][index]
        if not map_info[category]:
            del map_info[category]
        save_map_data(map_name, map_info)

    # ---------- Быстрое переключение типа данжа ----------
    def toggle_dungeon_type(map_name, dung_index):
        map_info = map_dict[map_name]
        dung = map_info['dungeons'][dung_index]
        dung['type'] = 'DUNGEON_GROUP' if dung['type'] == 'DUNGEON_SOLO' else 'DUNGEON_SOLO'
        save_map_data(map_name, map_info)

    # ---------- Окно редактирования объекта ----------
    def edit_object(map_name, category, index):
        map_info = map_dict[map_name]
        obj = map_info[category][index]
        dialog = tk.Toplevel(editor)
        dialog.title(LANG[lang]['edit_object_title'])
        dialog.geometry("300x250")
        dialog.resizable(False, False)

        tk.Label(dialog, text=LANG[lang]['obj_type']).pack(anchor='w', padx=10, pady=(5,0))
        type_var = tk.StringVar(value=obj['type'])
        if category == 'chests':
            type_values = ['GREEN', 'BLUE', 'GOLD']
        elif category == 'dungeons':
            type_values = ['DUNGEON_SOLO', 'DUNGEON_GROUP']
        else:
            type_values = ['STONE', 'WOOD', 'HIDE', 'FIBER', 'ORE']
        type_combo = ttk.Combobox(dialog, textvariable=type_var, values=type_values, state='readonly')
        type_combo.pack(padx=10)

        size_var = tk.StringVar(value=obj.get('size', ''))
        if category != 'dungeons':
            tk.Label(dialog, text=LANG[lang]['size']).pack(anchor='w', padx=10, pady=(5,0))
            size_combo = ttk.Combobox(dialog, textvariable=size_var, values=['small', 'large'], state='readonly')
            size_combo.pack(padx=10)

        tk.Label(dialog, text=LANG[lang]['count']).pack(anchor='w', padx=10, pady=(5,0))
        count_var = tk.StringVar(value=str(obj['count']))
        count_entry = tk.Entry(dialog, textvariable=count_var, width=10)
        count_entry.pack(padx=10)

        def on_size_change(*args):
            if category == 'dungeons':
                return
            new_size = size_var.get()
            old_size = obj.get('size', '')
            # Правило 4x действует только для зелёных сундуков
            if category == 'chests' and type_var.get() == 'GREEN':
                try:
                    cur_count = int(count_var.get())
                except ValueError:
                    return
                if old_size == new_size:
                    return
                if old_size == 'small' and new_size == 'large':
                    count_var.set(str(cur_count * 4))
                elif old_size == 'large' and new_size == 'small':
                    if cur_count % 4 != 0:
                        messagebox.showwarning(LANG[lang]['warn_size_change'], LANG[lang]['warn_not_multiple4'])
                        size_var.set(old_size)  # откат размера
                        return
                    count_var.set(str(cur_count // 4))
                obj['size'] = new_size
            else:
                # Для всех остальных объектов (BLUE, GOLD, ресурсы) просто меняем размер
                obj['size'] = new_size
        if category != 'dungeons':
            size_var.trace('w', on_size_change)

        def save_edit():
            obj['type'] = type_var.get()
            if category != 'dungeons':
                obj['size'] = size_var.get()
            try:
                obj['count'] = int(count_var.get())
            except ValueError:
                messagebox.showerror(LANG[lang]['err_invalid_count'])
                return
            if obj['count'] <= 0:
                messagebox.showerror(LANG[lang]['err_invalid_count'])
                return
            save_map_data(map_name, map_info)
            dialog.destroy()

        tk.Button(dialog, text=LANG[lang]['save'], command=save_edit).pack(pady=10)

    # ---------- Окно добавления нового объекта ----------
    def add_object_dialog(map_name):
        dialog = tk.Toplevel(editor)
        dialog.title(LANG[lang]['add_object_title'])
        dialog.geometry("280x300")
        dialog.resizable(False, False)

        tk.Label(dialog, text=LANG[lang]['obj_category']).pack(anchor='w', padx=10, pady=(5,0))
        obj_category = tk.StringVar(value='chest')
        cat_combo = ttk.Combobox(dialog, textvariable=obj_category, values=['chest', 'dungeon', 'resource'],
                                 state='readonly', width=20)
        cat_combo.pack(padx=10)

        type_frame = tk.Frame(dialog)
        type_frame.pack(pady=5, padx=10, fill='x')
        tk.Label(type_frame, text=LANG[lang]['obj_type']).pack(side='left')
        subtype_var = tk.StringVar()
        subtype_combo = ttk.Combobox(type_frame, textvariable=subtype_var, state='readonly', width=15)
        subtype_combo.pack(side='left', padx=5)

        size_frame = tk.Frame(dialog)
        size_frame.pack(pady=5, padx=10, fill='x')
        tk.Label(size_frame, text=LANG[lang]['size']).pack(side='left')
        size_var = tk.StringVar(value='small')
        size_combo = ttk.Combobox(size_frame, textvariable=size_var, values=['small', 'large'],
                                  state='readonly', width=10)
        size_combo.pack(side='left', padx=5)

        count_frame = tk.Frame(dialog)
        count_frame.pack(pady=5, padx=10, fill='x')
        tk.Label(count_frame, text=LANG[lang]['count']).pack(side='left')
        count_var = tk.StringVar(value='1')
        count_entry = tk.Entry(count_frame, textvariable=count_var, width=5)
        count_entry.pack(side='left', padx=5)

        def update_subtypes(*args):
            cat = obj_category.get()
            if cat == 'chest':
                subtypes = ['GREEN', 'BLUE', 'GOLD']
            elif cat == 'dungeon':
                subtypes = ['DUNGEON_SOLO', 'DUNGEON_GROUP']
            else:
                subtypes = ['STONE', 'WOOD', 'HIDE', 'FIBER', 'ORE']
            subtype_combo['values'] = subtypes
            subtype_var.set(subtypes[0])
            if cat == 'dungeon':
                size_frame.pack_forget()
            else:
                size_frame.pack(after=type_frame, pady=5, padx=10, fill='x')
        obj_category.trace('w', update_subtypes)
        update_subtypes()

        def do_add():
            cat = obj_category.get()
            sub = subtype_var.get()
            size = size_var.get() if cat != 'dungeon' else ''
            try:
                cnt = int(count_var.get())
            except ValueError:
                messagebox.showerror(LANG[lang]['err_invalid_count'])
                return
            if cnt <= 0:
                messagebox.showerror(LANG[lang]['err_invalid_count'])
                return

            map_info = map_dict[map_name]
            new_obj = {'type': sub, 'count': cnt}
            if cat != 'dungeon':
                new_obj['size'] = size

            if cat == 'chest':
                if 'chests' not in map_info:
                    map_info['chests'] = []
                map_info['chests'].append(new_obj)
            elif cat == 'dungeon':
                if 'dungeons' not in map_info:
                    map_info['dungeons'] = []
                map_info['dungeons'].append(new_obj)
            else:
                if 'resources' not in map_info:
                    map_info['resources'] = []
                map_info['resources'].append(new_obj)

            save_map_data(map_name, map_info)
            dialog.destroy()

        tk.Button(dialog, text=LANG[lang]['add'], command=do_add).pack(pady=10)

    # ---------- ВСПЛЫВАЮЩИЙ СПИСОК (создаётся после определения всех функций) ----------
    def create_popup():
        nonlocal popup, listbox
        if popup is not None:
            return
        popup = tk.Toplevel(editor)
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.withdraw()
        frame = tk.Frame(popup, bg='white', highlightthickness=1, highlightbackground='gray')
        frame.pack(fill='both', expand=True)
        scrollbar = tk.Scrollbar(frame, orient='vertical')
        listbox = tk.Listbox(frame, height=8, bg='white', fg='black',
                             selectmode=tk.SINGLE, exportselection=False,
                             yscrollcommand=scrollbar.set)
        listbox.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        scrollbar.config(command=listbox.yview)
        listbox.bind('<Button-1>', lambda e: on_listbox_click())
        listbox.bind('<Return>', lambda e: on_listbox_select())

    create_popup()

    def on_listbox_click():
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection[0])
            search_var.set(name)
            popup.withdraw()
            show_map_info()

    def on_listbox_select():
        selection = listbox.curselection()
        if selection:
            name = listbox.get(selection[0])
            search_var.set(name)
            popup.withdraw()
            show_map_info()

    def on_search_change(*args):
        nonlocal popup, listbox
        query = search_var.get().strip().lower()
        if not query:
            popup.withdraw()
            return
        matches = [name for name in map_names if query in name.lower()]
        if not matches:
            popup.withdraw()
            return
        listbox.delete(0, tk.END)
        for m in matches:
            listbox.insert(tk.END, m)
        x = search_entry.winfo_rootx()
        y = search_entry.winfo_rooty() + search_entry.winfo_height()
        w = search_entry.winfo_width()
        popup.geometry(f'{w}x200+{x}+{y}')
        popup.deiconify()
        listbox.selection_clear(0, tk.END)

    # Автоподстановка последней отсканированной карты
    if last_scanned_map and last_scanned_map in map_dict:
        search_var.set(last_scanned_map)
        show_map_info()

    search_var.trace('w', on_search_change)

    def on_key_press(event):
        nonlocal popup, listbox
        if event.keysym == 'Escape':
            popup.withdraw()
            editor.focus_set()
            return
        if not popup.winfo_viewable():
            return
        cur = listbox.curselection()
        if event.keysym == 'Up':
            if cur:
                idx = max(cur[0]-1, 0)
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(idx)
                listbox.see(idx)
            return "break"
        elif event.keysym == 'Down':
            if not cur:
                idx = 0
            else:
                idx = min(cur[0]+1, listbox.size()-1)
            listbox.selection_clear(0, tk.END)
            listbox.selection_set(idx)
            listbox.see(idx)
            return "break"
        elif event.keysym == 'Return':
            if cur:
                name = listbox.get(cur[0])
                search_var.set(name)
                popup.withdraw()
                show_map_info()
            return "break"

    search_entry.bind('<KeyPress>', on_key_press)

    def hide_popup(event=None):
        nonlocal popup
        editor.after(150, lambda: popup.withdraw() if popup and editor.focus_get() not in (search_entry, listbox) else None)

    search_entry.bind('<FocusOut>', hide_popup)

# ---------- Основная логика ----------
def process_scan():
    ocr_result = interactive_ocr()
    if not ocr_result:
        return
    print(f"OCR: {ocr_result}")
    map_name = find_best_map_name(ocr_result)
    if map_name:
        global last_scanned_map
        last_scanned_map = map_name
        print(LANG[lang]['map_found'].format(map_name))
        create_overlay(map_dict[map_name])
    else:
        print(LANG[lang]['map_not_found'])

# ---------- Управление горячей клавишей ----------
def update_hotkey_label():
    hotkey_label.config(text=f"{LANG[lang]['current_hotkey']} {current_hotkey}")

def start_hotkey_listener():
    """Запускает слежение за горячей клавишей."""
    keyboard.add_hotkey(current_hotkey, lambda: root.after(0, process_scan))

def stop_hotkey_listener():
    """Удаляет горячую клавишу."""
    keyboard.remove_hotkey(current_hotkey)

def change_hotkey():
    change_btn.config(state='disabled')
    status_label.config(text=LANG[lang]['listen_hotkey'])
    root.update()
    def capture():
        try:
            new_hotkey = keyboard.read_hotkey(suppress=False)
            if new_hotkey:   # если что-то записалось
                root.after(0, lambda: apply_new_hotkey(new_hotkey))
            else:            # отмена (Esc или пустой ввод)
                root.after(0, clear_status)
        except Exception as e:
            root.after(0, lambda: fail_hotkey(str(e)))
            # ошибка тоже через 3 сек очистится
            root.after(3000, clear_status)
    threading.Thread(target=capture, daemon=True).start()

def apply_new_hotkey(new_hotkey):
    global current_hotkey
    stop_hotkey_listener()
    current_hotkey = new_hotkey
    settings['hotkey'] = new_hotkey
    save_settings(settings)
    start_hotkey_listener()
    update_hotkey_label()
    clear_status()
    change_btn.config(state='normal')

def fail_hotkey(err):
    status_label.config(text=LANG[lang]['hotkey_error'])
    change_btn.config(state='normal')

def clear_status():
    status_label.config(text='')

# ---------- Настройки времени и языка ----------
def validate_duration(newval):
    """Проверяет, что введено целое число от 1000 до 120000."""
    if newval == "":
        return True
    try:
        val = int(newval)
        return 1000 <= val <= 120000
    except ValueError:
        return False

def on_duration_entry(event=None):
    global overlay_duration          # <-- теперь в самом начале
    val = duration_var.get()
    if not validate_duration(val):
        messagebox.showwarning("Ошибка", LANG[lang]['invalid_duration'])
        duration_var.set(str(overlay_duration))
        return
    overlay_duration = int(val)
    settings['overlay_duration'] = overlay_duration
    save_settings(settings)

def on_language_change(event):
    global lang
    lang = lang_var.get()
    settings['language'] = lang
    save_settings(settings)
    update_ui_language()

def update_ui_language():
    root.title(LANG[lang]['title'])
    dur_label.config(text=LANG[lang]['overlay_time'])
    lang_label.config(text=LANG[lang]['language'])
    hotkey_label.config(text=f"{LANG[lang]['current_hotkey']} {current_hotkey}")
    change_btn.config(text=LANG[lang]['change_btn'])
    # howto_label.config(text=LANG[lang]['howto'].format(current_hotkey))
    status_label.config(text='')
    editor_btn.config(text=LANG[lang]['editor_btn'])    # ← добавить
    help_btn.config(text=LANG[lang]['help_btn'])        # ← добавить

# ---------- Трей ----------
def create_tray_icon():
    global tray_icon
    img = Image.new('RGB', (16, 16), (0, 120, 212))
    draw = ImageDraw.Draw(img)
    draw.rectangle([2, 2, 13, 13], fill=(255, 255, 255))
    menu = pystray.Menu(
        pystray.MenuItem(LANG[lang]['tray_show'], show_window, default=True),
        pystray.MenuItem(LANG[lang]['tray_exit'], quit_app)
    )
    tray_icon = pystray.Icon("AvalonMapper", img, "Avalon Mapper", menu)
    threading.Thread(target=tray_icon.run, daemon=True).start()

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)

def quit_app(icon=None, item=None):
    stop_hotkey_listener()
    if tray_icon:
        tray_icon.stop()
    # Вместо root.destroy() — завершаем главный цикл
    root.after(0, root.withdraw)
    root.after(100, root.quit)

def on_close():
    # Просто сворачиваем в трей, не вызываем destroy
    root.withdraw()

# ---------- Главное окно ----------
def create_main_window():
    global root, dur_label, lang_label, hotkey_label, change_btn, status_label, lang_var, duration_var, editor_btn, help_btn

    root = tk.Tk()
    root.title(LANG[lang]['title'])
    root.geometry('420x350')
    root.protocol('WM_DELETE_WINDOW', on_close)

    # Время показа
    dur_label = tk.Label(root, text=LANG[lang]['overlay_time'])
    dur_label.pack(pady=(10,0))
    duration_var = tk.StringVar(value=str(overlay_duration))
    vcmd = (root.register(validate_duration), '%P')
    dur_entry = tk.Entry(root, textvariable=duration_var, validate='key', validatecommand=vcmd)
    dur_entry.pack()
    dur_entry.bind('<Return>', on_duration_entry)
    dur_entry.bind('<FocusOut>', on_duration_entry)

    # Язык
    lang_var = tk.StringVar(value=lang)
    lang_label = tk.Label(root, text=LANG[lang]['language'])
    lang_label.pack(pady=(10,0))
    lang_combo = ttk.Combobox(root, textvariable=lang_var, values=['ru', 'en'],
                              state='readonly')
    lang_combo.pack()
    lang_combo.bind('<<ComboboxSelected>>', on_language_change)

    # Горячая клавиша
    hotkey_label = tk.Label(root, text=f"{LANG[lang]['current_hotkey']} {current_hotkey}")
    hotkey_label.pack(pady=(10,5))
    change_btn = tk.Button(root, text=LANG[lang]['change_btn'], command=change_hotkey)
    change_btn.pack()

    # Кнопка редактора карт
    editor_btn = tk.Button(root, text=LANG[lang]['editor_btn'], command=open_map_editor)
    editor_btn.pack(pady=(5,0))

    # Справка
    help_btn = tk.Button(root, text=LANG[lang]['help_btn'], command=show_help)
    help_btn.pack(pady=(5,0))

    status_label = tk.Label(root, text='', fg='blue')
    status_label.pack()
    # Гильдейская плашка (иконка + подпись)
    guild_frame = tk.Frame(root, bg='#f0f0f0')
    guild_frame.pack(pady=(5,0))
    guild_icon_path = os.path.join(ICONS_DIR, 'stuffy_bunny.png')
    if os.path.exists(guild_icon_path):
        try:
            guild_img = Image.open(guild_icon_path).resize((16, 16), Image.LANCZOS)
            guild_photo = ImageTk.PhotoImage(guild_img)
            guild_icon_lbl = tk.Label(guild_frame, image=guild_photo, bg='#f0f0f0')
            guild_icon_lbl.image = guild_photo
            guild_icon_lbl.pack(side='left', padx=(0,3))
        except Exception:
            pass
    tk.Label(guild_frame, text="by Stuffy Bunny guild", fg='#555555', font=('Segoe UI', 7),
             bg='#f0f0f0').pack(side='left')

    start_hotkey_listener()
    create_tray_icon()
    root.mainloop()

if __name__ == '__main__':
    create_main_window()