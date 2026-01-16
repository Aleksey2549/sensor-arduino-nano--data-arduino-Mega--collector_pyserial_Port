# sensor-arduino-nano--data-arduino-Mega--collector_pyserial_Port
English:
This tool collects serial data from Arduino-based multi-sensor devices, splits the stream into separate files by sensor type, merges records by timestamp, and saves a unified raw dataset in structured CSV format. All files—including the original stringTest.txt—are stored in sequentially numbered archive folders for versioned organization. Designed for reliability, minimal dependencies (pyserial, pandas), and easy integration into sensor logging workflows.

Русский:
Эта программа собирает данные с многодатчиковых устройств на базе Arduino через последовательный порт, разделяет поток на файлы по типам датчиков, объединяет записи по временным меткам и сохраняет неочищенную объединённую базу в формате CSV. Все файлы — включая исходный stringTest.txt — сохраняются в папки с порядковой нумерацией (arh/1/, arh/2/, …) для удобного версионирования. Проект требует минимум зависимостей (pyserial, pandas) и подходит для автоматизации сбора данных с физических датчиков.
