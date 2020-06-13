
from django.contrib import admin
from django.urls import path,include
from Kameteeapp.API.views import *


app_name = 'Kameteeapp'

urlpatterns =[
    path('OTPVerify',OTP_Generate,name='OTP_Generate'),
    path('SendamountOTPVerify',OTP_Generate_SendAmount,name='OTP_Generate_SendAmount'),
    path('RegisterUser',RegisterUser,name='RegisterUser'),
    path('login',login_user,name='loginuser'),
    path('logout',logout_user,name='logoutuser'),
    path('forgetpassword',forget_password,name='forgetpassword'),

    
    path('usergroup', GroupUser.as_view(), name='usergroup'),
    path('usergroup/<int:id>', GroupUser.as_view(), name='usergroup'),
    
    path('adduser_togroup',adduser_togroup,name='adduser_togroup'),
    path('groupmember_list/<int:id>',groupmember_list,name='groupmember_list'),
    path('groupmember_update/<int:id>',groupmember_update,name='groupmember_update'),

    
    #path('StartGroupBidding/', StartGroupBidding.as_view(), name='StartGroupBidding'),
    #path('StartGroupBidding/<int:id>', StartGroupBidding.as_view(), name='StartGroupBidding'),
    path('groupstart',Group_Start,name='Group_Start'),
    path('Endgroupuser/<int:id>',Group_End,name='Group_End'),
    path('Group_Terminate/<int:id>',Group_Terminate,name='Group_Terminate'),
    path('Get_Group_ByStatus',Get_Group_ByStatus,name='Get_Group_ByStatus'),

    path('Manage_Group_ByStatus',Manage_Group_ByStatus,name='Manage_Group_ByStatus'),
    path('Group_Bidding',Group_Bidding,name='Group_Bidding'),

    
    path('Start_Group_Bidding',Start_Group_Bidding,name='Start_Group_Bidding'),
    path('Biddinglist',Group_Bidding_User_list,name='Group_Bidding_User_list'),


    path('Save_Group_Bidding/<int:id>',Save_Group_Bidding,name='Save_Group_Bidding'),
    path('Select_Group_Bidding/<int:id>',Select_Group_Bidding,name='Select_Group_Bidding'),
    
    # Fetch payments list and paid amount to the users
    path('Group_Payment_User_list',Group_Payment_User_list,name='Group_Payment_User_list'),
    # payments to the particular group
     path('Group_Payments/<int:id>',Group_Payments,name='Group_Payments'),
     path('SelectUserlist',Selected_User,name='Selected_User for Amount recived'),
      
       path('update_user_details',update_user_details,name='update_user_details'),

        path('Send_Amount',Send_Amount,name='Send_Amount'),

       path('getupdateuser', UserProfile.as_view(), name='getupdateuser'),
    path('getupdateuser/<int:id>', UserProfile.as_view(), name='getupdateuser'),

    path('groupuserchat',group_chat,name='group_chat'),
    path('PaymentsHistory',Group_Payments_History,name='Group_Payments_History'),
    path('AmountReceivedHistory',Group_AmountReceived_History,name='Group_AmountReceived_History'),

    
]
