from django.contrib import admin
from vendor.models import Vendor, OpeningHour

class VendorAdmin(admin.ModelAdmin):
    list_display = ('user', 'vendor_name', 'user_profile_address', 'is_approved', 'created_at')
    list_display_links = ('user', 'vendor_name')
    list_editable = ('is_approved', )

    def user_profile_address(self, obj):
        return obj.user_profile.address
    
    user_profile_address.short_description = "Address"


class OpeningHourAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'day', 'from_hour', 'to_hour')

admin.site.register(Vendor, VendorAdmin)
admin.site.register(OpeningHour, OpeningHourAdmin)
