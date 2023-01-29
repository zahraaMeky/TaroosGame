import json
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from .models import extend_user
from django.urls import reverse
from . models import *
import requests
import random
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import string
import secrets
from datetime import date
from dateutil.relativedelta import relativedelta

global Today
Today = date.today()


# Restrict access index page without login
def GenerateSessionKey():
    alphabet = string.ascii_letters + string.digits
    sess_key = ''.join(secrets.choice(alphabet) for i in range(8))
    return sess_key

@login_required(login_url='login')
def homePage(request):
    if request.user.is_authenticated:
        current_user = request.user.id
        getUserId = extend_user.objects.get(user_id=current_user)
        print('getUserId -----------------', getUserId)
        print('getUserId.is_login ', getUserId.is_login)
        print('current_user from homePage', current_user)
        if getUserId.is_login == 1:
            return render(request, 'pages/index.html')
        else:
            return redirect('logout')
    else:
        return redirect('login')


def GamePage(request):
    if request.user.is_authenticated:
        return render(request, 'pages/game.html')
    else:
        return redirect('login')


def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if request.user.is_authenticated:
            print("is_authenticated: Yes")
        else:
            print("is_authenticated: No")

        user = authenticate(request,username=username,password=password)
        if user is not None:
            print('userID',user.id)
            checksubscripttion =UserSubscription.objects.get(user=user.id) 
            subscripttionStatusb=checksubscripttion.active
            if subscripttionStatusb == 1:
                login(request, user)
                current_user = request.user.id
                print(current_user)
                retrieve_obj_id = extend_user.objects.filter(user_id=current_user)
                print(retrieve_obj_id)
                retrieve_obj_islogin = retrieve_obj_id.values_list('is_login')
                print(retrieve_obj_islogin)
                if (retrieve_obj_islogin):
                    is_in = retrieve_obj_islogin[0][0]
                    if is_in == 0:
                        retrieve_obj_id.update(user_id=current_user, is_login=1)
                        print('is_in', is_in)
                        return redirect('index')
                    else:
                        messages.warning(request, 'You Are Already Login !')
                else:
                    u = extend_user()
                    u.user = user
                    u.is_login = 0
                    u.IP = ""
                    u.save()
                    return redirect('password')
            else:return render(request, 'user/endSubscription.html')
    return render(request, 'user/login.html')


def logoutPage(request):
    current_user = request.user.id
    print('current_user',current_user)
    retrieve_obj_id = extend_user.objects.filter(user_id=current_user)
    print('retrieve_obj_id',retrieve_obj_id)
    try:
        if (retrieve_obj_id):
            retrieve_obj_id.update(user_id=current_user, is_login=0,IP='')
            retrieve_obj_islogin = retrieve_obj_id.values_list('is_login')
            if (retrieve_obj_islogin):
                is_in = retrieve_obj_islogin[0][0]
                print(is_in)
    except:
        print("exception")
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def updatePassword(request):
    x = False
    if request.user.is_authenticated:
        if request.method == 'POST':
            current_user = request.user.id
            password1 = request.POST.get('updatepassword')
            password2 = request.POST.get('Confirmpassword')
              
            if password1 == "" or password2 == "":
                messages.warning(request, 'Password can not be empty')
                return render(request, 'user/password.html')
                    
            if len(password1) < 6 == "" or len(password2) < 6 and not x:
                    messages.warning(request, 'Password at least must consist of six characters')
                    return render(request, 'user/password.html')
                  
            if password1 == password2:
                user = User.objects.get(id=current_user)
                user.set_password(password1)
                user.save()
                print('update password')
                messages.warning(request, 'Password Updated Successfully')
                return redirect('logout')
                
            else:
                  messages.warning(request, 'Password Not Identical')
    

    return render(request, 'user/password.html')


def game(request):
    return render(request, 'taroos/full/index.html')


def checkBrowser(request):
    print('settings.SESSION_EXPIRE_AT_BROWSER_CLOSE',
          settings.SESSION_EXPIRE_AT_BROWSER_CLOSE)
    return settings.SESSION_EXPIRE_AT_BROWSER_CLOSE


def RegisterPage(request):
    plans = GamePlans.objects.all()
    context = {'plans': plans}
    return render(request, 'user/registerPlan.html',context)

def planDetails(request):
    if request.method == "POST":
        plan ={}
        planname = request.POST.get('pname')
        plantime = request.POST.get('pperiod')
        getPlan= GamePlans.objects.get(PlanName=planname)
        if plantime == "month":
            plan ={'id': getPlan.id,'name': getPlan.PlanName,'account': getPlan.PlanAccounts,'price': getPlan.PlanPrice,'time':'month'}
        if plantime == "year":
            plan ={'id': getPlan.id,'name': getPlan.PlanName,'account': getPlan.PlanAccounts,'price':  getPlan.Annual_Price,'time':'year'}
        
        context = {'plan':plan}
        print('planname - plantime',planname,plantime)
        return render(request, 'user/checkout.html',context)


def checkOut(request):
    if request.method == "POST":
        global planID,planTime,UserName,UserEmail,UserPhone
        planName = request.POST.get('pname')
        planID = request.POST.get('pid')
        planTime = request.POST.get('ptime')
        price = int(request.POST.get('pprice'))
        unit_amount =price*1000
        UserName = request.POST.get('name')
        UserEmail = request.POST.get('email')
        UserPhone = request.POST.get('phone')
        print('planID',planID)
        url = "https://uatcheckout.thawani.om/api/v1/checkout/session"
        publishable_key = "HGvTMLDssJghr9tlN9gr4DVYt0qyBy"
        payload = {
            "mode": "payment",
            "products": [
                {
                    "name":planName,
                    "quantity": 1,
                    "unit_amount":unit_amount
                }
            ],
            "success_url": "http://127.0.0.1:8000/success",
            "cancel_url": "https://company.com/cancel",
            "save_card_on_success": 1,
            "metadata": {
                "Customer name": UserName,
            }
        }
        headers = {
            "Content-Type": "application/json",
            "thawani-api-key": "rRQ26GcsZzoEhbrP2HZvLYDbn9C9et"
        }

        response = requests.request("POST", url, json=payload, headers=headers)
        print(response.text)
        content = json.loads(response.text)
        session_id = content['data']['session_id']
        # content['data']['save_card_on_success'] = True
        print("session_id",session_id)
        NewURL =f"https://uatcheckout.thawani.om/pay/{session_id}?key={publishable_key}"
        return redirect(NewURL)

def generateUser():
        # user = UserName.split(maxsplit=1)
        number = '{:03d}'.format(random.randrange(1,999))
        username = UserName+str(number)
        print('generateUser',username)
        return username

def generatePassword():
    # choose from all lowercase letter
    letters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(letters) for i in range(8))
    # # print("Random string ", result_str)
    return result_str

def checkOutSucess(request):
    users =[]
    lastuser=[]
    print('planID',planID)
    getPlan= GamePlans.objects.get(id=planID)
    accountNum = getPlan.PlanAccounts
    for i in range(accountNum):
        username=generateUser()
        password = generatePassword()
        savePassword = password
        checkUser = User.objects.filter(username=username,email=UserEmail).exists()
        if(checkUser == False):
            user = User.objects.create_user(username=generateUser(),
                                    email=UserEmail,
                                    password=password)
            user.save()
            lstUser = User.objects.latest('id')
            lastUserID = lstUser.id 
            lastUserName= lstUser.username
            if lstUser is not None:
                lastuser.append({"index":i+1,'id':lastUserID,'username':lastUserName,"password":savePassword})
            print('lstUser',lstUser)
            ext_user = extend_user(user=lstUser, phone = UserPhone)  
            ext_user.save()
            if planTime == 'year':
               new_date = Today + relativedelta(years=1)
            if planTime == 'month':
               new_date = Today + relativedelta(months=1)

            sub_user = UserSubscription(user=lstUser,plan=getPlan,
            subscribeperiod=planTime,active= 1,
            createdDate=Today,expiredDate=new_date)  
            sub_user.save()
            users.append(lastUserID)
    msg = prepareMsg(lastuser)
    print('checkOutSucess',msg)
    checkSend= sendEmail(msg) 
    print('checkSend',checkSend)
    if checkSend:
        # return redirect('sucess')
        return render(request,'user/sucessRegister.html')
    return render(request, 'user/login.html')


def prepareMsg(lastuser):
    txt=f"""<p>you have {len(lastuser)} Accounts</p>"""
    for u in lastuser:
        txt+=f"""<p>Account {u['index']} :username {u['username']} && password {u['password']}</p>"""
    print('prepareMsg',txt)
    return txt


def sendEmail(msg):
    print('sendEmail',msg)
    sender_email = "eng.alzahraa.meky@gmail.com"
    receiver_email = UserEmail
    password = "wjontcqihhuqhknk"

    message = MIMEMultipart("alternative")
    message["Subject"] = "Taroos Game"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    Taroos Game:
    """
    html = f"""\
    <html>
    <body>
        <p>
        {msg}
        </p>
    </body>
    </html>
    """

    # Turn these into plain/html MIMEText objects
    part1 = MIMEText(text, "plain")
    part2 = MIMEText(html, "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(part1)
    message.attach(part2)

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        try:
            server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
            return True
        except Exception:
              return False
  

#this function run on backend
def CheckUserSubscription():
    subscriptions=UserSubscription.objects.all()
    for sub in subscriptions:
        if sub.expiredDate<Today:
            print('sub',sub.expiredDate)
            sub.active=0
            sub.save()
    print('CheckUserSubscription')
       

      
# Senario of Login
# Default value of is active is True
# make login
# check if is active == true
# change value of is active to false
# redirect to index
###########################################
# Senario of Logout
# change value of is active to true
# redirect to logout
@login_required(login_url='login')
def Profile(request):
    accounts = []
    current_user = request.user.id
    getUser= User.objects.get(id=current_user)
    print('current_user',current_user,getUser)
    useremail= getUser.email
    getAccounts= User.objects.filter(email=useremail)
    for account in getAccounts:
        accounts.append({'account':account.username})
    getplan= UserSubscription.objects.get(user=getUser)
    planid = getplan.plan_id
    subscribeperiod = getplan.subscribeperiod
    print('subscribeperiod',subscribeperiod)
    getplanName= GamePlans.objects.get(id=planid)
    planName = getplanName.PlanName
    PlanPrice = getplanName.PlanPrice
    if subscribeperiod == 'year':
        price = PlanPrice * 12
    if subscribeperiod == 'month':
        price = PlanPrice 
    print('current_user',current_user,getUser,useremail,'getplan',planName)
    userInfo={'currentLogin':getUser,'email':useremail,
    'AccountsNum':len(getAccounts),'PlanPrice':price,'subscribeperiod':subscribeperiod,
    'planName':planName}
    return render(request, 'user/profile.html',{'userInfo': userInfo,
    'accounts':accounts,
    'n' : range(len(getAccounts))})
