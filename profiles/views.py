from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from PIL import Image, ImageOps

PROFILE_NAME = "Stephen Careg"          
MAX_MB = 3

AVATAR_DIR = Path(settings.MEDIA_ROOT) / "profile"
AVATAR_FILE = AVATAR_DIR / "avatar.jpg"


class AvatarForm(forms.Form):
    
    photo = forms.ImageField(error_messages={
        "invalid_image": "That file is not a valid image.",
        "required": "Choose a photo first.",
    })

    def clean_photo(self):
        photo = self.cleaned_data["photo"]
        if photo.size > MAX_MB * 1024 * 1024:
            raise forms.ValidationError(f"Image must be {MAX_MB} MB or smaller.")
        return photo


def profile(request):
    avatar_url = None
    if AVATAR_FILE.exists():
        
        version = int(AVATAR_FILE.stat().st_mtime)
        avatar_url = f"{settings.MEDIA_URL}profile/avatar.jpg?v={version}"

    return render(request, "profile.html", {
        "name": PROFILE_NAME,
        "avatar_url": avatar_url,
    })


@require_POST
def upload_avatar(request):
    
    form = AvatarForm(request.POST, request.FILES)

    if form.is_valid():
        image = Image.open(form.cleaned_data["photo"])
        image = ImageOps.exif_transpose(image).convert("RGB")   
        image.thumbnail((800, 800))                             
        AVATAR_DIR.mkdir(parents=True, exist_ok=True)
        image.save(AVATAR_FILE, "JPEG", quality=90)
        messages.success(request, "Profile picture updated.")
    else:
        for errors in form.errors.values():
            for error in errors:
                messages.error(request, error)

    return redirect("profile")