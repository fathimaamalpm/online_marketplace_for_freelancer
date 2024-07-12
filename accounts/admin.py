from django.contrib import admin
from accounts.models import Profile,Job,JobApplication,Payment,Meeting,EmloyeeWork

# Register your models here.
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name','role','phone_number','email','designation','password','user')
    search_fields = ['name']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title','is_closed','opening_date','is_deleted','employer')
    search_fields = ['title']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('job','applied_position','work_status','applied_date','application_status','profile','employer_name')
    search_fields = ['applied_position']

    def employer_name(self, obj):
        if obj.job and obj.job.employer:
            return obj.job.employer.name
        return None

    employer_name.short_description = 'Employer'

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('profile','payment_method','upi_number','payment_status','amount','job_application','ifsc_number')
    search_fields = ['profile']

@admin.register(Meeting)
class MeetinAdmin(admin.ModelAdmin):
    list_display = ('profile','meet_date','link','is_deleted','created_on')
    search_fields = ['profile']

@admin.register(EmloyeeWork)
class EmployeeWorkAdmin(admin.ModelAdmin):
    list_display = ('title','uploaded_by','uploaded_for','work','uploaded_on')
    search_fields = ['title']
