from re import S
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from .forms import UserLoginForm, UserCreationForm, EditProfileForm, PasswordChangeForm, GetRestPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from youtube.models import VideoInfo
from wsgiref.util import FileWrapper
from django.core.files.storage import FileSystemStorage
import os
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from .tokens import generate_token


## start of account management views
def user_login(request):
    if request.user.is_authenticated:
        return redirect("home:index")
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            email = cd["email"]
            password = cd["password"]
            user = authenticate(request, email=email, password=password)
            # User.objects.filter(email=cd["email"])
            # if User.objects.filter(email=cd["email"]).exists() and user.is_active == False :
            #     messages.error(request, "Account with this email is not yet activated. Please hit the button and get the activation email", 'error')
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request, "you logged in successfully", "success")
                    return redirect("accounts:edit_profile")
                else:
                    messages.success(
                        request,
                        "Account is not active, you need to activate your account before login. An account activation link has been sent to your mailbox.",
                        "warning",
                    )
                    send_confirmation_link(user)
            else:
                messages.error(request, "username or password is wrong", "warning")
    else:
        form = UserLoginForm()
    context = {"form": form}
    return render(request, "accounts/registration/login.html", context)


def user_register(request):
    if request.user.is_authenticated:
        return redirect("home:index")
    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            # if User.objects.filter(email=cd["email"]):
            #     messages.error(request, "this email already exist! please try some other email or send reqeust for reset your password", "warning")
            user = User.objects.create_user(
                cd["email"], cd["full_name"], cd["password1"], cd["password2"]
            )
            messages.success(
                request,
                "Your Account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.",
                "warning",
            )

            # Welcome Email
            greeting_email(user)
            # send confirmation email for activating user account
            send_confirmation_link(user)
    else:
        form = UserCreationForm()
    context = {"form": form}
    return render(request, "accounts/registration/register.html", context)


def greeting_email(user):
    subject = "Welcome to PandaDL"
    message = f"Hello {user.full_name},\nWelcome to PandaDL,\nThank you for your visiting and join to your pandadl's family.\nWe have sent you a comfirmation email, please confirm your email address in order to activating your account"
    from_email = settings.EMAIL_HOST_USER
    to_list = [user.email]
    send_mail(subject, message, from_email, to_list, fail_silently=True)


# send confirmation email for activating user account
def send_confirmation_link(user):
    current_site = settings.SITE_URL
    confirm_email_subject = "Confirm your email @ pandadl"
    confirm_message = render_to_string(
        "accounts/registration/email_confirmation.html",
        {
            "name": user.full_name,
            "domain": current_site,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": generate_token.make_token(user),
        },
    )
    email = EmailMessage(
        confirm_email_subject, confirm_message, settings.EMAIL_HOST_USER, [user.email]
    )
    email.fail_silently = True
    email.send()


def user_activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your account successfully activated.", "success")
        login(request, user)
        return redirect("home:index")
    else:
        return render(request, "accounts/registration/activation_failed.html")


def user_logout(request):
    logout(request)
    messages.success(request, "you logged out from your account", "info")
    return redirect("home:index")


def edit_profile(request):
    if not request.user.is_active:
        send_confirmation_link(request.user)
    if request.method == "POST":
        profile_form = EditProfileForm(
            request.POST, request.FILES, instance=request.user
        )
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Your profile information was edited", "success")
            # messages.success(request, "Your Account has been successfully created. We have sent you a confirmation email, please confirm your email in order to activate your account.", "success")
            return redirect("accounts:edit_profile")
        else:
            messages.error(
                request,
                "There is a problem when editing profile, please try again",
                "warning",
            )
    else:
        profile_form = EditProfileForm(instance=request.user)
    context = {"profile_form": profile_form}
    return render(request, "accounts/registration/dashboard/profile.html", context)


def forget_password(request):
    if request.method == "POST":
        forgetpass_form = PasswordChangeForm(request.POST)
        if forgetpass_form.is_valid():
            email = request.POST["email"]
            if not User.objects.filter(email=email).first():
                messages.error(request, "Not user found with this Email", "danger")
                return redirect("accounts:forget_password")
            else:
                user = User.objects.filter(email=email).first()
                full_name = user.full_name
                current_site = settings.SITE_URL
                uid = urlsafe_base64_encode(force_bytes(user.pk))
                resetpass_email_subject = "Reset password @ PandaDL"
                resetpass_message = render_to_string(
                    "accounts/registration/forget_password/reset_password_email.html",
                    {
                        "name": user.full_name,
                        "domain": current_site,
                        "uid": uid,
                        "token": generate_token.make_token(user),
                    },
                )
                email = EmailMessage(
                    resetpass_email_subject,
                    resetpass_message,
                    settings.EMAIL_HOST_USER,
                    [user.email],
                )
                email.fail_silently = True
                email.send()
                messages.success(request,f"Dear {full_name}, we sent you email that you can reset your password with that, please check your inbox","success",)
                return redirect("accounts:forget_password")
    else:
        forgetpass_form = PasswordChangeForm()

    context = {'forgetpass_form': forgetpass_form}
    return render(request, "accounts/registration/forget_password/forget_password_get_email.html", context)


def change_password(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and generate_token.check_token(user, token):
        if request.method == "POST":
            send_passwords_form = GetRestPasswordForm(request.POST)
            if send_passwords_form.is_valid():
                new_password = request.POST["password1"]
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Your new password has been saved. You can now login to your account', 'success')
                return redirect('accounts:user_login')
        else:
            send_passwords_form = GetRestPasswordForm()
        
        context = {'send_passwords_form': send_passwords_form}
        return render(request, 'accounts/registration/forget_password/change_password_form.html', context)
            # if send_passwords_form.is_valid():
            #     print(user)
    #     user.is_active = True
    #     user.save()
    #     messages.success(request, "Your account successfully activated.", "success")
    #     login(request, user)
    #     return redirect("home:index")
    # else:
    #     return render(request, "accounts/registration/activation_failed.html")
    


# def forgot_password(request):
#     if request.method == "POST":
#         changepass_form = PasswordChangeForm(request.POST)
#         if changepass_form.is_valid():
#             email = request.POST["email"]
#         if not User.objects.filter(email=email).first():
#             messages.error(request, "Not user found with this Email", 'danger')
#             return redirect("accounts:user_reset_password")
#         else:
#             user = User.objects.filter(email=email).first()
#             current_site = settings.SITE_URL
#             resetpass_email_subject = "Reset password @ PandaDL"
#             resetpass_message = render_to_string("accounts/registration/password_change_email.html" ,{'name' : user.full_name, 'domain' : current_site,'uid' : urlsafe_base64_encode(force_bytes(user.pk)),'token': generate_token.make_token(user)})
#             email = EmailMessage(resetpass_email_subject, resetpass_message, settings.EMAIL_HOST_USER, [user.email])
#             email.fail_silently=True
#             email.send()

## end of account management views

## start downloading of video and audio file viwes


def downloads_all(request):
    all_file_downloaded = []
    videoinfo = VideoInfo.objects.filter(user=request.user).order_by("-created_on")
    for file in videoinfo:
        if file.video_is_downloaded:
            file_path = file.video_dl_link
            if os.path.exists(file_path):
                all_file_downloaded.append(file)

        if file.audio_is_downloaded:
            file_path = file.audio_dl_link
            if os.path.exists(file_path):
                if file not in all_file_downloaded:
                    all_file_downloaded.append(file)
    context = {"all_file_downloaded": all_file_downloaded}
    return render(request, "accounts/downloads/all_downloads.html", context)


def downloads_single_videos(request):
    single_video_list = []
    videoinfo = VideoInfo.objects.filter(
        user=request.user, video_is_downloaded=True, is_playlist=False
    )
    for video in videoinfo:
        if video.video_dl_link:
            video_file_path = video.video_dl_link
            if os.path.exists(video_file_path):
                single_video_list.append(video)
            else:
                video.video_dl_link = ""
                video.video_file_name = ""
                video.video_downloaded_resolution = ""
                video.video_is_downloaded = False
                video.save()
    context = {"single_video_list": single_video_list}
    return render(request, "accounts/downloads/single_videos.html", context)


def downloads_audios(request):
    audio_list = []
    videoinfo = VideoInfo.objects.filter(user=request.user, audio_is_downloaded=True)
    for audio in videoinfo:
        if audio.audio_dl_link:
            audio_file_path = audio.audio_dl_link
            if os.path.exists(audio_file_path):
                audio_list.append(audio)
            else:
                audio.audio_dl_link = ""
                audio.audio_file_name = ""
                audio.audio_downloaded_resolution = ""
                audio.audio_is_downloaded = False
                audio.save()
    context = {"audio_list": audio_list}
    return render(request, "accounts/downloads/audios.html", context)


def downloads_playlists(request):
    playlist_video = []
    videosinfo = VideoInfo.objects.filter(
        user=request.user, video_is_downloaded=True, is_playlist=True
    )
    for video in videosinfo:
        if video.video_dl_link:
            video_file_path = video.video_dl_link
            if os.path.exists(video_file_path):
                playlist_video.append(video)
            else:
                video.video_dl_link = ""
                video.video_file_name = ""
                video.video_downloaded_resolution = ""
                video.video_is_downloaded = False
                video.save()
    context = {"playlist_video": playlist_video}
    return render(request, "accounts/downloads/playlists.html", context)


def download_file(request, video_id, ext):
    video_info = VideoInfo.objects.get(video_id=video_id)
    file_link = ""
    file_name = ""
    if ext == "mp4":
        file_link = video_info.video_dl_link
        file_name = video_info.video_file_name
    elif ext == "mp3":
        file_link = video_info.audio_dl_link
        file_name = video_info.audio_file_name
    response = StreamingHttpResponse(
        FileWrapper(open(file_link, "rb")),
        content_type="mimetypes.guess_type(file_link)[0]",
    )
    response["Content-Length"] = os.path.getsize(file_link)
    response["Content-Disposition"] = "Attachment;filename=%s" % file_name
    return response


## end views of download file
