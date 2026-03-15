# accounts.py
from bank_account import BankAccount
from datetime import datetime, timedelta
from typing import Optional

class SavingsAccount(BankAccount):
    """Сберегательный счет: ограничение на количество снятий в месяц."""
    def __init__(self, account_number: str, owner: str, initial_balance: float = 0,
                 currency: str = "RUB", interest_rate: float = 0.0,
                 max_withdrawals_per_month: int = 5):
        super().__init__(account_number, owner, initial_balance, currency, interest_rate)
        self._max_withdrawals_per_month = max_withdrawals_per_month
        self._withdrawal_count = 0
        self._month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    def _reset_if_new_month(self):
        now = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if now > self._month_start:
            self._withdrawal_count = 0
            self._month_start = now

    def withdraw(self, amount: float, description: str = "") -> bool:
        self._reset_if_new_month()
        if self._withdrawal_count >= self._max_withdrawals_per_month:
            print(f"❌ Ошибка: превышен лимит снятий ({self._max_withdrawals_per_month} раз в месяц)")
            return False
        success = super().withdraw(amount, description)
        if success:
            self._withdrawal_count += 1
        return success


class CreditAccount(BankAccount):
    """Кредитный счет: можно уходить в минус до лимита."""
    def __init__(self, account_number: str, owner: str, initial_balance: float = 0,
                 currency: str = "RUB", interest_rate: float = 0.0,
                 credit_limit: float = 10000):
        super().__init__(account_number, owner, initial_balance, currency, interest_rate)
        self._credit_limit = float(credit_limit)

    def withdraw(self, amount: float, description: str = "") -> bool:
        if not self._is_active:
            print("❌ Ошибка: счет закрыт")
            return False
        if amount <= 0:
            print("❌ Ошибка: сумма должна быть положительной!")
            return False
        if self._balance - amount < -self._credit_limit:
            print(f"❌ Ошибка: превышен кредитный лимит!")
            print(f"  Доступно (с учётом лимита): {self._balance + self._credit_limit}{self._currency}")
            print(f"  Запрошено: {amount}{self._currency}")
            return False
        self._balance -= amount
        self._add_transaction("WITHDRAWAL", amount, description)
        print(f" Снято: {amount}{self._currency}")
        if description:
            print(f"  Описание: {description}")
        print(f"  Текущий баланс: {self._balance}{self._currency}")
        return True


class DepositAccount(BankAccount):
    """Депозитный счет: нельзя снимать до окончания срока."""
    def __init__(self, account_number: str, owner: str, initial_balance: float = 0,
                 currency: str = "RUB", interest_rate: float = 0.0,
                 term_days: int = 365):
        super().__init__(account_number, owner, initial_balance, currency, interest_rate)
        self._term_end = datetime.now() + timedelta(days=term_days)

    def withdraw(self, amount: float, description: str = "") -> bool:
        now = datetime.now()
        if now < self._term_end and self._balance - amount < 0:
            print(f"❌ Ошибка: срок депозита не истек!")
            print(f"  Текущая дата: {now.strftime('%Y-%m-%d')}")
            print(f"  Дата окончания: {self._term_end.strftime('%Y-%m-%d')}")
            return False
        return super().withdraw(amount, description)