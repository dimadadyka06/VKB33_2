import re

# 1
def validate_login(login):
    pattern = r'^[a-zA-Z][a-zA-Z0-9_]{3,18}[a-zA-Z0-9]$'
    return bool(re.match(pattern, login))

# 2
def find_dates(text):
    pattern = r'\b\d{1,2}[.\-/]\d{1,2}[.\-/]\d{2,4}\b'
    return re.findall(pattern, text)

# 3
def parse_log(log_line):
    pattern = r'(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2}:\d{2})\s+\w+\s+user=(\w+)\s+action=(\w+)\s+ip=([\d.]+)'
    match = re.match(pattern, log_line)
    if match:
        return {
            'date': match.group(1),
            'time': match.group(2),
            'user': match.group(3),
            'action': match.group(4),
            'ip': match.group(5)
        }
    return None

# 4
def validate_password(password):
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*]).{8,}$'
    return bool(re.match(pattern, password))

# 5
def validate_email(email, domains):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    domain = email.split('@')[1]
    return domain in domains

# 6
def normalize_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        digits = '7' + digits
    if digits.startswith('8'):
        digits = '7' + digits[1:]
    if digits.startswith('7') and len(digits) == 11:
        return f'+{digits}'
    return None

print("Выберите задание (1-6):")
choice = input()

if choice == '1':
    login = input("Введите логин: ")
    print(validate_login(login))

elif choice == '2':
    text = input("Введите текст: ")
    print(find_dates(text))

elif choice == '3':
    log = input("Введите строку лога: ")
    print(parse_log(log))

elif choice == '4':
    password = input("Введите пароль: ")
    print(validate_password(password))

elif choice == '5':
    email = input("Введите email: ")
    domains = ['gmail.com', 'yandex.ru', 'edu.ru']
    print(validate_email(email, domains))

elif choice == '6':
    phone = input("Введите номер телефона: ")
    print(normalize_phone(phone))

else:
    print("Неверный выбор")