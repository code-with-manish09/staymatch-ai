from django.contrib import admin
from .models import FlatmateInquiry, Message

admin.site.register(Message)
admin.site.register(FlatmateInquiry)