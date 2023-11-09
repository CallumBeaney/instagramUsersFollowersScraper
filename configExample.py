DEBUG = False
# DEBUG = True # this just stops a scrape after a few profiles

profileToTarget = "profileName" # the profile username you want to get info about

myAccountUserName = "instaHandle" 
myAccountPassword = "instaPassword"


# KNOWN FOLLOW_ERS/EES FILES
knownFollowersFile = "alreadyKnownFollowers.txt"
knownFolloweesFile = "alreadyKnownFollowees.txt"
# Because we are checking the target profile without being logged in _as_ that profile, we cannot use the API's functions to check whether we are being followed by X or not. So here, we build a list of already known followers, and followees. 
# We must build these files, and then reference the .txt files produced, and see whether they contain the same entries. If they do, there is a mutual follow. See the function getProfileData in scrapy.py
# These files should be persistent; they shouldn't be deleted but kept in the directory as a reference

# ALREADY PROCESSED FILE
# this is added to in much the same manner as above, but rather than used to just check for mutual follows, this is used to indicate data already stored in a spreadsheet
knownProfiles = "alreadyProcessedProfiles.txt" 

# This is the output file. You can take the results of this and add it to your spreadsheet or CSV
# The first times you use the program it will be large. Then, the more followers you log, the smaller the output will be, which you can then append to your master spreadsheet or CSV
userDataFile = "outputData.csv"



