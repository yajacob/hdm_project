import os
import sys
from django import forms
sys.path.append( os.path.dirname(os.path.abspath(os.path.dirname(__file__))) )
from hdm.models import Hdm

class HdmForm(forms.ModelForm):
    class Meta:
        model = Hdm
        fields = ('hdm_objective', 'hdm_criteria', 'hdm_factors', 'hdm_alternatives',)

    # overriding for save method
"""
    def save(self, commit = True):
        hdm_design = super(HDMForm, self).save(commit = False)
        if commit:
            hdm_design.save()
        return hdm_design
"""