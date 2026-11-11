from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import FriendGroup, Currency, Expense
from .clearing import compute_balances, compute_clearing


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


def find_group(request):
    # the group id comes from the address (?id=3); only groups of the user are searched
    if 'id' in request.GET:
        for group in FriendGroup.objects.filter(members=request.user):
            if str(group.id) == request.GET['id']:
                return group
    return None


@login_required
def home(request):
    groups = FriendGroup.objects.filter(members=request.user)
    return render(request, 'home.html', {'groups': groups})


@login_required
def group_detail(request):
    group = find_group(request)
    if group is None:
        return redirect('/')

    balances, paid = compute_balances(group)
    payments = compute_clearing(balances)
    rows = []
    for user, balance in balances.items():
        rows.append({'user': user, 'paid': paid.get(user, 0), 'balance': balance})
    context = {
        'group': group,
        'members': group.members.all(),
        'currencies': Currency.objects.filter(group=group),
        'expenses': group.expense_set.all(),
        'rows': rows,
        'payments': payments,
    }
    return render(request, 'group_detail.html', context)


@login_required
def create_group(request):
    if 'name' in request.GET:
        name = request.GET['name']
        if name == '' or len(name) > 100:
            template_values = {'error': 'Please enter a group name (100 characters maximum).'}
            return render(request, 'create_group.html', template_values)
        newGroup = FriendGroup(name=name)
        newGroup.save()
        newGroup.members.add(request.user)  # the creator is a member
        return redirect('/group/?id=' + str(newGroup.id))
    else:
        return render(request, 'create_group.html')


@login_required
def add_member(request):
    group = find_group(request)
    if group is None:
        return redirect('/')

    if 'username' in request.GET:
        users = User.objects.filter(username=request.GET['username'], is_superuser=False)
        if len(users) == 0:
            template_values = {'group': group, 'error': 'No user with that name.'}
            return render(request, 'member_form.html', template_values)
        group.members.add(users[0])
        return redirect('/group/?id=' + str(group.id))
    else:
        return render(request, 'member_form.html', {'group': group})


@login_required
def add_currency(request):
    group = find_group(request)
    if group is None:
        return redirect('/')

    if 'code' in request.GET and 'rate' in request.GET:
        code = request.GET['code']
        rate = request.GET['rate']

        error = ''
        if code == '' or len(code) > 5:
            error = 'Please enter a currency code (5 characters maximum), for example USD.'
        elif not rate.replace('.', '', 1).isdigit() or len(rate) > 10:
            error = 'Please enter a valid rate, for example 0.92.'
        elif float(rate) <= 0 or float(rate) >= 100000:
            error = 'The rate must be positive and smaller than 100000.'

        if error != '':
            template_values = {'group': group, 'error': error}
            return render(request, 'currency_form.html', template_values)

        newCurrency = Currency(group=group, code=code.upper(), rate_to_eur=rate)
        newCurrency.save()
        return redirect('/group/?id=' + str(group.id))
    else:
        return render(request, 'currency_form.html', {'group': group})


@login_required
def add_expense(request):
    group = find_group(request)
    if group is None:
        return redirect('/')
    members = group.members.all()
    currencies = Currency.objects.filter(group=group)
    template_values = {'group': group, 'members': members, 'currencies': currencies}

    if 'description' in request.GET and 'amount' in request.GET and 'payer' in request.GET:
        description = request.GET['description']
        amount = request.GET['amount']
        payerId = request.GET['payer']
        currencyId = ''
        if 'currency' in request.GET:
            currencyId = request.GET['currency']

        # the people who benefited: one checkbox per member
        beneficiaries = []
        for member in members:
            if 'beneficiary_' + str(member.id) in request.GET:
                beneficiaries.append(member)

        payer = None
        if payerId.isdigit() and len(members.filter(id=payerId)) == 1:
            payer = members.get(id=payerId)

        # no currency chosen means euros
        currency = None
        currencyFound = True
        if currencyId != '':
            currencyFound = False
            if currencyId.isdigit() and len(currencies.filter(id=currencyId)) == 1:
                currency = currencies.get(id=currencyId)
                currencyFound = True

        error = ''
        if description == '' or len(description) > 200:
            error = 'Please enter a description (200 characters maximum).'
        elif not amount.replace('.', '', 1).isdigit() or len(amount) > 15:
            error = 'Please enter a valid amount, for example 45.50.'
        elif float(amount) <= 0 or float(amount) >= 100000000:
            error = 'The amount must be positive and smaller than 100000000.'
        elif payer == None:
            error = 'Please choose who paid.'
        elif not currencyFound:
            error = 'Unknown currency.'
        elif len(beneficiaries) == 0:
            error = 'Tick at least one person who benefited.'

        if error != '':
            template_values['error'] = error
            return render(request, 'expense_form.html', template_values)

        newExpense = Expense(group=group, description=description, amount=amount, currency=currency, payer=payer)
        newExpense.save()
        for person in beneficiaries:
            newExpense.beneficiaries.add(person)
        return redirect('/group/?id=' + str(group.id))
    else:
        return render(request, 'expense_form.html', template_values)
