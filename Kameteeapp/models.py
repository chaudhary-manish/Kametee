import os
import sys
from django.db import models
from django.utils import timezone
from  django.contrib.auth.models import User,Group


# Create your models here.
def upload_to(instance, filename):
    now = timezone.now()
    base, extension = os.path.splitext(filename.lower())
    milliseconds = now.microsecond // 1000
    return f"profile/{instance.pk}/{now:%Y%m%d%H%M%S}{milliseconds}{extension}"

class UserDetails(models.Model):   
    id = models.AutoField(primary_key=True)
    User= models.ForeignKey(User, on_delete=models.CASCADE,null=True,blank=True,related_name='UserDetails')
    DateofBirth = models.DateField(max_length=12,null=True, blank=True)
    AlternateMobileNumber=models.BigIntegerField(null=True,default=0 , blank=True)
    ProfilePic = models.ImageField(upload_to =upload_to,null=True,blank=True)


class UserGroup(models.Model):   
    id = models.AutoField(primary_key=True)
    groupname = models.TextField(max_length=30,null=True)
    startDate=models.DateField(max_length=12,null=True)
    usercount = models.IntegerField(null=True)
    createBy = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    isActive = models.IntegerField(default=1) 
    AmountPerUser = models.DecimalField(max_digits=8, decimal_places=2)
    sarkriGhata =  models.DecimalField(max_digits=8, decimal_places=2)
    groupbiddingtype = models.IntegerField(default=1)
    groupStatus = models.IntegerField(default=5) 
    biddingdate = models.DateField(max_length=12,null=True)
    biddingflag = models.IntegerField(default=0)
    biddgingCycle = models.IntegerField(null=True,default=1)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class GroupMember(models.Model):   
    id = models.AutoField(primary_key=True)
    UserGroup= models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    Mobilenumber = models.BigIntegerField() 
    isAdmin  = models.SmallIntegerField(default = 0)
    UserName = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
  
   
class GroupBidding(models.Model):   
    id = models.AutoField(primary_key=True)
    UserGroup= models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    ActualAmount = models.DecimalField(max_digits=8, decimal_places=2) 
    biddingAmount =models.DecimalField(max_digits=8, decimal_places=2,null=True,default=0) 
    selectedName = models.TextField(null=True)
    SelectedMobileNumber=models.BigIntegerField(null=True)  
    Cyclenumber = models.IntegerField(null=True,default=0)  
    IsSelected = models.IntegerField(default=0)
    BiddingStatus = models.IntegerField(default= 5)  # it means last group bidding status 5 or 20 means open and finished n 10 means in progress
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

class GroupBiddingEntries(models.Model):
    id = models.AutoField(primary_key=True)
    GroupBidding= models.ForeignKey(GroupBidding, on_delete=models.CASCADE)
    TotalAmount =models.DecimalField(max_digits=8, decimal_places=2,null=True,default=0) 
    MinCyclelossAmount = models.IntegerField(default = 0)
    BidlossAmount = models.IntegerField(default = 0)
    selectedName = models.TextField()
    SelectedMobileNumber=models.BigIntegerField()  
    Cyclenumber = models.IntegerField(default=0)  
    IsSelected = models.IntegerField(default=0)
    AddedBy  = models.BigIntegerField(default = 0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    
class GroupPaymentHistory(models.Model):   
    id = models.AutoField(primary_key=True)
    UserGroup= models.ForeignKey(UserGroup, on_delete=models.CASCADE,default=0)
    GroupBidding= models.ForeignKey(GroupBidding, on_delete=models.CASCADE)
    Mobilenumber = models.BigIntegerField(null=True,default=0) 
    UserName = models.TextField()
    ActualAmount = models.DecimalField(max_digits=8, decimal_places=2,null=True,default=1)
    AmountPaid = models.DecimalField(max_digits=8, decimal_places=2,null=True,default=0)
    AmountDue = models.DecimalField(max_digits=8, decimal_places=2,null=True,default=0)  
    Cyclenumber = models.IntegerField(null=True,default=1)     
    startDate=models.DateField(default=timezone.now)
    IsReceived = models.IntegerField(default=0)
    Status = models.IntegerField(default=5)
    created_at = models.DateTimeField(default=timezone.now)

class AmountRecived(models.Model):   
    id = models.AutoField(primary_key=True)
    UserGroup= models.ForeignKey(UserGroup, on_delete=models.CASCADE)
    ActualAmount = models.DecimalField(max_digits=8, decimal_places=2) 
    ActualRecived = models.DecimalField(max_digits=8, decimal_places=2) 
    Cyclenumber = models.IntegerField()
    Amountsend = models.IntegerField(default=0)
    RevicerName = models.TextField()
    Recivermobile =models.BigIntegerField() 
    RecivedDate=models.DateField(max_length=12)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)


class Biddingtype(models.Model):   
    id = models.AutoField(primary_key=True)
    Typename = models.TextField()
    TypeDescription =models.TextField()

class StatusDetail(models.Model):
    id = models.AutoField(primary_key=True)
    StatusID = models.IntegerField()
    StatusDescritpion =models.TextField()

class GroupMessage(models.Model):
    id = models.AutoField(primary_key=True)
    UserGroup= models.ForeignKey(UserGroup, on_delete=models.CASCADE)   
    UserName = models.TextField()
    UserMobile =models.BigIntegerField() 
    MessageDescription =models.TextField()   
    created_at = models.DateTimeField(default=timezone.now)

