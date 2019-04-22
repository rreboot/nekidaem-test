from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import mail_managers
from django.conf import settings


class Post(models.Model):
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='posts')
    title = models.CharField(max_length=200, db_index=True)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    viewed_by = models.ManyToManyField('auth.User', related_name='views', symmetrical=False)

    def get_absolute_url(self):
        return reverse('post_detail_url', kwargs={'pk': self.id})

    def get_username(self):
        return self.author.username

    def viewed(self, user):
        return user in self.viewed_by.all()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created']


@receiver(post_save, sender=Post)
def send_emails(sender, instance, **kwargs):  # TODO: Need Full absolute url with domain!
    title = 'New post'
    body = instance.get_absolute_url()
    settings.MANAGERS.extend([(obj.username, obj.email) for obj in User.objects.all()
                              if obj.email not in [instance.author.email, '']])
    mail_managers(title, body)


class Contact(models.Model):
    user_from = models.ForeignKey('auth.User',
                                  related_name='rel_from_set',
                                  on_delete=models.CASCADE)
    user_to = models.ForeignKey('auth.User',
                                related_name='rel_to_set',
                                on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True,
                                   db_index=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{} follows {}'.format(self.user_from,
                                      self.user_to)


User.add_to_class('following',
                  models.ManyToManyField('self',
                                         through=Contact,
                                         related_name='followers',
                                         symmetrical=False))
