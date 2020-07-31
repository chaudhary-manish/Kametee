from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
#from quickstart.models import UserDetails,UserGroup
from Kameteeapp.API.serializer import *
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import login as django_login, logout as django_logout
from rest_framework import generics
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from Kameteeapp.models import *
from rest_framework.views import APIView
import datetime
from django.db.models import Q
from django.db.models.aggregates import Max
import http.client # this is used for client connection of msg api
from random import randint
import json
from datetime import timedelta 
import uuid
from base64 import b64decode
from django.core.files.base import ContentFile  

def Send_message(SMSTemplate,Phone_number,var1 ='',var2='',var3='',var4='',var5=''):
    conn = http.client.HTTPConnection("2factor.in")    
    api_key = '5e31f7cf-8dd5-11ea-9fa5-0200cd936042'
    
    # set payload and set variable to SMS template
    if SMSTemplate == 'OTPVerification':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "TemplateName": "OTPVerification"})
    elif SMSTemplate == 'New-Registration':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "TemplateName": "New-Registration"}) 
    elif SMSTemplate == 'groupregistration':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1,"VAR2": var2 ,"VAR3": var3 ,"TemplateName": "groupregistration"})
    elif SMSTemplate == 'Startbiddingalert':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "VAR2": var2 ,"VAR3": var3 ,"TemplateName": "Startbiddingalert"})
    elif SMSTemplate == 'SelectedbiddingAlert':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "VAR2": var2 ,"VAR3": var3,"VAR4": var4 ,"TemplateName": "SelectedbiddingAlert"})
    elif SMSTemplate == 'PaymentRecived':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "VAR2": var2 ,"VAR3": var3, "TemplateName": "PaymentRecived"})
    elif SMSTemplate == 'UserRecivedVerification':
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "TemplateName": "UserRecivedVerification"})
  
    if payloads is not None:
        header = {"content-type": "application/json"}
        conn.request("POST", "/API/V1/5e31f7cf-8dd5-11ea-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS", payloads)
        res = conn.getresponse()
        data = res.read()        
        return data.decode("utf-8")
    else:
        return True

# OTP generate to send for number verificaiton
@api_view(['POST'])
def OTP_Generate(request):
    data=request.data
    MobileNo = data['MobileNumber']
    condition = data['Purpose']
    random = randint(1001, 9999)
    if condition == 'forgetpassword':
        usercheck  =  User.objects.filter(username = int(MobileNo))       
        if usercheck.count() > 0:        
            data = Send_message('OTPVerification',MobileNo,random)    
            return Response({"radomno": random,'Response' : True,'Message':''}, status=200)
        else:
            return Response({"radomno": '','Response' : False,'Message' : 'Number not found in our system'}, status=200)
    else:
        usercheck  =  User.objects.filter(username = int(MobileNo))       
        if usercheck.count() < 1:        
            data = Send_message('OTPVerification',MobileNo,random)    
            return Response({"radomno": random,'Response' : True,'Message':''}, status=200)
        else:
            return Response({"radomno": '','Response' : False,'Message' : 'Your number already registred '}, status=200)

# send OTP to confirm user recive that amount
@api_view(['GET'])
def Contact_Details(request):
    data=request.data
    try:
        token = request.GET.get('token')  
        userid = Token.objects.get(key=token).user_id
        contactDetails = {}
        #return Response(userid)
        if userid is not None:
            contactDetails.update( {'enquiryemail' : 'chaudhary94rc@gmail.com'} )
            contactDetails.update( {'techsupportemail' : 'chaudhary94rc@gmail.com'} )
            contactDetails.update( {'contactNumber' : 8279463818} )
            contactDetails.update( {'whatappNumber' : 9412289096} )
            contactDetails.update( {'address' : 'C 603 Amrapali Empire Crossing rebublic'} )
            contactDetails.update( {'Longitude' : '28.6343° N'} )
            contactDetails.update( {'Latitude' : '77.4455° E'} )
 
            return Response({'contactDetails':contactDetails,'Response' : True,'Message' :''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' : False})
    except Exception as e:
        return Response({'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e),'Response' : False})


# send OTP to confirm user recive that amount
@api_view(['POST'])
def OTP_Generate_SendAmount(request):
    data=request.data
    MobileNo = data['MobileNumber']
    random = randint(1001, 9999)
    data = Send_message('UserRecivedVerification',MobileNo,random) 
    return Response({"radomno": random ,'Response' : data,'Message':''}, status=200)

# Signup User 
@api_view(['POST'])
def RegisterUser(request):
    data=request.data
    serializer = RegisterSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    MobileNo =data['MobileNumber']
    token, created = Token.objects.get_or_create(user=user)
    data = Send_message('New-Registration',MobileNo,MobileNo) 
    return Response({"token": token.key,'Response' : True,'Message':''}, status=200)

#@login_required(login_url="/login/")
@api_view(['POST'])
def logout_user(request):
    data=request.data
    token = data['token']
    token_destroy = Token.objects.get(key=token)
    token_destroy.delete()
    logout(request)
    return  Response({'Response' : True,'Message' :'User Logout Successfully'})

# login user 
@api_view(['POST'])
def login_user(request):
    try:
        data=request.data
        #return Response(data)
        serializer = LoginSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        userid = Token.objects.get(key=token.key).user_id
        Userdata = User.objects.get(id = userid)
        serializer = ProfileSerializer(Userdata)
        UserDetailsupdate = UserDetails.objects.get(User_id=userid)      
        userprofiledetails = ProfilePic.objects.get(User=Userdata)
        serializerprofile = ProfilePicSerializer(userprofiledetails)
        return Response({"token": token.key,'username':serializer.data['username'],'first_name':serializer.data['first_name'],'last_name':serializer.data['last_name'],
        'pic_url':serializerprofile.data['ProfilePic'],'loginstatus':True,'Response' : True,'Message' :''}, status=200)
    except ValueError as ve:
        return Response({'Message' : str(ve),'loginstatus':False,'Response' : False})
    except Exception as e:
        return Response({'Response' : False,'loginstatus':False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# login user 
@api_view(['POST'])
def forget_password(request):
    try:
        data=request.data 
        MobileNo = data['MobileNumber']   
        Password = data['Password'] 
        userexist = User.objects.filter(username = MobileNo).count()
        if userexist != 0:   
            userdata =  User.objects.get(username=MobileNo) 
            userdata.set_password(Password)
            userdata.save()
            passnew =  User.objects.get(username=MobileNo).password
            return Response({"Message": 'Password Update successfully','Response' : True}, status=200)
        else:
            return Response({"Message": 'User not exist in system','Response' :False}, status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

   

# Create user Group 
class GroupUser(generics.GenericAPIView,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin):

    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = UserGroupSerializer
    queryset = UserGroup.objects.all()
    lookup_field = 'id'
    

    def get_queryset(self):
        return self.queryset.filter(createBy=self.request.user,isActive=1,groupStatus=5)

    def get(self, request, id=None):
        if id:
            data= self.retrieve(request, id)
        else:
            data =  self.list(request)
        
        return Response({"Message":"Please use another method for retrive data",'Response' :True},status=200)
    def post(self, request):
        self.create(request)
        return Response({"Message":"data Save successfully",'Response' :True},status=200)

    def perform_create(self, serializer):
        usergroup = serializer.save(createBy=self.request.user)
        Userdetail =  User.objects.get(username=self.request.user)
        GroupUser =GroupMember(UserGroup=usergroup,Mobilenumber=Userdetail.username,UserName=Userdetail.first_name,isAdmin =1)
        GroupUser.save()
        Send_message('groupregistration',Userdetail.username,usergroup.groupname , str(usergroup.AmountPerUser) ,str(usergroup.startDate))        

    def put(self, request, id=None):
        self.update(request, id)
        return Response({"Message":"data updated successfully",'Response' :True},status=200)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)        

    def delete(self, request, id=None):
        self.destroy(request, id)
        return Response({'Message':'Data Deleted successfully','Response' :True})

#Add Member to Group
@api_view(['POST'])
def adduser_togroup(request):
    data=request.data    
    try:
        token = data['token']
        userMobileno = data['MobileNumber']
        userid = Token.objects.get(key=token).user_id
        #return Response(userid)
        if userid is not None:
            serializer = AddGroupUserSerializer(data=data,context={'user_id':userid})
            serializer.is_valid(raise_exception=True)
            usergroup =  UserGroup.objects.get(id=data['GroupID'])
            GroupMemberlist = GroupMember.objects.filter(UserGroup_id=data['GroupID'])
            serializer = GroupMemberSerializer(GroupMemberlist,many=True)
            data = Send_message('groupregistration',userMobileno,usergroup.groupname , str(usergroup.AmountPerUser) ,str(usergroup.startDate))
            return Response({'userlist' : "",'Response' : True,'Message':'User Add successfully'})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
   
    except ValueError as ve:
        return Response({'Message' : str(ve),'Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

#get User list of Group BY ID
@api_view(['get'])
def groupmember_list(request):    
    try:
        token = request.GET.get('token')
        id =  int(request.GET.get('GroupID'))        
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupMemberlist = GroupMember.objects.filter(UserGroup_id=id)
            serializer = GroupMemberSerializer(GroupMemberlist,many=True)
            return Response({'data':serializer.data,'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


#update gruop member list when group is in open state ie: 5
@api_view(['PUT','DELETE'])
def groupmember_update(request):
    data=request.data
    try:
        token = data['token']
        id  = data['GroupMemberID']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            Mobilenumber = data['MobileNumber']
            UserName = data['UserName']
            status = UserGroup.objects.get(id__in=GroupMember.objects.filter(id=id).values('UserGroup_id')).groupStatus
            UsergroupID = GroupMember.objects.filter(id=id).values('UserGroup_id')[0]  
            checkuserexist  = GroupMember.objects.filter(UserGroup_id=UsergroupID['UserGroup_id'],Mobilenumber = Mobilenumber).exclude(UserName=UserName).count()

            checkuserexistname  = GroupMember.objects.filter(UserGroup_id=UsergroupID['UserGroup_id'],UserName=UserName).exclude(Mobilenumber = Mobilenumber).count()
           
            if status == 5:
                if request.method == 'PUT':
                    if checkuserexist > 0 or  checkuserexistname > 0 :
                          return Response({'Message' :"Name or Mobile Number already exist for this group ",'Response' :True},status=200)
                    else:
                        GroupMemberupdate =  GroupMember.objects.filter(id=id).update(Mobilenumber=Mobilenumber,UserName=UserName)
                    return Response({'Message' :"User update successfully ",'Response' :True},status=200)
                else:
                    GroupMember.objects.filter(id=id).delete()
                    return Response({'Message' :"User Deleted successfully ",'Response' :True},status=200)
            else:
                return Response({'Message' :"Group no longer in open state",'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :True})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


@api_view(['GET'])
def Get_Group_forChat(request):  
    try:
        token = request.GET.get('token')        
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            usermobilenumber = User.objects.get(id=userid).username            
            GroupDetail = UserGroup.objects.filter(groupStatus__in =(10,15),id__in =
                          GroupMember.objects.filter(Mobilenumber = usermobilenumber).values('UserGroup'))
            serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
            
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data,'Response' :False,'Message' :'Your are not register with any  group'},status=200)
            else:
                return Response({'data':serializer.data,'Response' :True,'Message' :''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :True},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

#Group message with all member of group
@api_view(['Post','Get'])
def group_chat(request):
    data=request.data
    try:        
        if request.method == 'POST':
            token = data['token']            
            userid = Token.objects.get(key=token).user_id
            usergroupdata = UserGroup.objects.get(id = data['GroupID'])
            messagedesc = data['Message']              
            UserDetails = User.objects.get(id = userid)
            GroupMessagedetails = GroupMessage(UserGroup =usergroupdata ,UserName= UserDetails.first_name,UserMobile=UserDetails.username , MessageDescription=messagedesc)
            GroupMessagedetails.save()
            return Response({'Message':"Send Successfully",'Response' :True},status=200) 

        else:
            token = request.GET.get('token')
            offset = int(request.GET.get('offset'))
            startoffset = int(request.GET.get('startoffset'))

            usergroupdata = UserGroup.objects.get(id = request.GET.get('GroupID'))
            GroupMessagedetails = GroupMessage.objects.filter(UserGroup =usergroupdata).order_by('id')[startoffset:offset]

        serializer = GroupMessageSerializer(GroupMessagedetails,many=True)
        return Response({'chatdata':serializer.data,'Response' :True,'Message':''},status=200)                  
        
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# to start group group of first time insert bidding date concept 
@api_view(['PUT'])
def Group_Start(request):
    data=request.data    
    try:
        token = data['token']
        id = data['GroupID']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupDetaildetails = UserGroup.objects.get(id=id,createBy = userid )
            if int(GroupDetaildetails.groupStatus) == 5 and int(GroupDetaildetails.biddingflag) == 0:
                groupmembercount = GroupMember.objects.filter(UserGroup_id = id).count()
                UserGroup.objects.filter(id=id,createBy = userid ).update(usercount=groupmembercount,groupStatus=10,biddgingCycle=1,biddingdate = datetime.datetime.today())
                Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
                serializer = StatEndGroupUserSerializer(Groupdetail)
                return Response({'data':serializer.data,'Response' :True,'Message':''})   
            else:
                return Response({'Message' :" User Group Already Start",'Response' :True},status=200) 
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})



@api_view(['PUT'])
def Group_End(request,id = None):
    data=request.data
    try:
        if id is None:
            return Response('Id Requried')
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupDetail = UserGroup.objects.filter(id=id,createBy = userid ).update(groupStatus=20,biddingflag = 0)
            Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
            serializer = StatEndGroupUserSerializer(Groupdetail)
            return Response({'GruopList':serializer.data,'Response' :True,'Message':''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

# terminate group if it is  in open state
@api_view(['PUT'])
def Group_Terminate(request,id = None):
    data=request.data
    try:
        if id is None:
            return Response('Id Requried')
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            status = UserGroup.objects.get(id=id,createBy = userid )            
            if status.groupStatus == 5:
                GroupDetail = UserGroup.objects.filter(id=id,createBy = userid ).update(groupStatus=25)
                Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
                serializer = StatEndGroupUserSerializer(Groupdetail)
                return Response({'GroupList':serializer.data,'Response' :True,'Message':''},status=200)
            else:
                return Response({'Message' :"Group can't be termenated because it already in running state",'Response' :True},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
        return Response({'Message' : 'Something Went worng either token or variable name format','Response' :False,'ErrorMessage':str(e)})

# get group list by group status got both group Admin and regular admin
@api_view(['GET'])
def Get_Group_ByStatus(request):  
    try:
        token = request.GET.get('token')
        status = int(request.GET.get('status'))       
        if status is None:
            status = 10
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            usermobilenumber = User.objects.get(id=userid).username            
            GroupDetail = UserGroup.objects.filter(groupStatus=status,id__in =
                          GroupMember.objects.filter(Mobilenumber = usermobilenumber).values('UserGroup'))
            serializer = StatEndGroupUserSerializer(GroupDetail, many = True)            
            if status == 10:
                statusname = 'Active'
            elif status == 15:
                statusname = 'Running'
            else:
                statusname = 'Finished'        
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data,'IsAdmin':False,'Response' :False,'Message' :'Your are not register with ' + str(statusname) + ' group'},status=200)
            else:
                return Response({'data':serializer.data,'IsAdmin':False,'Response' :True,'Message' :''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :True},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# let list of group for managing  this only fetch for admin only
@api_view(['GET'])
def Manage_Group_ByStatus(request):   
    try:
        token = request.GET.get('token')
        status = int(request.GET.get('status')) 
        if status is None:
            status = 10
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupDetail = UserGroup.objects.filter(groupStatus=status, createBy = userid)
            serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
            
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data,'IsAdmin':True,'Response' :False,'Message' :'Your are not admin to any group'},status=200)
            else:
                return Response({'data':serializer.data,'IsAdmin':True,'Response' :True,'Message' :''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


#
@api_view(['GET'])
def Group_Bidding(request):
    try:
        token = request.GET.get('token')
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupDetail = UserGroup.objects.filter(Q(biddingdate__isnull=True) | Q(biddingdate__lte = datetime.datetime.today())  ,
            Q(groupStatus=5) | Q(groupStatus = 15), createBy = userid )
            serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
            return Response({'data':serializer.data,'Response' :True,'Message' :''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
         return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# only admin can activate group admin
@api_view(['PUT'])
def Start_Group_Bidding(request):
    try:            
        data=request.data
        token = data['token']
        id = data['GroupID']
        userid = Token.objects.get(key=token).user_id
        # validate that user exist in our database or not
        if userid is not None:
            Userdetail  =User.objects.get(id=userid)
            UserGroupDetails = UserGroup.objects.get(id=id)
            ActualTotalAmount = UserGroupDetails.usercount * UserGroupDetails.AmountPerUser
           
            if UserGroupDetails.biddgingCycle == 2:
                minloss = 0
            else:
                minloss  = (ActualTotalAmount * UserGroupDetails.sarkriGhata)/100 * (UserGroupDetails.usercount - UserGroupDetails.biddgingCycle)
            # check weather group biddings are still in progress or finished
            biddinggruopStatus = GroupBidding.objects.filter(UserGroup = UserGroupDetails).values('BiddingStatus')
            # if len(biddinggruopStatus) == 0:
            #     groupbiddingstatus =5
            # else:
            #    groupbiddingstatus = biddinggruopStatus[0]['BiddingStatus']
            if UserGroupDetails.groupStatus == 10 and UserGroupDetails.biddingdate <= datetime.date.today():
                biddingcycle = UserGroupDetails.biddgingCycle
                if biddingcycle == 1:
                    GroupMemberlists = GroupMember.objects.filter(UserGroup = UserGroupDetails)
                else:
                    GroupMemberlists = GroupMember.objects.filter(UserGroup = UserGroupDetails).exclude(
                                        Mobilenumber__in = GroupBidding.objects.filter(UserGroup = UserGroupDetails,IsSelected =1
                                        ).values('SelectedMobileNumber'))  
                insertgroupbidding = GroupBidding(UserGroup = UserGroupDetails,ActualAmount=UserGroupDetails.AmountPerUser,
                                    Cyclenumber =biddingcycle,biddingAmount = 0,BiddingStatus=15)
                insertgroupbidding.save()
                
                for GroupMemberlist in GroupMemberlists:
                    GroupBiddingEntriesdata = GroupBiddingEntries(GroupBidding =insertgroupbidding,selectedName =GroupMemberlist.UserName,
                    SelectedMobileNumber = GroupMemberlist.Mobilenumber,Cyclenumber = biddingcycle ,TotalAmount = ActualTotalAmount,MinCyclelossAmount = minloss)
                    GroupBiddingEntriesdata.save()
                    fromdate = datetime.date.today() + timedelta(days=1)
                    todate  = fromdate + timedelta(days=1)
                    Send_message('Startbiddingalert',Userdetail.username,UserGroupDetails.groupname , str(fromdate) ,str(todate))

                UserGroup.objects.filter(id=id,createBy = userid ).update(groupStatus = 15,biddingflag=0)
                Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
                serializer = StatEndGroupUserSerializer(Groupdetail)
                return Response({'data':serializer.data,'Response' :True,'Message':''},status=200) 
            else:
                return Response({'Message' :"Previous bidding already in progress",'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})



# fetch data for single user of particular group
@api_view(['GET'])
def Group_Bidding_User_list_for_User(request):    
    try:
        token = request.GET.get('token')
        id = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id
        
        if userid is not None:
            UserGroupDetails = UserGroup.objects.get(id=id)
            usermobile  =  User.objects.get(id=userid)
            Groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroupDetails,IsSelected =0).aggregate(id=Max('pk'))
            GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding =Groupbiddingdetails["id"],IsSelected =0,SelectedMobileNumber =usermobile.username)
            serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data,'IsAdmin':True,'Response' :False,'Message' :'Bidding is submit or group is not running'},status=200)
            else:
               return Response({'data':serializer.data[0],'Response' :True,'Message':''},status=200)
            
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# fetch data for admin and single user of particular group
@api_view(['GET'])
def Group_Bidding_User_list(request):    
    try:
        token = request.GET.get('token')
        id = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            UserGroupDetails = UserGroup.objects.filter(id=id)
            UserGroup_id = UserGroup.objects.get(id=id)
            Groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroup_id,IsSelected =0).aggregate(id=Max('pk'))
            
            #userid = Token.objects.get(key=token).user_id
            GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding =Groupbiddingdetails["id"],IsSelected =0)
            # if UserGroupDetails.count() == 1:        
            #     GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding__in =Groupbiddingdetails,IsSelected =0)
            # else:
            #     mobilenumber =User.objects.get(id=userid)
            #     GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding__in =Groupbiddingdetails,IsSelected =0,
            #     SelectedMobileNumber  = int(mobilenumber.username) )

            serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data,'IsAdmin':True,'Response' :False,'Message' :'Bidding is submit or group is not running'},status=200)
            else:
               return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
         
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# save bidding amount of group of individuals
@api_view(['PUT'])
def Save_Group_Bidding(request):
    data=request.data
    try:
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            Usermobilenumber = User.objects.get(id=userid).username
            biddingAmount = (float(data['BiddingAmount']))
            UserMobileNumber = data['MobileNumber']
            id = data['GroupBiddingEntriesID']            
            minloss = GroupBiddingEntries.objects.get(id=id,SelectedMobileNumber = UserMobileNumber).MinCyclelossAmount
            if float(minloss) >= biddingAmount:
                return Response({'Message' : 'Loss not less than' ,'value':minloss})  
            GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber).update(BidlossAmount=biddingAmount,AddedBy =Usermobilenumber)
            GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber)
            serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
            return Response({'Response' :True,'Message':'Bidding save successfully'},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

# Only Admin can select Bidding User
# update user group status to 15 ie bidding close or final
# id is groupbiddingentriesID 
@api_view(['PUT'])
def Select_Group_Bidding(request):
    data=request.data
    try:
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not  None:
            UserMobileNumber = data['MobileNumber']
            id = data['GroupBiddingEntriesID']   
            # Get Select Bidding entries Details        
            GroupBiddingEntriesdetails = GroupBiddingEntries.objects.get(id=id,SelectedMobileNumber = UserMobileNumber)
            
            GroupBiddingDetails  = GroupBidding.objects.get(id=GroupBiddingEntriesdetails.GroupBidding_id)
            GroupUserDetails   =   UserGroup.objects.get(id=GroupBiddingDetails.UserGroup_id) 
            #cal Amount paid by per user
            AmountPaidbyPerUser =int ((GroupBiddingEntriesdetails.TotalAmount - GroupBiddingEntriesdetails.BidlossAmount)/GroupUserDetails.usercount)
            totalbiddingamount = int(AmountPaidbyPerUser * GroupUserDetails.usercount)
            SelectedUserName = GroupBiddingEntriesdetails.selectedName
            if GroupBiddingEntriesdetails.IsSelected == 0:       
                GroupMemberlists = GroupMember.objects.filter(UserGroup = GroupUserDetails)    
                #fill n make group payments history    
                for GroupMemberlist in GroupMemberlists:
                    GroupHistorydata = GroupPaymentHistory(GroupBidding =GroupBiddingDetails,UserName =GroupMemberlist.UserName,
                    Mobilenumber = GroupMemberlist.Mobilenumber,Cyclenumber = GroupBiddingDetails.Cyclenumber,
                    ActualAmount =AmountPaidbyPerUser,UserGroup = GroupUserDetails )
                    GroupHistorydata.save()
                    fromdate = datetime.date.today()   +  timedelta(days=7)    
                    #Send_message('SelectedbiddingAlert',GroupMemberlist.Mobilenumber,GroupUserDetails.groupname ,str(totalamount),str(AmountPaidbyPerUser), str(fromdate) )
                GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber).update(IsSelected=1)    
                GroupBidding.objects.filter(id=GroupBiddingEntriesdetails.GroupBidding_id).update(selectedName=SelectedUserName,SelectedMobileNumber = UserMobileNumber,IsSelected=1,biddingAmount = totalbiddingamount)
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding=GroupBiddingDetails)
                serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
                return Response({'data':serializer.data,'Message':'user selected successfully','Response' :True},status=200)
            else:
                return Response({'Message':"User Already Selected for this cycle",'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# group Payments user list after selection
@api_view(['GET'])
def Group_Payment_User_list_for_user(request):  
    try:  
        token = request.GET.get('token')
        id = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id  
        
        if userid is not None:
            CheckgroupAdmin  = UserGroup.objects.filter(id=id,createBy=userid).count()            
            UserGroupDetails = UserGroup.objects.get(id=id)             
            groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=int(UserGroupDetails.biddgingCycle)).aggregate(id=Max('pk'))
            mobilenumber =User.objects.get(id=userid)
            GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding = groupbiddingdetails['id'],Status =5,
            Mobilenumber  = int(mobilenumber.username) )
            serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
            if len(serializer.data) < 1:               
                return Response({'data':serializer.data[0],'IsAdmin':True,'Response' :False,'Message' :'Payment history not found'},status=200)
            else:
               return Response({'data':serializer.data[0],'Response' :True,'Message':''},status=200)
            
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False},status=200)
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# group Payments user list after selection
@api_view(['GET'])
def Group_Payment_User_list(request):   
    try:  
        token = request.GET.get('token')
        id = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id  
        
        if userid is not None:
            CheckgroupAdmin  = UserGroup.objects.filter(id=id,createBy=userid).count()            
            UserGroupDetails = UserGroup.objects.get(id=id)             
            groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=int(UserGroupDetails.biddgingCycle)).aggregate(id=Max('pk'))
            
            if CheckgroupAdmin == 1:
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding_id = groupbiddingdetails['id'],Status =5)
                serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)       
            else:
                mobilenumber =User.objects.get(id=userid)
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding = groupbiddingdetails['id'],Status =5,
                Mobilenumber  = int(mobilenumber.username) )
                serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
                if len(serializer.data) < 1: 
                    return Response({'data':serializer.data,'IsAdmin':True,'Response' :False,'Message' :'Payment history not found'},status=200)
                else:
                    return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
            
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

# add Recived Amount by admin after user group bidding selected 
@api_view(['PUT'])
def Group_Payments(request):
    data=request.data
    try:
        token = data['token']
        userid = Token.objects.get(key=token).user_id 
        if userid is not None:
            PaidAmount = data['AmountPaid']
            UserMobileNumber = data['MobileNumber']
            id = data['GroupPaymentID']
            GroupPaymentHistorydetails = GroupPaymentHistory.objects.get(id=id,Mobilenumber = UserMobileNumber)
            usergrupdetail  = UserGroup.objects.get(id=GroupPaymentHistorydetails.UserGroup_id)
            groupbiddingdetails = GroupBidding.objects.filter(UserGroup = usergrupdetail,Cyclenumber=int(usergrupdetail.biddgingCycle)).aggregate(id=Max('pk'))
            groupcreatemobile = User.objects.get(username = usergrupdetail.createBy)
            loginusermobie = User.objects.get(id = userid)    
            recivedflag = 0
            
            if groupcreatemobile.username == loginusermobie.username:
                recivedflag =1
                Send_message('PaymentRecived',UserMobileNumber,PaidAmount , str(groupcreatemobile.username),str(groupcreatemobile.username))

            if GroupPaymentHistorydetails.Status == 5:
                totalAmountDue = int(GroupPaymentHistorydetails.ActualAmount) - int(PaidAmount)
                GroupPaymentHistory.objects.filter(id=id,GroupBidding_id=groupbiddingdetails['id'],Mobilenumber = UserMobileNumber).update(AmountPaid=PaidAmount,AmountDue=totalAmountDue,
                                                IsReceived = recivedflag )
            if recivedflag == 1:
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding_id = groupbiddingdetails['id'],Status =5)
                serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)       
            else:
                mobilenumber =User.objects.get(id=userid)
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding = groupbiddingdetails['id'],Status =5,
                Mobilenumber  = int(mobilenumber.username) )
                serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
            if len(serializer.data) < 1: 
                return Response({'data':serializer.data,'Response' :False,'Message' :'Group Payments list not found'},status=200)
            else:
                return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
           
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

    


# get Selected user list for current cycle
@api_view(['get'])
def Selected_User(request):    
    try:
        token = request.GET.get('token')
        id  = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            Usermobilenumber = User.objects.get(id=userid).username
            usergroupdetails=  UserGroup.objects.get(id=id,createBy=userid)
            selecteduser = GroupBidding.objects.filter(Cyclenumber=usergroupdetails.biddgingCycle,
                            UserGroup=usergroupdetails,IsSelected = 1)[0]
            serializer = GroupBiddingSerializer(selecteduser)
            if len(serializer.data) < 1: 
                return Response({'data':serializer.data,'Response' :False,'Message' :'Bidding is not selected yet'},status=200)
            else:
                return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
           

            # return Response({"data":selecteduser.SelectedMobileNumber},status=200)
            # GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(id=id,Mobilenumber = UserMobileNumber)[0]
            # totalAmountDue = int(GroupPaymentHistorydetails.ActualAmount) - int(PaidAmount)
            # GroupPaymentHistory.objects.filter(GroupBidding_id=id,Mobilenumber = UserMobileNumber).update(AmountPaid=PaidAmount,AmountDue=totalAmountDue)
            # return Response({'Message' :"Payemts successfully",'Response' :True},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :True})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

# Send Amount to the user who is selected
@api_view(['PUT'])
def Send_Amount(request):
    data=request.data
    try:
        token = data['token']
        id  = data['GroupID']
        AmountSendtoUser  = data['AmountSend']
        userid = Token.objects.get(key=token).user_id  
        if userid is not None:            
            CheckgroupAdmin  = UserGroup.objects.get(id=id,createBy=userid) 
            if CheckgroupAdmin.usercount is not None:
                
                UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
                biddingcycle = UserGroupDetails.biddgingCycle                            
                groupbiddingDetail = GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle)[0]
                
                Amountdetails = AmountRecived(UserGroup = UserGroupDetails,ActualAmount= groupbiddingDetail.biddingAmount ,ActualRecived= groupbiddingDetail.biddingAmount ,
                                Cyclenumber = biddingcycle,RevicerName = groupbiddingDetail.selectedName,Amountsend =AmountSendtoUser,
                                Recivermobile =groupbiddingDetail.SelectedMobileNumber ,RecivedDate= datetime.datetime.today())
                Amountdetails.save()
                
                GroupPaymentHistory.objects.filter(UserGroup = UserGroupDetails).update(Status = 20)
                # 15 means bidding cycle close amount recived but group still is in active state
                GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle).update(BiddingStatus=20)
                if biddingcycle == CheckgroupAdmin.usercount:
                    # 20 means group close all cycle complete 
                    UserGroup.objects.filter(id=id,createBy=userid).update(groupStatus = 20)
                    GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle).update(BiddingStatus=20)
                else:
                    UserGroup.objects.filter(id=id,createBy=userid).update(groupStatus = 10,biddingdate = CheckgroupAdmin.biddingdate + datetime.timedelta(30),biddgingCycle =biddingcycle+1)
                return Response({'Message' :"Payemts successfully",'Response' :True},status=200)
            else:
                return Response({'Message' :"You dont have permission to send amount",'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


# get Gruop Payments history
@api_view(['Get'])
def Group_Payments_History(request):   
    try:
        token = request.GET.get('token')
        userid = Token.objects.get(key=token).user_id
        id = request.GET.get('GroupID')
        if userid is not None:
            Usermobilenumber = User.objects.get(id=userid).username
            admincheck  = UserGroup.objects.filter(id=id,createBy =userid).count()
            UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
            if admincheck == 0:
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(UserGroup = UserGroupDetails,Mobilenumber =Usermobilenumber)
            else:
                GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(UserGroup = UserGroupDetails)          
        
            serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails,many=True)
            if len(serializer.data) < 1: 
                return Response({'data':serializer.data,'Response' :False,'Message' :'Payments history not found'},status=200)
            else:
                return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
           
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


@api_view(['Get'])
def Group_AmountReceived_History(request):    
    try:
        token = request.GET.get('token')
        id = request.GET.get('GroupID')
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            Usermobilenumber = User.objects.get(id=userid).username
            admincheck  = UserGroup.objects.filter(id=id,createBy =userid).count()
            UserGroupDetails=  UserGroup.objects.get(id=id)
            # if admincheck == 0:
            #     GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(UserGroup = UserGroupDetails,Recivermobile =Usermobilenumber)
            # else:
            #     GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(Mobilenumber =Usermobilenumber)          
            GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(UserGroup = UserGroupDetails)
            serializer = GroupAmountRecivedSerializer(GroupAmountRecivedHistorydetails,many=True)
            if len(serializer.data) < 1: 
                return Response({'data':serializer.data,'Response' :False,'Message' :'Amount recived history not found'},status=200)
            else:
                return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
           
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

import base64

@api_view(['PUT'])
def Update_Profile(request):
    data = request.data
    try: 
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            ProfilePhoto = data['ProfilePic']
            user = User.objects.get(id=userid)  

            if len(ProfilePhoto) > 100: 
                random = randint(1001, 9999) 
                user = User.objects.get(id=userid)               
                format, imgstr = ProfilePhoto.split(';base64,')  # format ~= data:image/X,                       
                ext = format.split('/')[-1]  # guess file extension
                dynamicname = str(user.username) + str(random)               
                ProfilePic.objects.filter(User=user).delete()
                imageuploaded = ContentFile(base64.b64decode(imgstr), name= dynamicname + '.' + ext)                                
                UserDetailphoto =  ProfilePic(User=user,ProfilePic=imageuploaded)
                UserDetailphoto.save()
            else:
                ProfilePic.objects.filter(User=user).delete()                                               
                UserDetailphoto =  ProfilePic(User=user,ProfilePic='')
                UserDetailphoto.save()
            
            Userdata = User.objects.get(id = userid)
            userprofiledetails = ProfilePic.objects.get(User=Userdata)
            serializerprofile = ProfilePicSerializer(userprofiledetails)

            return Response({'Response' :True,'pic_url':serializerprofile.data['ProfilePic'],'Message':'Profile pic update successfully'},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})
    


@api_view(['PUT'])
def Update_UserDetails(request):
    data = request.data
    try:      
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            AlternateMobileNumber = data['AlternateMobileNumber']                  
            DateofBirth = data['DateofBirth']   
            userid = Token.objects.get(key=token).user_id
            user = User.objects.get(id=userid)                    
            UserDetails.objects.filter(User_id=userid).update(AlternateMobileNumber=AlternateMobileNumber,DateofBirth=DateofBirth)
            UserDetailsupdate = UserDetails.objects.get(User_id=userid)            
            firstname = data['first_name']
            lastname = data['last_name']
            email = data['email']
            userid = Token.objects.get(key=token).user_id
            User.objects.filter(id=userid).update(first_name = firstname,last_name = lastname,email =email)
            return Response({'Response' :True,'Message':'Profile update successfully'},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

@api_view(['GET'])
def Get_UserDetails(request):
    data = request.data
    try:        
        token = request.GET.get('token')
        userid = Token.objects.get(key=token).user_id          
        Userdata = User.objects.get(id = userid)
        userprofiledetails = UserDetails.objects.filter(User=Userdata)
        serializer = ProfileSerializer(Userdata)
        UserDetailsupdate = UserDetails.objects.get(User_id=userid)
        serializerprofile = UserDetailsSerializer(UserDetailsupdate)
        return Response({'data':serializer.data,'Profiledata':serializerprofile.data,'Response' :True,'Message':''},status=200)
    
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})



@api_view(['Get'])
def Get_Terms_Condition(request):    
    try: 
        token = request.GET.get('token')       
        userid = Token.objects.get(key=token).user_id
        if userid is not None:      
            data={
                
            'privacypolicy' : """ \nThis Privacy Policy explains and governs how Kametee Pvt. Ltd. (hereinafter "Company", "we", "our" or  "us") treats the Personal Information collected, used and disclosed by you on any of your use of our Website or Application (collectively, the "Services") or when you otherwise interact with us, including your Personal Information. "Personal Information" is defined as any information that relates to a natural person, that would be you if you are an individual), which, either directly or indirectly, in combination with other information, is capable of identifying such person. We may change this Privacy Policy from time to time. If we make changes, we will notify you by revising the date at the top of the policy and, in some cases, we may provide you with more prominent notice (such as adding a statement to our homepage or sending you an email notification).
                 We encourage you to review the Privacy Policy whenever you access the Services to stay informed about our information practices and the ways you can help protect your privacy. \n
                 All the capitalized terms used in the Privacy Policy, if not otherwise defined, will have the same meaning as in our Terms of Use. 
                    1: Nature of Personal Information Collected
                       We collect some Personal Information when you register with us, such as your name, address, phone number, email address, birth date, gender, pin code, occupation, industry and personal preferences and interests relevant to us. Once you register with us and sign in to our Services, we automatically receive and record information on our server logs from your browser, including your IP address, cookie information, and the page you request.
                       All the capitalized terms used in the Privacy Policy, if not otherwise defined, will have the same meaning as in our Terms of Use.

                    2: Use of Personal Information
                       We shall not sell your Personal Information. The information you provide to us or we collect is used for the customization of Services or content to your requirement, providing the Services, communicate with you, conduct research and improve our Services, [and provide anonymous, aggregated reporting for internal and external clients]. \n

                    3: Confidentiality and Security
                       We provide the Services through secure servers and all data collected in course of your use of the Services is stored and controlled on servers located in Hyderabad, India and USA. We have stringent security measures in place to protect the loss, misuse, and alteration of the information under our control. Once your information is in our possession we adhere to strict security guidelines, protecting it against unauthorized access.\n
                       We limit access to Personal Information about you to employees, affiliates and/or persons who we believe reasonably need that information to provide services to you or in order to operate and improve the Services. \n

                    4: Accessing, Changing and Protecting Your Information
                       You can access and edit your account information at any time. While you are our Member, we will send you certain communications relating to the service, such as service announcements, administrative messages and a newsletter. These communications are considered as part of your account, and you can opt out of receiving them by updating your account settings or only opt-out of receiving them by deleting your account with us. You can delete your account by contacting us or visiting your account page.\n

                    5: Disclosure of Your Personal Information
                       We may be required to disclose information collected by us, including your Personal Information, to comply with our legal obligations or requests from law enforcement agencies, to resolve any disputes that we may have with any of our users, and enforce our agreements with third parties, or to carry out any other purpose for which the information was collected. We may also share aggregated or de-identified information, which cannot reasonably be used to identify you. The Service may offer social sharing features and other integrated tools (such as the Facebook "Like" button), which let you share actions you take on the Service with other media, and vice versa. The use of such features enables the sharing of information with your friends or the public, depending on the settings you establish with the entity that provides the social sharing feature. For more information about the purpose and scope of data collection and processing in connection with social sharing features, please visit the privacy policies of the entities that provide those features. We may also share our users' information with any successor in interest if the Company is acquired by or merged with another company, or sells a significant portion of its assets, or all of its assets, to any third party.\n

                    6: Consent
                       By using the Services by providing your information, you consent to the collection and use of the information you disclose on the Website in accordance with this Privacy Policy, including but not limited to your consent for sharing your information as per this privacy policy. If we decide to change our privacy policy, we will post those changes on this page so that you are always aware of what information we collect, how we use it, and under what circumstances we disclose it.\n

                    7: Grievance Officer
                        In accordance with Information Technology Act 2000 and rules made there under, the name and contact details of the Grievance Officer are provided below: \n                       
                    Manish Chaudhary \n
                    Kametee Pvt. Ltd.\n
                    Phone: +91 8279463818\n
                    Email: chaudhary94rc@gmail.com \n
                    C-603, Amarapali Empire, \n
                    Crossing Republic, Ghaziabad \n            
            """,
            'TermsCondition' : """\nIMPORTANT - READ THESE TERMS CAREFULLY BEFORE DOWNLOADING, INSTALLING OR USING THIS SOFTWARE. BY DOWNLOADING OR INSTALLING THIS SOFTWARE, YOU ACKNOWLEDGE THAT YOU HAVE READ THIS LICENSE AGREEMENT, THAT YOU UNDERSTAND IT, AND THAT YOU AGREE TO BE BOUND BY ITS TERMS. IF YOU ARE ENTERING INTO THIS AGREEMENT ON BEHALF OF A COMPANY OR OTHER LEGAL ENTITY, YOU REPRESENT THAT YOU HAVE THE AUTHORITY TO BIND SUCH ENTITY AND ITS AFFILIATES TO THESE TERMS AND CONDITIONS, IN WHICH CASE THE TERMS "YOU" OR "YOUR" SHALL REFER TO ITS AFFILIATES. IF YOU DO NOT HAVE SUCH AUTHORITY,OR IF YOU DO NOT AGREE WITH THESE TERMS AND CONDITIONS, YOU MUST NOT DOWNLOAD OR INSTALL THIS SOFTWARE.\n
                            . Grant of Software License for Free Trial Period\n
                                Subject to the terms and conditions and except as otherwise provided in this License Agreement, Kamitee grants to you a limited, non­ exclusive, non-transferable and non-assignable license to evaluate Kamitee software, modules, and feature(s) (the "Software") for Your personal purposes only. As used herein the "Software" is subject to licenses,you do not have any rights in or to the Software except as expressly granted in this License Agreement. Kametee retains all copyright, trademarks, patent, and other intellectual property rights to the Software. You acknowledge that the Software, all copies of the Software, any derivative works, compilations, and collective works of the Software, and any know-how and trade secrets related to the Software are the sole and exclusive property of Kametee Private Limited and contain Kamitee's confidential and proprietary materials \n
                            . General Limitations\nExcept as otherwise expressly provided under this License Agreement, you shall have no right, and you specifically agree not to: \n

                               a: Utilize the Software beyond the applicable Term;\n
                               b: Transfer, assign or sublicense Your license rights to any other person, and any such attempted transfer, assignment or sublicense shall be void; \n
                               c: Provide, divulge, disclose, or make available to, or permit the use of the Software by any third party; \n
                               d: Sell, resell, license, sublicense, distribute, rent or lease the Software or include the Software in a service bureau or outsourcing offering; \n
                               e: Make error corrections to or otherwise modify or adapt the Software or create derivative works based upon the Software, or to permit third parties  to do the same; \n
                               f: Decompile, decrypt, reverse engineer, disassemble or otherwise reduce the Software to human-readable form, or to permit third parties to do the same; \n
                               g: Circumvent or disable any features or technological protection measures in the Software;\n

                            . Limited Warranty & Limitation of Liability\n THE SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. ALL EXPRESS, IMPLIED OR STATUTORY CONDITIONS,REPRESENTATIONS, AND WARRANTIES INCLUDING,WITHOUT LIMITATION, ANY IMPLIED WARRANTY OR CONDITION OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON­ INFRINGEMENT, SATISFACTORY QUALITY OR ARISING FROM A COURSE OF DEALING, LAW, USAGE, OR TRADE PRACTICE, ARE HEREBY EXCLUDED TO THE MAXIMUM EXTENT ALLOWED BY APPLICABLE LAW. NEITHER KAMITEE NOR ITS LICENSORS SHALL BE LIABLE FOR YOUR ACTION, OR FAILURE TO ACT, IN RELIANCE ON ANY INFORMATION FURNISHED AS PART OF THE SOFTWARE. 
                                YOU ARE SOLELY RESPONSIBLE FOR MAINTAINING THE SECURITY OF YOUR NETWORK AND COMPUTER SYSTEMS. NEITHER KAMITEE NOR ITS LICENSORS REPRESENT, WARRANT, OR GUARANTEE THAT (A) SECURITY THREATS, MALICIOUS CODE AND/OR VULNERABILITIES WILL BE IDENTIFIED, OR (B) THE CONTENT WILL RENDER YOUR NETWORK AND SYSTEMS SAFE FROM MALICIOUS CODE, VULNERABILITIES, INTRUSIONS, OR OTHER SECURITY BREACHES, (C) EVERY VULNERABILITY ON EVERY TESTED SYSTEM OR APPLICATION WILL BE DISCOVERED, OR (D) THERE WILL BE NO FALSE POSITIVES.
                                IN NO EVENT WILL KAMITEE OR ITS LICENSORS BE LIABLE TO YOU OR YOUR EMPLOYEES, OR ANY THIRD PARTY, FOR ANY LOST REVENUE, PROFIT, OR DATA, BUSINESS INTERRUPTION, OR FOR SPECIAL, INDIRECT, CONSEQUENTIAL, INCIDENTAL, OR PUNITIVE DAMAGES, HOWEVER CAUSED AND REGARDLESS OF THE THEORY OF LIABILITY ARISING OUT OF THE USE OF OR INABILITY TO USE THE SOFTWARE EVEN IF KAMITEE HAVE BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.IN NO EVENT SHALL KAMITEE BE LIABLE TO YOU, WHETHER IN CONTRACT, WARRANTY OR TORT (INCLUDING NEGLIGENCE OR STRICT LIABILITY),OR OTHERWISE EXCEED THE FEE PAID BY YOU.\n

                            . Term and Termination \n
                                This License Agreement is effective until terminated or the end of the Term. You may terminate this License Agreement at any time (i) by destroying all copies of Software, related documentation, analysis data and report and purging same from memory devices (required at the end of a Term). Your rights under this License Agreement will terminate immediately without notice from Kamitee if you fail to comply with any provision of this Agreement. Upon any termination, you must destroy all copies of Software and related documentation and purge same from memory devices. All provisions of this License Agreement relating to disclaimers of warranties, limitation of liabilities, remedies, damages protection of information and shall survive termination. \n

                              """
            }
            return Response({'data':data,'Response' :True,'Message':''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
        
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})




@api_view(['Put'])
def ChangePassword(request):    
    try: 
        data = request.data
        token = data['token']
        oldpassword = data['oldpassword']
        newpassword = data['newpassword']
        userid = Token.objects.get(key=token).user_id
        Userdata = User.objects.get(id = userid)
        user = authenticate(request, username=Userdata.username, password=oldpassword)
        if user is not None: 
            userdata =  User.objects.get(id=userid) 
            userdata.set_password(newpassword)
            userdata.save()           
            return Response({'Response' :True,'Message':'Password Update Successfully'},status=200)
        else:
            return Response({'Message' : 'Password Mismatch','Response' :False})
        
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

