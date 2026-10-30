from decimal import Decimal


def compute_balances(group):
    """Return (balances, paid), both in euros. A positive balance means the person is owed money."""
    balances = {}
    paid = {}
    for member in group.members.all():
        balances[member] = Decimal("0")
        paid[member] = Decimal("0")

    for expense in group.expense_set.all():
        if expense.currency:
            amount_eur = expense.amount * expense.currency.rate_to_eur
        else:
            amount_eur = expense.amount

        beneficiaries = list(expense.beneficiaries.all())
        if len(beneficiaries) == 0:
            continue
        share = amount_eur / len(beneficiaries)

        balances[expense.payer] = balances.get(expense.payer, Decimal("0")) + amount_eur
        paid[expense.payer] = paid.get(expense.payer, Decimal("0")) + amount_eur
        for person in beneficiaries:
            balances[person] = balances.get(person, Decimal("0")) - share

    return balances, paid


def compute_clearing(balances):
    """Return a list of (debtor, creditor, amount) that makes everybody even."""
    creditors = []
    debtors = []
    for user, balance in balances.items():
        balance = balance.quantize(Decimal("0.01"))
        if balance > 0:
            creditors.append([user, balance])
        elif balance < 0:
            debtors.append([user, -balance])

    payments = []
    i = 0
    j = 0
    while i < len(debtors) and j < len(creditors):
        amount = min(debtors[i][1], creditors[j][1])
        payments.append((debtors[i][0], creditors[j][0], amount))
        debtors[i][1] = debtors[i][1] - amount
        creditors[j][1] = creditors[j][1] - amount
        if debtors[i][1] == 0:
            i = i + 1
        if creditors[j][1] == 0:
            j = j + 1
    return payments