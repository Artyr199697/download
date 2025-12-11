#!/usr/bin/env python3
"""
MP4 to MP3 Audio Extractor
Программа для извлечения аудиодорожек из MP4 видеофайлов.
"""

import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
from threading import Thread

# Путь к ffmpeg (измени если у тебя другой путь)
FFMPEG_PATH = r"C:\Program Files\Virtual Desktop Streamer\ffmpeg.exe"


class AudioExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MP4 → MP3 Конвертер")
        self.root.geometry("600x400")
        self.root.resizable(True, True)

        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status_text = tk.StringVar(value="Выберите папки и нажмите 'Начать'")
        self.progress_var = tk.DoubleVar()

        self.setup_ui()

    def setup_ui(self):
        """Создание графического интерфейса"""
        # Главный фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Заголовок
        title_label = ttk.Label(main_frame, text="Извлечение аудио из MP4 файлов",
                                font=("Arial", 14, "bold"))
        title_label.pack(pady=10)

        # Фрейм для выбора исходной папки
        source_frame = ttk.LabelFrame(main_frame, text="Папка с MP4 файлами", padding="5")
        source_frame.pack(fill=tk.X, pady=5)

        source_entry = ttk.Entry(source_frame, textvariable=self.source_folder, width=50)
        source_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        source_btn = ttk.Button(source_frame, text="Обзор...",
                                command=self.select_source_folder)
        source_btn.pack(side=tk.RIGHT)

        # Фрейм для выбора папки назначения
        output_frame = ttk.LabelFrame(main_frame, text="Папка для сохранения MP3", padding="5")
        output_frame.pack(fill=tk.X, pady=5)

        output_entry = ttk.Entry(output_frame, textvariable=self.output_folder, width=50)
        output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        output_btn = ttk.Button(output_frame, text="Обзор...",
                                command=self.select_output_folder)
        output_btn.pack(side=tk.RIGHT)

        # Чекбокс для поиска в подпапках
        self.recursive_var = tk.BooleanVar(value=True)
        recursive_check = ttk.Checkbutton(main_frame, text="Искать в подпапках",
                                          variable=self.recursive_var)
        recursive_check.pack(pady=5)

        # Прогресс бар
        progress_frame = ttk.LabelFrame(main_frame, text="Прогресс", padding="5")
        progress_frame.pack(fill=tk.X, pady=10)

        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var,
                                            maximum=100, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=5)

        status_label = ttk.Label(progress_frame, textvariable=self.status_text)
        status_label.pack()

        # Лог
        log_frame = ttk.LabelFrame(main_frame, text="Лог", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = tk.Text(log_frame, height=8, state=tk.DISABLED)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)

        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопки
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(btn_frame, text="🎵 Начать конвертацию",
                                    command=self.start_conversion)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        quit_btn = ttk.Button(btn_frame, text="Выход", command=self.root.quit)
        quit_btn.pack(side=tk.RIGHT, padx=5)

    def log(self, message):
        """Добавить сообщение в лог"""
        self.log_text.configure(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state=tk.DISABLED)
        self.root.update_idletasks()

    def select_source_folder(self):
        """Выбор папки с MP4 файлами"""
        folder = filedialog.askdirectory(title="Выберите папку с MP4 файлами")
        if folder:
            self.source_folder.set(folder)
            # Автоматически предложить папку для вывода
            if not self.output_folder.get():
                output = os.path.join(folder, "extracted_audio")
                self.output_folder.set(output)

    def select_output_folder(self):
        """Выбор папки для сохранения MP3"""
        folder = filedialog.askdirectory(title="Выберите папку для сохранения MP3")
        if folder:
            self.output_folder.set(folder)

    def find_mp4_files(self, folder, recursive=True):
        """Поиск всех MP4 файлов в папке"""
        mp4_files = []
        folder_path = Path(folder)

        if recursive:
            pattern = "**/*.mp4"
        else:
            pattern = "*.mp4"

        for mp4_file in folder_path.glob(pattern):
            mp4_files.append(mp4_file)

        # Также ищем с расширением в верхнем регистре
        if recursive:
            pattern = "**/*.MP4"
        else:
            pattern = "*.MP4"

        for mp4_file in folder_path.glob(pattern):
            if mp4_file not in mp4_files:
                mp4_files.append(mp4_file)

        return mp4_files

    def check_ffmpeg(self):
        """Проверка наличия ffmpeg"""
        # Сначала проверяем указанный путь
        if os.path.exists(FFMPEG_PATH):
            return True
        # Потом проверяем в PATH
        try:
            subprocess.run(["ffmpeg", "-version"],
                          capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def get_ffmpeg_cmd(self):
        """Получить команду ffmpeg"""
        if os.path.exists(FFMPEG_PATH):
            return FFMPEG_PATH
        return "ffmpeg"

    def extract_audio(self, input_file, output_file):
        """Извлечение аудио из видео файла"""
        cmd = [
            self.get_ffmpeg_cmd(),
            "-i", str(input_file),
            "-vn",  # Без видео
            "-acodec", "libmp3lame",  # Кодек MP3
            "-ab", "192k",  # Битрейт
            "-ar", "44100",  # Частота дискретизации
            "-y",  # Перезаписывать без вопросов
            str(output_file)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def start_conversion(self):
        """Запуск конвертации в отдельном потоке"""
        if not self.source_folder.get():
            messagebox.showerror("Ошибка", "Выберите папку с MP4 файлами!")
            return

        if not self.output_folder.get():
            messagebox.showerror("Ошибка", "Выберите папку для сохранения MP3!")
            return

        # Запускаем в отдельном потоке, чтобы не блокировать интерфейс
        thread = Thread(target=self.do_conversion, daemon=True)
        thread.start()

    def do_conversion(self):
        """Основная логика конвертации"""
        self.start_btn.configure(state=tk.DISABLED)

        # Проверка ffmpeg
        self.log("Проверка ffmpeg...")
        if not self.check_ffmpeg():
            self.log("❌ ОШИБКА: ffmpeg не найден!")
            self.log("Установите ffmpeg:")
            self.log("  Ubuntu/Debian: sudo apt install ffmpeg")
            self.log("  macOS: brew install ffmpeg")
            self.log("  Windows: скачайте с https://ffmpeg.org/download.html")
            messagebox.showerror("Ошибка",
                "ffmpeg не установлен!\n\nУстановите его и попробуйте снова.")
            self.start_btn.configure(state=tk.NORMAL)
            return

        self.log("✓ ffmpeg найден")

        # Создание выходной папки
        output_path = Path(self.output_folder.get())
        output_path.mkdir(parents=True, exist_ok=True)
        self.log(f"Папка для вывода: {output_path}")

        # Поиск MP4 файлов
        self.status_text.set("Поиск MP4 файлов...")
        mp4_files = self.find_mp4_files(self.source_folder.get(),
                                         self.recursive_var.get())

        if not mp4_files:
            self.log("❌ MP4 файлы не найдены!")
            messagebox.showwarning("Предупреждение",
                "В выбранной папке нет MP4 файлов.")
            self.start_btn.configure(state=tk.NORMAL)
            return

        self.log(f"Найдено MP4 файлов: {len(mp4_files)}")

        # Конвертация
        success_count = 0
        error_count = 0

        for i, mp4_file in enumerate(mp4_files, 1):
            progress = (i / len(mp4_files)) * 100
            self.progress_var.set(progress)
            self.status_text.set(f"Обработка {i}/{len(mp4_files)}: {mp4_file.name}")

            # Формируем имя выходного файла
            output_file = output_path / (mp4_file.stem + ".mp3")

            self.log(f"[{i}/{len(mp4_files)}] {mp4_file.name} → {output_file.name}")

            if self.extract_audio(mp4_file, output_file):
                self.log(f"  ✓ Готово")
                success_count += 1
            else:
                self.log(f"  ❌ Ошибка")
                error_count += 1

        # Итоги
        self.progress_var.set(100)
        self.status_text.set("Готово!")

        summary = f"\n{'='*40}\n"
        summary += f"ЗАВЕРШЕНО!\n"
        summary += f"Успешно: {success_count}\n"
        summary += f"Ошибок: {error_count}\n"
        summary += f"Файлы сохранены в: {output_path}\n"
        summary += f"{'='*40}"
        self.log(summary)

        messagebox.showinfo("Готово!",
            f"Конвертация завершена!\n\n"
            f"Успешно: {success_count}\n"
            f"Ошибок: {error_count}\n\n"
            f"Файлы сохранены в:\n{output_path}")

        self.start_btn.configure(state=tk.NORMAL)

    def run(self):
        """Запуск приложения"""
        self.root.mainloop()


def main():
    app = AudioExtractor()
    app.run()


if __name__ == "__main__":
    main()
