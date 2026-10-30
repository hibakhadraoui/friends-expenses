from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import FriendGroup
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


@login_required
def home(request):
    groups = FriendGroup.objects.filter(members=request.user)
    return render(request, 'home.html', {'groups': groups})


@login_required
def group_detail(request, group_id):
    group = get_object_or_404(FriendGroup, id=group_id, members=request.user)
    balances, paid = compute_balances(group)
    payments = compute_clearing(balances)
    rows = []
    for user, balance in balances.items():
        rows.append({'user': user, 'paid': paid.get(user, 0), 'balance': balance})
    context = {
        'group': group,
        'expenses': group.expense_set.all(),
        'rows': rows,
        'payments': payments,
    }
    return render(request, 'group_detail.html', context)