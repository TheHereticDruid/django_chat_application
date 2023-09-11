from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from chatapp.models import User, Message
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
import json
from chatapp.consumers import ChatConsumer

# Create your views here.
@api_view(['POST'])
def register(request):
    username = request.POST.get("username", None)
    if not username:
        return Response("Username is missing", status=status.HTTP_404_NOT_FOUND)
    email = request.POST.get("email", None)
    if not email:
        return Response("Email is missing", status=status.HTTP_404_NOT_FOUND)
    password = request.POST.get("password", None)
    if not password:
        return Response("Password is missing", status=status.HTTP_404_NOT_FOUND)
    if User.objects.filter(username=username).exists():
        return Response("Username already in use", status=status.HTTP_401_UNAUTHORIZED)
    if User.objects.filter(email=email).exists():
        return Response("Email already in use", status=status.HTTP_401_UNAUTHORIZED)
    new_user=User()
    new_user.username=username
    new_user.email=email
    new_user.set_password(password)
    new_user.save()
    return Response("User created successfully", status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login(request):
    username_or_email = request.POST.get("username_or_email", None)
    if not username_or_email:
        return Response("Neither Username nor Email are provided", status=status.HTTP_404_NOT_FOUND)
    password = request.POST.get("password", None)
    if not password:
        return Response("Password is missing", status=status.HTTP_404_NOT_FOUND)
    if User.objects.filter(username=username_or_email).exists():
        current_user=authenticate(username=username_or_email, password=password)
    elif User.objects.filter(email=username_or_email).exists():
        current_user=authenticate(email=username_or_email, password=password)
    else:
        return Response("User not found", status=status.HTTP_404_NOT_FOUND)
    if current_user is None:
        return Response("Wrong password entered", status=status.HTTP_401_UNAUTHORIZED)
    token = Token.objects.get_or_create(user=current_user)
    return Response(f"User {username_or_email} successfully logged in with Token {token[0].key}", status=status.HTTP_200_OK)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def online_users(request):
    all_tokens=Token.objects.all()
    json_return={}
    json_return["active_users"]=[]
    for token in all_tokens:
        json_return["active_users"].append({"username": token.user.username, "status": "Active"})
    return Response(json_return, status=status.HTTP_200_OK)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def chat_start(request):
    username=request.POST.get("username")
    if not username:
        return Response("Username is missing", status=status.HTTP_404_NOT_FOUND)
    token_query_set=Token.objects.filter(user__username=username)
    if not token_query_set.exists():
        return Response("User is not online or is not a valid User", status=status.HTTP_404_NOT_FOUND)
    room_name=username+"_"+request.user.username
    return Response("User is active, chat is open at room "+room_name, status=status.HTTP_200_OK)

# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def chat_send(request):
#     username=request.POST.get("username")
#     if not username:
#         return Response("Username is missing", status=status.HTTP_404_NOT_FOUND)
#     token_query_set=Token.objects.filter(user__username=username)
#     if not token_query_set.exists():
#         return Response("User is not online or is not a valid User", status=status.HTTP_404_NOT_FOUND)
#     return Response("In Progress")

@api_view(['GET'])
def suggested_friends(request, user_id):
    user_id_to_users_dict={}
    with open("users.json") as ufp:
        users_dict=json.loads(ufp.read())
    for user in users_dict["users"]:
        user_id_to_users_dict[user["id"]]=user
    if user_id not in user_id_to_users_dict:
        return Response("User does not exist", status=status.HTTP_404_NOT_FOUND)
    current_user=user_id_to_users_dict[user_id]
    user_id_to_score_dict={}
    for user_it in user_id_to_users_dict:
        score=0
        for key in current_user["interests"]:
            if key not in user_id_to_users_dict[user_it]["interests"]:
                score+=100
            else:
                score+=abs(current_user["interests"][key]-user_id_to_users_dict[user_it]["interests"][key])
        user_id_to_score_dict[user_id_to_users_dict[user_it]["id"]]=score
    top_friends_list=sorted(user_id_to_score_dict.items(), key=lambda item: item[1])[1:6]
    json_response={"suggested_users": []}
    for tf in top_friends_list:
        json_response["suggested_users"].append(user_id_to_users_dict[tf[0]])
    return Response(json_response, status=status.HTTP_200_OK)