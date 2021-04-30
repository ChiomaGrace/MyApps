from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
import bcrypt
from django.http import JsonResponse #imported in order to display django errors via ajax
from django.core.files.storage import FileSystemStorage #imported in order to display uploaded images
from django.urls import reverse #imported in order to pass variables when redirecting
from django.db.models import Q #imported in order to filter multiple queries at once
# import operator #imported in order to eliminate spaces in the search bar
# from django.db.models.functions import Lower, Replace
import json


def regAndLoginPage(request):
    return render(request, "regAndLogin.html")

def processRegistration(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR REGISTERING AN ACCOUNT.")
    print("This is the data submitted on the form via ajax/jquery.")
    print(request.POST.get)
    print("This is the data submitted on the form.")
    print("*"*50)
    print(request.POST)
    print("*"*50)
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
            request.session['rememberBirthdayMonth'] = request.POST.get('birthdayMonth', False)
            request.session['rememberBirthdayDay'] = request.POST.get('birthdayDay', False)
            request.session['rememberBirthdayYear'] = request.POST.get('birthdayYear', False)
        return JsonResponse({"errors": registrationErrors}, status=400)
    else:
        hashedPassword = bcrypt.hashpw(request.POST['initialPassword'].encode(), bcrypt.gensalt()).decode()
        print("This is the birthday month:", request.POST.get('birthdayMonth'))
        newUser = User.objects.create(firstName = request.POST['userFirstName'].capitalize(), lastName = request.POST['userLastName'].capitalize(), emailAddress = request.POST['initialEmail'], birthdayMonth = request.POST.get('birthdayMonth'), birthdayDay = request.POST.get('birthdayDay'), birthdayYear = request.POST.get('birthdayYear'), password = hashedPassword, confirmPassword = hashedPassword)
        request.session['loginInfo'] = newUser.id
    print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS REGISTRATION ROUTE.")
    return redirect("/wall")

def processLogin(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR LOGGING IN.")
    # print("*"*50)
    loginErrors = User.objects.loginValidator(request.POST)
    # print(loginErrors)
    if len(loginErrors) > 0:
        for key, value in loginErrors.items():
            messages.error(request,value, extra_tags="loginErrors") #Extra tags separates the two types of validation errors (login and registration)
            request.session['rememberEmail'] = request.POST['userEmail'] #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
        return redirect('/')
    else:
        loginUser = User.objects.filter(emailAddress= request.POST['userEmail'])[0] #if no errors hit and the user did successfully register, this filters to get that correctly submitted email and password
        request.session['loginInfo'] = loginUser.id #now store that info in session into a new variable
        print("THIS IS THE LAST PRINT STATEMENT IN THE THE PROCESS LOGIN ROUTE.")
    return redirect("/wall")

def wall(request):
    print("THIS FUNCTION IS THE WALL OF THE COLLEGEBOOK")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #make the loggedinuser friends with themselves so their posts display on the wall (if friends statement)
    loggedInUser.friends.add(loggedInUser)
    loggedInUsersFriends = loggedInUser.friends.all()
    # print("These are the logged in user's friends:", loggedInUsersFriends)
    wallOfLoggedInUser = Message.objects.filter(userReceivesPost = loggedInUser).order_by('createdAt')
    allMessages = Message.objects.all().order_by('-createdAt')
    print("These are the messages on the logged in user's wall:", allMessages)
    # print("These are all the users the logged in user sent friend requests to:", loggedInUser.friends.all())
    print("THIS IS THE LAST PRINT STATEMENT IN THE WALL FUNCTION")
    context = {
        'loggedInUser': loggedInUser,
        'allMessages': allMessages,
        'wallOfLoggedInUser': wallOfLoggedInUser,
        'notifications': Notification.objects.all,
        'loggedInUsersFriends': loggedInUsersFriends,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "wall.html", context)

#The above line of code is for the registration and login.

def loggedInUsersPage(request, messageId=0):
#if they are not logged in (if loginInfo is not in session), then this directs the user back to the index page
    if 'loginInfo' not in request.session:
        return redirect('/')
    print("THIS IS THE LOGGED IN USERS PAGE ROUTE.")
    # print("This prints the currently logged in user.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    # print(loggedInUser)
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    # print("This prints all the messages posted on the wall (by the user and by others) of the logged in user and orders them from latest post created.")
    wallOfLoggedInUser = Message.objects.filter(userReceivesPost = loggedInUser).order_by('-createdAt')
    # print(wallOfLoggedInUser)
    commentsOnWall = Notification.objects.filter(user = loggedInUser)
    # print("These are the comments on the logged in user's wall:", commentsOnWall)
    # how to do a multi query #wallOfLoggedInUser = Message.objects.filter(Q(user = (loggedInUser)) | Q(userReceivesPost = (loggedInUser))).order_by('-createdAt')
    if messageId: #if these lines of code run it means a like occurred
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
    # print("This prints all the users that have an account except the logged in user.")
    allUsers = User.objects.exclude(id=request.session['loginInfo']).order_by('?') #filter will be randomized
    # print(allUsers)
    friends = loggedInUser.friends.all().order_by('?')
    # print("These are all the friends of the logged in user:", friends)
    friendCount = friends.count() - 1
    print("This is the friend count:", friendCount)
    # print("This is the notification count", Notification.objects.filter(user=loggedInUser).count())
    # print("*"*50)
    context = {
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'wallOfLoggedInUser': wallOfLoggedInUser,
        'commentsOnWall': commentsOnWall,
        'allUsers': allUsers,
        'friends': friends,
        'friendCount': friendCount,
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "loggedInUsersPage.html", context)

def processProfilePic(request):
    print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM/UPLOADING OF A PROFILE PICTURE.")
    # if request.is_ajax():
    #     if request.method == 'POST':
    #         print("POST request occurred.")
    if request.method == 'POST' and request.FILES.get('userProfilePic'):
        userProfilePic = request.FILES['userProfilePic']
        print("This is the submitted profile picture:", userProfilePic)
        fileSystem = FileSystemStorage()
        uploadedImage = fileSystem.save(userProfilePic.name, userProfilePic)
        uploadedImageURL = fileSystem.url(uploadedImage)
        print("This is the uploaded image url:", uploadedImageURL)
        addProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic=uploadedImageURL) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE PIC ROUTE.")
    print("*"*50)
    return redirect("/home")

def userDeletesProfilePic(request):
    print("THIS FUNCTION REMOVES THE PROFILE PIC OF THE USER FROM THE USER FROM THE DATABASE.")
    deleteProfilePic = User.objects.filter(id=request.session['loginInfo']).update(profilePic="") 
    print("THIS IS THE LAST PRINT STATEMENT IN THE USER DELETES PROFILE PIC ROUTE.")
    return redirect("/home")

def processProfileHeader(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR UPLOADING THE PROFILE HEADER THAT IS UNDERNEATH THE PROFILE PHOTO.")
    # print("*"*50)
    # print(request.POST)
    submittedProfileHeader = request.POST['userProfileHeader']
    # print(submittedProfileHeader)
    # print("*"*50)
    addProfileHeader= User.objects.filter(id=request.session['loginInfo']).update(profileHeader=submittedProfileHeader) 
    print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE HEADER ROUTE.")    
    return redirect("/home")

def processProfileIntro(request):
    print("THIS FUNCTION PROCESSES THE FORM FOR UPLOADING A PROFILE INTRODUCTION.")
    print("*"*50)
    profileIntroErrors = User.objects.profileIntroValidator(request.POST)
    if request.POST['userCheckBox'] == 'true':
        request.session['rememberUniversity'] = request.POST['userUniversity']
        request.session['rememberHighSchool'] = request.POST['userHighSchool']
        request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
        request.session['rememberHomeTown'] = request.POST['userHomeTown']
        print("This print statement means the checkbox is checked.", request.POST['userCheckBox'])
        submittedUserUniversity = request.POST['userUniversity']
        # print("This is the university the user submitted:", submittedUserUniversity)
        submittedUserHighSchool = request.POST['userHighSchool']
        # print("This is the highschool the user submitted:", submittedUserHighSchool)
        submittedUserDormBuilding = request.POST['userDormBuilding']
        # print("This is the dorm building the user submitted:", submittedUserDormBuilding)
        submittedUserHomeTown= request.POST['userHomeTown']
        # print("This is the home town the user submitted:", submittedUserHomeTown)
        print("This will save the data if the user chooses to input it, but still also means the user chooses to hide it.")
        addProfileIntro = User.objects.filter(id=request.session['loginInfo']).update(userUniversity=submittedUserUniversity, userHighSchool = submittedUserHighSchool, userDormBuilding = submittedUserDormBuilding, userHomeTown = submittedUserHomeTown, userCheckBox = True ) 
        print("*"*50)
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INTRO ROUTE.")   
    elif request.POST['userCheckBox'] == 'false':
        if len(profileIntroErrors) > 0:
            for key, value in profileIntroErrors.items():
                messages.error(request,value)
            #When an error occurs on one field input, the below code keeps the fields that are filled out correctly instead of removing all inputs.
                request.session['rememberUniversity'] = request.POST['userUniversity']
                request.session['rememberHighSchool'] = request.POST['userHighSchool']
                request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
                request.session['rememberHomeTown'] = request.POST['userHomeTown']
                # print("These are the errors submitted on the profile intro form.")
            return JsonResponse({"errors": profileIntroErrors}, status=400)
        else:
            print("This will save the data if the user chooses to input it, but still also means the user chooses to hide it.")
            submittedUserUniversity = request.POST['userUniversity']
            # print("This is the university the user submitted:", submittedUserUniversity)
            submittedUserHighSchool = request.POST['userHighSchool']
            # print("This is the highschool the user submitted:", submittedUserHighSchool)
            submittedUserDormBuilding = request.POST['userDormBuilding']
            # print("This is the dorm building the user submitted:", submittedUserDormBuilding)
            submittedUserHomeTown= request.POST['userHomeTown']
            # print("This is the home town the user submitted:", submittedUserHomeTown)
            request.session['rememberUniversity'] = request.POST['userUniversity']
            request.session['rememberHighSchool'] = request.POST['userHighSchool']
            request.session['rememberDormBuilding'] = request.POST['userDormBuilding']
            request.session['rememberHomeTown'] = request.POST['userHomeTown']
            addProfileIntro = User.objects.filter(id=request.session['loginInfo']).update(userUniversity=submittedUserUniversity, userHighSchool = submittedUserHighSchool, userDormBuilding = submittedUserDormBuilding, userHomeTown = submittedUserHomeTown, userCheckBox = False ) 
            print("*"*50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS PROFILE INTRO ROUTE.")    
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
        print(userMessage)
        #print("This prints the logged in user.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        # print(loggedInUser)
        recipientOfPost = request.POST['userWhoReceivesPost'] # is a number but as a string so need to convert before comparison   
        print("The id of the user receiving the post:", recipientOfPost)
        recipientOfPostObject = User.objects.get(id = recipientOfPost)
        # print("The id of the loggedInUser:", loggedInUser.id)
        # print("These are the friends of the user receiving the posts:", recipientOfPostObject.friends.all())
        # print("These are the logged in user's friends:", loggedInUser.friends.all())
        # if recipientOfPostObject in loggedInUser.friends.all() and loggedInUser in recipientOfPostObject.friends.all():
        #     print("This means there are friends.")
        # if recipientOfPostObject not in loggedInUser.friends.all() and loggedInUser in recipientOfPostObject.friends.all():
        #     print("This means the friend request is still pending/hasn't been accepted or declined yet.")
        # if recipientOfPostObject not in loggedInUser.friends.all() and loggedInUser not in recipientOfPostObject.friends.all():
        #     print("You're not friends! Send friend request")
        if loggedInUser.id == int(recipientOfPost): #this means the logged in user is writing on their own wall
            #this creates the message and saves it to the database
            submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
            userReceivesNewPost = User.objects.get(id = recipientOfPost)
            notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS POSTING A MESSAGE ROUTE.")    
            return redirect("/home")
        else: #this means the logged in user is writing a post to a different user
            #this creates the message and saves it to the database
            submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
            userReceivesNewPost = User.objects.get(id = recipientOfPost)
            notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
            userReceivesNewPost.notifications += 1 #a counter for all the notifications (posted messages, comments, and friend requests)
            userReceivesNewPost.save()
            # print("*"*50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS MESSAGE ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processMessageOnWall(request):
    # print("*"*50)
    print("THIS FUNCTION PROCESSES THE FORM OF POSTING A MESSAGE ON THE WALL.")
    postAMessageErrors = Message.objects.messageValidator(request.POST) #linking the messageValidator instance in the model that's containing the errors
    # print(postAMessageErrors)
    if len(postAMessageErrors) > 0:
        for key, value in postAMessageErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postAMessageErrors}, status=400)
    else:
        #print("This prints the messaged created by the logged in user.")
        userMessage = request.POST['userMessage']
        print(userMessage)
        #print("This prints the logged in user.")
        loggedInUser = User.objects.get(id=request.session['loginInfo'])
        # print(loggedInUser)
        recipientOfPost = request.POST['userWhoReceivesPost'] # is a number but as a string so need to convert before comparison   
        print("The id of the user receiving the post:", recipientOfPost)
        recipientOfPostObject = User.objects.get(id = recipientOfPost)
        print("The id of the loggedInUser:", loggedInUser.id)
        print("These are the friends of the user receiving the posts:", recipientOfPostObject.friends.all())
        print("These are the logged in user's friends:", loggedInUser.friends.all())
        submittedMessageByUser = Message.objects.create(message = userMessage, user = loggedInUser, userReceivesPost_id = recipientOfPost)
        userReceivesNewPost = User.objects.get(id = recipientOfPost)
        notifyUser = Notification.objects.create(user = userReceivesNewPost, message = submittedMessageByUser) #This creates a notification for the user receiving the posted message
        print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS POSTING A MESSAGE ON THE WALL ROUTE.")    
    return redirect("/wall")

def deleteMessage(request, userFirstName, userLastName, userId):
    # print("*"*50)
    print("THIS FUNCTION DELETES A POSTED MESSAGE.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    messageData = json.loads(request.body)
    # print("This is the received message data:", messageData) # it is in a dictionary so we need to loop through to get the values
    for messageID in messageData.values():
        print("This is the message id:", messageID)
        messageToBeDeleted = Message.objects.get(id = messageID)
        print("This is the message being deleted:", messageToBeDeleted)
        print("This is the user who received the post:", messageToBeDeleted.userReceivesPost) #user object
        if loggedInUser == messageToBeDeleted.userReceivesPost: #this means the logged in user is attempting to delete a message on their own wall and should be directed back here
            messageToBeDeleted.delete()
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETING A MESSAGE ROUTE.")    
            return redirect("/home")
        else: #this means the user is trying to delete a post they created on a specific user's page
            # print("*"*50)
            messageToBeDeleted = Message.objects.get(id = messageID)
            # print("This is the message being deleted:", messageToBeDeleted)
            messageToBeDeleted.delete()
            userId = messageToBeDeleted.userReceivesPost.id
            print("This is the user's first name of the page to be redirected to:", userId)
            userObject = User.objects.get(id = userId)
            userFirstName = userObject.firstName
            userLastName = userObject.lastName
            userId = userObject.id
            print("This is the user's first name, last name, and id of the page to be redirected to:", userFirstName, userLastName, userId)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS MESSAGE ROUTE.")    
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
        # print("This is the logged in user's comment:", comment)
        # print("This is the post id where the comment is made.")
        messageSelectedForComment = request.POST['postLocationForComment']
        # print(messageSelectedForComment)
        # print("This is the user that made the comment.")
        user = User.objects.get(id=request.session['loginInfo'])
        # print(user)
        # print("This prints the id of the specific user who received the comment.")
        userReceivesComment = request.POST['userReceivesComment']
        print("This is the user receiving the comment:", userReceivesComment)
        recipientOfComment = User.objects.get(id= userReceivesComment)
        #Now that I have the post that receives the comment(messageSelectedForComment), and the user who receives the comment(userReceivesComment), I can use said variables for a query to obtain its' instances.
        #To do that I need to get the message object via id to use for the foreign key/one to many relationship
        theSpecificPost = Message.objects.get(id = messageSelectedForComment)
        if user.id == recipientOfComment.id: #This means the user is commenting on their own page and should be directed home
            commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user, userReceivesComment = recipientOfComment)
            notifyUser = Notification.objects.create(user = user, comment = commentByUser) #This creates a notification for the user receiving the posted message
            return redirect("/home")
        else: #This means the user is commenting on someone else's page and should be directed their
            commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user, userReceivesComment = recipientOfComment)
            notifyUser = Notification.objects.create(user = recipientOfComment, comment = commentByUser) #This creates a notification for the user receiving the posted message
            print("This is the user that needs to be notified of the comment that was made on their page:", recipientOfComment)
            recipientOfComment.notifications += 1
            recipientOfComment.save()
            # print("*"* 50)
            print("THIS IS THE LAST PRINT STATEMENT IN THE PROCESS COMMENT ROUTE.")  
    return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def processCommentOnWall(request):
    postACommentErrors = Comment.objects.commentValidator(request.POST)
    print(postACommentErrors)
    if len(postACommentErrors) > 0:
        for key, value in postACommentErrors.items():
            messages.error(request,value)
        return JsonResponse({"errors": postACommentErrors}, status=400)
    else:
        print("THIS FUNCTION PROCESSES THE FORM FOR POSTING A COMMENT ON THE WALL.")
        # print("*"* 50)
        # print("This is the comment left by the logged in user.")
        comment = request.POST['userComment']
        # print("This is the logged in user's comment:", comment)
        # print("This is the post id where the comment is made.")
        messageSelectedForComment = request.POST['postLocationForComment']
        # print(messageSelectedForComment)
        # print("This is the user that made the comment.")
        user = User.objects.get(id=request.session['loginInfo'])
        # print(user)
        # print("This prints the id of the specific user who received the comment.")
        userReceivesComment = request.POST['userReceivesComment']
        print("This is the user receiving the comment:", userReceivesComment)
        recipientOfComment = User.objects.get(id= userReceivesComment)
        #Now that I have the post that receives the comment(messageSelectedForComment), and the user who receives the comment(userReceivesComment), I can use said variables for a query to obtain its' instances.
        #To do that I need to get the message object via id to use for the foreign key/one to many relationship
        theSpecificPost = Message.objects.get(id = messageSelectedForComment)
        commentByUser = Comment.objects.create(comment = comment, message = theSpecificPost, user = user, userReceivesComment = recipientOfComment)
        notifyUser = Notification.objects.create(user = user, comment = commentByUser) #This creates a notification for the user receiving the posted message
        return redirect("/wall")

def deleteComment(request, userFirstName, userLastName, userId):
    # print("*"*50)
    print("THIS FUNCTION DELETES A POSTED COMMENT.")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    commentData = json.loads(request.body)
    print("This is the received comment data:", commentData) # it is in a dictionary so we need to loop through to get the values
    for commentID in commentData.values():
        print("This is the comment id:", commentID)
        commentToBeDeleted = Comment.objects.get(id = commentID)
        print("This is the comment being deleted:", commentToBeDeleted)
        print("This is the user who received the comment:", commentToBeDeleted.userReceivesComment) #user object
        if loggedInUser == commentToBeDeleted.userReceivesComment: #this means the logged in user is attempting to delete a comment on their own wall and should be directed back here
            commentToBeDeleted.delete()
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETING A COMMENT ROUTE.")    
            return redirect("/home")
        else: #this means the post attempted to be deleted is on a specific user's page
            # print("*"*50)
            print("This is the id of the comment needed to be deleted", commentID)
            commentToBeDeleted = Comment.objects.get(id = commentID)
            print("This is the comment being deleted:", commentToBeDeleted)
            commentToBeDeleted.delete()
            userFirstName = commentToBeDeleted.userReceivesComment.firstName
            userLastName = commentToBeDeleted.userReceivesComment.lastName
            userId = commentToBeDeleted.userReceivesComment.id
            print("THIS IS THE LAST PRINT STATEMENT IN THE DELETE A MESSAGE ROUTE.")    
        return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template

def specificUsersPage(request, userFirstName, userLastName, userId, messageId = 0):
    print("THIS IS THE SPECIFIC USER'S PAGE ROUTE.")
    # print("*"*50)
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    specificUsersPage = User.objects.get(id=userId) #retreiving from the url
    specificUsersFirstName = User.objects.get(firstName=userFirstName) #retreiving from the url
    specificUsersLastName = User.objects.get(lastName=userLastName) #retreiving from the url
    # print("This prints all the messages posted on a page of a specific user and orders them from latest post created.")
    specificUsersMessages = Message.objects.filter(userReceivesPost = userId).order_by('-createdAt')
    if messageId:
        print("THIS IS THE SPECIFIC USER'S PAGE ROUTE THAT WAS REACHED BY THE LOGGED IN USER LIKING A MESAGE ON THE SPECIFIC USER'S PAGE.")
        # print("*"*50)
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
    # print("This prints all the users that have an account, excluding the specific user's page")
    allUsers = User.objects.all().exclude(id=specificUsersPage.id).order_by('?')
    # print(allUsers)
    specificUsersFriends = specificUsersPage.friends.all()
    # print("These are the friends of the specific user:", specificUsersFriends)
    friendCount = specificUsersPage.friends.count() - 1
    print("This is the friend count:", friendCount)
    # print("*"*50)
    print("THIS IS THE LAST PRINT STATEMENT OF THE SPECIFIC USER'S PAGE ROUTE.")
    context = {
        'specificUsersPage': specificUsersPage,
        'specificUsersMessages': specificUsersMessages,
        'allUsers': allUsers,
        'specificUsersFriends': specificUsersFriends,
        'friendCount': friendCount,
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
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

def userLikesOnWall(request, messageId):
    print("THIS IS THE USER LIKES ROUTE ON THE WALL")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:",messageId)
    print("*"*50)
    # print("This is the specific message being liked")
    messageBeingLiked = Message.objects.get(id=messageId)
    print(messageBeingLiked) #prints as a Message Object(#)
    print("This is the user liking the message")
    userWhoLikes = User.objects.get(id=request.session['loginInfo'])
    print(userWhoLikes) # prints as a User Object(#)
    # print("The id of the user giving the like", userWhoLikes.id)
    print("The id of the user receiving the like(the person who wrote the post)", messageBeingLiked.user.id)
    # print("The id of the users who have liked messages:", messageBeingLiked.userLikes.all())
    if userWhoLikes in messageBeingLiked.userLikes.all():
        print("You've already liked the message!")
        return redirect('/wall') #using the name of the url to redirect and passing the variables/params to the form rendering the template
    else:
        messageBeingLiked.userLikes.add(userWhoLikes) #This creates the like - userLikes is the instance name in the Message model holding the many to many relationship
        messageBeingLiked.likeMessageCount += 1
        messageBeingLiked.save()
        print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ON THE WALL ROUTE")
        return redirect('/wall')

def userUnlikesOnWall(request, messageId):
    print("THIS IS THE USER UNLIKES ROUTE ON THE WALL")
    print("*"*50)
    print("THIS IS THE MESSAGE ID:",messageId)
    print("*"*50)
    # print("This is the specific message being liked")
    messageBeingUnliked = Message.objects.get(id=messageId)
    print(messageBeingUnliked) #prints as a Message Object(#)
    print("This is the user unliking the message")
    userWhoUnlikes = User.objects.get(id=request.session['loginInfo'])
    print(userWhoUnlikes) # prints as a User Object(#)
    # print("The id of the user giving the like", userWhoUnlikes.id)
    print("The id of the user receiving the like(the person who wrote the post)", messageBeingUnliked.user.id)
    # print("The id of the users who have liked messages:", messageBeingUnliked.userLikes.all())
    if userWhoUnlikes in messageBeingUnliked.userLikes.all(): #this checks if the logged in user has liked the specific message to begin with
        messageBeingUnliked.userLikes.remove(userWhoUnlikes) #userLikes is the instance name in the Message model holding the many to many relationship
        messageBeingUnliked = Message.objects.get(id = messageId)
        if messageBeingUnliked.likeMessageCount > 0: #this prevents the subtraction when the user tries to unlike a message they have never liked initially
            print("This is the amount of likes the message has:", messageBeingUnliked.likeMessageCount)
            messageBeingUnliked.likeMessageCount -= 1
            print("This is the amount of likes the message has after subtracting one:", messageBeingUnliked.likeMessageCount)
            messageBeingUnliked.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE USER LIKES ON THE WALL ROUTE")
        return redirect('/wall')

def sendFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0):
    print("THIS IS THE SEND A FRIEND REQUEST ROUTE")
    # print("*"*50)
    userReceivesRequest = User.objects.get(id=userId) #the recipient of the friend request
    print("This prints the user object of the user receiving the friend request.", userReceivesRequest)
    # print(userReceivesRequest) #prints as a User Object(#)
    userFirstName = userReceivesRequest.firstName # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    userId = userReceivesRequest.id # need for params to reroute
    userWhoSentFriendRequest = User.objects.get(id=request.session['loginInfo'])
    print("This prints the user object of the user sending the friend request aka the logged in user.")
    print(userWhoSentFriendRequest) # prints as a User Object(#)
    if userWhoSentFriendRequest in userReceivesRequest.friends.all():
        print("You're already friends!")
    else:
        if userWhoSentFriendRequest.id != userReceivesRequest.id: #if this line of code runs it means the friend request occurred on the specific user's page
            print("This print statement means the friend request is being created")
            userReceivesRequest.friends.add(userWhoSentFriendRequest)
            # print("These are all the users the logged in user sent friend requests to:", userWhoSentFriendRequest.friends.all())
            # print("These are all the users who asked to be the logged in user's friend:", userReceivesRequest.friends.all())
            notifyUser = Notification.objects.create(user= userReceivesRequest, friendRequest = userWhoSentFriendRequest) #This creates a notification for the user receiving the posted message
            userReceivesRequest.notifications += 1
            userReceivesRequest.save()
            # print("*"*50)
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,)))
        else: #if these lines of code run it means the friend request occurred on the logged in user's page
            userReceivesRequest.friends.add(userWhoSentFriendRequest)
            print("These are all the users the logged in user sent friend requests to:", userWhoSentFriendRequest.friends.all())
            print("These are all the users who asked to be the logged in user's friend:", userReceivesRequest.friends.all())
            userReceivesRequest.notifications += 1
            userReceivesRequest.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
        return redirect("/home")

def removeFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0):
    print("THIS IS THE REMOVE A FRIEND REQUEST ROUTE")
    print("*"*50)
    userReceivesRequest = User.objects.get(id=userId) #the recipient of the friend request
    print("This prints the user object of the user receiving the friend request.")
    print(userReceivesRequest) #prints as a User Object(#)
    userFirstName = userReceivesRequest.firstName # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    userId = userReceivesRequest.id # need for params to reroute
    userWhoSentFriendRequest = User.objects.get(id=request.session['loginInfo'])
    print("This prints the user object of the user sending the friend request aka the logged in user.")
    print(userWhoSentFriendRequest) # prints as a User Object(#)
    print("*"*50)
    idOfPageLocation = request.POST['userWhoReceivesPost'] #This identifies the location of where the user is currently browsing
    # print("This identifies the id of the location of where the user is currently browsing", idOfPageLocation)
    currentPageLocation = User.objects.get(id= idOfPageLocation) #a hidden input containing the id of the specific user
    if userWhoSentFriendRequest in userReceivesRequest.friends.all():
        userReceivesRequest.friends.remove(userWhoSentFriendRequest)
        if userReceivesRequest.notifications >= 0:
            userReceivesRequest.notifications -= 1
            userReceivesRequest.save()
            print("THIS IS THE LAST PRINT STATEMENT OF THE REMOVE A FRIEND REQUEST ROUTE.")
    if currentPageLocation == loggedInUser:
        return redirect("/home")
    else:
        return redirect(reverse('specificUsersPage', args=(currentPageLocation.firstName, currentPageLocation.lastName, currentPageLocation.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template


def acceptFriendRequest(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0):
    print("THIS IS THE ACCEPT A FRIEND REQUEST ROUTE POOP")
    # print("*"*50)
    userReceivesRequest = User.objects.get(id=request.session['loginInfo'])
    # print(userReceivesRequest) #prints as a User Object(#)
    userWhoSentFriendRequest = User.objects.get(id=userId) #the recipient of the friend request
    # print(userWhoSentFriendRequest) #prints as a User Object(#)
    idOfPageLocation = request.POST['userWhoReceivesPost'] #This identifies the location of where the user is currently browsing
    print("This identifies the id of the location of where the user is currently browsing", idOfPageLocation)
    currentPageLocation = User.objects.get(id= idOfPageLocation) #a hidden input containing the id of the specific user
    # print("This identifies the location of where the user is currently browsing", currentPageLocation)
    print("This is the user page the logged in user is currently on", currentPageLocation)
    userFirstName = currentPageLocation.firstName # need for params to reroute
    userId = currentPageLocation.id # need for params to reroute
    userLastName = userReceivesRequest.lastName # need for params to reroute
    if userReceivesRequest in userWhoSentFriendRequest.friends.all():
        print("You've already accepted the friend request!")
    else:
        print("This print statement means the friend request is being accepted")
        userWhoSentFriendRequest.friends.add(userReceivesRequest)
        #need to remove the notification after accepting the friend request
        removeNotif = Notification.objects.get(user = userReceivesRequest, friendRequest = userWhoSentFriendRequest)
        removeNotif.delete()
        # print("These are all the users the logged in user accepted friend requests from/is now friends with:", userReceivesRequest.friends.all())
        userReceivesRequest.notifications -= 1
        userReceivesRequest.save()
        # print("*"*50)
        if currentPageLocation!= userReceivesRequest:
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
            return redirect(reverse('specificUsersPage', args=(userFirstName, userLastName, userId,)))
        else: 
            print("THIS IS THE LAST PRINT STATEMENT OF THE SEND A FRIEND REQUEST ROUTE.")
        return redirect("/home")

def unfriend(request, userFirstName='firstName', userLastName='lastName', userId=0, messageId = 0):
    print("THIS IS THE DELETE A FRIEND REQUEST ROUTE")
    print("*"*50)
    userWhoSentFriendRequest = User.objects.get(id=userId) #the recipient of the friend request
    print("This prints the user object of the user who sent the friend request.")
    print(userWhoSentFriendRequest) #prints as a User Object(#)
    userFirstName = userWhoSentFriendRequest.firstName # need for params to reroute
    userLastName = userWhoSentFriendRequest.lastName # need for params to reroute
    userId = userWhoSentFriendRequest.id # need for params to reroute
    userReceivesRequest = User.objects.get(id=request.session['loginInfo'])
    print("This prints the user object of the user receiving request aka the logged in user.")
    print(userReceivesRequest) # prints as a User Object(#)
    # print("These are the people a specific user sent friend requests to:", userWhoSentFriendRequest.friends.all())
    #The below code removes the friendship
    userWhoSentFriendRequest.friends.remove(userReceivesRequest)
    userReceivesRequest.friends.remove(userWhoSentFriendRequest)
    #also need to delete this object in the notification model
    removeNotif = Notification.objects.get(user = userReceivesRequest, friendRequest = userWhoSentFriendRequest)
    if removeNotif:
        removeNotif.delete()
        if userReceivesRequest.notifications > 0:
            userReceivesRequest.notifications -= 1
            userReceivesRequest.save()
    print("*"*50)
    print("THIS IS THE LAST PRINT STATEMENT OF THE REMOVE A FRIEND REQUEST ROUTE.")
    return redirect("/home")

def removeMessageNotification(request, messageId):
    print("THIS FUNCTION REMOVES A MESSAGE NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lins of is needed because despite the correct logic below, always reverting to -1
    if messageId:
        print("This console log means there is a message id")
        newMessage = Message.objects.get(id= messageId)
        print("This is the message object that the user is being notified about:", newMessage)
        changeHoverStatus = Notification.objects.get(user = loggedInUser, message = newMessage)
        print("This is the notification object of the user that hovered over this specific message notification:", changeHoverStatus)
        if changeHoverStatus.hover != 0:
            print("This means the new comment notification has already been hovered over.")
        else:
            changeHoverStatus.hover += 1
            changeHoverStatus.save()
            updateLoggedInUserNotifications = loggedInUser
            if updateLoggedInUserNotifications.notifications >= 0:
                updateLoggedInUserNotifications.notifications -= 1
                updateLoggedInUserNotifications.save()
                print("THIS IS THE LAST PRINT STATEMENT IN THE REMOVE MESSAGE NOTIFICATION ROUTE")
        # changeMessageNotificationStatus = Message.objects.get(id=messageId)
        # # changeMessageNotificationStatus = Message.objects.get(id=messageId).update(notification = 0)
        # if changeMessageNotificationStatus.notification == 0: #0 signifies the user had not seen/hovered over the notification message
        #     changeMessageNotificationStatus.notification = 1 #1 signifies the user has now hovered over the notification message, so decrease the notification counter by one
        #     changeMessageNotificationStatus.save()
    return redirect("/home")

def removeCommentNotification(request, commentId):
    print("THIS FUNCTION REMOVES A NEW COMMENT NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the below three lines of code are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("THe notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if commentId:
        print("This console log means there is a comment id")
        newComment = Comment.objects.get(id= commentId)
        print("This is the comment as an object:", newComment)
        changeHoverStatus = Notification.objects.get(user = loggedInUser, comment = newComment)
        print("This is the notification object of the user that hovered over this specific message notification:", changeHoverStatus)
        if changeHoverStatus.hover != 0:
            print("This means the new comment notification has already been hovered over.")
        else:
            changeHoverStatus.hover += 1
            changeHoverStatus.save()
            updateLoggedInUserNotifications = loggedInUser
            if updateLoggedInUserNotifications.notifications >= 0:
                print("The notification is at minimum 0 and will decrease to one.")
                updateLoggedInUserNotifications.notifications -= 1
                updateLoggedInUserNotifications.save()
                print("THIS IS THE LAST PRINT STATEMENT IN THE REMOVE NEW COMMENT NOTIFICATION ROUTE")
    return redirect("/home")

def removeFriendRequestNotification(request, userId):
    print("THIS FUNCTION REMOVES A FIREND REQUEST NOTIFICATION FROM THE NOTIFICATION COUNTER")
    loggedInUser = User.objects.get(id=request.session['loginInfo'])
    #the above three lines of are needed because despite the correct logic below, always reverting to -1
    if loggedInUser.notifications < 0:
        print("The notification counter is negative and needs to be reset to 0.")
        resetNotificationCounter = User.objects.filter(id=request.session['loginInfo']).update(notifications=0) 
    #the above three lins of is needed because despite the correct logic below, always reverting to -1
    if userId:
        print("This console log means there is a user id")
        newFriendRequest = User.objects.get(id= userId)
        print("This is the object of the user that sent the friend request:", newFriendRequest)
        changeHoverStatus = Notification.objects.get(user = loggedInUser, friendRequest = newFriendRequest)
        print("This is the notification object of the user that hovered over this specific friend request notification:", changeHoverStatus)
        if changeHoverStatus.hover != 0:
            print("This means the friend request notification has already been hovered over.")
        else:
            changeHoverStatus.hover += 1
            changeHoverStatus.save()
            updateLoggedInUserNotifications = loggedInUser
            if updateLoggedInUserNotifications.notifications >= 0:
                print("The notification is at minimum 0")
                updateLoggedInUserNotifications.notifications -= 1
                updateLoggedInUserNotifications.save()
                print("THIS IS THE LAST PRINT STATEMENT IN THE REMOVE FRIEND REQUEST NOTIFICATION ROUTE")
    return redirect("/home")

def clearAllNotifications(request):
    print("THIS FUNCTION CLEARS ALL THE NOTIFICATIONS THE LOGGED IN USER HAS")
    loggedInUser = User.objects.get(id=request.session["loginInfo"])
    removeMessageNotifications = Notification.objects.filter(user= loggedInUser)
    print("These are the notifications that will be removed:", removeMessageNotifications)
    removeMessageNotifications.delete()
    removeFriendRequestNotifications = Notification.objects.filter(friendRequest= loggedInUser)
    removeFriendRequestNotifications.delete()
    print("THIS IS THE LAST PRINT STATEMENT IN THE CLEAR ALL NOTIFICATIONS")
    return redirect("/home")

def searchForUsersProfile(request):
    print("THIS IS THE SEARCH FOR A USER PROFILE ROUTE")
    loggedInUser = User.objects.get(id=request.session["loginInfo"])
    try: #used so i can incoperate 'except index error' in case the logged in user triggers an index error searching for a user not in the database
        if request.method == 'GET':
            # searchForUser = request.GET.get("searchBarInput")
            searchForUser = request.GET.get("searchBarInput")
            if searchForUser == '':
                print("No search submitted.") 
                id = loggedInUser.id #sends them back to their page
            searchForUser = request.GET.get('searchBarInput').split() #creates a list of arrays with the names submitted by the logged in user
            if searchForUser is not None: #use to prevent NoneType object attribute split error
            # print("The name(s) the logged in user typed", searchForUser)
                for name in searchForUser: # have to iterate to use title on a list
                    print("The name(s) searched:", name.title())
                    if len(searchForUser) == 1:
                        searchedNameOne = name.title() #title capitalizes the submitted data
                        print("This means there was only one name submitted", searchedNameOne)
                        id = User.objects.filter(Q(firstName = (searchedNameOne))| Q(lastName= (searchedNameOne))).values('id')[0]['id']
                    if len(searchForUser) > 1:
                        searchedNameOne = searchForUser[0].title()
                        searchedNameTwo = searchForUser[1].title()
                        print("This means there was two names submitted", searchedNameOne, searchedNameTwo)
                        id = User.objects.filter(Q(firstName = (searchedNameOne))| Q(lastName= (searchedNameTwo))| Q(firstName = (searchedNameTwo))| Q(lastName= (searchedNameOne))).values('id')[0]['id'] #switched the order to include all ways the user typers their search
                userProfile = User.objects.get(id = id) #this retrieves the searched user as an object
                userProfile.firstName
                userProfile.lastName
                print("This is the searched user's first name, last name, and id:", userProfile.firstName, userProfile.lastName, userProfile.id)
                print("THIS IS THE LAST PRINT STATEMENT OF THE SEARCH FOR A USER PROFILE ROUTE")
                return redirect(reverse('specificUsersPage', args=(userProfile.firstName, userProfile.lastName, userProfile.id,))) #using the name of the url to redirect and passing the variables/params to the form rendering the template
        else:
            print("This means it is empty")
    except IndexError:
        print("No results found!")
    context = {
        'loggedInUser': User.objects.get(id=request.session['loginInfo']),
        'allUsers': User.objects.all().exclude(id=request.session['loginInfo']).order_by('firstName'), #orders alphabetically
        # 'searchForUser': searchForUser,
        'notifications': Notification.objects.all,
        'loggedInUsersNotifs': Notification.objects.filter(user=loggedInUser)
    }
    return render(request, "noUserFound.html", context)

def logout(request):
    request.session.clear()
    return redirect('/')