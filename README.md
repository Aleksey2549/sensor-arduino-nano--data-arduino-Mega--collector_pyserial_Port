# sensor-arduino-nano--data-arduino-Mega--collector_pyserial_Port
English:
This tool collects serial data from Arduino-based multi-sensor devices, splits the stream into separate files by sensor type, merges records by timestamp, and saves a unified raw dataset in structured CSV format. All files—including the original stringTest.txt—are stored in sequentially numbered archive folders for versioned organization. Designed for reliability, minimal dependencies (pyserial, pandas), and easy integration into sensor logging workflows.

Русский:
Эта программа собирает данные с многодатчиковых устройств на базе Arduino через последовательный порт, разделяет поток на файлы по типам датчиков, объединяет записи по временным меткам и сохраняет неочищенную объединённую базу в формате CSV. Все файлы — включая исходный stringTest.txt — сохраняются в папки с порядковой нумерацией (arh/1/, arh/2/, …) для удобного версионирования. Проект требует минимум зависимостей (pyserial, pandas) и подходит для автоматизации сбора данных с физических датчиков.

## **mega_master.txt**

### **English Description**
This sketch runs on an **Arduino Mega** and acts as a **master device** in a multi-sensor system. It communicates with up to **four slave devices** via **SoftwareSerial** on the following pin pairs:
- Device 1: RX=10, TX=7  
- Device 2: RX=11, TX=8  
- Device 3: RX=12, TX=6  
- Device 4: RX=13, TX=5  

The master periodically sends a request byte (`0xAB`, decimal 171) to each slave and waits for a structured response starting with `?!` and ending with `#_`. Upon receiving valid data, it stores it temporarily in a buffer.

The system uses a **DS1307 RTC module** (via I²C) to timestamp sensor readings. Data is written to an **SD card** every **even second**, but only if new data has been received (`b_l > 0`) and writing is allowed (`dostupZapis == true`). Writing is disabled during odd seconds to prevent race conditions.

Additionally, pressing a button connected to analog pin **A1** (with threshold >630) triggers a dump of the last ~5000 bytes from the SD log file (`datalog.txt`) to the main **Serial** and **Serial3** ports, wrapped between `!!` and `##`.

Key features:
- Multi-device polling over SoftwareSerial
- RTC-synchronized logging
- SD card data storage
- On-demand log dump via button press

---

### **Русское описание**
Этот скетч работает на **Arduino Mega** и выступает в роли **ведущего устройства (мастера)** в системе с несколькими датчиками. Он взаимодействует с **четырьмя ведомыми устройствами** через **SoftwareSerial** на следующих пинах:
- Устройство 1: RX=10, TX=7  
- Устройство 2: RX=11, TX=8  
- Устройство 3: RX=12, TX=6  
- Устройство 4: RX=13, TX=5  

Мастер периодически отправляет байт запроса (`0xAB`, десятичное 171) каждому ведомому и ожидает структурированный ответ, начинающийся с `?!` и заканчивающийся `#_`. При получении корректных данных они сохраняются во временный буфер.

Система использует модуль **RTC DS1307** (по шине I²C) для привязки показаний к реальному времени. Данные записываются на **карту SD** каждую **чётную секунду**, но только если получены новые данные (`b_l > 0`) и разрешена запись (`dostupZapis == true`). В нечётные секунды запись блокируется, чтобы избежать конфликтов.

Также предусмотрена кнопка на аналоговом пине **A1** (порог срабатывания >630): при нажатии происходит выгрузка последних ~5000 байт из файла лога (`datalog.txt`) в основной **Serial** и **Serial3**, обрамлённая маркерами `!!` и `##`.

Основные функции:
- Опрос нескольких устройств через SoftwareSerial  
- Синхронизация записи по времени от RTC  
- Сохранение данных на SD-карту  
- Ручной сброс лога по нажатию кнопки  

---

## **Gy273_qmc5883l_Slave_M.txt**

### **English Description**
This sketch runs on a secondary Arduino (e.g., Uno or Nano) and serves as a **slave sensor node** equipped with a **QMC5883L 3-axis magnetometer**. It communicates with a master device (e.g., Arduino Mega) via **SoftwareSerial** on pins **RX=2, TX=3** at **4800 baud**.

The sensor is read every **100 ms**, and new magnetic field values (MX, MY, MZ) are stored only if they differ from the previous reading. A flag (`newDataAvailable`) tracks whether fresh data is ready to send.

The slave **waits passively** for a specific request byte (`0xAB`) from the master. Upon receiving it:
- If new data is available, it formats a string like:  
  `?!|1|Mag|Mg_x=|<mx>|Mg_y=|<my>|Mg_z=|<mz>|#_`  
  and sends it via SoftwareSerial.
- The `newDataAvailable` flag is then reset to prevent resending the same data.
- Any extra bytes in the buffer are cleared to avoid misinterpretation.

Debug output is optionally sent to the hardware Serial monitor (enabled via `DEBUG` macro), showing sensor reads, received requests, and transmitted data.



---

### **Русское описание**
Этот скетч работает на вторичном Arduino (например, Uno или Nano) и представляет собой **ведомый узел с датчиком магнитного поля QMC5883L**. Он общается с мастером (например, Arduino Mega) через **SoftwareSerial** на пинах **RX=2, TX=3** со скоростью **4800 бод**.

Датчик опрашивается каждые **100 мс**, и новые значения компонентов магнитного поля (MX, MY, MZ) сохраняются только при изменении. Флаг `newDataAvailable` указывает, есть ли готовые к отправке данные.

Ведомое устройство **пассивно ожидает** специальный байт запроса (`0xAB`) от мастера. При его получении:
- Если есть новые данные, формируется строка вида:  
  `?!|1|Mag|Mg_x=|<mx>|Mg_y=|<my>|Mg_z=|<mz>|#_`  
  и отправляется через SoftwareSerial.
- Флаг `newDataAvailable` сбрасывается, чтобы избежать повторной отправки тех же данных.
- Лишние байты в буфере очищаются для предотвращения ошибок.

Отладочная информация (при включённом `DEBUG`) выводится в аппаратный Serial Monitor: показания датчика, полученные запросы, отправленные данные.

Архитектура обеспечивает **неблокирующее**, событийное взаимодействие с минимальной задержкой.

