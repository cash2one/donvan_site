from django import forms
from django.db.models import get_model
from blog.widgets import CKEditor

class PostAdminModelForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor())

    class Meta:
        model = get_model('blog', 'post')