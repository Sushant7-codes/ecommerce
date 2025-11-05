# import django_filters
# from accounts.models import CustomUser

# class StaffFilter(django_filters.FilterSet):
#     class Meta:
#         model = CustomUser
#         fields = {
#             'first_name': ['icontains'],
#             'last_name': ['icontains'],
#             'phone_number': ['icontains'],
#             'address': ['icontains'],
#             'username': ['icontains'],
#             'email': ['icontains'],
#         }

import django_filters
from accounts.models import CustomUser
from django import forms

class StaffFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='First Name',
        widget=forms.TextInput(attrs={'placeholder': 'Search first name...'})
    )
    last_name = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Last Name',
        widget=forms.TextInput(attrs={'placeholder': 'Search last name...'})
    )
    phone_number = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Phone Number',
        widget=forms.TextInput(attrs={'placeholder': 'Search phone...'})
    )
    address = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Address',
        widget=forms.TextInput(attrs={'placeholder': 'Search address...'})
    )
    username = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Username',
        widget=forms.TextInput(attrs={'placeholder': 'Search username...'})
    )
    email = django_filters.CharFilter(
        lookup_expr='icontains',
        label='Email',
        widget=forms.TextInput(attrs={'placeholder': 'Search email...'})
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'address', 'username', 'email']