from django.contrib import admin
from .models import (Flight, Carrier, Airport)

admin.site.register(Flight)
admin.site.register(Carrier)
admin.site.register(Airport)
