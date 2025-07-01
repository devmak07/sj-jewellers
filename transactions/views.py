from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, CalculationHistory
from .forms import AddTransactionForm
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
import json
from django.db import models
import logging

logger = logging.getLogger(__name__)

def transactions_tabs(request):
    active_tab = request.GET.get("tab", "given")
    search_query = request.GET.get("search", "")
    all_transactions = Transaction.objects.all()
    if search_query:
        all_transactions = all_transactions.filter(carrier_name__icontains=search_query)
    transactions = all_transactions.filter(type=active_tab)

    # Debug print
    print("All transactions in DB:")
    for txn in all_transactions:
        print(f"{txn.carrier_name} | {txn.amount} | {txn.status} | {txn.type} | {txn.due_date}")

    total_gold_given = all_transactions.filter(type='given').aggregate(total=models.Sum('amount'))['total'] or 0
    total_gold_taken = all_transactions.filter(type='taken').aggregate(total=models.Sum('amount'))['total'] or 0

    if request.method == "POST":
        form = AddTransactionForm(request.POST)
        if form.is_valid():
            t = form.cleaned_data
            Transaction.objects.create(
                carrier_name=t["carrier_name"],
                amount=t["amount"],
                status=t["status"],
                type=active_tab,
                due_date=t["due_date"],
                history="New transaction, no history yet.",
            )
            messages.success(request, f"Transaction added for {t['carrier_name']}.")
            return redirect(f"{request.path}?tab={active_tab}")
        else:
            print("Form errors:", form.errors)
    else:
        form = AddTransactionForm(initial={"type": active_tab})

    context = {
        "transactions": transactions,
        "all_transactions": all_transactions,
        "active_tab": active_tab,
        "form": form,
        "search_query": search_query,
        "total_gold_given": total_gold_given,
        "total_gold_taken": total_gold_taken,
    }
    return render(request, "transactions/transactions_tabs.html", context)

def edit_transaction(request, pk):
    logger.warning("edit_transaction: session role = %s", request.session.get('role'))
    if request.session.get('role') == 'viewer':
        return HttpResponseForbidden('Viewers cannot modify data.')
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        form = AddTransactionForm(request.POST, instance=txn)
        if form.is_valid():
            form.save()
            messages.success(request, "Transaction updated successfully.")
            return redirect("transactions_tabs")
    else:
        form = AddTransactionForm(instance=txn)
    return render(request, "transactions/edit_transaction.html", {"form": form, "txn": txn})

def delete_transaction(request, pk):
    if request.session.get('role') == 'viewer':
        return HttpResponseForbidden('Viewers cannot modify data.')
    txn = get_object_or_404(Transaction, pk=pk)
    if request.method == "POST":
        txn.delete()
        messages.success(request, "Transaction deleted successfully.")
        return redirect("transactions_tabs")
    return render(request, "transactions/delete_transaction.html", {"txn": txn})

def toggle_status(request, pk):
    print("AJAX called for pk:", pk)
    if request.method == "POST":
        txn = get_object_or_404(Transaction, pk=pk)
        print("Before update, status:", txn.status)
        if txn.status == "pending":
            txn.status = "paid"
            txn.save()
            print("After update, status:", txn.status)
            return JsonResponse({"success": True, "new_status": txn.status})
        print("Status is not pending, status:", txn.status)
        return JsonResponse({"success": False, "error": "Status is not pending."})
    print("Invalid request method:", request.method)
    return JsonResponse({"success": False, "error": "Invalid request method."})

@require_POST
def mark_paid(request, pk):
    txn = get_object_or_404(Transaction, pk=pk)
    if txn.status == "pending":
        txn.status = "paid"
        txn.save()
    return redirect("transactions_tabs")

def calculation(request):
    if 'calc' not in request.session or request.method == 'GET':
        request.session['calc'] = {
            'name': '',
            'history': [],
            'total': None,
        }
    calc = request.session['calc']
    error = ''
    history_strings = []
    if request.method == 'POST':
        if 'start' in request.POST:
            calc['name'] = request.POST.get('name', '')
            try:
                calc['total'] = float(request.POST.get('amount', '0'))
                calc['history'] = [(calc['name'], calc['total'], 'Initial')]
            except ValueError:
                error = 'Invalid initial amount.'
        elif 'continue' in request.POST:
            op = request.POST.get('operation')
            try:
                value = float(request.POST.get('next_amount', '0'))
                label = request.POST.get('label', '')
                prev_total = calc['total']
                if op == 'add':
                    calc['total'] += value
                elif op == 'subtract':
                    calc['total'] -= value
                elif op == 'multiply':
                    calc['total'] *= value
                elif op == 'divide':
                    if value == 0:
                        error = 'Cannot divide by zero.'
                    else:
                        calc['total'] /= value
                if not error:
                    calc['history'].append((op, value, label, prev_total, calc['total']))
            except ValueError:
                error = 'Invalid number.'
        elif 'end' in request.POST:
            # Save calculation to database
            if calc['name'] and calc['total'] is not None and len(calc['history']) > 0:
                CalculationHistory.objects.create(
                    name=calc['name'],
                    total=calc['total'],
                    history=json.dumps(calc['history']),
                )
            request.session['calc'] = {
                'name': '',
                'history': [],
                'total': None,
            }
            request.session['calc_saved'] = True
            return redirect('calculation_history')
        request.session['calc'] = calc
    # Build classic history strings
    for idx, entry in enumerate(calc['history']):
        if idx == 0:
            history_strings.append(f"{entry[0]}: {entry[1]}")
        else:
            op, value, label, prev_total, new_total = entry
            op_symbol = {'add': '+', 'subtract': '-', 'multiply': '×', 'divide': '÷'}.get(op, op)
            label_str = f" ({label})" if label else ""
            history_strings.append(f"{prev_total:.2f} {op_symbol} {value:.2f} = {new_total:.2f}{label_str}")
    return render(request, 'transactions/calculation.html', {'calc': calc, 'error': error, 'history_strings': history_strings})

def calculation_pdf(request):
    if request.session.get('role') == 'viewer':
        return HttpResponseForbidden('Viewers cannot download PDF.')
    import json as _json
    calc_id = request.GET.get('id')
    if calc_id:
        calc_obj = get_object_or_404(CalculationHistory, id=calc_id)
        calc = {
            'name': calc_obj.name,
            'total': calc_obj.total,
            'history': _json.loads(calc_obj.history),
        }
    else:
        calc = request.session.get('calc', {'name': '', 'history': [], 'total': None})
    history_strings = []
    for idx, entry in enumerate(calc.get('history', [])):
        if idx == 0:
            history_strings.append(f"{entry[0]}: {entry[1]}")
        else:
            op, value, label, prev_total, new_total = entry
            op_symbol = {'add': '+', 'subtract': '-', 'multiply': '×', 'divide': '÷'}.get(op, op)
            label_str = f" ({label})" if label else ""
            history_strings.append(f"{prev_total:.2f} {op_symbol} {value:.2f} = {new_total:.2f}{label_str}")
    html = render_to_string('transactions/calculation_pdf.html', {'calc': calc, 'history_strings': history_strings})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="calculation.pdf"'
    pisa.CreatePDF(io.StringIO(html), dest=response)
    return response

def calculation_history(request):
    calculations = CalculationHistory.objects.all().order_by('-created_at')
    calc_saved = request.session.pop('calc_saved', False)
    return render(request, 'transactions/calculation_history.html', {'calculations': calculations, 'calc_saved': calc_saved})

def main_dashboard(request):
    return render(request, 'transactions/main_dashboard.html')

def delete_calculation_history(request, pk):
    if request.session.get('role') == 'viewer':
        return HttpResponseForbidden('Viewers cannot modify data.')
    calc = get_object_or_404(CalculationHistory, pk=pk)
    if request.method == "POST":
        calc.delete()
        messages.success(request, "Calculation history deleted successfully.")
        return redirect("calculation_history")
    return render(request, "transactions/delete_calculation.html", {"calc": calc})
