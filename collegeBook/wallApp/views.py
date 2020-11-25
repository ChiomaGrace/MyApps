from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse #imported in order to display django errors via ajax

#The below line of code is for the login registration.

def loginPage(request):
    return render(request, "login.html")

def processRegistration(request):
    print("This function processes the form for registering.")
    # print("This is the data submitted on the form via ajax/jquery.")
    # print(request.POST.get)
    print("This is the data submitted on the form.")
    print("*"*50)
    print(request.POST)
    print("*"*50)
    registrationErrors = User.objects.registrationValidator(request.POST)
    print("These are the errors submitted on the registration form.")
    print(registrationErrors)
    if len(registrationErrors) > 0:
        for key, value in registrationErrors.items():
            messages.error(request,value)
        #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
            request.session['rememberFirstName'] = request.POST['userFirstName']
            request.session['rememberLastName'] = request.POST['userLastName']
            request.session['rememberEmail'] = request.POST['initialEmail']
            request.session['rememberBirthdayMonth'] = request.POST.get('userBirthdayMonth', False)
            request.session['rememberBirthdayDay'] = request.POST.get('userBirthdayDay', False)
            request.session['rememberBirthdayYear'] = request.POST.get('userBirthdayYear', False)
        return JsonResponse({"errors": registrationErrors}, status=400)
    else:
        hashedPassword = bcrypt.hashpw(request.POST['initialPassword'].encode(), bcrypt.gensalt()).decode()
        newUser = User.objects.create(firstName = request.POST['userFirstName'], lastName = request.POST['userLastName'], birthdayMonth = request.POST.get('userBirthdayMonth'), birthdayDay = request.POST.get('userBirthdayDay'), birthdayYear = request.POST.get('userBirthdayYear'), emailAddress = request.POST['initialEmail'], password = hashedPassword, confirmPassword = hashedPassword)
        request.session['loginInfo'] = newUser.id
    return redirect("/wall")

def processLogin(request):
    print("This function processes the form for logining in")
    print("*"*50)
    loginErrors = User.objects.loginValidator(request.POST)
    print(loginErrors)
    if len(loginErrors) > 0:
        for key, value in loginErrors.items():
            messages.error(request,value, extra_tags="loginErrors") #Extra tags separates the two types of validation errors (login and registration)
    #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
            request.session['rememberEmail'] = request.POST['userEmail']
        return redirect('/')
    loginUser = User.objects.filter(emailAddress= request.POST['userEmail'])[0] #if no errors hit and the user did successfully register, this filters to get that correctly submitted email and password
    request.session['loginInfo'] = loginUser.id #now store that info in session into a new variable
    return redirect("/wall")

def success(request):
    #if they are not logged in( if loginInfo is not in session), then direct the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    userLoginInfo = User.objects.get(id=request.session['loginInfo'])
    context = {
        'loggedInUser': userLoginInfo
    }
    return render(request, "loggedInUsersPage.html", context)

#The above line of code is for the login registration.

#The below line of code is for posts submitted on the wall.

def loggedInUsersPage(request):
#if they are not logged in (if loginInfo is not in session), then direct the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    print("*"*50)
    print("This prints the currently logged in user.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    print(loggedInUser)
    print("This prints all the messages by all users.")
    allMessages = Message.objects.all()
    print(allMessages)
    print("This prints the messages the currently logged in user liked.")
    messagesUserLikes = Message.objects.filter(userLikes = loggedInUser)
    print(messagesUserLikes)
    print("This prints the count of how many messages liked.")
    likesCount = messagesUserLikes.count()
    print(likesCount)
    print("This prints the count of how many messages liked. minus the three display names")
    totalCountMinusThreeDisplayNames = likesCount - 3
    print(totalCountMinusThreeDisplayNames)
    print("This prints the messages the current logged in user unliked.")
    messagesUserUnliked= Message.objects.exclude(userLikes = loggedInUser)
    print(messagesUserUnliked)
    print("This prints the messages created by the logged in user and orders them my from latest post made.")
    userMessages = Message.objects.filter(user = loggedInUser).order_by('-createdAt')
    print("This prints all the users that have an account")
    allUsers = User.objects.all()
    print(allUsers)
    print("This prints the profile photo of the user.")
    userProfilePic = User.objects.filter(profilePic = loggedInUser)
    print(userProfilePic)
    print("*"*50)
    context = {
        'allMessages': allMessages,
        'userMessages': userMessages,
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'loggedInUserLikes': messagesUserLikes,
        'likesCount': likesCount,
        'allUsers': allUsers,
    }
    return render(request, "loggedInUsersPage.html", context)

def processProfilePic(request):
    print("This is the route that handles the uploading of a profile picture.")
    print(request.POST)
    #store the request.post in a variable
    # userProfilePic = request.POST['profilePicInputID'] Not sure if this would work Not the name but it is the ID??
    # print("*"*50)
    # print(userProfilePic)
    # print("*"*50)
    #retreive the user
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    return redirect("/wall")

def processMessage(request):
    print("This is the route that handles the post a message request.")
    print(request.POST)
    #store the request.post in a variable
    userMessage = request.POST['userMessage']
    print("*"*50)
    print(userMessage)
    print("*"*50)
    #retreive the user so the user can be corresponded with the correct post.
    user = User.objects.get(id=request.session['loginInfo'])
    #now that I have the message and user in a variable, I need to put it in a query so it can be stored in the database.
    Message.objects.create(message = userMessage, user = user)
    return redirect("/wall")

#The above line of code is for posts submitted on the wall.

#The below line of code is for the comments posted on the wall.

def processComments(request):
    print("This is the route that handles the post a comment request.")
    print(request.POST)
    #store the request.post in a variable
    print("This is the comment left by the user")
    comment = request.POST['userComment']
    print(comment)
    #retreive the post message so the comment is left on the correct post. used a hidden input for this. making the value the post id.
    print("This is the post id where the comment is made.")
    messageSelectedForComment = request.POST['postLocationForComment']
    print(messageSelectedForComment)
    #retreive the user so the user can be corresponded with the correct comment.
    print("This is the user that made the comment.")
    user = User.objects.get(id=request.session['loginInfo'])
    print(user)
    #Now that I have the post that receives the comment and the user who made the original post in a variable, the comment variable can be a query and stored in the database.
    #To do that I need to get the message object via id to use for the foreign key/one to many relationship
    print('This is the specific message where the comment is made.')
    theSpecificPost = Message.objects.get(id = messageSelectedForComment)
    print(theSpecificPost)
    commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user)
    print("This should print the comment of the user on the message.")
    return redirect("/wall")
#The above line of code is for the comments posted on the wall.

def userLikes(request, messageId):
    messageBeingLiked = Message.objects.get(id=messageId)
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    messageBeingLiked.userLikes.add(userWhoLikes)
    return redirect("/wall")

def userUnlikes(request, messageId):
    messageBeingUnliked = Message.objects.get(id=messageId)
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    messageBeingUnliked.userLikes.remove(userWhoUnlikes)
    return redirect("/wall")

def specificUserPage(request, userId):
    print("*"*50)
    print("This prints the profile of a specific user.")
    specificUserPage = User.objects.get(id=userId)
    print(specificUserPage)
    print("This prints the messages created by the logged in user and orders them my from latest post made.")
    specificUserMessages = Message.objects.filter(user = userId).order_by('-createdAt')
    print(specificUserMessages)
    print("This prints all the users that have an account")
    allUsers = User.objects.all()
    print(allUsers)
    print("*"*50)
    context = {
        'specificUserPage': specificUserPage,
        'specificUserMessages': specificUserMessages,
        'allUsers': allUsers
        }
    return render(request, "specificUserPage.html", context)

def logout(request):
    request.session.clear()
    return redirect('/')
