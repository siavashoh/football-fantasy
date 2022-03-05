import re
import json
import requests

from django.contrib import auth
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from django.http.response import JsonResponse
from django.shortcuts import render, redirect
from django.template.response import TemplateResponse
from django.utils.encoding import force_bytes, force_text
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from home.models import Log
from .models import UserProfile

def log(title, message, data, is_what):
    if is_what == "is_info":
        log = Log.objects.create(title=title, message=message, data=data, is_info=True)
    elif is_what == "is_warning":
        log = Log.objects.create(title=title, message=message, data=data, is_warning=True)
    elif is_what == "is_error":
        log = Log.objects.create(title=title, message=message, data=data, is_error=True)
    log.save()


# func to send email for verification and reset password
def send_email(to, email_subject, email_body, called_func, request):
    try:
        email = EmailMessage(
            email_subject,
            email_body,
            settings.EMAIL_HOST_USER,
            to
        )
        email.send(fail_silently=False)
        data = json.dumps({"user":request.user.id, "where":{"app": "accounts", "view":called_func, "part":"send_email"}, "exception_message":"no exp"})
        log("success", "email send successfully", data, "is_info")
        return True
    except Exception as e:
        data = json.dumps({"user":request.user.id, "where":{"app": "accounts", "view":called_func, "part":"send_email"}, "exception_message":str(e)})
        log("exeption", "erorr while sending email", data,"is_error")
        return False


def signup(request):
    if request.user.is_authenticated:
        return redirect('onboard:onboard')
    email_regex = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$'
    phone_regex = '(\+?98|0)9\d{7}'
    errors = {
        'first_name': [],
        'last_name': [],
        'email': [],
        'phone_number': [],
        'password1': [],
        'password2': []
    }

    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['email']
        phone_number = request.POST['phone_number']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # form validation

        # 1. check first_name and last_name are more than 3 chars
        if len(first_name) < 3:
            errors['first_name'].append('نام باید بیشتر از 3 کاراکتر باشد.')

        if len(last_name) < 3:
            errors['last_name'] = [
                'نام خانوادگی باید بیشتر از 3 کاراکتر باشد.']

        # 2. check email is not empty and is valid form
        if email:
            if not re.match(email_regex, email):
                errors['email'] = ['آدرس ایمیل معتبر نمی‌باشد.']

            if User.objects.filter(email=email).exists():
                errors['email'] = ['این ایمیل قبلا ثبت نام کرده است.']
        else:
            errors['email'] = ['فیلد ایمیل خالی است.']

        # 3. check phone number validation
        if not re.match(phone_regex, phone_number):
            errors['phone_number'] = [
                'شماره موبایل معتبر نمی‌باشد، باید به صورت ۰۹۱۲۱۲۳۴۵۶۷ وارد کنید.']

        # 4. check password1 and password2 are not empty and be equal and more than 8 char
        if len(password1) < 8:
            errors['password1'] = ['رمز عبور باید حداقل 8 حرف یا عدد باشد.']

        if not password2:
            errors['password2'] = ['رمز عبور باید حداقل 8 حرف یا عدد باشد.']

        if password1 != password2:
            errors['password2'] = ['تکرار رمز با خود رمز عبور برابر نیست.']
        
        # check if there is an error just send error and do notting else push data in user table
        if sum([len(errors[key]) for key in errors]):
            data = {
                'errors': errors,
                'user_data': {
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'phone_number': phone_number,
                    'password1': '',
                    'password2': ''
                }
            }
            return TemplateResponse(request, 'accounts/signup.html', {'response': data})
        else:
            # if everything is ok create user and route to email verification page
            # user = User.objects.create_user(username='sia@hsn.com', password='123456789', email='sia@hsn.com', first_name='sia', last_name='hsn')
            # userprofile = UserProfile.objects.create(user, phone_number='09120535348')
            
            # check recapcha
            captcha_token=request.POST.get("g-recaptcha-response")
            cap_url="https://www.google.com/recaptcha/api/siteverify"
            cap_secret="6LcvJxYcAAAAADcCIaIUC16Qg-RvOWETI_iF6ydp"
            cap_data={"secret":cap_secret,"response":captcha_token}
            cap_server_response=requests.post(url=cap_url,data=cap_data)
            cap_json=json.loads(cap_server_response.text)

            if cap_json['success']==False:
                messages.error(request,"ریکپچا نامعتبر است. لطفا دوباره امتحان کنید.")
                return redirect("accounts:signup")
            try:
                user = User.objects.create_user(
                    username=username, password=password1, email=email, first_name=first_name, last_name=last_name)
                user.save()
                userprofile = UserProfile.objects.create(
                    user=user, phone_number=phone_number)
                userprofile.save()
                print('user created')
                auth.login(request, user)
                data = json.dumps({"user":request.user.id, "where":{"app": "accounts", "view":"sign_up", "part":"post->create user"}, "exception_message":"no exp"})
                log("signed-up", "user successfully signed up", data, "is_info")
                return redirect('accounts:verificationemail')
            except Exception as e:
                data = json.dumps({"user":email, "where":{"app": "accounts", "view":"sign_up", "part":"post->create user"}, "exception_message":str(e)})
                log("exeption", "erorr while create user", data,"is_error")
                return redirect('accounts:signup')
 
    else:
        return render(request, 'accounts/signup.html')


def login(request):
    if request.user.is_authenticated:
        return redirect('onboard:onboard')
    email_regex = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$'
    errors = {
        'email': [],
        'password1': [],
    }

    if request.method == 'POST':
        email = request.POST['email']
        password1 = request.POST['password1']

        # 1. check email is not empty and is valid form
        if email:
            if not re.match(email_regex, email):
                errors['email'] = ['آدرس ایمیل معتبر نمی‌باشد.']

            if not User.objects.filter(email=email).exists():
                errors['email'] = ['این ایمیل در سامانه موجود نمی باشد']
            else:
                user_auth = auth.authenticate(request, username=email, password=password1)
        else:
            errors['email'] = ['فیلد ایمیل خالی است.']

        # 2. check password1 are not empty and be equal and more than 8 char
        if len(password1) < 8:
            errors['password1'] = ['رمز عبور باید حداقل 8 حرف یا عدد باشد.']

        if User.objects.filter(email=email).exists():
            if user_auth is None:
                errors['password1'] = ['رمز اشتباه است.']
            else:
                userprofile = UserProfile.objects.get(user=user_auth)

        # check recapcha
        captcha_token=request.POST.get("g-recaptcha-response")
        cap_url="https://www.google.com/recaptcha/api/siteverify"
        cap_secret="6LcvJxYcAAAAADcCIaIUC16Qg-RvOWETI_iF6ydp"
        cap_data={"secret":cap_secret,"response":captcha_token}
        cap_server_response=requests.post(url=cap_url,data=cap_data)
        cap_json=json.loads(cap_server_response.text)
        
        # check if there is an error just send error and do notting else push data in user table
        if sum([len(errors[key]) for key in errors]):
            data = {
                'errors': errors,
                'user_data': {
                    'email': email,
                    'password1': '',
                }
            }
            return TemplateResponse(request, 'accounts/login.html', {'response': data})
        elif cap_json['success']==False:
            messages.error(request,"ریکپچا نامعتبر است. لطفا دوباره امتحان کنید.")
            return redirect("accounts:login")
        elif not userprofile.is_email_verified:
            # if user not verified his email redirect user to verifiactionemail page
            auth.login(request, user_auth)
            return redirect('accounts:verificationemail')
        else:
            auth.login(request, user_auth)
            return redirect('createteam:chooseleague', hello='0')
    else:
        # auth.logout(request)
        return render(request, 'accounts/login.html')


def verification_email(request):
    # check if user not verified route to verificationemail page
    user_is_verified = UserProfile.objects.get(user_id=request.user.id)
    user_is_verified = user_is_verified.is_email_verified
    if user_is_verified:
        return redirect('createteam:chooseleague', hello=0)
    # if send email button clicked 
    if request.method == "POST": 
        domain = get_current_site(request).domain

        uidb64 = urlsafe_base64_encode(force_bytes(request.user.pk))
        token = default_token_generator.make_token(request.user)

        link = reverse('accounts:ve_confirmation', kwargs={'uidb64': uidb64, 'token': token})
        activate_link = 'http://'+domain + link

        email_subject = 'تایید حساب فوتبال فانتزی'
        to = [request.user.email]

        email_body = 'باسلام. لطفا برای تایید ایمیل خود بر روی لینک زیر کلیک کنید.\n\n' + activate_link
        try:
            send_email(to, email_subject, email_body, "verification_email", request)
            return JsonResponse({'status':'true'}, status=200)
        except Exception as e:
            message = 'در هنگام ارسال ایمیل مشکلی پیش آمده است، لطفا دوباره امتحان کنید.'
            return JsonResponse({'status':'false','message':message}, status=500)
    if request.method == 'GET':
        return render(request, "accounts/verificationemail.html")
        

def ve_confirmation(request, uidb64, token):
    try:
        # decode urls uidb64 and token check if user are exist in db
        user_id = int(force_text(urlsafe_base64_decode(uidb64)))

        # check if user with decoded pk is exist
        if User.objects.filter(id=user_id).exists:
            user = User.objects.get(id=user_id)
            userprofile = UserProfile.objects.get(user=user)
        else:
            print('user not exist')
            return render(request, 'accounts/signup.html')

        # if this was False its mean user has already use the link
        if not default_token_generator.check_token(user, token):
            return render(request, 'accounts/login.html')

        # check if user verified or not
        if userprofile.is_email_verified:
            if request.user.is_authenticated:
                return redirect('createteam:chooseleague', hello="0")
            else:
                # if user was verified but not login route to login page
                return render(request, 'accounts/login.html')
        else:
            # if not verified make email veridied tag true and route to ve-confirmation
            userprofile.is_email_verified = True
            userprofile.save()
            auth.logout(request)
            return render(request, 'accounts/ve-confirmation.html', {'user_name': user.email})

    except Exception as e:
        print("ve-confirmation exception -----------> ", e)


def forgot_password(request):
    email_regex = '^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,24}))$'
    errors = {
        'email': [],
    }
    if request.method == 'POST':
        email = request.POST['email']

        # 1. check email is not empty and is valid form
        if email:
            if not re.match(email_regex, email):
                errors['email'] = ['آدرس ایمیل معتبر نمی‌باشد.']
            if not User.objects.filter(email=email).exists():
                errors['email'] = ['این ایمیل در سامانه موجود نمی باشد']
            else:
                user = User.objects.get(email=email)
        else:
            errors['email'] = ['فیلد ایمیل خالی است.']

        # check if there is an error just send error and do notting else push data in user table
        if sum([len(errors[key]) for key in errors]):
            data = {
                'errors': errors,
                'user_data': {
                    'email': email,
                }
            }
            return TemplateResponse(request, 'accounts/forgotpassword.html', {'response': data})
        else:
            # if there is not an error send reset password email
            
            # get domain
            domain = get_current_site(request).domain
            
            # generate hash with this user
            token = default_token_generator.make_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            link = reverse('accounts:reset_password', kwargs={'uidb64': uidb64, 'token': token})
            
            # create activate link with domain and token
            activate_link = 'http://'+ domain + link

            # email subject
            email_subject = 'فراموشی رمز عبور'
            
            # send to email passed by user
            to = [email]

            # email body
            email_body = 'با سلام. لطفا برای بازیابی رمز عبور خود بر روی لینک زیر کلیک کنید.\n\n' + activate_link
            
            # try to send email
            try:
                send_email(to, email_subject, email_body, "forgot_password", request)
                return redirect('accounts:fp_confirmation')
            except Exception:
                return render(request,'accounts/forgotpassword.html')
    else:
        return render(request,'accounts/forgotpassword.html')


def fp_confirmation(request):
    return render(request, 'accounts/fp-confirmation.html')


def reset_password(request, uidb64, token):
    try:
        # decode urls uidb64 and token check if user are exist in db
        user_id = int(force_text(urlsafe_base64_decode(uidb64)))

        # check if user with decoded pk is exist
        if User.objects.filter(id=user_id).exists:
            user = User.objects.get(id=user_id)
        else:
            return redirect('accounts:login')

        # if this was False its mean user has already use the link
        if not default_token_generator.check_token(user, token):
            return redirect('accounts:login')
    except Exception as e:
        data = json.dumps({"user":user_id, "where":{"app": "accounts", "view":"reset_password", "part":"first part line 339 to 349"}, "exception_message":str(e)})
        log("exeption", "erorr while reseting password", data,"is_error")
        return render(request, 'accounts/resetpassword.html')

    # form validation check
    errors = {
        'password1': [],
        'password2': []
    }

    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        # form validation

        # check password1 and password2 are not empty and be equal and more than 8 char
        if len(password1) < 8:
            errors['password1'] = ['رمز عبور باید حداقل 8 حرف یا عدد باشد.']

        if not password2:
            errors['password2'] = ['رمز عبور باید حداقل 8 حرف یا عدد باشد.']

        if password1 != password2:
            errors['password2'] = ['تکرار رمز با خود رمز عبور برابر نیست.']

        # check if there is an error just send error and do notting else push data in user table
        if sum([len(errors[key]) for key in errors]):
            data = {
                'errors': errors,
                'user_data': {
                }
            }
            return TemplateResponse(request, 'accounts/resetpassword.html', {'response': data})
        else:
            # if everything is ok create user and route to email verification page
            try:
                user.set_password(password1)
                user.save()
                data = json.dumps({"user":user_id, "where":{"app": "accounts", "view":"reset_password", "part":"change password"}, "exception_message":"no exp"})
                log("success", "password successfully saved", data,"is_info")
                return render(request, 'accounts/login.html')
            except Exception as e:
                data = json.dumps({"user":user_id, "where":{"app": "accounts", "view":"reset_password", "part":"change password"}, "exception_message":str(e)})
                log("exception", "error while resetting password", data,"is_error")
                return render(request, 'accounts/resetpassword.html')
    else:
        return render(request, 'accounts/resetpassword.html')


def rp_confirmation(request):
    return render(request, 'accounts/rp-confirmation.html')


def logout(request):
    auth.logout(request)
    return redirect('onboard:onboard')
