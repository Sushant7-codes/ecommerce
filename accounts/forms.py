from django import forms
from .models import CustomUser
# from django.forms import widgets as widget


class RetailAdminLoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Username",
            }
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Password",
            }
        )
    )


class RetailAdminRegisterForm(forms.Form):
    username = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Username",
            }
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Email",
            }
        )
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Password",
            }
        )
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Confirm Password",
            }
        )
    )
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "First Name",
            }
        ),
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Last Name",
            }
        ),
    )
    phone_number = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Phone",
            }
        ),
    )
    address = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "input w-full p-2 border border-gray-800",
                "placeholder": "Address",
            }
        ),
    )
    profile_pic = forms.ImageField(
    required=False,
    widget=forms.ClearableFileInput(
        attrs={
            "class": "block w-full text-sm text-gray-500 \
                      file:mr-4 file:py-2 file:px-4 \
                      file:rounded-full file:border-0 \
                      file:text-sm file:font-semibold \
                      file:bg-indigo-600 file:text-white \
                      hover:file:bg-indigo-700 cursor-pointer"
        }
    ),
)


    def clean(self):
        print(self.cleaned_data["password1"], self.cleaned_data["password2"])
        if self.cleaned_data["password1"] != self.cleaned_data["password2"]:
            raise forms.ValidationError("Passwords do not match")

    def save(self, commit=True):
        user = CustomUser(
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            phone_number=self.cleaned_data["phone_number"],
            address=self.cleaned_data["address"],
            profile_pic=self.cleaned_data["profile_pic"],
        )
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user