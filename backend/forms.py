from .models import Add_chanel,Like
from django import forms



class AddChanelForm(forms.ModelForm):
    chanel_link=forms.CharField(max_length=63,label="Линк",widget=forms.TextInput(attrs={'class': 'form__input', 'placeholder': 'Введите ссылку/username канала для подключения детальной статистики'}))

    class Meta:
        model = Add_chanel
        fields = ['chanel_link']

class LikeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        language_code = kwargs.pop('language_code', 'en')  # Default to 'en' if not provided
        super().__init__(*args, **kwargs)

        if language_code == 'en':
            self.fields['node'].label = "Link"
            self.fields['node'].widget.attrs['placeholder'] = "You can leave a note. It will only be visible to you."
        else:  # Default to Russian
            self.fields['node'].label = "Линк"
            self.fields['node'].widget.attrs['placeholder'] = "Вы можете оставить заметку. Она будет видна только вам."

    node = forms.CharField(
        max_length=63,
        widget=forms.TextInput(attrs={'class': 'main-analitics__input'}),
        required=False
    )

    class Meta:
        model = Like
        fields = ['node']