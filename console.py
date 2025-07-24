from create import *
from add import *
import sys

if len(sys.argv) < 1:  # Должно быть не менее 1 аргументов
    print("Usage: python3 my_console_app.py <command> [X]")
    sys.exit()

# Получение команды
command = sys.argv[1]

# Обработка команд
if command == "-create":
    create()
elif command == "-top":
    if len(sys.argv) > 1:  # Проверяем, есть ли аргументы после "-top"
        X = sys.argv[2]
        if not X:
            print("Please enter the name of the tag")
        else:
            top(X)
    else:
        print("Please provide the name of the tag after -top")
    top(X)
elif command == "-vulnerability":
    if len(sys.argv) > 1:  # Проверяем, есть ли аргументы после "-vulnerability"
        X = " ".join(sys.argv[2:]).strip()
        if not X:  # Проверяем, не пустая ли строка
            print("Please enter the name of the product")
        else:
            vulnerability(X)
    else:
        print("Please provide the name of the product after -vulnerability")
else:
    print("Invalid command")
