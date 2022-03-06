from django import forms

class UserDeleteForm(forms.Form):
    """
    Simple form that provides a checkbox that signals deletion.
    """
    confirma_stergerea = forms.BooleanField(required=True, help_text='bifeaza pentru a confirma stergerea')
    confirma_stergerea.widget.attrs.update({'class': 'form-check-input'})