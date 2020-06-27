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
    return True
    # if payloads is not None:
    #     header = {"content-type": "application/json"}
    #     conn.request("POST", "/API/V1/5e31f7cf-8dd5-11ea-9fa5-0200cd936042/ADDON_SERVICES/SEND/TSMS", payloads)
    #     res = conn.getresponse()
    #     data = res.read()        
    #     return data.decode("utf-8")
    # else:
    #     return True

# OTP generate to send for number verificaiton
@api_view(['POST'])
def OTP_Generate(request):
    data=request.data
    MobileNo = data['MobileNumber']
    random = randint(1001, 9999)
    usercheck  =  User.objects.filter(username = MobileNo)    
    if usercheck.count() > 0:
        data = Send_message('OTPVerification',MobileNo,random)    
        return Response({"radomno": random,'Response' : True}, status=200)
    else:
        return Response({"radomno": random,'Response' : False,'Message' : 'You No already exist in our system'}, status=200)

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
    return Response({"radomno": random ,'Response' : data}, status=200)

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
    return Response({"token": token.key,'Response' : True}, status=200)

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
        return Response({"token": token.key,'loginstatus':True,'Response' : True,'Message' :''}, status=200)
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
def groupmember_list(request,id):
    
    try:
        token = request.GET.get('token')
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            GroupMemberlist = GroupMember.objects.filter(UserGroup_id=id)
            serializer = GroupMemberSerializer(GroupMemberlist,many=True)
            return Response({'Memberlist':serializer.data,'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})


#update gruop member list when group is in open state ie: 5
@api_view(['PUT','DELETE'])
def groupmember_update(request,id):
    data=request.data
    try:
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            Mobilenumber = data['MobileNumber']
            UserName = data['UserName']
            status = UserGroup.objects.get(id__in=GroupMember.objects.filter(id=id).values('UserGroup_id')).groupStatus
            UsergroupID = GroupMember.objects.filter(id=id).values('UserGroup_id')[0]  
            checkuserexist  = GroupMember.objects.filter(UserGroup_id=UsergroupID['UserGroup_id'],Mobilenumber = Mobilenumber).count()
           
            if status == 5:
                if request.method == 'PUT':
                    if checkuserexist > 0:
                         GroupMemberupdate =  GroupMember.objects.filter(id=id).update(UserName=UserName)
                    else:
                        GroupMemberupdate =  GroupMember.objects.filter(id=id).update(Mobilenumber=Mobilenumber,UserName=UserName)
                    return Response({'Message' :"User update successfully "},status=200)
                else:
                    GroupMember.objects.filter(id=id).delete()
                    return Response({'Message' :"User Deleted successfully ",'Response' :True},status=200)
            else:
                return Response({'Message' :"Group no longer in open state",'Response' :True})
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :True})
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
        return Response({'chatdata':serializer.data,'Response' :True},status=200)                  
        
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
                return Response({'data':serializer.data,'Response' :True})   
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
            return Response({'GruopList':serializer.data,'Response' :True},status=200)
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
                return Response({'GroupList':serializer.data,'Response' :True},status=200)
            else:
                return Response({'Message' :"Group can't be termenated because it already in running state"},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system'},status=200)
    except Exception as e:
        return Response({'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

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
            return Response({'data':serializer.data,'IsAdmin':False,'Response' :True},status=200)
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
            return Response({'data':serializer.data,'IsAdmin':True,'Response' :True},status=200)
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
            return Response({'data':serializer.data,'Response' :True},status=200)
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
            UserGroupDetails = UserGroup.objects.filter(id=id,createBy=userid)
            UserGroup_id = UserGroup.objects.get(id=id,createBy=userid)
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
            biddingAmount = data['BiddingAmount']
            UserMobileNumber = data['MobileNumber']
            id = data['GroupBiddingEntriesID']
            minloss = GroupBiddingEntries.objects.get(id=id,SelectedMobileNumber = UserMobileNumber).MinCyclelossAmount
            if int(minloss) > int(biddingAmount):
                return Response({'Message' : 'Loss not less than' ,'value':minloss})  
            
            GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber).update(BidlossAmount=biddingAmount,AddedBy =Usermobilenumber)
            GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber)
            serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
            return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
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
            return Response({'data':serializer.data,'Response' :True},status=200)
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
            return Response({'data':serializer.data,'Message':'Payments done Successfully','Response' :True},status=200)
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
            return Response({'data':serializer.data,'Message':'','Response' :True},status=200)

            return Response({"data":selecteduser.SelectedMobileNumber},status=200)
            GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(id=id,Mobilenumber = UserMobileNumber)[0]
            totalAmountDue = int(GroupPaymentHistorydetails.ActualAmount) - int(PaidAmount)
            GroupPaymentHistory.objects.filter(GroupBidding_id=id,Mobilenumber = UserMobileNumber).update(AmountPaid=PaidAmount,AmountDue=totalAmountDue)
            return Response({'Message' :"Payemts successfully",'Response' :True},status=200)
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
            UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
            # if admincheck == 0:
            #     GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(UserGroup = UserGroupDetails,Recivermobile =Usermobilenumber)
            # else:
            #     GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(Mobilenumber =Usermobilenumber)          
            GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(UserGroup = UserGroupDetails)
            serializer = GroupAmountRecivedSerializer(GroupAmountRecivedHistorydetails,many=True)
            return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
        else:
            return Response({'Message' : 'Token Not found in our system','Response' :False})
    except Exception as e:
        return Response({'Response' :False,'Message' : 'Something Went worng either token or variable name format','ErrorMessage':str(e)})

import base64

@api_view(['PUT'])
def Update_UserDetails(request):
    data = request.data
    try:      
        token = data['token']
        userid = Token.objects.get(key=token).user_id
        if userid is not None:
            AlternateMobileNumber = data['AlternateMobileNumber']
            ProfilePhoto = data['ProfilePic']                     
            format, imgstr = ProfilePhoto.split(';base64,')  # format ~= data:image/X,            
            ext = format.split('/')[-1]  # guess file extension
            imageuploaded = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)            
            DateofBirth = data['DateofBirth']   
            userid = Token.objects.get(key=token).user_id
            user = User.objects.get(id=userid)
            #UserDetails.objects.filter(User_id=userid).update(ProfilePic=ProfilePhoto,AlternateMobileNumber=AlternateMobileNumber,DateofBirth=DateofBirth)
            UserDetails.objects.filter(User_id=userid).delete()
            UserDetailphoto =  UserDetails(User=user,ProfilePic=imageuploaded,AlternateMobileNumber=AlternateMobileNumber,DateofBirth=DateofBirth)
            UserDetailphoto.save()
            UserDetailsupdate = UserDetails.objects.get(User_id=userid)
            serializer = UserDetailsSerializer(UserDetailsupdate)
            firstname = data['first_name']
            lastname = data['last_name']
            email = data['email']
            userid = Token.objects.get(key=token).user_id
            User.objects.filter(id=userid).update(first_name = firstname,last_name = lastname,email =email)
            return Response({'data':serializer.data,'Response' :True,'Message':''},status=200)
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
            'TermsCondition' :  'Hi Duresh',
            'privacypolicy' : 'Hi Manish'
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

