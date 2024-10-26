import re


# Класс для токенизации выражения
class Tokenizer:
    TOKEN_NUMBER = "number"
    TOKEN_OPERATOR = "operator"
    TOKEN_PARENTHESIS = "parenthesis"

    def __init__(self):
        # Список операторов с их приоритетами и функциями выполнения
        self.OPERATORS = {
            "+": {"func": lambda a, b: a + b, "priority": 1},
            "-": {"func": lambda a, b: a - b, "priority": 1},
            "*": {"func": lambda a, b: a * b, "priority": 2},
            "/": {"func": lambda a, b: a / b, "priority": 2},
            "^": {"func": lambda a, b: a ** b, "priority": 3},
            'unary_minus': {"func": lambda a: -a, "priority": 4}
        }

    def tokenize(self, expr):
        """Разбивает строку на токены, учитывая операторы, числа и скобки."""
        tokens = []
        current_token = ""
        previous_type = None

        for i, char in enumerate(expr):
            if char.isdigit() or char == ".":
                current_token += char
                previous_type = self.TOKEN_NUMBER
            else:
                if current_token:
                    tokens.append({"type": self.TOKEN_NUMBER, "value": float(current_token)})
                    current_token = ""

                if char in self.OPERATORS:
                    # Добавляем оператор в список токенов
                    tokens.append({"type": self.TOKEN_OPERATOR, "value": char})
                    previous_type = self.TOKEN_OPERATOR
                elif char in "()":
                    tokens.append({"type": self.TOKEN_PARENTHESIS, "value": char})
                    previous_type = self.TOKEN_PARENTHESIS

        if current_token:
            tokens.append({"type": self.TOKEN_NUMBER, "value": float(current_token)})

        return tokens



# Класс для парсинга токенов в постфиксную нотацию
class Parser:
    def __init__(self, operators):
        self.operators = operators

    def has_lower_priority(self, op1, op2):
        """Проверяет, ниже ли приоритет у op1 по сравнению с op2."""
        return self.operators[op1]["priority"] < self.operators[op2]["priority"]

    def to_postfix(self, tokens):
        """Конвертирует инфиксные токены в постфиксную нотацию с учетом унарного минуса."""
        output = []
        stack = []

        for i, token in enumerate(tokens):
            if token["type"] == Tokenizer.TOKEN_NUMBER:
                output.append(token)

            elif token["type"] == Tokenizer.TOKEN_OPERATOR:
                # Обработка унарного минуса
                if token["value"] == "-" and (
                        i == 0 or tokens[i - 1]["type"] == Tokenizer.TOKEN_OPERATOR or tokens[i - 1]["value"] == "("):
                    stack.append({"type": "unary_minus", "value": "unary_minus"})
                else:
                    # Обычный оператор
                    while stack and stack[-1]["type"] == Tokenizer.TOKEN_OPERATOR and not self.has_lower_priority(
                            stack[-1]["value"], token["value"]):
                        output.append(stack.pop())
                    stack.append(token)

            elif token["type"] == Tokenizer.TOKEN_PARENTHESIS:
                if token["value"] == "(":
                    stack.append(token)
                elif token["value"] == ")":
                    while stack and stack[-1]["value"] != "(":
                        output.append(stack.pop())
                    stack.pop()  # Удаляем "(" из стека

        while stack:
            output.append(stack.pop())

        return output



# Класс для выполнения вычислений по постфиксной нотации
class Calculator:
    def __init__(self, operators):
        self.operators = operators

    def calculate(self, postfix_tokens):
        """Вычисляет значение выражения в постфиксной записи."""
        stack = []

        for token in postfix_tokens:
            if token["type"] == Tokenizer.TOKEN_NUMBER:
                # Если токен - число, добавляем его в стек
                stack.append(token["value"])
            elif token["type"] == "unary_minus":
                # Применение унарного минуса к одному числу из стека
                if len(stack) < 1:
                    raise ValueError("Неверное выражение")
                a = stack.pop()
                result = self.operators["unary_minus"]["func"](a)
                stack.append(result)
            elif token["type"] == Tokenizer.TOKEN_OPERATOR:
                # Применение бинарного оператора (например, +, -, *, /, ^)
                if len(stack) < 2:
                    raise ValueError("Неверное выражение")
                b = stack.pop()
                a = stack.pop()
                result = self.operators[token["value"]]["func"](a, b)
                stack.append(result)

        # Если после всех операций в стеке больше одного элемента, значит выражение было неверным
        if len(stack) != 1:
            raise ValueError("Ошибка в выражении")
        return stack.pop()




# Класс для консольного интерфейса
class ConsoleInterface:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.parser = Parser(self.tokenizer.OPERATORS)
        self.calculator = Calculator(self.tokenizer.OPERATORS)

    def run(self):
        """Запускает консольный интерфейс для ввода выражений и вывода результата."""
        print("Добро пожаловать в консольный калькулятор! Введите выражение или 'exit' для выхода.")
        while True:
            expr = input("Введите выражение: ")
            if expr.lower() == "exit":
                print("Выход...")
                break

            try:
                tokens = self.tokenizer.tokenize(expr)
                postfix = self.parser.to_postfix(tokens)
                result = self.calculator.calculate(postfix)

                # Запрашиваем количество знаков после запятой
                precision = input("Введите количество знаков после запятой (нажмите Enter для стандартного): ")
                if precision.isdigit():
                    result = round(result, int(precision))
                print("Результат:", result)
            except Exception as e:
                print(f"Ошибка: {e}")

class ConsoleInterfaceTest:
    def __init__(self, interface):
        self.interface = interface

    def run_tests(self):
        """Выполняет тестирование консольного калькулятора."""
        test_cases = {
            "2+3": 5,
            "1-2*3": -5,
            "(1-2)*3": -3,
            "(1+(2/2))-(3-5)": 4,
            "1/2-1/2": 0,
            "(1+(2/2))-(3-5)^2": -2,  # Проверка возведения в степень
            "2^3": 8,  # Возведение в степень
            "3 + 4 * 2 / (1 - 5)^2": 3.5,  # Сложное выражение с приоритетами
            "-(2^2)": -4,  # Унарный минус со степенью
            "(-2)^2": 4  # Скобки с возведением в степень
        }

        print("Начинаем тестирование...")
        for expr, expected in test_cases.items():
            try:
                # Процесс вычисления
                tokens = self.interface.tokenizer.tokenize(expr)
                postfix = self.interface.parser.to_postfix(tokens)
                result = self.interface.calculator.calculate(postfix)

                # Проверка результата
                if result == expected:
                    print(f"Тест '{expr}' прошел: результат = {result}")
                else:
                    print(f"Тест '{expr}' провален: результат = {result}, ожидалось = {expected}")
            except Exception as e:
                print(f"Тест '{expr}' завершился с ошибкой: {e}")


# Запуск интерфейса
if __name__ == "__main__":
    interface = ConsoleInterface()
    tester = ConsoleInterfaceTest(interface)
    tester.run_tests()












