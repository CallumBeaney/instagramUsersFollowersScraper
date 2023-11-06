import csv
import os
import time

import instaloader
from instaloader import Profile
from instaloader import exceptions

from config import knownFollowersFile, knownFolloweesFile, knownProfiles, userDataFile, myAccountUserName, myAccountPassword, profileToTarget

# API NOTES:      https://instaloader.github.io/as-module.html
# RE: 429 ERRORS: https://instaloader.github.io/troubleshooting.html#too-many-requests

userData = {
  # These K:V pairs correspond with the CSV's header fields for the spreadsheet 
    "username": "",
    "name": "",
    "instagram" : "",
    "website": "",
    "follow status": "",
    "business type": "",
    "notes": ''
}


def main():

      ########### Must not change anything below this line ###########

  L = instaloader.Instaloader()   # Create an instance of the bot
  L.login(myAccountUserName, myAccountPassword)
  time.sleep(1)
  targetProfile = profileToTarget # see config.py  
  profile = Profile.from_username(L.context, targetProfile)
  time.sleep(1)

      ########### Must not change anything above this line ###########


  ##### COMMENT OUT THE FUNCTION GROUPS YOU DON'T NEED #####

  dataListToSave = [] 

  followers = profile.get_followers()
  # followees = profile.get_followees()

  ### BUILD REFERENCE .TXT FILES:
    # To avoid a 429 Error, try to do each of these one at a time, and wait a while after.
    # Once you have built a followers/followees file, you might not need to do so again for a while. 
  # buildFollowersFolloweesList(followers, knownFollowersFile)
  # buildFollowersFolloweesList(followees, knownFolloweesFile)

  ### BUILD & EXPORT USER INFO .CSV 
    # it is preferable to do only one of these at a time, then wait an hour or so and do the other.
  followersDataList = getProfileData(followers) 
  dataListToSave += followersDataList

  # followingDataList = getProfileData(followees)
  # dataListToSave += followingDataList

  ### OUTPUT SCRAPED DATA
  writeUserDataToSpreadsheet(dataListToSave, userDataFile)
  return



def buildFollowersFolloweesList(profiles, filePath):
  for profile in profiles:
    username = profile.username
    if checkUsernameInKnownUsersFile(username, filePath) == False:      
      saveUsernameToKnownUsersFile(username, filePath)
  return



# This extracts the user data from each profile in a list of profile objects. 
# Each time you use a method on a profile object, you are commanding a bot to interact with instagram in a virtual machine. It is preferable to make the minimum number of requests necessary. 
def getProfileData(profiles):
  
  user_data_list = []
  count = 0
  print("Started building profile list")

  for profile in profiles:

    try:
      username = profile.username

      if count == 3:
        print("_________DEBUG_________ : BREAKING")
        break
      
      print(f"checking {username} in known users")
      if checkUsernameInKnownUsersFile(username, knownProfiles) == True:
        print(username + " already scanned and in processed profiles list file. Skipping.")
        count += 1
        time.sleep(3)
        continue

      saveUsernameToKnownUsersFile(username, knownProfiles)

      # Make an instance of the userData dict and pass it all in
      user_data = userData.copy()
      user_data["username"] = username
      user_data["name"] = profile.full_name
      user_data["instagram"] = f"https://www.instagram.com/{username}/"    
      user_data["website"] = profile.external_url

      # This hack because I'm doing this from a 3rd account; see knownFollowersFile etc in config.py
      isFollowed  = checkUsernameInKnownUsersFile(username, knownFollowersFile)
      isFollowing = checkUsernameInKnownUsersFile(username, knownFolloweesFile)

      followStatus = ""
      if isFollowed and isFollowing:
        followStatus = "you follow each other"
      elif isFollowed and not isFollowing:
        followStatus = "they follow you"
      elif not isFollowed and isFollowing:
        followStatus = "you follow them"
    
      user_data["follow status"] = followStatus

      if profile.is_business_account:
        user_data["business type"] = profile.business_category_name

      user_data_list.append(user_data)

      print("added " + username + " to your user list.")
      time.sleep(3) # interrupt to alay risk of 429 error
      count += 1
    except TooManyRequestsException as ex:
      # if you get a 429 error, this should save what you got so far and output at least that
      return user_data_list

  print("Finished building data list")
  return user_data_list



def checkUsernameInKnownUsersFile(username, file_path):
  if not os.path.isfile(file_path):
    return False
  with open(file_path, 'r') as file:
    usernames = file.readlines()
    return username in [u.strip() for u in usernames]



def saveUsernameToKnownUsersFile(username, file_path):
  print(f"saving {username} to processed profiles list file")
  with open(file_path, 'a') as file:
    file.write(username + '\n')
  return



def writeUserDataToSpreadsheet(userList, filePath):
  print('writing to csv')
  fieldNames = list(userData.keys())

  # Check if the file already exists
  if os.path.isfile(filePath):
    with open(filePath, mode = 'a', newline = '') as csvFile:
      writer = csv.DictWriter(csvFile, fieldnames = fieldNames)
      for user in userList:
        writer.writerow(user)
    print(f"Data appended to {filePath}")
  else:
    with open(filePath, mode='w', newline='') as csvFile:
      writer = csv.DictWriter(csvFile, fieldnames = fieldNames)
      writer.writeheader()
      for user in userList:
        writer.writerow(user)
    print(f"Data written to {filePath}")
      
  return


if __name__ == "__main__":
  main()