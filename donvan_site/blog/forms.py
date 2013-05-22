from django import forms
from django.db.models import get_model
from blog.widgets import CKEditor
from blog.models import UploadFile


class PostAdminModelForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor())

    class Meta:
        model = get_model('blog', 'post')

class UploaderForm(forms.ModelForm):
    class Meta:
        model = UploadFile