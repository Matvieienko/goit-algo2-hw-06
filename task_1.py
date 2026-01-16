import mmh3

class BloomFilter:
    def __init__(self, size, num_hashes):
        self.size = size
        self.num_hashes = num_hashes
        self.bit_array = [0] * size

    def add(self, item):
        # Валідація
        if not isinstance(item, str) or not item:
            return

        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.size
            self.bit_array[index] = 1

    def check(self, item):
        if not isinstance(item, str) or not item:
            return False

        for i in range(self.num_hashes):
            index = mmh3.hash(item, i) % self.size
            if self.bit_array[index] == 0:
                return False
        return True

def check_password_uniqueness(bloom_filter, new_passwords):
    results = {}
    for pwd in new_passwords:
        # Обробка некоректних даних 
        if not isinstance(pwd, str) or not pwd:
            results[pwd] = "некоректний пароль"
            continue

        if bloom_filter.check(pwd):
            results[pwd] = "вже використаний"
        else:
            results[pwd] = "унікальний"
            # bloom_filter.add(pwd) # Опціонально можна додати новий унікальний пароль у базу
            
    return results

if __name__ == "__main__":
    # Ініціалізація фільтра Блума
    bloom = BloomFilter(size=1000, num_hashes=3)

    # Додавання існуючих паролів
    existing_passwords = ["password123", "admin123", "qwerty123"]
    for password in existing_passwords:
        bloom.add(password)

    # Перевірка нових паролів
    new_passwords_to_check = ["password123", "newpassword", "admin123", "guest"]
    results = check_password_uniqueness(bloom, new_passwords_to_check)

    # Виведення результатів
    for password, status in results.items():
        print(f"Пароль '{password}' — {status}.")
