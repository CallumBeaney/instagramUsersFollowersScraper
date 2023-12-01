import csv
import os
import time
import sys

import instaloader
from instaloader import Profile
from instaloader import exceptions
from instaloader.exceptions import QueryReturnedBadRequestException
from instaloader.exceptions import TooManyRequestsException


from config import knownFollowersFile, knownFolloweesFile, processedProfiles, userDataFile, myAccountUserName, myAccountPassword, profileToTarget, DEBUG

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

validArgs = ["scrape followers", "scrape followees", "get followers", "get followees"]
usage = "Usage: python3 scrapy.py scrape/get followers/followees" 

def main():

  if len(sys.argv) != 3:
    print(usage)
    sys.exit(1)

  userCommand = sys.argv[1] + " " + sys.argv[2]
  if (userCommand not in validArgs):
    print(usage)
    sys.exit(1)

  L = instaloader.Instaloader()   # Create an instance of the bot
  L.login(myAccountUserName, myAccountPassword)
  time.sleep(1) 
  targetProfile = profileToTarget
  profile = Profile.from_username(L.context, targetProfile)
  time.sleep(1)

  dataListToSave = [] 

  if (userCommand == "scrape followers"):
    followers = profile.get_followers()
    followingDataList = getProfileData(followers)
    dataListToSave += followingDataList

  elif (userCommand == "scrape followees"):
    followees = profile.get_followees()
    followeeDataList = getProfileData(followees)
    dataListToSave += followeeDataList
 
  elif (userCommand == "get followers"):
    followers = profile.get_followers()
    buildFollowersFolloweesList(followers, knownFollowersFile)
    sys.exit(0)

  elif (userCommand == "get followees"):
    followees = profile.get_followees()
    buildFollowersFolloweesList(followees, knownFollowersFile)
    sys.exit(0)

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
      
      if DEBUG is True:
        if (count == 3):
          print("_________DEBUG_________ : BREAKING")
          break
      
      print(f"checking {username} in known users")
      if checkUsernameInKnownUsersFile(username, processedProfiles) == True:
        print(username + " already scanned and in processed profiles list file. Skipping.")
        count += 1
        time.sleep(3)
        continue

      saveUsernameToKnownUsersFile(username, processedProfiles)

      # Make an instance of the userData dict and pass it all in
      user_data = userData.copy()
      user_data["username"] = username
      user_data["name"] = profile.full_name
      user_data["instagram"] = f"https://www.instagram.com/{username}/"  

      try:
        user_data["website"] = profile.external_url
      except KeyError:
          user_data["website"] = ""  

      # This hack because I'm doing this from a 3rd account; see knownFollowersFile etc in config.py
      isFollowed  = checkUsernameInKnownUsersFile(username, knownFollowersFile)
      isFollowing = checkUsernameInKnownUsersFile(username, knownFolloweesFile)

      followStatus = ""
      if isFollowed and isFollowing:
        followStatus = "each other"
      elif isFollowed and not isFollowing:
        followStatus = "follows you"
      elif not isFollowed and isFollowing:
        followStatus = "you follow"
    
      user_data["follow status"] = followStatus

      if profile.is_business_account:
        user_data["business type"] = profile.business_category_name

      user_data_list.append(user_data)

      print("added " + username + " to your user list.")
      time.sleep(3) # interrupt to alay risk of 429 error
      count += 1
    except Exception as ex:
      print(f"Exception: {ex}. Check your scraping profile's account status, or frequency of access. There may otherwise be an API issue.")
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