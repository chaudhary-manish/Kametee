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
        payloads = json.dumps({"From": "KameTi","To": Phone_number,"VAR1": var1, "TemplateName": "PaymentRecived"})
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

@api_view(['POST'])
def OTP_Generate(request):
    data=request.data
    MobileNo = data['MobileNumber']
    random = randint(1001, 9999)
    data = Send_message('OTPVerification',MobileNo,random)    
    return Response({"radomno": random,'Response' : data}, status=200)

@api_view(['POST'])
def OTP_Generate_SendAmount(request):
    data=request.data
    MobileNo = data['MobileNumber']
    random = randint(1001, 9999)
    return Response({"radomno": random}, status=200)

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
    return Response({"token": token.key,'Response' : data}, status=200)

#@login_required(login_url="/login/")
@api_view(['POST'])
def logout_user(request):
    data=request.data
    token = data['token']
    token_destroy = Token.objects.get(key=token)
    token_destroy.delete()
    logout(request)
    return  Response("User Logout Successfully")

# login user 
@api_view(['POST'])
def login_user(request):
    data=request.data
    #return Response(data)
    serializer = LoginSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    login(request, user)
    token, created = Token.objects.get_or_create(user=user)
    return Response({"token": token.key}, status=200)

# login user 
@api_view(['POST'])
def forget_password(request):
    data=request.data
    #return Response(data)  
    MobileNo = data['MobileNumber']   
    Password = data['Password'] 
    userexist = User.objects.filter(username = MobileNo).count()
    if userexist != 0:   
        userdata =  User.objects.get(username=MobileNo) 
        userdata.set_password(Password)
        userdata.save()
        passnew =  User.objects.get(username=MobileNo).password
        return Response({"Message": 'Password Update successfully'}, status=200)
    else:
        return Response({"Message": 'User not exist in system'}, status=200)


   

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
            return self.retrieve(request, id)
        else:
            return self.list(request)

    def post(self, request):
        return self.create(request)

    def perform_create(self, serializer):
        usergroup = serializer.save(createBy=self.request.user)
        Userdetail =  User.objects.get(username=self.request.user)
        GroupUser =GroupMember(UserGroup=usergroup,Mobilenumber=Userdetail.username,UserName=Userdetail.first_name,isAdmin =1)
        GroupUser.save()
        Send_message('groupregistration',Userdetail.username,usergroup.groupname , str(usergroup.AmountPerUser) ,str(usergroup.startDate))        

    def put(self, request, id=None):
        return self.update(request, id)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)        

    def delete(self, request, id=None):
        return self.destroy(request, id)

#Add Member to Group
@login_required(login_url="/login")
@api_view(['POST'])
def adduser_togroup(request):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    serializer = AddGroupUserSerializer(data=data,context={'user_id':userid})
    serializer.is_valid(raise_exception=True)
    usergroup =  UserGroup.objects.get(id=GroupID)
    Send_message('groupregistration',Userdetail.username,usergroup.groupname , str(usergroup.AmountPerUser) ,str(usergroup.startDate))
    return Response(serializer.data)

#get User list of Group BY ID
@api_view(['get'])
def groupmember_list(request,id):
    data=request.data
    token = data['token']
    GroupMemberlist = GroupMember.objects.filter(UserGroup_id=id)
    serializer = GroupMemberSerializer(GroupMemberlist,many=True)
    return Response(serializer.data)

@api_view(['PUT','DELETE'])
def groupmember_update(request,id):
    data=request.data
    token = data['token']
    Mobilenumber = data['MobileNumber']
    UserName = data['UserName']
    status = UserGroup.objects.get(id__in=GroupMember.objects.filter(id=id).values('UserGroup_id')).groupStatus
    if status == 5:
        if request.method == 'PUT':
            GroupMemberupdate =  GroupMember.objects.filter(id=id).update(Mobilenumber=Mobilenumber,UserName=UserName)
        else:
            GroupMember.objects.filter(id=id).delete()

        GroupMemberlist = GroupMember.objects.filter(UserGroup_id__in =
                    GroupMember.objects.filter(id=id).values('UserGroup_id'))
        serializer = GroupMemberSerializer(GroupMemberlist,many=True)
        return Response(serializer.data)
    else:
        return Response("Group no longer in open state")

# to start group group of first time insert bidding date concept 
@api_view(['PUT'])
def Group_Start(request,id = None):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    GroupDetaildetails = UserGroup.objects.get(id=id,createBy = userid )
    if int(GroupDetaildetails.groupStatus) == 5 and int(GroupDetaildetails.biddingflag) == 0:
        groupmembercount = GroupMember.objects.filter(UserGroup_id = id).count()
        UserGroup.objects.filter(id=id,createBy = userid ).update(usercount=groupmembercount,groupStatus=10,biddingdate = datetime.datetime.today())
        Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
        serializer = StatEndGroupUserSerializer(Groupdetail)
        return Response(serializer.data)   
    else:
        return Response(" User Group Already Start") 



@api_view(['PUT'])
def Group_End(request,id = None):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    GroupDetail = UserGroup.objects.filter(id=id,createBy = userid ).update(groupStatus=20,biddingflag = 0)
    Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
    serializer = StatEndGroupUserSerializer(Groupdetail)
    return Response(serializer.data)

# terminate group if it is  in open state
@api_view(['PUT'])
def Group_Terminate(request,id = None):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    status = UserGroup.objects.filter(id=id,createBy = userid ).values('groupStatus')
    if status == 5:
        GroupDetail = UserGroup.objects.filter(id=id,createBy = userid ).update(groupStatus=25)
        Groupdetail = UserGroup.objects.get(id=id,createBy = userid )
        serializer = StatEndGroupUserSerializer(Groupdetail)
        return Response(serializer.data)
    else:
        return Response("Group can't be termenated because it already in running state")

# get group list by group status got both group Admin and regular admin
@api_view(['GET'])
def Get_Group_ByStatus(request,status = None):
    data=request.data
    GroupDetail= {}
    token = data['token']
    if status is None:
        status = 10
    userid = Token.objects.get(key=token).user_id
    usermobilenumber = User.objects.get(id=userid).username
    GroupDetail = UserGroup.objects.filter(groupStatus=status,id__in =
                   GroupMember.objects.filter(Mobilenumber = usermobilenumber).values('UserGroup'))
    serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
    return Response(serializer.data)


# let list of group for managing  this only fetch for admin only
@api_view(['GET'])
def Manage_Group_ByStatus(request,status = None):
    data=request.data
    GroupDetail= {}
    token = data['token']
    if status is None:
        status = 10
    userid = Token.objects.get(key=token).user_id
    GroupDetail = UserGroup.objects.filter(groupStatus=status, createBy = userid)
    serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
    return Response(serializer.data)


#
@api_view(['GET'])
def Group_Bidding(request):
    data=request.data
    GroupDetail= {}
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    GroupDetail = UserGroup.objects.filter(Q(biddingdate__isnull=True) | Q(biddingdate__lte = datetime.datetime.today())  ,
    Q(groupStatus=5) | Q(groupStatus = 15), createBy = userid )
    serializer = StatEndGroupUserSerializer(GroupDetail, many = True)
    return Response(serializer.data)


# only admin can activate group admin
@api_view(['PUT'])
def Start_Group_Bidding(request,id):
    if id is None:
        return Response("Group ID requried")    
    data=request.data
    GroupDetail= {}
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    UserGroupDetails = UserGroup.objects.get(id=id)
    # check weather group biddings are still in progress or finished
    biddinggruopStatus = GroupBidding.objects.filter(UserGroup = UserGroupDetails).values('BiddingStatus')
    # if len(biddinggruopStatus) == 0:
    #     groupbiddingstatus =5
    # else:
    #    groupbiddingstatus = biddinggruopStatus[0]['BiddingStatus']
    if UserGroupDetails.groupStatus == 10:
        biddingcycle = UserGroupDetails.biddgingCycle
        if biddingcycle == 1:
            GroupMemberlists = GroupMember.objects.filter(UserGroup = UserGroupDetails)
        else:
            GroupMemberlists = GroupMember.objects.filter(UserGroup = UserGroupDetails).exclude(
                                Mobilenumber__in = GroupBidding.objects.filter(UserGroup = UserGroupDetails,IsSelected =1
                                ).values('SelectedMobileNumber'))  
        insertgroupbidding = GroupBidding(UserGroup = UserGroupDetails,ActualAmount=UserGroupDetails.AmountPerUser,
                            Cyclenumber =(biddingcycle),biddingAmount = 0,BiddingStatus=10)
        insertgroupbidding.save()
        
        for GroupMemberlist in GroupMemberlists:
            GroupBiddingEntriesdata = GroupBiddingEntries(GroupBidding =insertgroupbidding,selectedName =GroupMemberlist.UserName,
            SelectedMobileNumber = GroupMemberlist.Mobilenumber,Cyclenumber = (biddingcycle + 1))
            GroupBiddingEntriesdata.save()
            fromdate = datetime.today()
            todate  = fromdate + timedelta(days=5)
            Send_message('Startbiddingalert',Userdetail.username,usergroup.groupname , fromdate ,todate)

        UserGroup.objects.get(id=id).update(groupStatus = 15)
        return Response("data save succefully")
    else:
        return Response("Previous bidding already in progres")


# fetch data for admin and single user of particular group
@api_view(['GET'])
def Group_Bidding_User_list(request,id):
    data=request.data
    GroupDetail= {}
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    UserGroupDetails = UserGroup.objects.filter(id=id,createBy=userid)
    UserGroup_id = UserGroup.objects.get(id=id,createBy=userid)
    Groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroup_id,IsSelected =0)
    #userid = Token.objects.get(key=token).user_id
    GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding__in =Groupbiddingdetails,IsSelected =0)
    # if UserGroupDetails.count() == 1:        
    #     GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding__in =Groupbiddingdetails,IsSelected =0)
    # else:
    #     mobilenumber =User.objects.get(id=userid)
    #     GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(GroupBidding__in =Groupbiddingdetails,IsSelected =0,
    #     SelectedMobileNumber  = int(mobilenumber.username) )

    serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
    return Response(serializer.data)

# save bidding amount of group of individuals
@api_view(['PUT'])
def Save_Group_Bidding(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    Usermobilenumber = User.objects.filter(id=userid).username
    biddingAmount = data['BiddingAmount']
    UserMobileNumber = data['MobileNumber']
    GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber).update(biddingAmount=biddingAmount,AddedBy =Usermobilenumber)
    GroupBiddingEntriesdetails = GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber)
    serializer = GroupBiddingEntriesSerializer(GroupBiddingEntriesdetails, many = True)
    return Response(serializer.data)


# Only Admin can select Bidding User
# update user group status to 15 ie bidding close or final
# id is groupbiddingentriesID 
@api_view(['PUT'])
def Select_Group_Bidding(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    UserMobileNumber = data['MobileNumber']   
    # Get Select Bidding entries Details
    GroupBiddingEntriesdetails = GroupBiddingEntries.objects.get(id=id,SelectedMobileNumber = UserMobileNumber)
    biddingValue = GroupBiddingEntriesdetails.biddingAmount
    SelectedUserName = GroupBiddingEntriesdetails.selectedName
    if GroupBiddingEntriesdetails.IsSelected == 0:
        GroupBiddingDetails = GroupBidding.objects.get(id=GroupBiddingEntriesdetails.GroupBidding_id)
        GroupUserDetails = UserGroup.objects.get(id=GroupBiddingDetails.UserGroup_id)
        #cal Amount paid by per user 
        AmountPerUserPaid = int(biddingValue) / int(GroupUserDetails.usercount)
        
        GroupMemberlists = GroupMember.objects.filter(UserGroup = GroupUserDetails)
        
        for GroupMemberlist in GroupMemberlists:
            GroupHistorydata = GroupPaymentHistory(GroupBidding =GroupBiddingDetails,UserName =GroupMemberlist.UserName,
            Mobilenumber = GroupMemberlist.Mobilenumber,Cyclenumber = GroupBiddingDetails.Cyclenumber,
            ActualAmount =AmountPerUserPaid,UserGroup = GroupUserDetails )
            GroupHistorydata.save()
        GroupBiddingEntries.objects.filter(id=id,SelectedMobileNumber = UserMobileNumber).update(IsSelected=1)
    
        GroupBidding.objects.filter(id=GroupBiddingEntriesdetails.GroupBidding_id).update(biddingAmount=biddingValue,selectedName=SelectedUserName,SelectedMobileNumber = UserMobileNumber,IsSelected=1)
        return Response("User Selected Successfully")
    else:
        return Response("User Already Selected")


# group Payments user list after selection
@api_view(['GET'])
def Group_Payment_User_list(request,id):
    data=request.data
    GroupDetail= {}
    token = data['token']
    userid = Token.objects.get(key=token).user_id  
    CheckgroupAdmin  = UserGroup.objects.filter(id=id,createBy=userid)  
    UserGroupDetails = UserGroup.objects.get(id=id)   
    biddingcycle = GroupBidding.objects.filter(UserGroup = UserGroupDetails).count()    
    groupbiddingdetails = GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=int(biddingcycle))[0]

    
    if CheckgroupAdmin.count() == 1:
        GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding = groupbiddingdetails)
        serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
       
    else:
        mobilenumber =User.objects.get(id=userid)
        GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(GroupBidding = groupbiddingdetails,
        Mobilenumber  = int(mobilenumber.username) )
        serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails, many = True)
    return Response(serializer.data)


# add Recived Amount by admin after user group bidding selected 
@api_view(['PUT'])
def Group_Payments(request,id):
    data=request.data
    token = data['token']
    PaidAmount = data['AmountPaid']
    UserMobileNumber = data['Mobilenumber']
    GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(id=id,Mobilenumber = UserMobileNumber)[0]
    totalAmountDue = int(GroupPaymentHistorydetails.ActualAmount) - int(PaidAmount)
    GroupPaymentHistory.objects.filter(GroupBidding_id=id,Mobilenumber = UserMobileNumber).update(AmountPaid=PaidAmount,AmountDue=totalAmountDue)
    return Response("Payemts successfully")


# get Selected user list for current cycle
@api_view(['get'])
def Selected_User(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    Usermobilenumber = User.objects.filter(id=userid).username
    usergroupdetails=  UserGroup.objects.get(id=id,createBy=userid)
    selecteduser = GroupBidding.objects.get(Cyclenumber=usergroupdetails.biddgingCycle,
                    UserGroup=usergroupdetails,IsSelected = 1,).biddgingCycle
    
    GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(id=id,Mobilenumber = UserMobileNumber)[0]
    totalAmountDue = int(GroupPaymentHistorydetails.ActualAmount) - int(PaidAmount)
    GroupPaymentHistory.objects.filter(GroupBidding_id=id,Mobilenumber = UserMobileNumber).update(AmountPaid=PaidAmount,AmountDue=totalAmountDue)
    return Response("Payemts successfully")

# Send Amount to the user who is selected
@api_view(['PUT'])
def Send_Amount(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id  
    CheckgroupAdmin  = UserGroup.objects.filter(id=id,createBy=userid) 
    if CheckgroupAdmin.count() == 1:
        UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
        biddingcycle = GroupBidding.objects.filter(UserGroup = UserGroupDetails).count()  
           
        groupbiddingDetail = GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle)[0]
        
        Amountdetails = AmountRecived(UserGroup = UserGroupDetails,ActualAmount= groupbiddingDetail.biddingAmount ,ActualRecived= groupbiddingDetail.biddingAmount ,
                        Cyclenumber = biddingcycle,RevicerName = groupbiddingDetail.selectedName,
                        Recivermobile =groupbiddingDetail.SelectedMobileNumber ,RecivedDate= datetime.datetime.today())
        Amountdetails.save()
        # 15 means bidding cycle close amount recived but group still is in active state
        GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle).update(BiddingStatus=15)
        if CheckgroupAdmin.biddgingCycle == CheckgroupAdmin.usercount:
            # 20 means group close all cycle complete 
            UserGroup.objects.filter(id=id,createBy=userid).update(groupStatus = 20)
            GroupBidding.objects.filter(UserGroup = UserGroupDetails,Cyclenumber=biddingcycle).update(BiddingStatus=20)
        else:
            UserGroup.objects.filter(id=id,createBy=userid).update(biddingdate = CheckgroupAdmin.biddingdate + datetime.timedelta(30))
        return Response("Payemts successfully")
    else:
        return Response("You dont have permission to send amount")


# get Gruop Payments history
@api_view(['Get'])
def Group_Payments_History(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    Usermobilenumber = User.objects.filter(id=userid).username
    admincheck  = UserGroup.objects.filter(id=id,createBy =Usermobilenumber).count()
    UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
    if admincheck == 0:
        GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(UserGroup = UserGroupDetails,Mobilenumber =Usermobilenumber)
    else:
         GroupPaymentHistorydetails = GroupPaymentHistory.objects.filter(Mobilenumber =Usermobilenumber)          
   
    serializer = GroupPaymentHistorySerializer(GroupPaymentHistorydetails)
    return Response(serializer.data)


@api_view(['Get'])
def Group_AmountRecived_History(request,id):
    data=request.data
    token = data['token']
    userid = Token.objects.get(key=token).user_id
    Usermobilenumber = User.objects.filter(id=userid).username
    admincheck  = UserGroup.objects.filter(id=id,createBy =Usermobilenumber).count()
    UserGroupDetails=  UserGroup.objects.get(id=id,createBy=userid)
    if admincheck == 0:
        GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(UserGroup = UserGroupDetails,Recivermobile =Usermobilenumber)
    else:
         GroupAmountRecivedHistorydetails = AmountRecived.objects.filter(Mobilenumber =Usermobilenumber)          
   
    serializer = GroupAmountRecivedSerializer(GroupAmountRecivedHistorydetails)
    return Response(serializer.data)



@api_view(['PUT'])
def update_user_details(request):
    data = request.data
    token = data['token']
    AlternateMobileNumber = data['AlternateMobileNumber']
    ProfilePhoto = data['ProfilePic']
    DateofBirth = data['DateofBirth']   
    userid = Token.objects.get(key=token).user_id
    user = User.objects.get(id=userid)
    #UserDetails.objects.filter(User_id=userid).update(ProfilePic=ProfilePhoto,AlternateMobileNumber=AlternateMobileNumber,DateofBirth=DateofBirth)
    UserDetails.objects.filter(User_id=userid).delete()
    UserDetailphoto =  UserDetails(User=user,ProfilePic=ProfilePhoto,AlternateMobileNumber=AlternateMobileNumber,DateofBirth=DateofBirth)
    UserDetailphoto.save()
    UserDetailsupdate = UserDetails.objects.get(User_id=userid)
    serializer = UserDetailsSerializer(UserDetailsupdate)
    return Response(serializer.data)


# user group data crud
class UserProfile(generics.GenericAPIView,
                    mixins.ListModelMixin):

    authentication_classes = [TokenAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer
    queryset = User.objects.all()
    #queryset = User.objects.select_related('UserDetails').get(id=5)
    lookup_field = 'id'    

    def get_queryset(self):
        return self.queryset.filter(username=self.request.user)

    def get(self, request, id=None):
        if id:
            return self.retrieve(request, id)
        else:
            return self.list(request)



