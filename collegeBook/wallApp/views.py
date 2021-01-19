from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse #imported in order to display django errors via ajax
from django.core.files.storage import FileSystemStorage #imported in order to display uploaded images
from django.urls import reverse #imported in order to pass variables when redirecting
from django.db.models import Q #imported in order to filter multiple queries at once


#The below line of code is for the registration and login.

def regAndLoginPage(request):
    return render(request, "regAndLogin.html")

def processRegistration(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR REGISTERING AN ACCOUNT.")
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
    print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS REGISTRATION ROUTE.")
    return redirect("/home")

def processLogin(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR LOGGING IN.")
    print("*"*50)
    loginErrors = User.objects.loginValidator(request.POST)
    print(loginErrors)
    if len(loginErrors) > 0:
        for key, value in loginErrors.items():
            messages.error(request,value, extra_tags="loginErrors") #Extra tags separates the two types of validation errors (login and registration)
    #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
            request.session['rememberEmail'] = request.POST['userEmail']
        return redirect('/')
    else:
        loginUser = User.objects.filter(emailAddress= request.POST['userEmail'])[0] #if no errors hit and the user did successfully register, this filters to get that correctly submitted email and password
        request.session['loginInfo'] = loginUser.id #now store that info in session into a new variable
        print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS LOGIN ROUTE.")
    return redirect("/home")

def success(request):
    #if they are not logged in( if loginInfo is not in session), then direct the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    userLoginInfo = User.objects.get(id=request.session['loginInfo'])
    context = {
        'loggedInUser': userLoginInfo
    }
    return render(request, "loggedInUsersPage.html", context)

#The above line of code is for the registration and login.

# def loggedInUsersPage(request):
def loggedInUsersPage(request, messageId=0):
#if they are not logged in (if loginInfo is not in session), then direct the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    print("THIS IS THE LOGGED IN USERS PAGE ROUTE.")
    # print("This prints the currently logged in user.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    # print(loggedInUser)
    #("This prints all the messages posted.")
    allMessages = Message.objects.all()
    #print(allMessages)
    # print("This prints all the messages posted on the wall (by the user and by others) of the logged in user and orders them from latest post created.")
    wallOfLoggedInUser = Message.objects.filter(userReceivesPost = loggedInUser).order_by('-createdAt')
    # print(wallOfLoggedInUser)
    # how to do a multi query #wallOfLoggedInUser = Message.objects.filter(Q(user = (loggedInUser)) | Q(userReceivesPost = (loggedInUser))).order_by('-createdAt')
    if messageId:
        # print("This prints the id of the message that was just liked and passed via params from the userLikes function.")
        messageId = messageId
        # print(messageId)
        # print("This prints the message object.")
        messageBeingLiked = Message.objects.get(id=messageId)
        # print(messageBeingLiked)
        # print("This prints the amount of likes the message has.")
        # print(messageBeingLiked.likeMessageCount)
        if messageBeingLiked.likeMessageCount > 3:
                likesCountMinusDisplayNames = (messageBeingLiked.likeMessageCount) - 2
                print("This is the like count minus the display names:", likesCountMinusDisplayNames)
                displayCount = Message.objects.filter(id=messageId).update(likeMessageCountMinusDisplayNames=likesCountMinusDisplayNames) 
    # print("This prints the messages the current logged in user unliked.")
    messagesUserUnliked= Message.objects.exclude(userLikes = loggedInUser)
    # print(messagesUserUnliked)
    # print("This prints all the users that have an account except the logged in user.")
    allUsers = User.objects.exclude(id=request.session['loginInfo'])
    # print(allUsers)
    # print("*"*50)
    print("THIS IS THE LAST PRINT STATEMENT IN THE LOGGED IN USER'S PAGE ROUTE.")
    context = {
        'wallOfLoggedInUser': wallOfLoggedInUser,
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'allMessages': allMessages,
        'allUsers': allUsers,
    }
    return render(request, "loggedInUsersPage.html", context)

def processProfilePic(request):
    print("THIS FUNCTION PROCESSES THE FORM/UPLOADING OF A PROFILE PICTURE.")
    # print("This is the the submitted image by the user as a base64stringimage with <QueryDict: {'theFile': ['data:image/jpeg;base64,/9j/ before it.")
    # print("This is the submitted image by the user")
    # print("*"*50)
    # print(request.FILES)
    submittedProfilePic = request.FILES.get('userProfilePic')
    # print(submittedProfilePic)
    # print("*"*50)
    if request.method == 'POST' and request.FILES.get('userProfilePic'):
        userProfilePic = request.FILES['userProfilePic']
        fileSystem = FileSystemStorage()
        uploadedImage = fileSystem.save(userProfilePic.name, userProfilePic)
        uploadedImageURL = fileSystem.url(uploadedImage)
        addProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic=uploadedImageURL) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE PIC ROUTE.")
    return redirect("/home")

def userDeletesProfilePic(request):
    print("THIS FUNCTION REMOVES THE PROFILE PIC OF THE USER FROM THE USER FROM THE DATABASE.")
    deleteProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic="") 
    print("THIS IS THE LAST PRINT STATEMENT IN THE USER DELETES PROFILE PIC ROUTE.")
    return redirect("/home")

def processProfileInfo(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR UPLOADING PROFILE INFORMATION.")
    # print("*"*50)
    # print(request.POST)
    submittedProfileInfo = request.POST['userProfileInfo']
    # print(submittedProfileInfo)
    # print("*"*50)
    addProfileInfo = User.objects.filter(id=session['loginInfo']).update(profileInfo=submittedProfileInfo) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INFO ROUTE.")    
    return redirect("/home")

# def processMessageOnLoggedInUsersPage(request):
def processMessage(request, userFirstName, userLastName, userId):
    print("THIS FUNCTION PROCESSES THE FORM FOR CREATING A POST ON THE WALL OF THE LOGGED IN USER.")
    # print("*"*50)
    # postAMessageErrors = Message.objects.messageValidator(request.POST)
    # print(postAMessageErrors)
    # if len(postAMessageErrors) > 0:
    #     for key, value in postAMessageErrors.items():
    #         messages.error(request,value)
    #         return redirect('/home')
    # else:
    #print("This prints the messaged created by the logged in user.")
    userMessage = request.POST['userMessage']
    # print(userMessage)
    #print("This prints the logged in user.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    print(loggedInUser)
    recipientOfPost = request.POST['userWhoReceivesPost'] # is a string so need to convert before comparison   
    print(recipientOfPost)
    print(loggedInUser.id)
    if loggedInUser.id == int(recipientOfPost):
        #this creates the message and saves it to the database
        submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INFO ROUTE.")    
        return redirect("/home")
    else:
        #this creates the message and saves it to the database
        submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
        # # print("*"*50)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INFO ROUTE.")    
    return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

    # if request.method == 'POST':
    #     # print(request.POST) #This prints as query set: example: <QueryDict: {'userMessage': ['123']}>
    #     hotdog = Message.objects.filter(message=userMessage, user=loggedInUser)
    #     # print(newMessage) #This prints as a mesage object: example: Message object(#)
    #     submittedMessages = {userMessage:[]}
    #     for message in userMessage:
    #         print("******" * 50)
    #         print(submittedMessages[userMessage].append(message)) 
    #         print(message)
    #         # submittedMessages[newMessages].append(message)
    #         print("******" * 50)
    # return JsonResponse(submittedMessages)

def processComment(request, userFirstName, userLastName, userId):
    print("THIS FUNCTION PROCESSES THE FORM FOR POSTING A COMMENT.")
    # print("*"* 50)
    # print("This is the comment left by the logged in user.")
    comment = request.POST['userComment']
    # print(comment)
    # print("This is the post id where the comment is made.")
    messageSelectedForComment = request.POST['postLocationForComment']
    # print(messageSelectedForComment)
    # print("This is the user that made the comment.")
    user = User.objects.get(id=request.session['loginInfo'])
    # print(user)
    # print("This prints the id of the specific user who received the comment.")
    userReceivesComment = request.POST['userReceivesComment']
    # print(userReceivesComment)
    #Now that I have the post that receives the comment(messageSelectedForComment), and the user who receives the comment(userReceivesComment), I can use said variables for a query to obtain its' instances.
    #To do that I need to get the message object via id to use for the foreign key/one to many relationship
    theSpecificPost = Message.objects.get(id = messageSelectedForComment)
    recipientOfComment = User.objects.get(id = userReceivesComment)
    if user.id == recipientOfComment: #This means the user is commenting on their own page and should be directed home
        commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user, userReceivesComment = recipientOfComment)
        return redirect("/home")
    else: #This means the user is commenting on someone else's page and should be directed their
        commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user, userReceivesComment = recipientOfComment)
        # print("*"* 50)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS COMMENT ROUTE.")  
    return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def specificUsersPage(request, userFirstName, userLastName, userId, messageId = 0):
    print("THIS IS THE SPECIFIC USER'S PAGE ROUTE.")
    # print("*"*50)
    specificUsersPage = User.objects.get(id=userId) #retreiving from the url
    specificUsersFirstName = User.objects.get(firstName=userFirstName) #retreiving from the url
    specificUsersLastName = User.objects.get(lastName=userLastName) #retreiving from the url
    # print("This prints all the messages posted on a page of a specific user and orders them from latest post created.")
    specificUsersMessages = Message.objects.filter(userReceivesPost = userId).order_by('-createdAt')
    if messageId:
        print("*"*50)
        print("This prints the id of the message that was just liked and passed via params from the userLikes function.")
        messageId = messageId
        print(messageId)
        print("This prints the message object.")
        messageBeingLiked = Message.objects.get(id=messageId)
        print(messageBeingLiked)
        print("This prints the amount of likes the message has.")
        print(messageBeingLiked.likeMessageCount)
        if messageBeingLiked.likeMessageCount > 3:
                likesCountMinusDisplayNames = (messageBeingLiked.likeMessageCount) - 2
                print("This is the like count minus the display names:", likesCountMinusDisplayNames)
                displayCount = Message.objects.filter(id=messageId).update(likeMessageCountMinusDisplayNames=likesCountMinusDisplayNames) 
    # print(specificUsersMessages)
    # print("This prints all the users that have an account")
    allUsers = User.objects.all()
    # print(allUsers)
    # print("*"*50)
    print("THIS IS THE LAST PRINT STATEMENT OF THE SPECIFIC USER'S PAGE ROUTE.")
    context = {
        'specificUsersPage': specificUsersPage,
        'specificUsersMessages': specificUsersMessages,
        'allUsers': allUsers,
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        }
    return render(request, "specificUserPage.html", context)

def userLikes(request, messageId):
    print("THIS IS THE USER LIKES ROUTE")
    # print("*"*50)
    # print("This is the specific message being liked")
    messageBeingLiked = Message.objects.get(id=messageId)
    print("*"*50)
    userFirstName = messageBeingLiked.userReceivesPost.firstName # need for params to reroute
    userLastName = messageBeingLiked.userReceivesPost.lastName # need for params to reroute
    userId = messageBeingLiked.userReceivesPost.id # need for params to reroute
    print("*"*50)
    # print(messageBeingLiked) #prints as a Message Object(#)
    # print("This is the user liking the message")
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    print("The user who likes id", userWhoLikes.id)
    print("The message being liked id", messageBeingLiked.userReceivesPost.id)
    # print(userWhoLikes) # prints as a User Object(#)
    #The below code creates the like 
    messageBeingLiked.userLikes.add(userWhoLikes) #userLikes is the instance name in the Message model holding the many to many relationship
    # print("*"*50)
    if userWhoLikes.id != messageBeingLiked.userReceivesPost.id: #if this line of code runs it means the like occurred on the specific user's page
        messageBeingLiked = Message.objects.get(id = messageId)
        messageBeingLiked.likeMessageCount += 1
        messageBeingLiked.save()
        print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE.")
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else: #if these lines of code run it means the like occurred on logged in user's home page
        messageBeingLiked = Message.objects.get(id = messageId)
        messageBeingLiked.likeMessageCount += 1
        messageBeingLiked.save()
        print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE.")
    return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    # return redirect("/home")

def userUnlikes(request, messageId):
    messageBeingUnliked = Message.objects.get(id=messageId)
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    messageBeingUnliked.userLikes.remove(userWhoUnlikes)
    return redirect("/home")

def logout(request):
    request.session.clear()
    return redirect('/')