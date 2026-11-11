# Friends expenses

A small Django app to share expenses inside a group of friends and see who owes whom, in euros.

Live site: https://hkha0033.pythonanywhere.com/

## What it does

- Register, log in, log out.
- Create a group and add other registered users to it.
- Add currencies to a group, each with a rate to the euro (for example 1 USD = 0.92 EUR).
- Add expenses: description, amount, currency, who paid, who benefited.
- The group page shows what each person paid, their balance in euros, and the simplest list of payments that settles everyone.

## Try it

Open the live site and click "Create an account". Then create a group, add a friend (they need an account too), add a currency and an expense.

## Run it locally

```
python -m venv .venv
.venv\Scripts\activate
pip install django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Then open http://127.0.0.1:8000/

## How the money works

Every expense is converted to euros. The amount is split equally between the people who benefited. The payer gets credited the full amount, each beneficiary is debited their share. Then people who owe money are matched with people who are owed money until everything is settled (see `expenses/clearing.py`).

## Files

- `expenses/models.py`: FriendGroup, Currency, Expense
- `expenses/views.py`: the pages and the forms
- `expenses/clearing.py`: balances and who pays whom
- `expenses/templates/`: the HTML pages
