"""
Скрипт для конвертации медиафайлов с помощью FFmpeg.

Вариант 2: видеоматериалы.
Конвертация: MP4 -> MKV.

Использование:
    python convert_media.py <входной_файл.mp4> <выходной_файл.mkv>
"""

import os
import shutil
import subprocess
import sys

# Допустимые расширения для варианта 2
INPUT_EXTENSION = '.mp4'
OUTPUT_EXTENSION = '.mkv'


def check_ffmpeg():
    """
    Проверяет наличие FFmpeg в системе (в переменной PATH).
    Если FFmpeg не найден, выводит сообщение и завершает работу.
    """
    if shutil.which('ffmpeg') is None:
        print(
            "Ошибка: FFmpeg не найден в системе.\n"
            "Установите FFmpeg (https://ffmpeg.org/) и добавьте папку bin в PATH.",
            file=sys.stderr
        )
        sys.exit(1)


def check_paths(input_path, output_path):
    """
    Проверяет входной и выходной пути перед конвертацией.

    :param input_path: путь к исходному файлу
    :param output_path: путь к выходному файлу
    :raises FileNotFoundError: если исходного файла нет
    :raises ValueError: если путь не файл или расширение неверное
    """
    # Исходный файл должен существовать и быть файлом
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Входной файл не найден: {input_path}")
    if not os.path.isfile(input_path):
        raise ValueError(f"Входной путь не является файлом: {input_path}")

    # Проверяем расширения (в варианте 2 только MP4 -> MKV)
    input_ext = os.path.splitext(input_path)[1].lower()
    output_ext = os.path.splitext(output_path)[1].lower()

    if input_ext != INPUT_EXTENSION:
        raise ValueError(
            f"Неверный формат входного файла: {input_ext or '(нет расширения)'}. "
            f"Ожидается {INPUT_EXTENSION}"
        )
    if output_ext != OUTPUT_EXTENSION:
        raise ValueError(
            f"Неверный формат выходного файла: {output_ext or '(нет расширения)'}. "
            f"Ожидается {OUTPUT_EXTENSION}"
        )


def convert_file(input_path, output_path):
    """
    Конвертирует медиафайл с помощью FFmpeg.

    :param input_path: путь к исходному файлу
    :param output_path: путь к выходному файлу
    :return: True при успехе, False при ошибке
    """
    # Создаём папку для результата, если её ещё нет
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Формируем команду FFmpeg:
    #   -hide_banner / -loglevel error - выводить только ошибки,
    #   -i  - входной файл,
    #   -y  - перезаписывать выходной файл без вопросов
    cmd = [
        'ffmpeg', '-hide_banner', '-loglevel', 'error',
        '-i', input_path, '-y', output_path
    ]

    # Запускаем FFmpeg и ждём завершения
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True,
            encoding='utf-8', errors='replace'
        )
    except OSError as e:
        print(f"Ошибка: не удалось запустить FFmpeg: {e}", file=sys.stderr)
        return False

    # Проверяем код возврата (0 - успех)
    if result.returncode != 0:
        print(f"Ошибка FFmpeg (код {result.returncode}):", file=sys.stderr)
        print(result.stderr.strip(), file=sys.stderr)
        # Удаляем недописанный файл, если FFmpeg успел его создать
        if os.path.exists(output_path):
            os.remove(output_path)
        return False

    return True


def main():
    """Основная функция."""
    if len(sys.argv) < 3:
        print("Использование: python convert_media.py <входной_файл> <выходной_файл>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = sys.argv[2]

    # Проверяем наличие FFmpeg
    check_ffmpeg()

    # Проверяем входной и выходной файлы
    try:
        check_paths(input_path, output_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    # Запускаем конвертацию
    print(f"Конвертация: {input_path} -> {output_path} ...")
    if not convert_file(input_path, output_path):
        sys.exit(1)

    # Выводим результат
    size_kb = os.path.getsize(output_path) / 1024
    print(f"Конвертация завершена: {output_path} ({size_kb:.1f} КБ)")


if __name__ == '__main__':
    main()
    # Конец
