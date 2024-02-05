from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import FormView, UpdateView
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .import forms
from .import models
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views import View
from django. contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, EmailMultiAlternatives
# Create your views here.

class UserRegistrationView(FormView):
    template_name='user_registration.html'
    form_class=forms.UserRegistrationForm
    success_url= reverse_lazy('login')
    
    def form_valid(self, form):
        user= form.save()
        login(self.request, user)
        return super().form_valid(form)
    #shob thik thakle ashol function call hobe

class UserLoginView(LoginView):
    template_name='user_login.html'
    def get_success_url(self) -> str:
        return reverse_lazy('profile')
    
class UserLogoutView(LogoutView):
    def get_success_url(self):
        if self.request.user.is_authenticated:
            logout(self.request)
        
        return reverse_lazy('home')
    
class PasswordChange(View):
    def get(self, request):
        form= PasswordChangeForm(request.user)
        return render(request, 'PasswordChange.html',{'form': form},)
    
    def post(self, request):
        form= PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password Changed Successfully')
            update_session_auth_hash(request, request.user)
            
            
            message= render_to_string('PasswordEmail.html', {
                "user" : self.request.user,
            })
            
            send_email= EmailMultiAlternatives("Password Change Email",'', to=[self.request.user.email] )
            send_email.attach_alternative(message, 'text/html')
            send_email.send()
            
            return redirect('profile')  
        return render(request, 'PasswordChange.html',{'form': form},)    
    
    
# class ProfileView(UpdateView):
#     model= models.User
#     form_class=forms.UserUpdateForm
#     template_name='profile.html'
    
#     def get_success_url(self) -> str:
#         return reverse_lazy('profile')
    
class ProfileView(View):
    template_name= 'profile.html'
    
    def get(self, request):
        form= forms.UserUpdateForm(instance= self.request.user)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form= forms.UserUpdateForm(request.POST, instance= request.user)
        
        if form.is_valid():
            form.save()
            return redirect('profile')
        
        return render(request, self.template_name, {'form': form})

