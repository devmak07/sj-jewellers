from django import forms
from .models import Transaction

class AddTransactionForm(forms.ModelForm):
    due_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Transaction
        fields = ['carrier_name', 'amount', 'status', 'due_date']
