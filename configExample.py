profileToTarget = "profileName"

# KNOWN FOLLOW_ERS/EES FILES
# Because we are checking the target profile without being logged in _as_ that profile, we cannot use the API's functions to check whether we are being followed by X or not. So here, we build a list of already known followers, and followees. 
# We must build these files, and then reference the .txt files produced, and see whether they contain the same entries. If they do, there is a mutual follow. See the function getProfileData() in scrapy.py:

    # isFollowed  = checkUsernameInKnownUsersFile(username, knownFollowersFile)
    # isFollowing = checkUsernameInKnownUsersFile(username, knownFolloweesFile)
    #
    # if isFollowed and isFollowing:
    #   user_data["follow status"] = "you follow each other"
    # elif isFollowed and not isFollowing:
    #   user_data["follow status"] = "they follow you"
    # elif not isFollowed and isFollowing:
    #   user_data["follow status"] = "you follow them"

# We can add to these periodically, but they should not be run in a normal scrape.  
# These files should be persistent; they shouldn't be deleted but kept in the directory as a reference
knownFollowersFile = "alreadyKnownFollowers.txt"
knownFolloweesFile = "alreadyKnownFollowees.txt"

# ALREADY PROCESSED FILE
# this is added to in much the same manner as above, but rather than used to just check for mutual follows, this is used to indicate data already stored in a spreadsheet
knownProfiles = "alreadyProcessedProfiles.txt" 

# This is the output file. You can take the results of this and add it to your spreadsheet or CSV
# The first times you use the program it will be large. Then, the more followers you log, the smaller the output will be, which you can then append to your master spreadsheet or CSV
userDataFile = "./userData.csv"

myAccountUserName = "instaHandle"
myAccountPassword = "instaPassword"

