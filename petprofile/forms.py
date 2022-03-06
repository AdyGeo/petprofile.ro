from django.db.models.fields import NullBooleanField
from django.forms import widgets
from django.http import request
from petprofile.models import PetProfile, Breed
from django import forms


class PetProfileCreateForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ['petPhoto','petName','petSpecies','petBreed','petGender','petDescription']
        widgets = {
            'petName': forms.TextInput(attrs={'class':'form-control mb-3'}),
            'petSpecies': forms.Select(attrs={'class':'form-select mb-3'}),
            'petBreed': forms.Select(attrs={'class':'form-select mb-3'}),
            'petGender': forms.Select(attrs={'class':'form-select mb-3'}),
            'petDescription': forms.Textarea(attrs={'class':'form-control mb-3', 'placeholder':'''Spune-ne ceva despre animalul tau de companie: temperament, obiceiuri, intamplari...
Poti relata din perspectiva ta sau din perspectiva lui. 😀'''}),
            'petPhoto': forms.FileInput(attrs={'class':'d-none','id':'id_image'}),
        }

    def __init__(self, *args, **kwargs):
        super(PetProfileCreateForm, self ).__init__(*args, **kwargs)
        self.fields['delete_image'] = forms.NullBooleanField(widget=forms.HiddenInput())
        self.fields['petBreed'].queryset = Breed.objects.none()
        if 'petSpecies' in self.data:
            try:
                species_id = int(self.data.get('petSpecies'))
                self.fields['petBreed'].queryset = Breed.objects.filter(species=species_id).order_by('breed_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            print('in elif')
            self.fields['petBreed'].queryset = self.instance.petSpecies.breed_set.order_by('breed_name')


class PetProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = PetProfile
        fields = ['petPhoto','petName','petSpecies','petBreed','petGender','petDescription']
        widgets = {
            'petName': forms.TextInput(attrs={'class':'form-control mb-3'}),
            'petSpecies': forms.Select(attrs={'class':'form-select mb-3'}),
            'petBreed': forms.Select(attrs={'class':'form-select mb-3'}),
            'petGender': forms.Select(attrs={'class':'form-select mb-3'}),
            'petDescription': forms.Textarea(attrs={'class':'form-control mb-3'}),
            'petPhoto': forms.FileInput(attrs={'class':'d-none','id':'id_image'}),
        }
    
    def __init__(self, *args, **kwargs):
        super(PetProfileUpdateForm, self ).__init__(*args, **kwargs)
        self.fields['delete_image'] = forms.NullBooleanField(widget=forms.HiddenInput())
        self.fields['petBreed'].queryset = Breed.objects.none()
        if 'petSpecies' in self.data:
            try:
                species_id = int(self.data.get('petSpecies'))
                self.fields['petBreed'].queryset = Breed.objects.filter(species=species_id).order_by('breed_name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['petBreed'].queryset = self.instance.petSpecies.breed_set.order_by('breed_name')