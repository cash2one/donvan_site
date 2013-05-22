#encoding=utf-8
from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.context_processors import csrf
from blog.models import Post, Tag, Category, Link
from blog.forms import UploaderForm
import datetime
import logging
import sys
reload(sys)
sys.setdefaultencoding("utf-8")


POSTS_PER_PAGE = 15

def postDateCategory():
    date_list = [post.publish_time.strftime('%Y-%m') for post in Post.objects.all()]
    result = dict()
    for date in date_list:
        if result.has_key(date):
            result[date] += 1
        else:
            result[date] = 1
    return sorted(result.items(), key=lambda x: x[0])

BASE_RESPONSE_DATA = {
                      'categories': Category.objects.all(),
                      'tags': Tag.objects.all(),
                      'date_categories': postDateCategory(),
                      'links': Link.objects.all()
                      }

def getPost(condition_value, condition_field=list(), query_method='iexact', combiner='and'):
    posts = dict()
    if 'category' in condition_field:
        condition = {
                        'content__%s' % query_method: condition_value
                    }
        for cate in Category.objects.select_related().filter(**condition):
            posts['category'] = cate.post_set.all()
            
    if 'tag' in condition_field:
        condition = {
                        'content__%s' % query_method: condition_value
                     }
        tags = Tag.objects.prefetch_related().filter(**condition)
        if tags:
            posts['tag'] = tags[0].post_tag.all()
        else:
            posts['tag'] = []
        
    if 'year' in condition_field:
        if type(condition_value) == int:
            posts['year'] = Post.objects.filter(publish_time__year=condition_value)
        else:
            posts['year'] = []
        
    if 'month' in condition_field:
        if type(condition_value) == int:
            posts['month'] = Post.objects.filter(publish_time__month=condition_value)
        else:
            posts['month'] = []
    if 'day' in condition_field:
        if type(condition_value) == int:
            posts['day'] = Post.objects.filter(publish_time__day=condition_value)
        else:
            posts['day'] = []
    if 'post_title' in condition_field:
        condition = {
                        'title__%s' % query_method: condition_value
                    }
        posts['post_title'] = Post.objects.filter(**condition)
    
    if 'post_content' in condition_field:
        posts['post_content'] = Post.objects.filter(content__contains=condition_value)
    
    if not condition_field:
        condition_field = ['category', 'tag', 'year', 'month', 'day', 'post_title', 'post_content']
        return getPost(condition_value, condition_field, 'contains', 'or')
    if combiner == 'and':
        return reduce(lambda x,y: list(set(x) & set(y)), posts.values())
    else:
        return reduce(lambda x,y: list(set(x) | set(y)), posts.values())

def AddBaseData(template_name):
    def _AddBaseData(func):
        def new_func(*args, **kwargs):
            request = args[0]
            posts = func(*args, **kwargs)
            response_data = {
                'posts': posts,
                'isAdminUser': request.user.is_authenticated()
            }
            response_data.update(BASE_RESPONSE_DATA)
            response_data.update(csrf(request))
            logging.error(request.user.is_authenticated())
            return render_to_response(template_name, response_data)
        return new_func
    return _AddBaseData

def Paginated():
    def _paginated(func):
        def new_func(*args, **kwargs):
            request = args[0]
            posts_list = func(*args, **kwargs)
            paginator = Paginator(posts_list, POSTS_PER_PAGE)
            try:
                posts = paginator.page(request.GET.get('page'))
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            return posts
        return new_func
    return _paginated

@AddBaseData('index.html')
@Paginated()
def Index(request):
    logging.error(request.user)
    logging.error(request.user.is_authenticated())
    return Post.objects.all()

@AddBaseData('post_view.html')
def PostView(request, title):
    posts = Post.objects.filter(title__iexact=title)
    if posts.exists():
        post = posts[0]
        post.view_count += 1
        post.save()
        return post
    return posts

@AddBaseData('index.html')
@Paginated()
def CategoryView(request, content):
    return getPost(content, ['category'])

@AddBaseData('index.html')
@Paginated()
def TagView(request, content):
    return getPost(content, ['tag'])

@AddBaseData('index.html')
@Paginated()
def DateView(request, year, month=None, day=None):
    selection_posts = dict()
    selection_posts['year'] = getPost(year, ['year'])
    if not month is None:
        selection_posts['month'] = getPost(month, ['month'])
    if not day is None:
        selection_posts['day'] = getPost(day, ['day'])
    return reduce(lambda x,y: list(set(x) & set(y)), selection_posts.values())

@AddBaseData('index.html')
@Paginated()
def SearchView(request, content=None):
    if content is None:
        return Index(request)
    else:
        return getPost(content)

def SendMail(request):
    if request.method == 'GET':
        if request.GET.has_key('cmd'):
            if not request.GET['cmd'] == 'backupDB':
                return HttpResponse('')
        else:
            return HttpResponse('')
    now = datetime.datetime.now()
    def dumpData(database):
        import subprocess
        CMD = 'mysqldump -u%s -p%s %s'%(database['USER'], database['PASSWORD'], database['NAME'])
        db = subprocess.Popen(CMD, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        db_stdout, db_stderr = db.communicate()
        if db_stderr:
            logging.error(db_stderr)
            return None
        else:
            return db_stdout

    def zipData(data):
        import zipfile
        from StringIO import StringIO
        buf = StringIO()
        with zipfile.ZipFile(buf, 'w') as db_zip:
            db_zip.writestr('%s.sql'%now.strftime('%Y-%m-%d_%H-%M-%S'),data, zipfile.ZIP_DEFLATED)
        return buf.getvalue()

    def sendMail(dst_address, attach_data):
        from django.core.mail import EmailMessage


        subject = '[%s] backup db'%now.strftime('%Y-%m-%d %H:%M:%S')
        body = 'statistic'
        from_email = 'donvan@donvan.info'
        to = (dst_address,)
        attachments = ('%s.zip'%now.strftime('%Y-%m-%d_%H-%M-%S'), attach_data, 'application/zip')
        bcc = None
        connection = None
        headers = None
        cc = None

        email = EmailMessage(
            subject,
            body,
            from_email,
            to,
            bcc,
            connection,
            headers,
            cc,
        )
        email.attach(*attachments)
        try:
            email.send()
        except Exception, e:
            logging.error(e)
        else:
            logging.info('db backup ok. size: %s'%len(attach_data))

    from django.conf import settings

    logging.basicConfig(format='%(asctime)s - %(levelname)-7s - %(filename)s:%(funcName)s:%(lineno)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    sql_data = dumpData(settings.DATABASES['default'])
    if sql_data:
        zip_sql_data = zipData(sql_data)
        with open('test.zip', 'w') as f:
            f.write(zip_sql_data)
        sendMail(settings.ADMINS[0][1], zip_sql_data)
    return HttpResponse('backup ok\n')


def insert_posts(number):
    content='''<pre class="brush:python;">
# Django settings for donvan_site project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     (&#39;donvan&#39;, &#39;donvanf@hotmail.com&#39;),
)

MANAGERS = ADMINS

#current path
import os
PATH = os.path.dirname(os.path.realpath(__file__))

DATABASES = {
    &#39;default&#39;: {
#        &#39;ENGINE&#39;: &#39;django.db.backends.mysql&#39;, # Add &#39;postgresql_psycopg2&#39;, &#39;mysql&#39;, &#39;sqlite3&#39; or &#39;oracle&#39;.
        &#39;ENGINE&#39;: &#39;django.db.backends.sqlite3&#39;,
#        &#39;NAME&#39;: &#39;donvan_site&#39;,                      # Or path to database file if using sqlite3.
        &#39;NAME&#39;: &#39;F:\\z_priviate\\aptana\\donvan_site\\sqlite.db&#39;,
        # The following settings are not used with sqlite3:
        &#39;USER&#39;: &#39;donvan&#39;,
        &#39;PASSWORD&#39;: &#39;qweqwe&#39;,
        &#39;HOST&#39;: &#39;&#39;,                      # Empty for localhost through domain sockets or &#39;127.0.0.1&#39; for localhost through TCP.
        &#39;PORT&#39;: &#39;&#39;,                      # Set to empty string for default.
    }
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = &#39;Asia/Shanghai&#39;

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = &#39;en-us&#39;

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = False

DATETIME_FORMAT = &#39;Y-m-d H:i:s&#39;

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: &quot;/var/www/example.com/media/&quot;
MEDIA_ROOT = &#39;%s/media&#39;%PATH

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: &quot;http://example.com/media/&quot;, &quot;http://media.example.com/&quot;
MEDIA_URL = &#39;/media/&#39;

# Absolute path to the directory static files should be collected to.
# Don&#39;t put anything in this directory yourself; store your static files
# in apps&#39; &quot;static/&quot; subdirectories and in STATICFILES_DIRS.
# Example: &quot;/var/www/example.com/static/&quot;
STATIC_ROOT = &#39;%s/static_root/&#39;

# URL prefix for static files.
# Example: &quot;http://example.com/static/&quot;, &quot;http://static.example.com/&quot;
STATIC_URL = &#39;/static/&#39;

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like &quot;/home/html/static&quot; or &quot;C:/www/django/static&quot;.
    # Always use forward slashes, even on Windows.
    # Don&#39;t forget to use absolute paths, not relative paths.
    &#39;%s/static&#39;%PATH,
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    &#39;django.contrib.staticfiles.finders.FileSystemFinder&#39;,
    &#39;django.contrib.staticfiles.finders.AppDirectoriesFinder&#39;,
#    &#39;django.contrib.staticfiles.finders.DefaultStorageFinder&#39;,
)

# Make this unique, and don&#39;t share it with anybody.
SECRET_KEY = &#39;(3)m#74^8yk*m#nol(@ev=n)1xoy5v6%7)q&amp;90e!1+mj74h+bv&#39;

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    &#39;django.template.loaders.filesystem.Loader&#39;,
    &#39;django.template.loaders.app_directories.Loader&#39;,
#     &#39;django.template.loaders.eggs.Loader&#39;,
)

MIDDLEWARE_CLASSES = (
    &#39;django.middleware.common.CommonMiddleware&#39;,
    &#39;django.contrib.sessions.middleware.SessionMiddleware&#39;,
    &#39;django.middleware.csrf.CsrfViewMiddleware&#39;,
    &#39;django.contrib.auth.middleware.AuthenticationMiddleware&#39;,
    &#39;django.contrib.messages.middleware.MessageMiddleware&#39;,
    # Uncomment the next line for simple clickjacking protection:
    # &#39;django.middleware.clickjacking.XFrameOptionsMiddleware&#39;,
)

ROOT_URLCONF = &#39;donvan_site.urls&#39;

# Python dotted path to the WSGI application used by Django&#39;s runserver.
WSGI_APPLICATION = &#39;donvan_site.wsgi.application&#39;

TEMPLATE_DIRS = (
    # Put strings here, like &quot;/home/html/django_templates&quot; or &quot;C:/www/django/templates&quot;.
    # Always use forward slashes, even on Windows.
    # Don&#39;t forget to use absolute paths, not relative paths.
    &#39;%s/templates&#39;%PATH,
)

INSTALLED_APPS = (
    &#39;django.contrib.auth&#39;,
    &#39;django.contrib.contenttypes&#39;,
    &#39;django.contrib.sessions&#39;,
    &#39;django.contrib.sites&#39;,
    &#39;django.contrib.messages&#39;,
    &#39;django.contrib.staticfiles&#39;,
    # Uncomment the next line to enable the admin:
    &#39;suit&#39;,
#     &#39;grappelli&#39;,
    &#39;django.contrib.admin&#39;,
    # Uncomment the next line to enable admin documentation:
    # &#39;django.contrib.admindocs&#39;,
    &#39;blog&#39;,
    &#39;mptt&#39;,
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    &#39;version&#39;: 1,
    &#39;disable_existing_loggers&#39;: False,
    &#39;filters&#39;: {
        &#39;require_debug_false&#39;: {
            &#39;()&#39;: &#39;django.utils.log.RequireDebugFalse&#39;
        }
    },
    &#39;handlers&#39;: {
        &#39;mail_admins&#39;: {
            &#39;level&#39;: &#39;ERROR&#39;,
            &#39;filters&#39;: [&#39;require_debug_false&#39;],
            &#39;class&#39;: &#39;django.utils.log.AdminEmailHandler&#39;
        }
    },
    &#39;loggers&#39;: {
        &#39;django.request&#39;: {
            &#39;handlers&#39;: [&#39;mail_admins&#39;],
            &#39;level&#39;: &#39;ERROR&#39;,
            &#39;propagate&#39;: True,
        },
    }
}

#mptt settings
MPTT_ADMIN_LEVEL_INDENT = 30

#django admin suit
from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS as TCP
 
TEMPLATE_CONTEXT_PROCESSORS = TCP + (
    &#39;django.core.context_processors.request&#39;,
)

#django admin grappelli
ADMIN_MEDIA_PREFIX = &#39;/static/admin/&#39;
# ADMIN_MEDIA_PREFIX = STATIC_URL + &quot;grappelli/&quot;</pre>

<p><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">2)设置ADMIN_MEDIA_PREFIX,而不是采用上面的参考资料中的设置adminmedia到grapplli什么的.</span><br />
<br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">#ADMIN_MEDIA_PREFIX = &#39;/static/admin/&#39;ADMIN_MEDIA_PREFIX = STATIC_URL + &quot;grappelli/&quot;这个的作用就是把admin的静态文件,由原来的admin目录,改为映射到static目录下的grapplli.</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">3)设置Url</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">(r&#39;^admin/doc/&#39;, include(&#39;django.contrib.admindocs.urls&#39;)), (r&#39;^grappelli/&#39;,include(&#39;grappelli.urls&#39;)), # Uncomment the next line to enable the admin: (r&#39;^admin/&#39;, include(admin.site.urls)),</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">同settings中配置的一样,grapplli的url映射,必须在admin之前.</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">4)收集静态资源</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">通过运行命令:</span><br />
<br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">manage.py collectstatic&nbsp;</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">此命令,收集grapplli app目录下的static目录中的所有静态资源(CSS,js,images)到你配置的STATIC目录</span><br />
<span style="color:rgb(102, 102, 102); font-family:宋体,arial; font-size:12px">下的grapplli目录下去.</span></p>
'''

    post = {
        'title': None,
        'content': content,
    }
    for i in xrange(number):
        post['title'] = 'this is a test title - %s'%i
        Post(**post).save()
        
def test(request):
    number = 200
    try:
        insert_posts(number)
    except Exception, e:
        return HttpResponse(e)
    return HttpResponse('inseted %s posts.'%number)