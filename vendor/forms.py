from django import forms
from vendor.models import Vendor


class VendorForm(forms.ModelForm):
    class Meta:
        model = Vendor
        fields = ['vendor_name', 'vendor_license']


    def clean(self):
        cleaned_data = super(VendorForm, self).clean()
        