# bank_account.py
"""
Модуль для работы с банковскими счетами.
Содержит класс BankAccount и методы для анализа/сохранения.
"""

from datetime import datetime
import json
import os
from typing import Optional, List, Tuple


class BankAccount:
    """Класс для банковского счета с защитой данных, историей и дополнительными возможностями."""

    def __init__(self, account_number: str, owner: str, initial_balance: float = 0,
                 currency: str = "RUB", interest_rate: float = 0.0):
        # Проверки
        if not account_number or not isinstance(account_number, str):
            raise ValueError("Номер счета должен быть непустой строкой")
        if not owner or not isinstance(owner, str):
            raise ValueError("Имя владельца должно быть непустой строкой")
        if initial_balance < 0:
            raise ValueError("Начальный баланс не может быть отрицательным")
        if interest_rate < 0:
            raise ValueError("Процентная ставка не может быть отрицательной")

        # Приватные атрибуты
        self._account_number = account_number
        self._owner = owner
        self._balance = float(initial_balance)
        self._currency = currency
        self._interest_rate = float(interest_rate)
        self._transactions: List[dict] = []
        self._is_active = True

        # Добавляем начальную операцию
        if initial_balance > 0:
            self._add_transaction("DEPOSIT", initial_balance, "Начальный взнос")

        print(f"✅ Счет {account_number} создан для {owner}")
        print(f"  Начальный баланс: {initial_balance}{currency}")
        print(f"  Процентная ставка: {interest_rate}%")

    def _add_transaction(self, transaction_type: str, amount: float, description: str = ""):
        """Внутренний метод для добавления транзакции."""
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": transaction_type,
            "amount": float(amount),
            "balance_after": self._balance,
            "description": description
        }
        self._transactions.append(transaction)

    # --- Свойства (только чтение) ---
    @property
    def account_number(self) -> str:
        return self._account_number

    @property
    def owner(self) -> str:
        return self._owner

    @property
    def balance(self) -> float:
        return self._balance

    @property
    def currency(self) -> str:
        return self._currency

    @property
    def interest_rate(self) -> float:
        return self._interest_rate

    # --- Методы операций ---
    def deposit(self, amount: float, description: str = "") -> bool:
        """Вносит деньги на счет."""
        if not self._is_active:
            print("❌ Ошибка: счет закрыт")
            return False
        if amount <= 0:
            print("❌ Ошибка: сумма должна быть положительной!")
            return False
        self._balance += amount
        self._add_transaction("DEPOSIT", amount, description)
        print(f" Внесено: {amount}{self._currency}")
        if description:
            print(f"  Описание: {description}")
        print(f"  Текущий баланс: {self._balance}{self._currency}")
        return True

    def withdraw(self, amount: float, description: str = "") -> bool:
        """Снимает деньги со счета."""
        if not self._is_active:
            print("❌ Ошибка: счет закрыт")
            return False
        if amount <= 0:
            print("❌ Ошибка: сумма должна быть положительной!")
            return False
        if amount > self._balance:
            print(f"❌ Ошибка: недостаточно средств!")
            print(f"  Запрошено: {amount}{self._currency}")
            print(f"  Доступно: {self._balance}{self._currency}")
            return False
        self._balance -= amount
        self._add_transaction("WITHDRAWAL", amount, description)
        print(f" Снято: {amount}{self._currency}")
        if description:
            print(f"  Описание: {description}")
        print(f"  Текущий баланс: {self._balance}{self._currency}")
        return True

    def transfer(self, to_account: 'BankAccount', amount: float, description: str = "") -> bool:
        """Переводит деньги на другой счет."""
        if not isinstance(to_account, BankAccount):
            print("❌ Ошибка: получатель должен быть банковским счетом")
            return False
        if self.withdraw(amount, f"Перевод: {description}"):
            to_account.deposit(amount, f"Перевод от {self._owner}: {description}")
            print(" Перевод выполнен успешно")
            return True
        return False

    def close_account(self) -> bool:
        """Закрывает счет (только если баланс = 0)."""
        if self._balance > 0:
            print(f"⏨ ️ На счете остались средства: {self._balance}{self._currency}")
            print("  Снимите все средства перед закрытием")
            return False
        self._is_active = False
        print(f" Счет {self._account_number} закрыт")
        return True

    # --- ЗАДАНИЕ 1: Процентная ставка ---
    def set_interest_rate(self, rate: float) -> bool:
        """Устанавливает новую процентную ставку."""
        if rate < 0:
            print("❌ Ошибка: ставка не может быть отрицательной")
            return False
        self._interest_rate = float(rate)
        print(f"✅ Процентная ставка установлена: {self._interest_rate}%")
        return True

    def add_interest(self) -> bool:
        """Начисляет проценты на текущий баланс."""
        if not self._is_active:
            print("❌ Ошибка: счет закрыт — начисление процентов невозможно")
            return False
        if self._interest_rate <= 0:
            print("ℹ️  Процентная ставка = 0% — проценты не начисляются")
            return False
        interest = self._balance * (self._interest_rate / 100)
        if interest > 0:
            self.deposit(interest, f"Начисление процентов ({self._interest_rate}%)")
            return True
        return False

    # --- ЗАДАНИЕ 3: Сохранение/загрузка ---
    def save_to_file(self, filename: str) -> None:
        """Сохраняет состояние счета в JSON-файл."""
        data = {
            "_account_number": self._account_number,
            "_owner": self._owner,
            "_balance": self._balance,
            "_currency": self._currency,
            "_interest_rate": self._interest_rate,
            "_transactions": self._transactions,
            "_is_active": self._is_active
        }
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"💾 Сохранено в: {filename}")
        except Exception as e:
            print(f"❌ Ошибка при сохранении: {e}")

    @classmethod
    def load_from_file(cls, filename: str) -> Optional['BankAccount']:
        """Загружает счет из JSON-файла."""
        if not os.path.exists(filename):
            print(f"❌ Файл не найден: {filename}")
            return None
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            account = cls.__new__(cls)
            account._account_number = data["_account_number"]
            account._owner = data["_owner"]
            account._balance = float(data["_balance"])
            account._currency = data["_currency"]
            account._interest_rate = float(data.get("_interest_rate", 0.0))
            account._transactions = data["_transactions"]
            account._is_active = data["_is_active"]
            print(f"📂 Загружено из: {filename}")
            return account
        except Exception as e:
            print(f"❌ Ошибка при загрузке: {e}")
            return None

    # --- ЗАДАНИЕ 4: Статистика ---
    def total_deposits(self) -> float:
        """Общая сумма всех пополнений."""
        return sum(t["amount"] for t in self._transactions if t["type"] == "DEPOSIT")

    def total_withdrawals(self) -> float:
        """Общая сумма всех снятий."""
        return sum(t["amount"] for t in self._transactions if t["type"] == "WITHDRAWAL")

    def average_transaction(self) -> float:
        """Средняя сумма операции."""
        if not self._transactions:
            return 0.0
        return sum(t["amount"] for t in self._transactions) / len(self._transactions)

    def busiest_day(self) -> Tuple[Optional[str], int]:
        """Возвращает день с наибольшим количеством операций: (дата, количество)."""
        from collections import Counter
        dates = [t["date"].split()[0] for t in self._transactions]
        if not dates:
            return None, 0
        counter = Counter(dates)
        day, count = counter.most_common(1)[0]
        return day, count

    # --- Вспомогательные методы ---
    def display_info(self) -> None:
        status = "Активен" if self._is_active else "Закрыт"
        print("\n" + "=" * 50)
        print("ИНФОРМАЦИЯ О СЧЕТЕ")
        print("=" * 50)
        print(f"Номер счета: {self._account_number}")
        print(f"Владелец: {self._owner}")
        print(f"Баланс: {self._balance}{self._currency}")
        print(f"Статус: {status}")
        print(f"Процентная ставка: {self._interest_rate}%")
        print(f"Количество операций: {len(self._transactions)}")
        print("=" * 50)

    def show_history(self, last_n: Optional[int] = None) -> None:
        print("\n" + "=" * 70)
        print(f"ИСТОРИЯ ОПЕРАЦИЙ ПО СЧЕТУ {self._account_number}")
        print("=" * 70)
        if not self._transactions:
            print("История операций пуста")
            return
        transactions_to_show = self._transactions[-last_n:] if last_n else self._transactions
        print(f"Показаны последние {last_n or 'все'} операций:\n")
        for t in transactions_to_show:
            emoji = "" if t["type"] == "DEPOSIT" else ""
            operation = "ПОПОЛНЕНИЕ" if t["type"] == "DEPOSIT" else "СНЯТИЕ"
            print(f"{emoji} {t['date']} | {operation}")
            print(f"  Сумма: {t['amount']}{self._currency}")
            if t["description"]:
                print(f"  Описание: {t['description']}")
            print(f"  Баланс после: {t['balance_after']}{self._currency}")
            print("-" * 70)


if __name__ == "__main__":
    print("=== ТЕСТ ЗАДАНИЙ ===")
    acc = BankAccount("TEST123", "Анна", 1000, "USD", interest_rate=5.0)
    acc.deposit(200, "Зарплата")
    acc.withdraw(150, "Кафе")
    acc.add_interest()
    print(f"Общее пополнение: {acc.total_deposits()}")
    print(f"Средняя операция: {acc.average_transaction():.2f}")
    print(f"Самый активный день: {acc.busiest_day()}")
    acc.save_to_file("test_account.json")
    loaded = BankAccount.load_from_file("test_account.json")
    if loaded:
        loaded.display_info()