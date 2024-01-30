from .models import Add_chanel
from django import forms



class AddChanelForm(forms.ModelForm):
    chanel_link=forms.CharField(max_length=63,label="Линк",widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Введите ссылку/username канала для подключения детальной статистики'}))

    class Meta:
        model = Add_chanel
        fields = ['chanel_link']