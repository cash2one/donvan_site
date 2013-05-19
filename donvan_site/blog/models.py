from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.template.defaultfilters import striptags, truncatewords, safe

class Post(models.Model):
    
    STATUS_CHOICES = (
                        ('Published', 'Published'),
                        ('Draft', 'Draft')
                      )
    title = models.CharField(max_length=100, unique=True)
    content = models.TextField()
    publish_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=9, choices=STATUS_CHOICES, default='Published')
    visible = models.BooleanField(default=True)
    tag = models.ManyToManyField('Tag', related_name='post_tag', null=True, blank=True)
    category = TreeForeignKey('Category', null=True, blank=True)
    view_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-publish_time']
    @property
    def fields(self):
        return [field.name for field in self._meta.fields]
    def brief(self):
        return safe(truncatewords(striptags(self.content), 100))
    def postTagList(self):
        return [tag.content for tag in self.tag.all()]
    def postTag(self):
        return ', '.join(self.postTagList())
    postTag.short_description = "tags"
    def save(self, *args, **kwargs):
        if self.status == 'Draft':
            self.title = '%s [draft]' % self.title
        else:
            self.title = self.title.replace(' [draft]', '')
        super(Post, self).save(*args, **kwargs)
    def __unicode__(self):
        return self.title


class Tag(models.Model):
    
    content = models.CharField(unique=True, max_length=20)
    
    @property
    def postCount(self):
        return self.post_tag.count()
    def __unicode__(self):
        return self.content

        
class Category(MPTTModel):
    
    parent = TreeForeignKey('self', blank=True, null=True, related_name='children')
    content = models.CharField(max_length=20)
    unique_together = ("parent", "content")
    
    class MPTTMeta:
        order_insertion_by = ['content']

    @property
    def postCount(self):
        return self.post_set.count()
    def __unicode__(self):
        return self.content

class Link(models.Model):
    
    name = models.CharField(unique=True, max_length=20)
    url = models.CharField(max_length=200)
    
    def __unicode__(self):
        return self.name
