from django.contrib import admin
from vendor.models import Vendor

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'user_profile_address', 'is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name')
    list_editable = ('is_approved', )

    def user_profile_address(self, obj):
        return obj.user_profile.address
    
    user_profile_address.short_description = "Address"


admin.site.register(Vendor, VendorAdmin)
