from django import forms

from main.models import *
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'name':forms.TextInput(attrs={'class':'form-control'}),
            'category':forms.Select(attrs={'class':'form-control'}),
            'desc':forms.Textarea(attrs={'class':'from-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'product_available_count':forms.NumberInput(attrs={'class':'form-control'}),
            'img':forms.FileInput(attrs={'class':'form-control'}),

        }


class Checkoutform(forms.Form):

    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder':'1234 main st',
    }))
    apartment_address=forms.CharField(required=False,widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder' : 'apartment or suite',
    }))
    country = CountryField(blank_label='(select country)').formfield(widget=CountrySelectWidget(attrs={
        'class':'Custom-select d-block w-100',
    }))
    zip_code =forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': '123456',
    }))