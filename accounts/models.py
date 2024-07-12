from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User

PROFILE_ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employer', 'Employer'),
        ('employee', 'Employee'),
    )

JOB_APPLICATION_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('shortlisted', 'Selected'),
    ('rejected', 'Rejected'),
    )

JOB_APPLICATION_WORK_STATUS_CHOICES = (
    ('started', 'Started'),
    ('in_progress', 'In progress'),
    ('work_paused', 'Work Paused'),
    ('pending', 'Pending'),
    ('completed', 'Completed'),
)

PAYMENT_METHOD_CHOICES = (
    ('gpay','Gpay'),
    ('paypal','Paypal'),
    ('credit_card','Credit Card'),
)

PAYMENT_STATUS_CHOICES = (
    ('failed', 'Failed'),
    ('in_progress', 'In progress'),
    ('success', 'Succcess')
)

class Profile(models.Model):
    name = models.CharField(max_length=156)
    phone_number =  models.CharField(max_length=156)
    email = models.CharField(max_length=156)
    designation = models.CharField(max_length=156)
    password = models.CharField(max_length=156)
    role = models.CharField(choices=PROFILE_ROLE_CHOICES,null=True,blank=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    profile_image = models.ImageField(upload_to='profile_images/',null=True,blank=True)

    class Meta:
        db_table = 'accounts_profile'
        verbose_name = _('Profile')
        verbose_name_plural = _('Profile')
        ordering = ('name',)

    def __str__(self):
        return self.name
    

class Job(models.Model):
    title = models.CharField(max_length=156)
    description = models.TextField()
    requirements = models.TextField()
    created_date = models.DateTimeField(null=True, blank=True)
    opening_date =  models.DateTimeField(null=True,blank=True)
    closing_date = models.DateTimeField(null=True,blank=True)
    no_of_openings = models.IntegerField(null=True, blank=True)
    is_closed =  models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    employer = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True, blank=True )

    class Meta:
        db_table = 'accounts_Job'
        verbose_name = _('Job')
        verbose_name_plural = _('Jobs')
        ordering = ('title',)

    def __str__(self):
        return self.title
    

class JobApplication(models.Model):
    applied_position = models.CharField(max_length=256,null=True,blank=True)
    applied_date = models.DateTimeField(null=True,blank=True)
    application_status = models.CharField(choices=JOB_APPLICATION_STATUS_CHOICES,null=True,blank=True)
    job = models.ForeignKey(Job,on_delete=models.CASCADE,null=True,blank=True,related_name="applications")
    profile = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True,related_name="job_applications")
    about = models.TextField()
    resume = models.FileField(upload_to='resumes')
    work_status = models.CharField(choices=JOB_APPLICATION_WORK_STATUS_CHOICES,null=True,blank=True)

    class Meta:
        db_table = 'accounts_job_applications'
        verbose_name = _('Job apllication')
        verbose_name_plural = _('Job applications')
        ordering = ('job',)

    def __str__(self):
        return str(self.job)
    

class Payment(models.Model):
    profile = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True)
    payment_method  = models.CharField(choices=PAYMENT_METHOD_CHOICES,null=True,blank=True)
    upi_number = models.CharField(max_length=256,null=True,blank=True)
    ifsc_number = models.CharField(max_length=256,null=True,blank=True)
    amount = models.IntegerField(default=0)
    payment_status = models.CharField(choices=PAYMENT_STATUS_CHOICES,max_length=256,null=True,blank=True)
    job_application = models.ForeignKey('accounts.jobapplication',on_delete=models.CASCADE,null=True,blank=True)

    class Meta:
        db_table = 'accounts_payment'
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ('profile',)

    def __str__(self):
        return str(self.profile)
    

class Meeting(models.Model):
    profile = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True,related_name='profile_meetings')
    meet_date = models.DateTimeField(null=True,blank=True)
    link = models.CharField(max_length=700,null=True,blank=True)
    is_deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True,related_name='created_meetings')

    class Meta:
        db_table = 'accounts_meeting'
        verbose_name = _('Meeting')
        verbose_name_plural = _('Meetings')
        ordering = ('profile',)

    def __str__(self):
        return str(self.profile)
    

class EmloyeeWork(models.Model):
    uploaded_by = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True,related_name='uploaded_by')
    title = models.CharField(max_length=700,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    work = models.FileField(upload_to='employee-work,',null=True,blank=True)
    uploaded_for = models.ForeignKey('accounts.profile',on_delete=models.CASCADE,null=True,blank=True,related_name='uploaded_for')
    uploaded_on = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts_emloyee_work'
        verbose_name = _('Employee Work')
        verbose_name_plural = _('employee Works')
        ordering = ('title',)

    def __str__(self):
        return str(self.title)

    

