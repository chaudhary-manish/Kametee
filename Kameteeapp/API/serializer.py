from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User
from rest_framework import exceptions
from Kameteeapp.models import *

# user register 
class RegisterSerializer(serializers.Serializer):    
    MobileNumber = serializers.CharField()
    Firstname = serializers.CharField()
    LastName = serializers.CharField()
    Password = serializers.CharField()


    def validate(self, data):
        username = data.get("MobileNumber", "")
        Firstname = data.get("Firstname", "")
        LastName = data.get("LastName", "")
        Email = 'chaudhary94rc@gmail.com'
        Password = data.get("Password", "")
        userexist = User.objects.filter(username = username).count()

        #check weather use is alreday exit or not
        if userexist != 0:
            msg = "User already exist with given mobile number"
            raise exceptions.ValidationError(msg)

        if username and Password and Firstname and LastName:
            user = User(username=username, password=Password,
            first_name=Firstname,last_name=LastName,email=Email)
            user.set_password(Password)
            user.save()
            userdeatil = UserDetails(User=user)
            userdeatil.save()
            UserDetailphoto =  ProfilePic(User=user,ProfilePic='')
            UserDetailphoto.save()
            data['user']=user           
        else:
            msg = "Must provide username and password FirstName and LastName both."
            raise exceptions.ValidationError(msg)
        return data

# user Login
class LoginSerializer(serializers.Serializer):    
    MobileNumber = serializers.CharField()
    Password = serializers.CharField()


    def validate(self, data):
        MobileNumber = data.get("MobileNumber", "")     
        Password = data.get("Password", "")

        if MobileNumber and Password:
            user = authenticate(username=MobileNumber, password=Password)

            if user is not None:
                if user.is_active:
                    data["user"] = user
                else:
                    msg = "User is deactivated. "
                    raise ValueError(msg)
            else:
                msg = "Unable to login with given credentials."
                raise ValueError(msg)
        else:
            msg = "Must provide username and password both."
            raise ValueError(msg)
        return data
  

class AddGroupUserSerializer(serializers.Serializer):    
    GroupID = serializers.IntegerField()
    MobileNumber = serializers.IntegerField()
    UserName = serializers.CharField()

    def validate(self,data):
        GroupID = data.get("GroupID", "")
        Mobilenumber = data.get("MobileNumber", "")
        UserName = data.get("UserName", "")
        #user_id = self.context["user_id"]
        groupuser = UserGroup.objects.get(id=GroupID)
        total = groupuser.usercount
        isactviegroup = groupuser.isActive
        Status = groupuser.groupStatus
        Totalcount = GroupMember.objects.filter(UserGroup=GroupID).count()

        if Status != 5:
            msg = "Group is no longer in open state" 
            raise ValueError(msg)

        elif isactviegroup == 0:
            msg = "Group is no longer active" 
            raise ValueError(msg)

        elif total == Totalcount:
            msg = "Group Member count filled" 
            raise ValueError(msg)
            
        elif GroupMember.objects.filter(UserGroup=GroupID,UserName=UserName).exists():
            msg = "Name and Mobile Number both should be unique."
            raise ValueError(msg)

        elif GroupMember.objects.filter(UserGroup=GroupID,Mobilenumber=Mobilenumber).exists():
            msg = "Name and Mobile Number both should be unique."
            raise ValueError(msg)
        elif GroupID and Mobilenumber:
            Group =  UserGroup.objects.get(id=GroupID)
            NewGroupUser =GroupMember(UserGroup=Group,Mobilenumber=Mobilenumber,UserName=UserName)
            NewGroupUser.save()                             
            msg = "User Added successfully" 
            return data       
        else:
            msg = "Must provide all required field."
            raise exceptions.ValidationError(msg)
        return data 



class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = [
            "id",
            "groupname",
            "startDate",
            "usercount",
            "createBy",
            "isActive",
            "AmountPerUser",
            "sarkriGhata",
            "groupStatus",
            "groupbiddingtype",
            "biddgingCycle"
        ]


class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = [
            "id",
            "UserGroup",
            "Mobilenumber",
            "UserName",
        ]

class GroupBiddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBidding
        fields = [
            "id",
            "UserGroup",
            "ActualAmount",
            "selectedName",
            "SelectedMobileNumber",
            "biddingAmount",
            "IsSelected"
        ]

class StatEndGroupUserSerializer(serializers.ModelSerializer):
     class Meta:
        model = UserGroup
        fields = [
            "id",
            "groupname",
            "startDate",
            "usercount",
            "createBy",
            "isActive",
            "AmountPerUser",
            "sarkriGhata",
            "groupbiddingtype",
            "groupStatus",
            "biddingdate",
            "biddgingCycle",
            "biddingflag"
         ]

class GroupBiddingEntriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupBiddingEntries
        fields = [
            "id",
            "GroupBidding",
            "TotalAmount",
            "MinCyclelossAmount",
            "BidlossAmount",
            "selectedName",
            "SelectedMobileNumber",
            "Cyclenumber",
            "AddedBy",
            "created_at",
            "IsSelected"
        ]



class UserDetailsSerializer(serializers.ModelSerializer):
    #ProfilePic  = serializers.ImageField(max_length=None,  use_url=True)
    class Meta:
        model = UserDetails
        fields = ['DateofBirth', 'AlternateMobileNumber']

class ProfilePicSerializer(serializers.ModelSerializer):
    #ProfilePic  = serializers.ImageField(max_length=None,  use_url=True)
    class Meta:
        model = ProfilePic
        fields = ['ProfilePic']


class ProfileSerializer(serializers.ModelSerializer):
    #UserDetails = UserDetailsSerializer()

    class Meta:
        model = User
        
        fields = ('username', 'first_name',
                'last_name', 'email',
                'is_staff', 'is_active', 'date_joined',
                'is_superuser')

class GroupPaymentHistorySerializer(serializers.ModelSerializer):
    #UserDetails = UserDetailsSerializer()

    class Meta:
        model = GroupPaymentHistory
        fields = ('id', 'GroupBidding',
                'Mobilenumber', 'UserName', 'ActualAmount',
                'AmountPaid', 'AmountDue', 'Cyclenumber',
                'IsReceived','Status')


class GroupAmountRecivedSerializer(serializers.ModelSerializer):

    class Meta:
        model = AmountRecived
        fields = ('id', 'ActualAmount',
                'ActualRecived', 'Cyclenumber', 'Amountsend',
                'RevicerName', 'Recivermobile', 'RecivedDate')


class GroupMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model = GroupMessage
        fields = ('id', 'UserGroup',
                'UserName', 'UserMobile', 'MessageDescription',
                'created_at')
         
