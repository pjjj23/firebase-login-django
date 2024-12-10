from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpRequest
from django.contrib import messages
import hashlib
from .firebase import auth_instance,db   
import time, threading
from django.utils import timezone
import random
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from .firebase import storage 
import uuid, math
import json
from django.views.decorators.csrf import csrf_exempt
import os, re
from uuid import uuid4
import requests
from datetime import datetime, timedelta
import logging
from django.urls import reverse
from django.core.mail import EmailMessage
from django.utils.html import strip_tags
from django.views import View
from collections import Counter

def home(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # Authenticate user with Firebase Authentication
            user = auth_instance.sign_in_with_email_and_password(email, password)
            user_id = user["localId"]

            # Fetch user data from Firebase to get the role
            user_data = db.child("users").child(user_id).get().val()

            if not user_data:
                messages.error(request, "User not found. Please log in again.")
                return redirect("home")

            role = user_data.get("role")  # Assuming 'role' is stored in the user data

            # Generate OTP
            otp = random.randint(100000, 999999)

            # Update user session details in Firebase without overwriting existing data
            db.child("users").child(user_id).update({
                "otp": otp,
                "email": email,
                "timestamp": time.time()
            })

            # Send OTP via email
            subject = "Your OTP for Login"
            message = f"Your OTP is: {otp}"
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            try:
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "OTP has been sent to your email.")
            except Exception as e:
                messages.error(request, f"Failed to send OTP email: {e}")
                return redirect("home")

            # Redirect based on the user's role
            if role == "user":
                return redirect(f"{reverse('OTPVerification')}?user_id={user_id}")
            elif role == "admin":
                return redirect(f"{reverse('OTPVerification')}?user_id={user_id}")
            else:
                messages.error(request, "Invalid role. Please contact support.")
                return redirect("home")
        except Exception:
            messages.error(request, "Invalid credentials. Please try again.")
            return redirect("home")

    return render(request, "index.html")




 
def OTPVerification(request):
    if request.method == "POST":
        input_otp = request.POST.get("otp")
        user_id = request.POST.get("user_id")

        if not user_id:
            messages.error(request, "User ID is missing. Please log in again.")
            return redirect("home")

        # Fetch session data from Firebase
        session_data = db.child("users").child(user_id).get().val()

        if not session_data:
            messages.error(request, "Session expired. Please log in again.")
            return redirect("home")

        # Check OTP
        if str(input_otp) == str(session_data.get("otp")):
            # Remove OTP field but keep the other user data
            updated_data = {k: v for k, v in session_data.items() if k != "otp"}
            db.child("users").child(user_id).set(updated_data)

            # Save user_id manually in the session
            request.session["user_id"] = user_id

            # Check role and redirect accordingly
            role = session_data.get("role")

            if role == "user":
                messages.success(request, "User logged in successfully.")
                return redirect("userhomepage")  # Redirect to user homepage
            elif role == "admin":
                messages.success(request, "Admin logged in successfully.")
                return redirect("adminhomepage")  # Redirect to admin homepage
            else:
                messages.error(request, "Invalid role. Please contact support.")
                return redirect("home")

        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect("OTPVerification")

    # For GET request, pass user_id to the template
    user_id = request.GET.get("user_id")
    if not user_id:
        messages.error(request, "User ID is missing. Please log in again.")
        return redirect("home")

    return render(request, "verify-to-login.html", {"user_id": user_id})




 




def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirmPassword")
        role = request.POST.get("role")

        # Validate input
        if len(username) < 4:
            messages.error(request, "Username must be at least 4 characters long")
            return redirect("signup")  # Replace "signup" with the name of your signup URL

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("signup")

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long")
            return redirect("signup")

        try:
            # Create user in Firebase Authentication
            user = auth_instance.create_user_with_email_and_password(email, password)

            # Save additional user info to Realtime Database
            user_id = user["localId"]
            db.child("users").child(user_id).set({
                "username": username,
                "email": email,
                "role": role,
            })

            # Success message
            messages.success(request, "User registered successfully")
            return redirect("home")  # Replace "home" with the name of your success page

        except Exception as e:
            error_message = str(e)
            messages.error(request, f"An error occurred: {error_message}")
            return redirect("signup")

    return render(request, "signup.html")

def userhomepage(request):
    # Check if the user is logged in by verifying the session
    user_id = request.session.get("user_id")
    if not user_id:
        messages.error(request, "Please log in to access your homepage.")
        return redirect("home")

    # Fetch user data from Firebase using the session user_id
    try:
        user_data = db.child("users").child(user_id).get().val()

        if not user_data:
            messages.error(request, "User data not found. Please log in again.")
            return redirect("home")

        # Pass the user data to the template
        return render(request, "userhomepage.html", {"user_data": user_data})
    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return redirect("home")




def logout_view(request):
    # Clear the session data
    request.session.flush()
    
    # Optionally, display a logout success message
    messages.success(request, "You have been successfully logged out.")
    
    # Redirect to the home page
    return redirect("home")   

def adminhomepage(request):
    try:
        # Fetch all user data from Firebase
        all_users = db.child("users").get().val()

        if not all_users:
            messages.error(request, "No users found in the database.")
            return render(request, "adminhomepage.html", {"users": []})

        # Pass the fetched data to the template
        return render(request, "adminhomepage.html", {"users": all_users})

    except Exception as e:
        messages.error(request, f"An error occurred: {e}")
        return render(request, "adminhomepage.html")
