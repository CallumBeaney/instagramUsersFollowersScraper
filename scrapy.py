import csv
import os

import instaloader
from instaloader import Profile

from config import alreadyKnown, userDataFile, myAccountUserName, myAccountPassword, profileToTarget

# https://instaloader.github.io/as-module.html

userData = {
    "username": "",
    "name": "",
    "instaUrl" : "",
    "url": "",
    "business": "",
    "follows": 0,
    "followers": 0,
    "notes": ''
}

def main():
  L = instaloader.Instaloader()
  L.login(myAccountUserName, myAccountPassword)
  targetProfile = profileToTarget
  # targetProfile = L.check_profile_id(targetProfile)

  profile = Profile.from_username(L.context, targetProfile)

  userDataList = getProfileData(profile)
  writeUserDataToSpreadsheet(userDataList, userDataFile)


def getProfileData(profile):
  user_data_list = []
  count = 0
  print("Started building profile list")
  for follower in profile.get_followers():

    # if count == 3: # for debug
    #   break

    if checkUsernameInKnownUsersFile(follower.username, alreadyKnown) == True:
      print("#" + str(count) + " " + follower.username + " already scanned.\tSkipping.")
      count += 1
      continue

    saveUsernameToKnownUsersFile(follower.username, alreadyKnown)

    # Make an instance of the userData dict and pass it all in
    user_data = userData.copy()

    user_data["username"] = follower.username
    user_data["name"] = follower.full_name
    user_data["instaUrl"] = f"https://www.instagram.com/{follower.username}/"    
    user_data["url"] = follower.external_url

    if follower.is_business_account:
      user_data["business"] = follower.business_category_name
    
    if follower.is_private == False:
      user_data["follows"] = follower.followees
      user_data["followers"] = follower.followers

    user_data_list.append(user_data)

    print("#" + str(count) + " added " + follower.username + " to your user list.")
    count += 1

  print("Finished building profile list")
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