from django.db import models

class Question_Answer(models.Model):
    ID = models.AutoField(primary_key= True, auto_created=True) 
    user_key = models.CharField(max_length=200, null=True)
    Question = models.CharField(max_length=1000,default='질문') # 질문(필수)
    Answer = models.CharField(max_length=2000,default='답변') # 답변(필수)
    upvotes = models.IntegerField(default=0)
    downvotes = models.IntegerField(default=0)
    is_accepted=models.BooleanField(default=False)
    view_count = models.IntegerField(default=0)
    Keywords = models.CharField(max_length=200, null=True)
    Date = models.DateTimeField(auto_now_add=True, null=True)
    Links = models.CharField(max_length=200, null=True)
    
