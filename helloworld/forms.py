from django import forms


class PictureForm(forms.Form):
    file = forms.FileField()
