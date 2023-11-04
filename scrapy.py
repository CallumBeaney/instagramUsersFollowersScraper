import csv
import os
import time

import instaloader
from instaloader import Profile

from config import knownFollowersFile, knownFolloweesFile, knownProfiles, userDataFile, myAccountUserName, myAccountPassword, profileToTarget

# https://instaloader.github.io/as-module.html

userData = {
    "username": "",
    "name": "",
    "instagram" : "",
    "website": "",
    "follow status": "",
    "business type": "",
    "following count": 0,
    "followers count": 0,
    "notes": ''
}

def main():
  L = instaloader.Instaloader()
  L.login(myAccountUserName, myAccountPassword)
  time.sleep(1)
  targetProfile = profileToTarget
  # targetProfile = L.check_profile_id(targetProfile)

  dataListToSave = []
  
  profile = Profile.from_username(L.context, targetProfile)
  time.sleep(1)


  # IMPORTANT RE: 429 ERRORS: https://instaloader.github.io/troubleshooting.html#too-many-requests

  # To avoid a 429 Error, try to do each of these one at a time, and wait a while after.
  followers = profile.get_followers()
  time.sleep(2)

  followees = profile.get_followees()
  time.sleep(2)


  # Once you have built a file, you might not need to do so again for a while. 
  buildFollowersFolloweesList(followers, knownFollowersFile)
  buildFollowersFolloweesList(followees, knownFolloweesFile)

  followersDataList = getProfileData(followers)
  dataListToSave += followersDataList

  followingDataList = getProfileData(followees)
  dataListToSave += followingDataList

  writeUserDataToSpreadsheet(dataListToSave, userDataFile)


def buildFollowersFolloweesList(profiles, filePath):
  for follower in profiles:
    username = follower.username
    if checkUsernameInKnownUsersFile(username, filePath) == False:      
      saveUsernameToKnownUsersFile(username, filePath)
  return


def getProfileData(profiles):
  user_data_list = []
  count = 0
  print("Started building profile list")
  for follower in profiles:

    # if count == 3: # for debug
    #   print("_________DEBUG_________ : BREAKING")
    #   break
    username = follower.username
    
    print("checkingUsernamesInKnownUsers")
    if checkUsernameInKnownUsersFile(username, knownProfiles) == True:
      print("#" + str(count) + " " + username + " already scanned.\tSkipping.")
      count += 1
      continue

    print("saving to known users")
    saveUsernameToKnownUsersFile(username, knownProfiles)

    # Make an instance of the userData dict and pass it all in
    user_data = userData.copy()
    user_data["username"] = username
    user_data["name"] = follower.full_name
    user_data["instagram"] = f"https://www.instagram.com/{username}/"    
    user_data["website"] = follower.external_url

    # This hack because I'm doing this from a 3rd account

    isFollowed  = checkUsernameInKnownUsersFile(username, knownFollowersFile)
    isFollowing = checkUsernameInKnownUsersFile(username, knownFolloweesFile)

    if isFollowed and isFollowing:
      user_data["follow status"] = "you follow each other"
    elif isFollowed and not isFollowing:
      user_data["follow status"] = "they follow you"
    elif not isFollowed and isFollowing:
      user_data["follow status"] = "you follow them"

    if follower.is_business_account:
      user_data["business type"] = follower.business_category_name
    
    if follower.is_private == False:
      user_data["following count"] = follower.followees
      user_data["followers count"] = follower.followers

    user_data_list.append(user_data)

    print("#" + str(count) + " added " + username + " to your user list.")
    count += 1

  print("Finished building data list")
  return user_data_list


def checkUsernameInKnownUsersFile(username, file_path):
  if not os.path.isfile(file_path):
    return False
  with open(file_path, 'r') as file:
    usernames = file.readlines()
    return username in [u.strip() for u in usernames]


def saveUsernameToKnownUsersFile(username, file_path):
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