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
    # print("This is the data submitted on the form.")
    # print("*"*50)
    # print(request.POST)
    # print("*"*50)
    registrationErrors = User.objects.registrationValidator(request.POST)
    # print("These are the errors submitted on the registration form.")
    # print(registrationErrors)
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
    # print("*"*50)
    loginErrors = User.objects.loginValidator(request.POST)
    # print(loginErrors)
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
#if they are not logged in (if loginInfo is not in session), then this directs the user back to the index page
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
    if messageId: #if these lines of code run it means a like occurred
        print("This prints the id of the message that was just liked and passed via params from the userLikes function.")
        messageId = messageId
        print(messageId)
        print("This prints the message object.")
        messageBeingLiked = Message.objects.get(id=messageId)
        print(messageBeingLiked)
        # print("This prints the amount of likes the message has.")
        # print(messageBeingLiked.likeMessageCount)
        if messageBeingLiked.likeMessageCount > 3:
                likesCountMinusDisplayNames = (messageBeingLiked.likeMessageCount) - 2
                print("This is the like count minus the display names:", likesCountMinusDisplayNames)
                displayCount = Message.objects.filter(id=messageId).update(likeMessageCountMinusDisplayNames=likesCountMinusDisplayNames) 
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
    addProfileInfo = User.objects.filter(id=request.session['loginInfo']).update(profileInfo=submittedProfileInfo) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INFO ROUTE.")    
    return redirect("/home")

def processMessage(request, userFirstName, userLastName, userId):
    # print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM OF POSTING A MESSAGE.")
    postAMessageErrors = Message.objects.messageValidator(request.POST) #linking the messageValidator instance in the model that's containing the errors
    # print(postAMessageErrors)
    if len(postAMessageErrors) > 0:
        for key, value in postAMessageErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postAMessageErrors}, status=400)
    else:
        #print("This prints the messaged created by the logged in user.")
        userMessage = request.POST['userMessage']
        # print(userMessage)
        #print("This prints the logged in user.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        # print(loggedInUser)
        recipientOfPost = request.POST['userWhoReceivesPost'] # is a string so need to convert before comparison   
        # print(recipientOfPost)
        # print(loggedInUser.id)
        if loggedInUser.id == int(recipientOfPost):
            #this creates the message and saves it to the database
            submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS POSTING A MESSAGE ROUTE.")    
            return redirect("/home")
        else:
            #this creates the message and saves it to the database
            submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
            # # print("*"*50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INFO ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processComment(request, userFirstName, userLastName, userId):
    postACommentErrors = Comment.objects.commentValidator(request.POST)
    print(postACommentErrors)
    if len(postACommentErrors) > 0:
        for key, value in postACommentErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postACommentErrors}, status=400)
    else:
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
        print("THIS IS THE SPECIFIC USER'S PAGE ROUTE THAT WAS REACHED BY THE LOGGED IN USER LIKING A MESAGE ON THE SPECIFIC USER'S PAGE.")
        print("*"*50)
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
                # print("This is the like count minus the display names:", likesCountMinusDisplayNames)
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

def userLikes(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0): #need to have positional arguments in order to do the reroute to the specific page
    print("THIS IS THE USER LIKES ROUTE")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:",messageId)
    print("*"*50)
    # print("This is the specific message being liked")
    messageBeingLiked = Message.objects.get(id=messageId)
    # print(messageBeingLiked) #prints as a Message Object(#)
    userFirstName = messageBeingLiked.userReceivesPost.firstName # need for params to reroute
    # print(userFirstName)
    userLastName = messageBeingLiked.userReceivesPost.lastName # need for params to reroute
    # print(userLastName)
    userId = messageBeingLiked.userReceivesPost.id # need for params to reroute
    # print(userId)
    # print("This is the user liking the message")
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    # print(userWhoLikes) # prints as a User Object(#)
    # print("The id of the user giving the like", userWhoLikes.id)
    # print("The id of the user receiving the like", messageBeingLiked.userReceivesPost.id)
    # print("The id of the users who have liked messages:", messageBeingLiked.userLikes.all())
    if userWhoLikes in messageBeingLiked.userLikes.all():
        print("You've already liked the message!")
        if userWhoLikes.id != messageBeingLiked.userReceivesPost.id: #if this line of code runs it means the repetitive like attempt occurred on the specific user's page
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if this line of code runs it means the repetitive like attempt occurred on the logged in user's page
            return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        if userWhoLikes.id != messageBeingLiked.userReceivesPost.id: #if this line of code runs it means the like occurred on the specific user's page
                messageBeingLiked.userLikes.add(userWhoLikes) #This creates the like - userLikes is the instance name in the Message model holding the many to many relationship
                messageBeingLiked.likeMessageCount += 1
                messageBeingLiked.save()
                print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE (LIKE IS OCCURING ON A SPECIFIC USER'S PAGE).")
                # return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
                return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if these lines of code run it means the like occurred on logged in user's home page
            messageBeingLiked.userLikes.add(userWhoLikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingLiked.likeMessageCount += 1
            messageBeingLiked.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ROUTE (LIKE IS OCCURRING ON THE LOGGED IN USER'S PAGE).")
        return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    # return redirect("/home")

# def userUnlikes(request, messageId):
def userUnlikes(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0): #need to have positional arguments in order to do the reroute to the specific page
    messageBeingUnliked = Message.objects.get(id=messageId)
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    userFirstName = messageBeingUnliked.userReceivesPost.firstName # need for params to reroute
    userLastName = messageBeingUnliked.userReceivesPost.lastName # need for params to reroute
    userId = messageBeingUnliked.userReceivesPost.id # need for params to reroute
    if userWhoUnlikes in messageBeingUnliked.userLikes.all(): #this checks if the logged in user has liked the specific message to begin with
        if userWhoUnlikes.id != messageBeingUnliked.userReceivesPost.id: #if this line of code runs it means the 'unliking' occurred on the specific user's page
            messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingUnliked = Message.objects.get(id = messageId)
            if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
                print("This is the amount of likes the message has:", messageBeingUnliked.likeMessageCount)
                messageBeingUnliked.likeMessageCount -= 1
                print("This is the amount of likes the message has after subtracting one:", messageBeingUnliked.likeMessageCount)
                messageBeingUnliked.save()
                print("THIS IS THE LAST PRINT STATEMENT OF THE USER UNLIKES ROUTE THAT REDIRECTS TO THE SPECIFIC USER'S PAGE.")
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else: #if these lines of code run it means the 'unliking' occurred on logged in user's home page
            messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
            messageBeingUnliked = Message.objects.get(id = messageId)
            if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
                messageBeingUnliked.likeMessageCount -= 1
                messageBeingUnliked.save()
                print("THIS IS THE LAST PRINT STATEMENT OF THE USER UNLIKES ROUTE THAT REDIRECTS TO LOGGED IN USER'S PAGE.")
        return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        print("You've never liked the message, so you cannot unlike it!")
        if userWhoUnlikes.id != messageBeingUnliked.userReceivesPost.id: #if this line of code runs it means the attemptive 'unliking' occurred on the specific user's page
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId, messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else:
            return redirect(reverse('home', args=(messageId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def sendFriendRequest(request, userId):
    print("THIS IS THE SEND A FRIEND REQUEST ROUTE")
    # print("*"*50)
    # print("This prints the user object of the user receiving the friend request.")
    userReceivesRequest = User.objects.get(id=userId) #the recipient of the friend request
    userFirstName = userReceivesRequest.firstName # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    userId = userReceivesRequest.id # need for params to reroute
    # print(userReceivesRequest) #prints as a User Object(#)
    # print("This prints the user object of the user sending the friend request aka the logged in user.")
    userWhoSentFriendRequest = User.objects.get(id=request.session['loginInfo'])
    # print(userWhoSentFriendRequest) # prints as a User Object(#)
    if userWhoSentFriendRequest in userReceivesRequest.friends.all():
        print("You're already friends!")
    else:
        #This sends the friend request.
        userReceivesRequest.friends.add(userWhoSentFriendRequest)
        # if user.id != loggedInUser.id:
        #     return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        # else: #if these lines of code run it means the like occurred on logged in user's home page
        # return redirect(reverse('home', args=(userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        # print("*"*50)
        print("THIS IS THE LAST PRINT STATEMENT OF THE ADD A FRIEND ROUTE.")
    return redirect("/home")

def addFriend(request, userId):
    print("THIS IS THE ADD A FRIEND ROUTE")
    # print("*"*50)
    # print("This prints the user object of the user receiving the friend request.")
    userReceivesRequest = User.objects.get(id=userId) #the recipient of the friend request
    userFirstName = userReceivesRequest.firstName # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    userId = userReceivesRequest.id # need for params to reroute
    # print(userReceivesRequest) #prints as a User Object(#)
    # print("This prints the user object of the user sending the friend request aka the logged in user.")
    userWhoSentFriendRequest = User.objects.get(id=request.session['loginInfo'])
    # print(userWhoSentFriendRequest) # prints as a User Object(#)
    friendships = userReceivesRequest.friends
    if userWhoSentFriendRequest in userReceivesRequest.friends.all():
        print("You're already friends!")
    else:
        #This creates the friend request.
        userReceivesRequest.friends.add(userWhoSentFriendRequest)
        print("THIS IS THE LAST PRINT STATEMENT OF THE ADD A FRIEND ROUTE.")
        # if user.id != loggedInUser.id:
        #     return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        # else: #if these lines of code run it means the like occurred on logged in user's home page
        # return redirect(reverse('home', args=(userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        # print("*"*50)
    return redirect("/home")

def logout(request):
    request.session.clear()
    return redirect('/')