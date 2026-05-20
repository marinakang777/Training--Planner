import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data.json"

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner")
        self.root.geometry("700x500")
        
        # Данные
        self.trainings = []
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        self.update_table()
        
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky="w", padx=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Поле Тип тренировки
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=0, column=2, sticky="w", padx=5)
        self.type_var = tk.StringVar()
        self.type_combo = ttk.Combobox(input_frame, textvariable=self.type_var, width=15)
        self.type_combo['values'] = ('Бег', 'Велосипед', 'Плавание', 'Силовая', 'Йога')
        self.type_combo.grid(row=0, column=3, padx=5)
        self.type_combo.current(0)
        
        # Поле Длительность
        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w", padx=5)
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5)
        
        # Кнопка Добавить
        add_btn = ttk.Button(input_frame, text="Добавить тренировку", command=self.add_training)
        add_btn.grid(row=0, column=6, padx=10)
        
        # Рамка для фильтров
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, padx=5)
        self.filter_type_var = tk.StringVar()
        self.filter_type_combo = ttk.Combobox(filter_frame, textvariable=self.filter_type_var, width=15)
        self.filter_type_combo['values'] = ('Все', 'Бег', 'Велосипед', 'Плавание', 'Силовая', 'Йога')
        self.filter_type_combo.grid(row=0, column=1, padx=5)
        self.filter_type_combo.current(0)
        
        ttk.Label(filter_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5)
        self.filter_date_entry = ttk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=3, padx=5)
        
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.grid(row=0, column=4, padx=10)
        
        clear_filter_btn = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.clear_filter)
        clear_filter_btn.grid(row=0, column=5, padx=5)
        
        # Таблица для отображения тренировок
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Создание таблицы Treeview
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=150)
        self.tree.column("duration", width=120)
        
        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопка удаления
        del_btn = ttk.Button(self.root, text="Удалить выбранную тренировку", command=self.delete_training)
        del_btn.pack(pady=5)
        
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False
    
    def add_training(self):
        date = self.date_entry.get().strip()
        training_type = self.type_var.get()
        duration = self.duration_entry.get().strip()
        
        # Валидация
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        
        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность должна быть положительным числом")
            return
        
        # Добавление
        training = {
            "date": date,
            "type": training_type,
            "duration": float(duration)
        }
        self.trainings.append(training)
        self.save_data()
        self.update_table()
        
        # Очистка поля длительности
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    def delete_training(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        # Получаем индекс выбранной записи
        for item in selected:
            values = self.tree.item(item, "values")
            # Ищем запись в self.trainings для удаления
            for i, training in enumerate(self.trainings):
                if (training["date"] == values[0] and 
                    training["type"] == values[1] and 
                    str(training["duration"]) == values[2]):
                    del self.trainings[i]
                    break
        
        self.save_data()
        self.update_table()
        messagebox.showinfo("Успех", "Тренировка удалена!")
    
    def apply_filter(self):
        filter_type = self.filter_type_var.get()
        filter_date = self.filter_date_entry.get().strip()
        
        filtered = self.trainings.copy()
        
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        
        if filter_date and self.validate_date(filter_date):
            filtered = [t for t in filtered if t["date"] == filter_date]
        elif filter_date:
            messagebox.showerror("Ошибка", "Неверный формат даты фильтра")
            return
        
        self.update_table(filtered)
    
    def clear_filter(self):
        self.filter_type_combo.current(0)
        self.filter_date_entry.delete(0, tk.END)
        self.update_table()
    
    def update_table(self, data=None):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if data is None:
            data = self.trainings
        
        # Сортируем по дате
        data.sort(key=lambda x: x["date"])
        
        for training in data:
            self.tree.insert("", "end", values=(
                training["date"],
                training["type"],
                training["duration"]
            ))
    
    def save_data(self):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.trainings, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except:
                self.trainings = []
        else:
            # Создаём пример данных
            self.trainings = [
                {"date": "2024-01-15", "type": "Бег", "duration": 30},
                {"date": "2024-01-17", "type": "Плавание", "duration": 45},
                {"date": "2024-01-20", "type": "Силовая", "duration": 60}
            ]
            self.save_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()
