from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe

class CKEditor(forms.Textarea):
    class Media:
#         css = {
#             'all': ('syntaxhighlighter/styles/shCore.css', '/static/syntaxhighlighter/styles/shThemeDjango.css'),
#         }
        js = (
            'ckeditor/ckeditor.js',
            'ckeditor/config.js',
            'ckeditor/styles.js',
            'ckeditor/lang/en.js',
#             'syntaxhighlighter/scripts/shCore.js',
#             '/static/syntaxhighlighter/scripts/shBrushBash.js',
        )

    def __init__(self, language=None, attrs=None):
        self.language = language or settings.LANGUAGE_CODE[:2]
        self.attrs = {'class': 'ckeditor'}
        if attrs:
            self.attrs.update(attrs)
        super(CKEditor, self).__init__(attrs)

    def render(self, name, value, attrs=None):
        rendered = super(CKEditor, self).render(name, value, attrs)
        return rendered + mark_safe(u'''<script type="text/javascript">
            CKEDITOR.replace( 'id_content' );
            //SyntaxHighlighter.all();
            </script>''')