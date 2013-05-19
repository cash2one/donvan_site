from django.conf.urls import patterns, include, url


# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

blog_patterns = patterns('blog.views',
                         url(r'^test/$', 'test'),
)

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'donvan_site.views.home', name='home'),
                       # url(r'^donvan_site/', include('donvan_site.foo.urls')),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       # (r'^grappelli/',include('grappelli.urls')),
                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       #     url(r'', include(blog_patterns)),
)

urlpatterns += patterns('blog.views',
                        url(r'^$', 'Index'),
                        url(r'^post/(?P<title>.+)/$', 'PostView'),
                        url(r'^postContent/(?P<post_content>.+)/$', 'PostView'),
                        url(r'^category/(?P<content>.+)/$', 'CategoryView'),
                        url(r'^tag/(?P<content>.+)/$', 'TagView'),
                        url(r'^date/(?P<year>\d{4})/$', 'DateView'),
                        url(r'^date/(?P<year>\d{4})/(?P<month>\d{2})/$', 'DateView'),
                        url(r'^date/(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', 'DateView'),
                        url(r'^search/(?P<content>.+)/$', 'SearchView'),
                        url(r'^backup/$', 'SendMail'),
                        url(r'^test/$', 'test'),
)