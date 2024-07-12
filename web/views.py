from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from accounts.models import Profile
from django.contrib.auth.models import User


def root_redirect(request):
    return render(request,'auth/login.html')

def initial_page(request):
    return redirect('/index/')


# def initial_page(request):
#     return redirect('index')


def index(request):
    return render(request,'index.html')


def login_view(request):
    message = ""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if Profile.objects.filter(user=user,role='employee').exists():
                role='employee'
                login(request,user)
                return redirect('employee_dashboard')
            elif Profile.objects.filter(user=user,role='employer').exists():
                role='employee'
                login(request,user)
                return redirect('employer_dashboard')
            elif Profile.objects.filter(user=user,role='admin').exists():
                role='admin'
                login(request,user)
                return redirect('admin_dashboard')
            else:
                message = 'user doesnt exist'
        else:
            message = 'enter valid details'

    context = {
        'message' : message
    }
    return render(request,'auth/login.html',context)

def register_employee(request):
    if request.method == 'POST':
        username = request.POST.get('name')
        phone_number = request.POST.get('number')
        email = request.POST.get('email')
        designation = request.POST.get('designation')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = User.objects.create_user(username=phone_number,password=password)

        new_profile = Profile.objects.create(
            name=username,
            phone_number=phone_number,
            email=email,
            designation=designation,
            password=password,
            role=role,
            user=user
        )
        return redirect('login')

    return render(request,'auth/register.html')

def logout_user(request):
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        message = f'Successfully logged out {username}.'
    else:
        message = 'No user was logged in.'
    return redirect('login')
