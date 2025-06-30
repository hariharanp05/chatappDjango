from django import forms

class RoomForm(forms.Form):
    room_name = forms.CharField(
        label='Room Name',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter room name'
        })
    )

class MessageForm(forms.Form):
    content = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Type your message here...'
        })
    )
    file = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control-file'
        })
    )
