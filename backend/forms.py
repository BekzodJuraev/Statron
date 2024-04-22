from .models import Add_chanel,Like
from django import forms



class AddChanelForm(forms.ModelForm):
    chanel_link=forms.CharField(max_length=63,label="Линк",widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Введите ссылку/username канала для подключения детальной статистики'}))

    class Meta:
        model = Add_chanel
        fields = ['chanel_link']

class LikeForm(forms.ModelForm):
    node = forms.CharField(
        max_length=63,
        label="Линк",
        widget=forms.TextInput(attrs={'class': 'main-analitics__input',
                                      'placeholder': 'Вы можете оставить заметку. Она будет видна только вам.'}),
        required=False  # Make the node field not required
    )

    class Meta:
        model = Like
        fields = ['node']