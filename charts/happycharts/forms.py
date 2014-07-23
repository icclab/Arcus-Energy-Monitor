# Copyright 2014 Zuercher Hochschule fuer Angewandte Wissenschaften
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from django import forms
from functools import partial

CHOICES = [('B', 'Server 1'),
           ('C', 'Server 2'),
           ('D', 'Server 3')]


DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class FormRadio(forms.Form):
    servers = forms.ChoiceField(choices = CHOICES, widget = forms.RadioSelect())

class FormDate(forms.Form):
        start_date=forms.DateField()
        end_date=forms.DateField()

class FormUser(forms.Form):
        password = forms.CharField(widget=forms.PasswordInput)
        user = forms.CharField()
