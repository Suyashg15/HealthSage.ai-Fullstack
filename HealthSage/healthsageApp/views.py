from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import pickle
from django.http import HttpResponseRedirect
# import joblib
import os
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from .dl_model import getResult, get_className
from django.utils.text import get_valid_filename
from .dl_model_DR import preprocess_image, class_name
from tensorflow.keras.models import load_model 
from .forms import SignUpForm,LoginForm
# Create your views here.
model1 = pickle.load(open('models/svm.pkl','rb'))
# model2 = 
# model = joblib.load('./models/svm.pkl')

def home(request):
    return render(request, 'index.html')

def diabetes(request):
    if request.method=='POST':
        pregnancies = request.POST['Pregnancies']
        glucose = request.POST['glucose']
        bp = request.POST['BP']
        skinthickness = request.POST['skinthickness']
        insulin = request.POST['insulin']
        bmi = request.POST['bmi']
        dpf = request.POST['DPF']
        age = request.POST['age']
        
        y_pred = model1.predict([[pregnancies,glucose,bp,skinthickness,insulin,bmi,dpf,age]])
        
        if y_pred[0]==1:
            y_pred = "Positive"
        else:
            y_pred = "Negative"
        
        return render(request,'diabetes.html',{'result' : y_pred})
        
    return render(request, 'diabetes.html')

@csrf_exempt
def pneumonia(request):
    if request.method == 'POST':
        file = request.FILES['file']
        filename = get_valid_filename(file.name)
        file_storage = FileSystemStorage()
        file_path = file_storage.save(filename, file)
        file_full_path = file_storage.path(file_path)
        
        value = getResult(file_full_path)
        result = get_className(value[0])
        
        file_storage.delete(file_path)
        
        return render(request, 'pneumonia.html', {'result': result})
    return render(request, 'pneumonia.html')
    
            

def DR(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        filename = get_valid_filename(file.name)
        file_storage = FileSystemStorage()
        file_path = file_storage.save(filename,file)
        file_full_path = file_storage.path(file_path)
        
        predicted_class = preprocess_image(file_full_path)
        result = class_name(predicted_class)
        # file_storage.delete(file_path)
        
        return render(request, 'DR.html', {'result': result})
    return render(request, 'DR.html')

# def breast_cancer(request):
#     if request.method=="POST":
        
def user_signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            messages.success(request,"CONGRATULATION, You are Registered!")
            form.save()
            # group = Group.objects.get(name = 'Author')
            # user.groups.add(group)
    else:
        form=SignUpForm()
    return render(request,'signup.html',{'form':form})

def user_login(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            form = LoginForm(request = request, data = request.POST)
            if form.is_valid():
                uname = form.cleaned_data['username']
                pwd = form.cleaned_data['password']
                user = authenticate(username=uname, password=pwd)
                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect('/signup/')
        else:
            form = LoginForm()
        return render(request, 'blog/login.html', {'form':form})
    else:
        return HttpResponseRedirect('/signup/')
    