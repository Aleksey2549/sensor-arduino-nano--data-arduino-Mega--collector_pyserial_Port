#!/usr/bin/env python3
# pip install pyserial pandas

import serial
import serial.tools.list_ports
import time
import pandas as pd
from pathlib import Path

# ==============================
# Настройки
# ==============================

BAUDRATE = 9600
TIMEOUT = 15

# Размер буфера ОС (~4095 байт)
BUFFER_SIZE = 4095
READ_MULTIPLIER = 3  # коэффициент кратности
READ_TOTAL = BUFFER_SIZE * READ_MULTIPLIER

ARCHIVE_DIR = Path.cwd() / "arh"

SENSOR_CONFIG = {
    "MagTest.txt": "Mag",
    "txt_Atm_tem_h.txt": "Atm_tem_h",
    "SGP30_aht20.txt": "SGP30_aht20",
}

TIME_COLUMNS = ["day", "hour", "min"]


# ==============================
# Часть 1: Чтение данных через Serial
# ==============================

def collect_serial_data(archive_folder: Path):
    """Читает данные с порта и сохраняет stringTest.txt в указанную папку."""
    ports = serial.tools.list_ports.comports()
    target_port = None

    for p in ports:
        print(f"Найден порт: {p.device} — {p.description}")
        if "CH340" in p.description:
            target_port = p.device
            break

    if target_port is None:
        if ports:
            target_port = ports[0].device
            print(f"CH340 не найден. Используем первый порт: {target_port}")
        else:
            raise RuntimeError("Нет доступных последовательных портов!")

    ser = serial.Serial(port=target_port, baudrate=BAUDRATE, timeout=TIMEOUT)
    time.sleep(2)  # Стабилизация Arduino

    ser.reset_output_buffer()
    ser.reset_input_buffer()

    # Отправка команды
    ser.write(b'sbrosdannih\n')

    print("Настройки порта:", ser.get_settings())

    # Чтение данных
    total_read = 0
    all_data = b""
    while total_read < READ_TOTAL:
        available = ser.in_waiting
        if available > 0:
            chunk = ser.read(min(available, READ_TOTAL - total_read))
            all_data += chunk
            total_read += len(chunk)
        else:
            time.sleep(0.05)

    ser.close()

    # Сохранение в папку архива
    source_file = archive_folder / "stringTest.txt"
    decoded_data = all_data.decode('utf-8', errors='replace')
    with open(source_file, "w", encoding='utf-8', newline='\r\n') as f:
        f.write(decoded_data)

    print(f"✅ Прочитано {len(all_data)} байт. Сохранено в {source_file}")
    return source_file


# ==============================
# Часть 2: Обработка данных
# ==============================

def get_next_archive_folder():
    """Возвращает путь к следующей папке архива с порядковым номером."""
    ARCHIVE_DIR.mkdir(exist_ok=True)
    existing = [int(f.name) for f in ARCHIVE_DIR.iterdir() if f.is_dir() and f.name.isdigit()]
    next_num = max(existing) + 1 if existing else 1
    folder = ARCHIVE_DIR / str(next_num)
    folder.mkdir(exist_ok=True)
    return folder


def split_source_file(source_file: Path, target_folder: Path):
    """Разделяет stringTest.txt на файлы по датчикам."""
    with open(source_file, "r", encoding="utf-8") as f:
        content = f.read()

    records = content.split("!!")
    file_handles = {}

    try:
        for filename in SENSOR_CONFIG:
            file_handles[filename] = open(target_folder / filename, "w", encoding="utf-8")

        for record in records:
            record = record.strip()
            if not record.endswith("||"):
                continue
            if len(record) > 70:
                continue
            for filename, keyword in SENSOR_CONFIG.items():
                if keyword in record:
                    file_handles[filename].write(record + "\n")
                    break
    finally:
        for fh in file_handles.values():
            fh.close()

    print(f"✅ Разделение завершено. Файлы сохранены в {target_folder}")


def parse_sensor_file(filepath):
    """Парсит файл датчика в список списков."""
    if not filepath.exists():
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()
    parsed = []
    for line in lines:
        line = line.rstrip().replace("\\r\\n", "").strip()
        if not line or line == "||":
            continue
        parts = [p.strip() for p in line.split("|") if p.strip() != ""]
        if parts and parts[-1] == "":
            parts = parts[:-1]
        parsed.append(parts)
    return parsed


def build_dataframe(parsed_data):
    """Создаёт DataFrame без фильтрации по длине."""
    if not parsed_data:
        return pd.DataFrame()
    max_len = max(len(row) for row in parsed_data)
    clean_data = [row + [""] * (max_len - len(row)) for row in parsed_data]
    base_cols = ["placeholder"] + TIME_COLUMNS
    extra_cols = [f"col_{i}" for i in range(max_len - len(base_cols))]
    columns = base_cols + extra_cols
    return pd.DataFrame(clean_data, columns=columns)


def main():
    # Шаг 1: Создать папку архива
    archive_folder = get_next_archive_folder()
    print(f"📁 Используется папка: {archive_folder}")

    # Шаг 2: Сбор данных → сохранение stringTest.txt в эту папку
    source_file = collect_serial_data(archive_folder)

    # Шаг 3: Разделение
    split_source_file(source_file, archive_folder)

    # Шаг 4: Загрузка и объединение
    dataframes = {}
    for filename in SENSOR_CONFIG:
        filepath = archive_folder / filename
        parsed = parse_sensor_file(filepath)
        df = build_dataframe(parsed)
        if not df.empty:
            dataframes[filename] = df
            print(f"Загружено {len(df)} строк из {filename}")

    if not dataframes:
        print("⚠️ Ни один файл не был успешно загружен.")
        return

    # Объединение по времени (без очистки!)
    merged = None
    for name, df in dataframes.items():
        if merged is None:
            merged = df.copy()
        else:
            merged = pd.merge(merged, df, on=TIME_COLUMNS, how="outer")

    if merged is None:
        print("⚠️ Нечего объединять.")
        return

    # Сохраняем "как есть" — с нечисловыми данными
    output_csv = archive_folder / "unified_raw_data.csv"
    merged.to_csv(output_csv, index=False)

    print(f"\n✅ Объединённая база сохранена в: {output_csv}")
    print("\n📊 Пример:")
    print(merged.head())


if __name__ == "__main__":
    main()