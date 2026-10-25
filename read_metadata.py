"""
Скрипт для чтения метаданных медиафайлов.

Вариант 2: видеоматериалы.
Типы файлов: MP4, MKV.
Читаемые метаданные: длительность, разрешение, fps.

Использование:
    python read_metadata.py <путь_к_видеофайлу>
"""

import os
import sys

import cv2

# Соответствие расширения файла типу медиа (для варианта 2 - только видео)
MEDIA_TYPES = {
    '.mp4': 'video',
    '.mkv': 'video',
}


def check_file_exists(file_path):
    """
    Проверяет, что по указанному пути существует обычный файл.

    :param file_path: путь к файлу
    :raises FileNotFoundError: если файла нет
    :raises ValueError: если путь указывает не на файл (например, на папку)
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    if not os.path.isfile(file_path):
        raise ValueError(f"Указанный путь не является файлом: {file_path}")


def detect_media_type(file_path):
    """
    Определяет тип медиафайла по расширению.

    :param file_path: путь к файлу
    :return: строка с типом медиа ('video')
    :raises ValueError: если расширение не поддерживается
    """
    extension = os.path.splitext(file_path)[1].lower()
    if extension not in MEDIA_TYPES:
        supported = ', '.join(MEDIA_TYPES)
        shown = extension if extension else '(нет расширения)'
        raise ValueError(
            f"Неверный формат файла: {shown}. Поддерживаются: {supported}"
        )
    return MEDIA_TYPES[extension]


def read_video_metadata(file_path):
    """
    Читает метаданные видеофайла (MP4, MKV) с помощью OpenCV.

    :param file_path: путь к файлу
    :return: словарь с метаданными (разрешение, fps, длительность)
    :raises ValueError: если файл не удалось открыть или он повреждён
    """
    metadata = {}

    # Открываем видео; любые ошибки OpenCV превращаем в понятное ValueError
    try:
        cap = cv2.VideoCapture(file_path)
        try:
            if not cap.isOpened():
                raise ValueError(
                    "не удалось открыть видеофайл "
                    "(файл повреждён или не является видео)"
                )

            # Чтение свойств видео
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        finally:
            # Освобождаем файл в любом случае
            cap.release()
    except Exception as e:
        raise ValueError(f"Не удалось прочитать метаданные: {e}")

    # Если свойства нулевые, контейнер открылся, но данные видео повреждены
    if width <= 0 or height <= 0 or fps <= 0 or frame_count <= 0:
        raise ValueError(
            "Не удалось прочитать метаданные: файл повреждён "
            "(не удалось получить разрешение, fps или число кадров)"
        )

    # Разрешение
    metadata['Разрешение'] = f"{width}x{height}"

    # Частота кадров
    metadata['Кадров в секунду (fps)'] = f"{fps:.2f}"

    # Расчёт длительности: число кадров / кадров в секунду
    duration = frame_count / fps
    metadata['Количество кадров'] = frame_count
    metadata['Длительность'] = f"{duration:.2f} сек"

    return metadata


def main():
    """Основная функция."""
    # Получаем имя файла из аргументов командной строки
    if len(sys.argv) < 2:
        print("Использование: python read_metadata.py <файл>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        # Проверяем файл и определяем его тип по расширению
        check_file_exists(file_path)
        media_type = detect_media_type(file_path)

        # Вызываем соответствующую функцию чтения метаданных
        if media_type == 'video':
            metadata = read_video_metadata(file_path)
        else:
            # Сюда попадаем, только если тип добавили в MEDIA_TYPES,
            # а обработчик для него ещё не написали
            raise ValueError(f"Нет обработчика для типа: {media_type}")
    except (FileNotFoundError, ValueError) as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)

    # Выводим результат
    print(f"Метаданные для {file_path}:")
    for key, value in metadata.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
