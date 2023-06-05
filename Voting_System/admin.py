from django.contrib import admin
from .models import Elections,Candidate,Votes,Portfolios,Voters

# Register your models here.
admin.site.register(Elections)
admin.site.register(Candidate)
admin.site.register(Votes)
admin.site.register(Portfolios)
admin.site.register(Voters)
