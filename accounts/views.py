import json
from datetime import datetime,time
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.db.models import Count
from django.contrib import messages
from accounts.models import Job,Profile,JobApplication,Payment,Meeting,EmloyeeWork


def employer_dashboard(request):
    current_user = request.user
    employer = Profile.objects.get(user=current_user)
    job_count = Job.objects.filter(employer=employer,is_deleted=False).count()
    applications = JobApplication.objects.filter(job__employer=employer,).order_by('-applied_date')[:7]
    shorlisted_count = JobApplication.objects.filter(job__employer=employer, application_status='shortlisted').count()

    context = {
        'current_user' : current_user,
        'job_count' : job_count,
        'applications' : applications,
        'applications_count' : applications.count(),
        'shorlisted_count' : shorlisted_count
    }
    return render(request,'employer/employer-dashboard.html',context)


def employer_meeting(request):
    current_user = request.user

    employees = JobApplication.objects.filter(job__employer__user=current_user,application_status="shortlisted")
    meetings = Meeting.objects.filter(created_by__user=current_user)
    context = {
        'current_user' : current_user,
        'employees' : employees,
        'meetings' : meetings
    }
    
    return render(request,'employer/employer-meeting.html',context)


def create_meeting(request):
    current_user = request.user
    employee_id = request.POST.get('employee_id')
    meet_date = request.POST.get('meet_date')
    link = request.POST.get('link')

    employee = Profile.objects.get(id=employee_id)
    created_by = Profile.objects.get(user=current_user)
        
    new_meeting = Meeting.objects.create(
                profile = employee,
                meet_date = meet_date,
                link = link,
                created_by = created_by
            )

    context = {
        'current_user' : current_user
    }

    # return render(request,'employer/employer-meeting.html',context)
    return redirect('employer_meeting')


def employee_meeting(request):
    current_user = request.user

    meetings = Meeting.objects.filter(profile__user=current_user)
    context = {
        'current_user' : current_user,
        'meetings' : meetings
    }
    return render(request,'employee/employee-meeting.html',context)


def employee_work(request):
    current_user = request.user

    employee_works = EmloyeeWork.objects.filter(uploaded_by__user=current_user)
    employers = Profile.objects.filter(role="employer")

    context = {
        'current_user' : current_user,
        'employee_works' : employee_works,
        'employers' : employers,
    }
    return render(request,'employee/employee-work.html',context)


def employer_work(request):
    current_user = request.user

    employer_works = EmloyeeWork.objects.filter(uploaded_for__user=current_user)

    context = {
        'current_user' : current_user,
        'employer_works' : employer_works,
    }
    return render(request,'employer/employer-work.html',context)


def admin_work(request):
    current_user = request.user

    admin_works = EmloyeeWork.objects.all()

    context = {
        'current_user' : current_user,
        'admin_works' : admin_works,
    }
    return render(request,'admin/admin-work.html',context)

def upload_work(request):
    print("dxfhjopiutydsrdyhijo;lythdtfhjo;gtdhfyhijoj;ggchgjo;")
    current_user = request.user
    employer=""
    
    uploaded_by = Profile.objects.get(user=current_user)

    title = request.POST.get('title')
    description = request.POST.get('description')
    work = request.POST.get('document')
    title = request.POST.get('title')
    employer_id = request.POST.get('employer')

    if Profile.objects.filter(id=employer_id).exists():
        employer = Profile.objects.get(id=employer_id)

    EmloyeeWork.objects.create(
        uploaded_by = uploaded_by,
        title = title,
        description = description,
        work = work,
        uploaded_for = employer
    )
    
    return redirect('employee_work')


def admin_meeting(request):
    current_user = request.user

    meetings = Meeting.objects.all()
    context = {
        'current_user' : current_user,
        'meetings' : meetings
    }
    return render(request,'admin/admin-meeting.html',context)


def get_recent_application_update(request):
    if request.method == 'GET':
        application_id = request.GET.get('id')
        try:
            job_application = JobApplication.objects.get(id=application_id)
            job_application.application_status = "shortlisted"
            job_application.save()

            formatted_applied_date = datetime.strftime(job_application.applied_date, '%d/%m/%Y')

            job_applications_details = {
                'name' : job_application.profile.name,
                'about' : job_application.about,
                'applied_date' : formatted_applied_date,
            }
            return JsonResponse(job_applications_details)
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def update_application_reject(request):
    if request.method == 'GET':
        application_id = request.GET.get('id')
        try:
            job_application = JobApplication.objects.get(id=application_id)
            job_application.application_status = "rejected"
            job_application.save()

            return JsonResponse({"status": "success"})
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)


def get_payment_details(request):
    if request.method == 'GET':
        application_id = request.GET.get('id')
        try:
            job_application = JobApplication.objects.get(id=application_id)
            formatted_applied_date = datetime.strftime(job_application.applied_date, '%d/%m/%Y')
            if Payment.objects.filter(job_application=job_application).exists():
                payment = Payment.objects.get(job_application=job_application)

                payment_name = payment.profile.name
                payment_upi = payment.upi_number
                payment_ifsc = payment.ifsc_number
                total_amount = payment.amount

            else:
                payment_name = "No data found"
                payment_upi = "No data found"
                payment_ifsc = "No data found"
                total_amount = "No data found"

            job_applications_details = {
                'name' : job_application.profile.name,
                'employer_name' : job_application.job.employer.name,
                'about' : job_application.about,
                'applied_date' : formatted_applied_date,
                'work_status' : job_application.work_status,
                'payment_name' : payment_name,
                'payment_upi' : payment_upi,
                'payment_ifsc' : payment_ifsc,
                'total_amount' : total_amount,

            }

            return JsonResponse(job_applications_details)
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def edit_payment_details(request):
    if request.method == 'POST':

        viewPaymentName = request.POST.get('viewPaymentName')
        viewPaymentUPINumber = request.POST.get('viewPaymentUPINumber')
        viewPaymentIFSCNumber = request.POST.get('viewPaymentIFSCNumber')
        viewPaymentInstanceId = request.POST.get('viewPaymentInstanceId')

        if Payment.objects.filter(id=viewPaymentInstanceId):
            payment_instance = Payment.objects.get(id=viewPaymentInstanceId)

            payment_instance.upi_number = viewPaymentUPINumber
            payment_instance.ifsc_number = viewPaymentIFSCNumber
            payment_instance.save()

            return redirect('employee_application')
        
        return redirect('employee_application')
    
    return redirect('employee_application')

def edit_payment_details_dashboard(request):
    if request.method == 'POST':

        viewPaymentName = request.POST.get('viewPaymentName')
        viewPaymentUPINumber = request.POST.get('viewPaymentUPINumber')
        viewPaymentIFSCNumber = request.POST.get('viewPaymentIFSCNumber')
        viewPaymentInstanceId = request.POST.get('viewPaymentInstanceId')

        if Payment.objects.filter(id=viewPaymentInstanceId):
            payment_instance = Payment.objects.get(id=viewPaymentInstanceId)

            payment_instance.upi_number = viewPaymentUPINumber
            payment_instance.ifsc_number = viewPaymentIFSCNumber
            payment_instance.save()

            return redirect('employee_dashboard')
        
        return redirect('employee_dashboard')
    
    return redirect('employee_dashboard')

def make_payment(request):
    if request.method == 'POST':
        application_id = request.POST.get('applicationId')
        selected_payment_method = request.POST.get('selected_payment_method')
        amount_str = request.POST.get('amount')
        amount = float(amount_str)

        try:
            job_application = JobApplication.objects.get(id=application_id)
            payment_detail = Payment.objects.get(job_application=job_application)

            payment_detail.payment_method = selected_payment_method
            payment_detail.amount = payment_detail.amount + amount
            payment_detail.payment_status = "success"
            payment_detail.save()

            return JsonResponse({'status': 'success',"StatusCode":6000})
        except (JobApplication.DoesNotExist, Payment.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': str(e),"StatusCode":6001})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def payment_details(request):
    if request.method == 'POST':
        application_id = request.POST.get('paymentDetailId')
        # payment_name = request.POST.get('paymentName')
        payment_upi_number = request.POST.get('paymentAccountNumber')
        payment_ifsc = request.POST.get('paymentIFSC')
        
        try:
            job_application = JobApplication.objects.get(id=application_id)
            new_payment = Payment.objects.create(

                profile = job_application.profile,
                upi_number = payment_upi_number,
                ifsc_number = payment_ifsc,
                job_application = job_application
            )

            return JsonResponse({'status': 'success',"StatusCode":6000})
        except (JobApplication.DoesNotExist, Payment.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': str(e),"StatusCode":6001})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


def get_view_payment_details(request):
    if request.method == 'GET':
        current_user = request.user
        job_application_id = request.GET.get('id')
        try:
            job_application = JobApplication.objects.get(id=job_application_id)
            payment_details = Payment.objects.get(job_application=job_application)
            paymentDetails = {
                'name' : payment_details.profile.name,
                'upi_number' : payment_details.upi_number,
                'ifsc_number' : payment_details.ifsc_number,
                'payment_id' : payment_details.id
            }
            return JsonResponse(paymentDetails)
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def work_status_update(request):
    if request.method == 'POST':
        application_id = request.POST.get('employeeHiddenInput')
        current_work_status = request.POST.get('currentJobStatusView')

        print(current_work_status,"current_work_status")
        
        try:
            job_application = JobApplication.objects.get(id=application_id)
            
            job_application.work_status = current_work_status
            job_application.save()

            return redirect('employee_application')
        except (JobApplication.DoesNotExist, Payment.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    

def work_status_update_dashboard(request):
    if request.method == 'POST':
        application_id = request.POST.get('employeeHiddenInput')
        current_work_status = request.POST.get('currentJobStatusView')

        print(current_work_status,"current_work_status")
        
        try:
            job_application = JobApplication.objects.get(id=application_id)
            
            job_application.work_status = current_work_status
            job_application.save()

            return redirect('employee_dashboard')
        except (JobApplication.DoesNotExist, Payment.DoesNotExist) as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    

def employer_job(request):
    current_user = request.user
    employer = Profile.objects.get(user=current_user)
    jobs = Job.objects.filter(employer=employer,is_deleted=False).annotate(received_count=Count('applications'))
    # posted_jobs = jobs.count()

    context = {
        'current_user' : current_user,
        'jobs' : jobs,
    }
    return render(request,'employer/employer-job.html',context)


def employer_application(request):
    current_user = request.user
    employer = Profile.objects.get(user=current_user)
    applications = JobApplication.objects.filter(job__employer=employer)

    context = {
        'current_user' : current_user,
        'applications' : applications
    }
    return render(request,'employer/employer-application.html',context)


def employee_dashboard(request):
    current_user = request.user
    employee = Profile.objects.get(user=current_user)
    applied_jobs = JobApplication.objects.filter(profile=employee).order_by('applied_date')[:7]
    pending_jobs_count = JobApplication.objects.filter(profile=employee,application_status='pending').count()
    shortlisted_jobs_count = JobApplication.objects.filter(profile=employee,application_status='shortlisted').count()

    context = {
        'current_user' : current_user,
        'applied_jobs' : applied_jobs,
        'applied_jobs_count' : applied_jobs.count(),
        'pending_jobs_count' : pending_jobs_count,
        'shortlisted_jobs_count' : shortlisted_jobs_count
    }
    return render(request,'employee/employee-dashboard.html', context)


def employee_job(request):
    current_user = request.user
    jobs = Job.objects.filter(is_closed=False,is_deleted=False,)

    context = {
        'current_user' : current_user,
        'jobs' : jobs
    }
    return render(request,'employee/employee-job.html',context)


def employee_application(request):
    current_user = request.user
    employee = Profile.objects.get(user=current_user)
    applied_jobs = JobApplication.objects.filter(profile=employee)

    context = {
        'current_user' : current_user,
        'applied_jobs' : applied_jobs,
    }
    return render(request,'employee/employee-application.html',context)


def create_job(request):
    if request.method == 'POST':    
        current_user = request.user
        title = request.POST.get('title')
        description = request.POST.get('description')
        requirements = request.POST.get('requirements')
        opening_date = request.POST.get('opening-date')
        closing_date = request.POST.get('closing-date')
        no_of_openings = request.POST.get('openings')
        created_date = datetime.now()
        is_closed = False
        is_deleted = False
        employer = Profile.objects.get(user=current_user)

        opening_datetime = datetime.strptime(opening_date, '%Y-%m-%d')  # Assuming opening_date format is YYYY-MM-DD
        closing_datetime = datetime.strptime(closing_date, '%Y-%m-%d')  # Assuming closing_date format is YYYY-MM-DD

        # Set default time if not provided
        default_time = time(0, 0)  # midnight

        opening_datetime = datetime.combine(opening_datetime.date(), default_time)
        closing_datetime = datetime.combine(closing_datetime.date(), default_time)

        new_job = Job.objects.create (
            title = title,
            description = description,
            requirements = requirements,
            opening_date = opening_datetime,
            closing_date = closing_datetime,
            no_of_openings = no_of_openings,
            created_date = created_date,
            is_closed = is_closed,
            is_deleted = is_deleted,
            employer = employer
        )

        return redirect('employer_job')


def get_job_details(request):
    current_user = request.user
    
    if request.method == 'GET':
        job_id = request.GET.get('id')
        if Job.objects.filter(id=job_id).exists():
            job = Job.objects.get(id=job_id)
            received_number = JobApplication.objects.filter(job=job).count()
            shortlisted_number = JobApplication.objects.filter(job=job, application_status='shortlisted').count()
            rejected_number = JobApplication.objects.filter(job=job, application_status='rejected').count()

            is_applied = job.applications.filter(profile__user = current_user).exists()

            # if Job.objects.filter(id=job_id,job__applications__profile__user=current_user).exists():
            #     print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

            job_details = {
                'title': job.title,
                'description': job.description,
                'requirements': job.requirements.split('\n') ,
                'received_number': received_number,
                'shortlisted_number' : shortlisted_number,
                'rejected_number' : rejected_number,
                'is_applied' : is_applied,   
            }
            return JsonResponse(job_details)
        else:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def get_job_application_details(request):
    if request.method == 'GET':
        job_application_id = request.GET.get('id')
        amount = 0
        try:
            job_application = JobApplication.objects.get(id=job_application_id)

            print(job_application.work_status,"job_application.work_status")

            if Payment.objects.filter(job_application=job_application).exists():
                current_payment = Payment.objects.get(job_application=job_application)
                amount = current_payment.amount
                button_status = "view"
            else:
                button_status = "add"

            formatted_applied_date = datetime.strftime(job_application.applied_date, '%d/%m/%Y')

            job_applications_details = {
                'name' : job_application.profile.name,
                'title': job_application.job.title,
                'description': job_application.job.description,
                'requirements': job_application.job.requirements.split('\n'),
                'applied_date' : formatted_applied_date,
                'status' : job_application.application_status,
                'work_status' : job_application.work_status,
                'button_status' : button_status,
                'amount' : amount,
            }
            return JsonResponse(job_applications_details)
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def download_resume(request):
    job_application_id = request.GET.get('id')
    job_application = get_object_or_404(JobApplication, id=job_application_id)
    response = FileResponse(open(job_application.resume.path, 'rb'))
    return response


def update_employer_job_details(request):
    if request.method == 'GET':
        job_application_id = request.GET.get('id')
        try:
            job_application = JobApplication.objects.get(id=job_application_id)

            # Assuming you have fields title, description, and requirements in your Job model
            job_applications_details = {
                'applied_date' : job_application.applied_date,
                # 'resume' : job_application.resume
                'about' : job_application.about,
                'name' : job_application.profile.name
            }
            return JsonResponse(job_applications_details)
        except Job.DoesNotExist:
            return JsonResponse({'error': 'Job not found'}, status=404)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=405)
    

def apply_employee_job(request):

    current_user = request.user
    current_datetime = timezone.now()
    about = request.POST.get('about')
    resume = request.FILES.get('file')
    job_id = request.POST.get('job_id')
    application_status = 'pending'
    
    job = Job.objects.get(id=job_id)
    applied_position = Job.objects.get(id=job_id)
    profile =Profile.objects.get(user=current_user)

    if JobApplication.objects.filter(job=job,profile__user=current_user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('employee_job')
    
    new_job_application = JobApplication.objects.create(
        about = about,
        resume = resume,
        profile = profile,
        job = job,
        applied_date=current_datetime,
        application_status=application_status
    )

    return redirect('employee_job')
    

        
def edit_employer_project(request):
    
    current_user = request.user
    title = request.POST.get('title')
    description = request.POST.get('description')
    requirements = request.POST.get('requirements')
    job_id = request.POST.get('jobApplicationId')

    job_application = Job.objects.get(id=job_id)

    job_application.title = title
    job_application.description = description
    job_application.requirements = requirements

    job_application.save()

    return redirect('employer_job')


def edit_admin_project(request):
    
    current_user = request.user
    title = request.POST.get('title')
    description = request.POST.get('description')
    requirements = request.POST.get('requirements')
    job_id = request.POST.get('jobApplicationId')

    job_application = Job.objects.get(id=job_id)

    job_application.title = title
    job_application.description = description
    job_application.requirements = requirements

    job_application.save()

    return redirect('admin_job')


def update_application_status(request):
    if request.method == "GET":
        job_application_id = request.GET.get("id")
        status = request.GET.get("status")  # Get the status parameter from the request
        try:
            job_application = JobApplication.objects.get(pk=job_application_id)
            # Update application status based on the value of the 'status' parameter
            if status == "rejected":
                job_application.application_status = "rejected"
            else:
                job_application.application_status = "shortlisted"
            job_application.save()
            return JsonResponse({"status": "success"})
        except JobApplication.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Job application not found"}, status=404)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


def delete_employer_project(request):
    if request.method == "POST":
        job_application_id = request.POST.get('deleteId')
        job_application = Job.objects.get(pk=job_application_id)
        job_application.is_deleted = True
        job_application.save()

    return redirect('employer_job')

def delete_admin_project(request):
    if request.method == "POST":
        job_application_id = request.POST.get('deleteId')
        job_application = Job.objects.get(pk=job_application_id)
        job_application.is_deleted = True
        job_application.save()

    return redirect('admin_job')


def cancel_url(request):
    return redirect('employer_job')


def admin_dashboard(request):
    current_user = request.user
    job_count = Job.objects.filter(is_deleted=False).count()
    applications = JobApplication.objects.all().order_by('-applied_date')[:3]
    applications_count = JobApplication.objects.all().count()
    pending_requests_count = JobApplication.objects.filter(application_status="pending").count()
    total_hired_count = JobApplication.objects.filter(application_status="shortlisted").count()
    jobs = Job.objects.filter(is_deleted=False)[:2]

    context = {
        'current_user' : current_user,
        'job_count' : job_count,
        'applications' : applications,
        'applications_count' : applications_count,
        'pending_requests_count' : pending_requests_count,
        'total_hired_count' : total_hired_count,
        'jobs' : jobs,
    }
    
    return render(request,'admin/admin-dashboard.html',context)


def admin_job(request):
    current_user = request.user
    employer = Profile.objects.get(user=current_user)
    jobs = Job.objects.filter(is_deleted=False)
    context = {
        'current_user' : current_user,
        'jobs' : jobs,
    }
    return render(request,'admin/admin-job.html',context)


def admin_application(request):
    current_user = request.user
    employer = Profile.objects.get(user=current_user)
    applications = JobApplication.objects.all()

    context = {
        'current_user' : current_user,
        'applications' : applications
    }
    return render(request,'admin/admin-application.html',context)