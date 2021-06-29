from django.db import models

# Create your models here.

class Blog_post(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    b_head0 = models.CharField(max_length=500,default="")
    b_chead0 = models.CharField(max_length=5000,default="")
    b_head1 = models.CharField(max_length=500,default="")
    b_chead1 = models.CharField(max_length=5000,default="")
    b_head2 = models.CharField(max_length=500,default="")
    b_chead2 = models.CharField(max_length=5000,default="")
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to='blog/images',default="")


    def __str__(self):

        return self.title
