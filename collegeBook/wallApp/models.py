from django.db import models
import re
import bcrypt
from datetime import datetime, date

#The below code is for the login registration

class UserManager(models.Manager):
    def registrationValidator(self, postData):
        errors = {}
        print('This is the registrationValidation from models.')

        #The below line of code makes sure the first name is submitted. 
        if len(postData['userFirstName']) == 0:
            errors['firstName'] = "Must submit a first name."

        #The below line of code makes sure the last name is submitted. 
        if len(postData['userLastName']) == 0:
            errors['lastName'] = "Must submit a last name."

        #The below line of code makes sure the first name is a certain length. 
        if len(postData['userFirstName']) < 2:
            if len(postData['initialPassword']) != 0: #This logic prevents this error from displaying when nothing is typed in the first name field and only shows when too short of a first name is typed
                errors['firstName'] = "First name should be at least 2 characters."

        #The below line of code makes sure the last name is a certain length. 
        if len(postData['userLastName']) < 2:
            if len(postData['initialPassword']) != 0: #This logic prevents this error from displaying when nothing is typed in the last name field and only shows when too short of a first name is typed
                errors['lastName'] = "Last name should be at least 2 characters."

        if len(postData['initialEmail']) == 0:
            errors['emailAddressRequired'] = "Must submit an email address."

        # #The below line of code makes sure the birthday is in the past. This is why I imported datetime
        # #First I set a variable equal to the current date.
        # currentDate = datetime.now()
        # print(postData['userBirthday'])
        # print(currentDate.strftime('%m-%d-%Y'))
        # #Secondly, I comapred the above variable to the inputed birthday by the user. I had to convert the current date variable to a string using strftime in order for the comparsion to work.
        # if (postData['userBirthday']) >= currentDate.strftime('%Y-%m-%d'):
        #     errors['birthday'] = "Birthday should be prior to the current date. Please try again."
        
        # #The below line of code makes sure the user is at least 13 years old. This is why I imported datetime
        # submittedBirthday = postData['userBirthday']
        # atLeastAge = 13
        # atLeastAgeInBirthdayFormat = '2007-12-31'
        # todaysDate = date.today()
        # print("*"*50)
        # # print(todaysDate)
        # print(submittedBirthday)
        # # print(atLeastAge)
        # # print(atLeastAgeInBirthdayFormat)
        # print("*"*50)
        # atLeastAgeInBirthdayFormat = datetime.strptime(atLeastAgeInBirthdayFormat,"%Y-%m-%d")
        # submittedBirthday = datetime.strptime(submittedBirthday,"%Y-%m-%d")
        # #The > symbol because the year is higher than the required year meaning they are too young.
        # if submittedBirthday > atLeastAgeInBirthdayFormat:
        #     errors['tooYoung'] = "You must be at least 13 years of age."

        #The below line of code makes sure it is a correct email format. 
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['initialEmail']):
            if len(postData['initialEmail']) != 0: #This logic prevents this error from displaying when nothing is typed in the email field and only shows when an incorrect email formation is typed
                errors['emailAddress'] = "Invalid email address."
        
        #The  below line of code makes sure that email is not already chosen.
        alreadyUsedEmail = User.objects.filter(emailAddress = postData['initialEmail'])
        if len(alreadyUsedEmail) > 0:
            errors['emailAddress'] = "Email address already used. Please try another email address."
        
        #The below line of code makes sure the password is submitted. 
        if len(postData['initialPassword']) == 0:
            errors['password'] = "Must submit a password."

        
        #The below line of code makes sure the password and confirmed password are the same.
        submittedPassword = postData['initialPassword']
        submittedConfirmPassword = postData['userConfirmPassword']
        if submittedPassword != submittedConfirmPassword:
            errors['password'] = "Passwords do not match. Please try again."
        
        #The below line of code makes sure the password is a certain length.
        if len(submittedPassword) < 8:
            if len(submittedPassword) != 0: #This logic prevents this error from displaying when nothing is typed in the password field and only shows when the password field is not long enough
                errors['password'] = "Password should be at least 8 characters."

        #The below line of code makes sure the birthday month is submitted. 
        # if len(postData.get("userBirthdayMonth", [])) < 1: #Written slightly different with get because it's a select dropbuttton
            # errors["birthdayMonth"] = "Must submit a month for the birthday field."
        #THE ABOVE WORKS(SORT OF)
        # if len(postData["userBirthdayMonth"]) < 1:
        #     errors["birthdayMonth"] = "Must submit a month for the birthday field."
        
        # #The below line of code makes sure the birthday day is submitted. 
        # if len(postData.get("userBirthdayDay", [])) < 1:
        #     errors["birthdayDay"] = "Must submit a day for the birthday field."

        # #The below line of code makes sure the birthday year is submitted. 
        # if len(postData.get("userBirthdayYear", [])) < 1:
        #     errors["birthdayYear"] = "Must submit a year for the birthday field."

        # print('This is the registrationValidation from models with the errors.')
        # print(errors)

        #TIME TO DO PHOTO IMAGE ERRORS
        return errors
    
    def loginValidator(self, postData):
        errors = {}
        print("*"*50)

        #The below line of code makes sure an email is submitted. 
        if len(postData['userEmail']) == 0:
            errors['emailAddressRequired'] = "Must submit an email address"
        
        #The below line of code makes sure it is a correct email format. 
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['userEmail']):
            if len(postData['userEmail']) != 0: #This logic prevents the "Must submit an email address" error from displaying when nothing is typed in the email field and only shows when an incorrect email formation is typed
                errors['emailAddress'] = "Invalid email address."
        
        #The below line of code makes sure the email is registered prior to logining in. 
        #Filter instead of get because even if the query is empty, it will return an empty list whereas get would throw an error
        verifyLoginEmail = User.objects.filter(emailAddress = postData['userEmail'])
        if len(verifyLoginEmail)  == 0:
            if len(postData['userEmail']) != 0: #This logic prevents this error from displaying when nothing is typed in the email field and only shows when an unregistered email is typed
                errors['emailAddress'] = "Email address is not recognized. Please register."
        else:
        #The below line of code makes sure the password entered when loggining in is the same as the password from registration. 
        # We make a variable equal to array[0] because there should only be one email(value) available in the query because of the prior registration validations  
            verifyUser = verifyLoginEmail[0]
            if bcrypt.checkpw(postData['userPassword'].encode(), verifyUser.password.encode()):
                print("password match")
            else:
                if len(postData['userPassword']) != 0: #This logic prevents this error from displaying when nothing is typed in the password field and only shows when an incorrect password is typed
                    errors['passwordIncorrect'] = "Invalid password. Please try again."
        
        #The below line of code makes sure a password is submitted. 
        # if len(postData['userPassword']) == 0:
        #         errors['passwordRequired'] = "Must submit a password"

        #The below line of code makes sure a password is submitted. 
        if (len(verifyLoginEmail)  == 0) and (len(postData['userEmail']) != 0): #These combined if statements prevent the invalid password error from occuring when an email is given by the user but it is an unregistered email.
            print("inside initial if statement for the submit a password error")
        else:
            if len(postData['userPassword']) == 0:
                errors['passwordRequired'] = "Must submit a password"

        return errors

    def profileIntroValidator(self, postData):
        errors = {}
        print("*"*50)
        #The below line of code makes sure an email is submitted. 
        
        if len(postData['userUniversity']) == 0:
            errors['universityRequired'] = "Must submit a college"

        if len(postData['userHighSchool']) == 0:
            errors['highSchoolRequired'] = "Must submit a high school"
        
        # if len(postData['userDormBuilding']) == 0:
        #     errors['dormBuildingRequired'] = "Must submit a dorm building"

        if len(postData['userHomeTown']) == 0:
            errors['homeTownRequired'] = "Must submit a home town"
        print("*"*50)
        return errors


#The above code is for the login registration

#The below code is for the validations of posting a message

class MessageManager(models.Manager):
    def messageValidator(self, postData):
        print("*"*50)
        errors = {}
        # print('This is the postingAMessageValidator from models.')
        #The below line of code makes sure a message is submitted. 
        if len(postData['userMessage']) == 0:
            errors['messageRequired'] = "Oops, you forgot to write something!"
        print("*"*50)
        return errors

#The above code is for the validations of posting a message

#The below code is for the validations of posting a comment

class CommentManager(models.Manager):
    def commentValidator(self, postData):
        print("*"*50)
        errors = {}
        # print('This is the postingAMessageValidator from models.')
        #The below line of code makes sure a comment is submitted. 
        if len(postData['userComment']) == 0:
            errors['commentRequired'] = "Oops, you forgot to reply!"
        print("*"*50)
        return errors

#The above code is for the validations of posting a comment

class User(models.Model):
    firstName = models.CharField(max_length = 255)
    lastName = models.CharField(max_length = 255)
    # birthday = models.DateField(null = True)
    birthdayMonth = models.CharField(max_length = 30, null = True)
    birthdayDay = models.IntegerField(null = True)
    birthdayYear = models.IntegerField(null = True)
    emailAddress = models.CharField(max_length = 255)
    password = models.CharField(max_length = 255)
    confirmPassword = models.CharField(max_length = 255)
    profilePic= models.ImageField(upload_to='submittedProfilePicImages/', null=True, verbose_name="")
    profileHeader = models.CharField(max_length = 255, default = "") #The caption underneath the profile picture
    friends = models.ManyToManyField('self', related_name="friendship", symmetrical= False) # Self states this ManyToManyField is symmetrical – that is, if I am your friend, then you are my friend. So setting symmetrical to false makes the 'friendship' one way
    notifications = models.IntegerField(default = "0")
    userCheckBox = models.BooleanField(default = "0") # An option for the user to not fill out the user intro fields. (the below instances) 0 signifies false
    userUniversity = models.CharField(max_length = 255, default = "")
    userHighSchool = models.CharField(max_length = 255, default = "")
    userDormBuilding = models.CharField(max_length = 255, default = "")
    userHomeTown = models.CharField(max_length = 255, default = "")
    objects = UserManager()
    createdAt = models.DateTimeField(auto_now_add = True)
    updatedAt = models.DateTimeField(auto_now = True)

    def __repr__(self):
        return f"<User object: {self.firstName} {self.lastName} {self.birthdayMonth} {self.birthdayDay} {self.birthdayYear} {self.emailAddress} {self.password} {self.confirmPassword} {str(self.profilePic)} ({self.id})>"

class Message(models.Model):
    message = models.TextField()
    user = models.ForeignKey(User, related_name = "messages", on_delete=models.CASCADE) #the user who makes the post
    userReceivesPost = models.ForeignKey(User, related_name = "postRecipient", on_delete=models.CASCADE, null=True,) #the user who receives the post
    userLikes = models.ManyToManyField(User, related_name = 'theLiker') # the user who likes the post
    likeMessageCount = models.IntegerField(default = 0)
    likeMessageCountMinusDisplayNames = models.IntegerField(default = 0)
    objects = MessageManager()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"<Message object: {self.message} {self.user} ({self.id})>"

class Comment(models.Model):
    comment = models.TextField()
    message = models.ForeignKey(Message, related_name = "comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name = "comments", on_delete=models.CASCADE) #the user who makes the comment
    userReceivesComment = models.ForeignKey(User, related_name = "commentee", on_delete=models.CASCADE, null=True,) #the user who receives the comment
    objects = CommentManager()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __repr__(self):
        return f"<Comment object: {self.comment} {self.message} {self.user} ({self.id})>"





