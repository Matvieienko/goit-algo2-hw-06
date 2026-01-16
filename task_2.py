import time
import math
import re
import mmh3


class HyperLogLog:
    def __init__(self, p=5):
        self.p = p
        self.m = 1 << p
        self.registers = [0] * self.m
        self.alpha = self._get_alpha()
        self.small_range_correction = 5 * self.m / 2 

    def _get_alpha(self):
        if self.p <= 16:
            return 0.673
        elif self.p == 32:
            return 0.697
        else:
            return 0.7213 / (1 + 1.079 / self.m)

    def add(self, item):
        x = mmh3.hash(str(item), signed=False)
        j = x & (self.m - 1)
        w = x >> self.p
        self.registers[j] = max(self.registers[j], self._rho(w))

    def _rho(self, w):
        return len(bin(w)) - 2 if w > 0 else 32

    def count(self):
        Z = sum(2.0 ** -r for r in self.registers)
        E = self.alpha * self.m * self.m / Z
        
        if E <= self.small_range_correction:
            V = self.registers.count(0)
            if V > 0:
                return self.m * math.log(self.m / V)
        
        return E

# Завантаження даних

def load_data(filename):
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ips = []
    
    try:
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                match = ip_pattern.search(line)
                if match:
                    ips.append(match.group())
    except FileNotFoundError:
        print(f"Помилка: Файл '{filename}' не знайдено.")
        return []
        
    return ips

# Методи підрахунку та порівняння
def count_exact_unique(data):
    #Точний підрахунок унікальних елементів за допомогою set
    start_time = time.time()
    unique_elements = set(data)
    count = len(unique_elements)
    end_time = time.time()
    return count, end_time - start_time

def count_hll_unique(data):
    # Наближений підрахунок за допомогою HyperLogLog
    hll = HyperLogLog(p=14)
    
    start_time = time.time()
    for item in data:
        hll.add(item)
    count = hll.count()
    end_time = time.time()
    return count, end_time - start_time


if __name__ == "__main__":
    log_file = "lms-stage-access.log"
    
    print(f"Завантаження даних з файлу {log_file}...")
    data = load_data(log_file)
    
    if data:
        print(f"Завантажено {len(data)} записів. Починаємо тестування...\n")
        
        # Точний підрахунок
        exact_count, exact_time = count_exact_unique(data)
        
        # HyperLogLog
        hll_count, hll_time = count_hll_unique(data)
        
        # Обчислення похибки 
        error_percentage = abs(exact_count - hll_count) / exact_count * 100
        
        # Виведення результатів у таблиці
        print("Результати порівняння:")
        print(f"{'':<25} {'Точний підрахунок':<20} {'HyperLogLog':<20}")
        print("-" * 65)
        print(f"{'Унікальні елементи':<25} {exact_count:<20} {hll_count:<20}")
        print(f"{'Час виконання (сек.)':<25} {exact_time:<20.5f} {hll_time:<20.5f}")
        print(f"{'Похибка (%)':<25} {'0.0':<20} {error_percentage:<20.2f}")
    else:
        print("Дані не завантажено. Перевірте наявність файлу.")

# Завантаження даних з файлу lms-stage-access.log...
# Завантажено 29553 записів. Починаємо тестування...

# Результати порівняння:
#                          Точний підрахунок    HyperLogLog
#-----------------------------------------------------------------
#Унікальні елементи        28                   28.023953075428718
#Час виконання (сек.)      0.00101              0.01100
#Похибка (%)               0.0                  0.09