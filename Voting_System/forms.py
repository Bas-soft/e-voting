from django import forms

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Candidate,Voters

class AddCandidateForm(forms.ModelForm):
    class Meta:
        model = Candidate
        fields=["name","position","Candidate_Number","image"]
        '''widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),

        }
        labels = {
            'approved': 'Approved',

            # Add more fields and corresponding labels
        }'''

class AddVoters(forms.ModelForm):
    class Meta:
        model=Voters
        fields=["name","index_number"]