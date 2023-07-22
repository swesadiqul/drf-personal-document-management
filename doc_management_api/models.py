from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Document(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length = 150)
    description = models.TextField()
    file = models.FileField(upload_to='documents/')
    shared_with = models.ManyToManyField(User, related_name='shared_documents', blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Documents'

    def __str__(self):
        return self.title
    

class DocumentSharing(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE)
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE)
    shared_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['document', 'shared_with']
    

    
    
    
    

     