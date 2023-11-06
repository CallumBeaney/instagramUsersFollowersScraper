This is a rudimentary instagram follower scraper built using Instaloader API.  
1. It saves the usernames of instagram profiles following/followed by a target profile, and saves those profiles to two Known Followers/ees files (see: buildFollowersFolloweesList).  
2. It then checks those profile list files to see who is following whom.  
3. You can then extract information about your target profile's followers/followees and saves the usernames it processes into an Already Processed Profiles file (see: getProfileData). Extracted data is parsed into a CSV output.  
4. It checks that file every time you run an extraction operation so that only new profiles are scraped in the future.  