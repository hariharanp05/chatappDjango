# chat/forms.py
from django import forms

class RoomForm(forms.Form):
    room_name = forms.CharField(label='', max_length=100)

class MessageForm(forms.Form):
    content = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Type your message here...'})
    )
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'})
    )
