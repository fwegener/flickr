#!/usr/bin/python

# pip install selenium
#

FLICKR_USERNAME = 'wegener_frank'
FLICKR_PASSWORD = 'TfQJ7Xk08VmuUxoVTRoZ'
MY_USERID       = '133142364@N04'

MY_GROUPS = [
#    '2753044@N23',   # Street One
#    '94761711@N00',  # HCSP (Hardcore Street Photography)

    '850014@N23',    # Urban Urban Urban
    '1225972@N20',   # Black and White Photography Art
    '97369127@N00',  # HS-Bilderflut
    '66351550@N00',  # White and Black Photography'
    '1213889@N25',   # Black & White Done Right !
    '1518582@N21',   # Aspiring Street Photographers
    '38613568@N00',  # Black and White Photo Heaven
    '16978849@N00',  # Black and White
    '1205830@N24',   # Black and White Master Photos
    '1714580@N21',   # Street!
    '1985435@N21',   # Street Photos only
    '2128344@N23',   # Streetlife
    '319155@N20',    # Streetphotography
    '1576994@N21',   # Street Photography Blog
    '1287600@N22',   # Street Photographer
    '2179059@N21',   # Street Photography Magazine
    '2146185@N24',   # Street Photography!
    '81445012@N00',  # Street Composition
    '870105@N22',    # Street Photography and Photographers Rights
    '579020@N23',    # Street Photographers
    '883415@N22',    # Street Photography
    '77501447@N00',  # The Real Street Photography
    '1798316@N21',   # The Secret Life of Pasta - Street Photographer only
    '1535600@N20',   # STREET PHOTOGRAPHY
    '71183855@N00',  # Street Life
    '2139291@N24',   # Street Photography in B&W
    '1035536@N24',   # All Street Photography
    '1609940@N23',   # The Street Photograph
    '967234@N24',    # Street Photographers
]


import time
import flickr
import pickle
import sys
import urllib

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException


verbose = False
Paused  = False



class User():
    def __init__(self, id):
        self._user = flickr.User(id)
        self._favorite_list = None
        self._contact_list = None
        self.photo_list = None
        self.likes_of_day = None
        self.id = str(self._user.id)


    def _contacts(self, paused = False):
        if self._contact_list == None:
            #if Paused:
            print(self.id)
            try:
                self._contact_list = flickr.contacts_getPublicList(self.id)
            except:
                self._contact_list = []
            
        return self._contact_list


    def _favorites(self):
        if self._favorite_list == None:
            try:
                self._favorites_list = self._user.getPublicFavorites(per_page=100000000)
            except:
                self._favorites_list = []

        return self._favorites_list


    def name(self):
        if len(self._user.realname) > 0:
            return self._user.realname

        return(self.username())


    def username(self):
        return self._user.username


    def firstdate(self):
        return datetime.fromtimestamp(float(self._user.photos_firstdate))


    def days_online(self):
        try:
           return((datetime.today() - datetime.fromtimestamp(float(self._user.photos_firstdate))).days)
        except:
           return(10.0 * 365.0)


    def photos(self):
        if self.photo_list == None:
            self.photo_list = []
            for p in flickr.people_getPublicPhotos(self.id, per_page=100):
               self.photo_list.append(Photo(p))

        return self.photo_list


    def number_of_follow_likes(self):
        cnt = 0
        favorites = self._favorites()

        for photo in favorites:
           for contact in self._contacts():
               if not hasattr(contact, 'id'): 
                   continue

               if photo.owner.id == contact.id:
                   cnt += 1
                   continue

        return(cnt)


    def likes_per_day(self):
        if not self.likes_of_day == None:
            return self.likes_day

        if self.days_online() == 0:
            return 0

        self.likes_day = float(self.number_of_follow_likes()) / float(self.days_online())
        return self.likes_day


    def number_of_contacts(self):
        return(len(self._contacts()))


    def follow_me(self):
        for contact in self._contacts():
            if not hasattr(contact, 'id'): 
                # has no contacts
                print("--> Exception: %s contact without 'id'" % self.id)
                break

            if str(contact.id) == MY_USERID:
                return True
           
        return False


    def follow_i(self):
        for contact in MY_User._contacts():
            if str(contact.id) == self.id:
                return True

        return False


    def is_follower(self, user):
        for contact in user._contacts():
           if not hasattr(contact, 'id'): 
               # has no contacts
               # print("--> Exception: %s contact without 'id'" % self.id)
               continue

           if str(contact.id) == self.id:
               return True
           
        return False


    def follow(self, friend = False):
        if friend:
            return UI.set_follow_friend(self.id)

        return UI.set_follow(self.id)


    def unfollow(self):
        return UI.set_unfollow(self.id)


    def contact_list(self):
        return [ User(contact.id) for contact in self._contacts() ]


    def favoriteUsers(self):
        ids = []
        users = []
        for photo in self.photos():

           for user in photo.favoriteUsers():
               if user.id in ids:
                   continue

               ids.append(user.id)

               if self.is_follower(user):
                   users.append(user)

        print("Number of Favorite User: %d  / Number of Favorite Follower %d" % (len(ids), len(users)))
        return(users)


    def number_of_favorites(self, user_id, max_photo_cnt = None):
        cnt = 0
        i = 0
        for photo in self.photos():

           for user in photo.favoriteUsers():
               if user_id == user.id:
                   cnt += 1
                   break

           i += 1
           if max_photo_cnt != None and i >= max_photo_cnt:
               break;

        return cnt


    def groups(self):
        print(flickr.groups_getPublicGroups())



class Photo:
    def __init__(self, flickr_photo):
        self._photo = flickr_photo
        self.favoriteUser_list = None


    def owner(self):
        return User(self._photo.owner.id)


    def favoriteUsers(self):
        if self.favoriteUser_list == None:
            self.favoriteUser_list = [ User(u['id']) for u in self._photo.getFavoriteUsers() ]

        return self.favoriteUser_list



class Group:
    def __init__(self, id):
        self._group = flickr.Group(id)
        self.member_list = None
   

    def name(self):
        return self._group.name
    

    def member(self):
        print(self._group.members)

        if self.member_list == None:
            self.member_list = [ User(id) for p in self._group.members ]

        return self.member_list


    def photos(self, max_number):
        return [ Photo(p) for p in self._group.getPhotos(per_page = max_number) ]
   

    def publishOwners(self, max_number):
        owners = []

        for owner in [ photo.owner() for photo in self.photos(max_number) ]:
            sys.stdout.write('+')
            if not user_in_list(owner, owners):
                owners.append(owner)

        return owners



class UI:
    driver = None

    def __init__(self):
        if UI.driver != None:
            return

        UI.driver = webdriver.Firefox()
        UI.driver.wait = WebDriverWait(UI.driver, 5)
        UI.driver.get("https://www.flickr.com/signin")

        try:
            id_field = UI.driver.wait.until(EC.presence_of_element_located((By.NAME, "username")))
            passwd_field = UI.driver.wait.until(EC.presence_of_element_located((By.NAME, "passwd")))
            signin_button = UI.driver.wait.until(EC.element_to_be_clickable((By.NAME, "signin")))

        except TimeoutException:
            print("Signin failed")

        id_field.send_keys(FLICKR_USERNAME)
        passwd_field.send_keys(FLICKR_PASSWORD)
        signin_button.click()

        try:
            search_button = UI.driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@value='Suchen']")))
        except TimeoutException:
            print("flickr failed")


    def _set_url(self, url = ''):
        print(url)
        UI.driver.get('https://www.flickr.com' + url)


    @staticmethod
    def set_follow(id):
       UI()._set_url('/photos/' + id)

       try:
           follow_button = UI.driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='follow white']")))
           follow_button.click()
           time.sleep(3)
       except TimeoutException:
           error('ui failed')
           return False

       return True


    @staticmethod
    def set_follow_friend(id):
        UI()._set_url('/photos/' + id)

        try:
            follow_button = UI.driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='follow is-following white']")))
            follow_button.click()
            time.sleep(2)
            friend_checkbox = UI.driver.wait.until(EC.element_to_be_clickable((By.ID, "friend-checkbox")))
        except TimeoutException:
            error('ui failed')
            return True

        checked = True
        try:
            UI.driver.find_element(By.XPATH, "//*[@class='following-friend']/*[@class='checked']")
        except NoSuchElementException:
            checked = False;

        if not checked: 
            friend_checkbox.click()
            time.sleep(3)
        else:
            follow_button.click()

        return True
        

    @staticmethod
    def set_unfollow(id):
        UI()._set_url('/photos/' + id)

        try:
            follow_button = UI.driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='follow is-following white']")))
            follow_button.click()
            unfollow_button = UI.driver.wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@class='follow unfollow']")))
            unfollow_button.click()
            time.sleep(3)
            return True
        except TimeoutException:
             error('ui failed')
             return True
          

class FollowList:
    def __init__(self): 
        try:
            self.list = pickle.load(open("flickr.p", "rb"))
        except IOError:
            self.list = []
            print("--> Exception: file 'flickr.p' not exist, create empty file")


    def __contains__(self, user):
        for entry in self.list:
            if user.id == entry['id']:
                return True
        return False


    def _save(self):
        pickle.dump(self.list, open("flickr.p", "wb"))


    def _add(self, user, state, lpd):
        self.list.append({ 'id': user.id, 'name': user.name(), 'date': datetime.today(), 'state': state, 'lpd': lpd })
        self._save()


    def _update(self, user, state, reason = ''):
        i = 0
        for entry in self.list:
            if entry['id'] == user.id:

                entry['state'] = state
                if state == 'filtered' or state == 'follow':
                    entry['date'] = datetime.today()

                if state == 'obsolete':
                    entry['reason'] = reason

                self._save()
                return
            i += 1


    def print_entry(self, msg, entry):
        d = entry['date']
        print("%s<%s> '%s' / %s / %d-%02d-%02d / %1.1f" % (msg, entry['state'], entry['name'], entry['id'], \
            d.year, d.month, d.day, entry['lpd']))

        
    def print_list(self, state):
        Paused = False
        self.list.sort(key=lambda entry: entry['date'])

        for entry in self.list:
            if state == entry['state']:
                if entry['state'] == 'follow' and User(entry['id']).follow_me():
                    self.print_entry("Follow: ", entry)
                else:
                    self.print_entry("        ", entry)


    def mark_friends(self):
        for contact in MY_User.contact_list():
            if not contact in self:
                contact.follow(friend = True)


    def delete_user(self, id):
        for entry in self.list:
            if id == entry['id']:
                self.list.remove(entry)
                self._save()


    def add_filtered_user(self, known_list, user):
        sys.stdout.write('.')

        if user.id in known_list:
            return False

        if user in self:
            return False 
    
        try:
            if user.number_of_contacts() > 500 or \
               user.number_of_contacts() < 10 or \
               user.follow_i() or \
               user.follow_me() or \
               user.likes_per_day() < 2.0:
                known_list.append(user.id)
                return
        except:
            print("add_filtered_user: Exeception %s", user.id)
            return

        self.print_entry("    (%s): " % user.number_of_contacts(),
                    { 'id': user.id, 'name': user.name(), 'date': user.firstdate(), 'state': 'filtered',
                       'lpd': user.likes_per_day()})

        self._add(user, 'filtered', user.likes_per_day())


    def filter_groups(self):
        Paused = True
        known = []

        for groupid in MY_GROUPS:
            group = Group(groupid)
            print("Scanning group: '%s'" % group.name())
            users = group.publishOwners(50)
 
            for user in users:
                self.add_filtered_user(known, user)
    

    def filter_group_member(self, groupid):
        Paused = True
        known = []

        group = Group(groupid)
        print("Scanning group: '%s'" % group.name())
        users = group.member()
 
        for user in users:
            print(user.id)
            self.add_filtered_user(known, user)


    def filter_user(self, id):
        known = []
        modified = False
        for u in User(id).favoriteUsers():
            print("%s   %1.1f" % (u.name(), u.likes_per_day()))

            if self.add_filtered_user(known, u):
                modified = True

        if modified:
            self._save()

    
    def follow(self, cnt):
        users = []
        for entry in self.list:
            if entry['state'] == 'filtered':
                users.append(entry)

        users.sort(key=lambda entry: entry['lpd'])

        i = 0
        for entry in reversed(users):
            if i >= cnt:
                break

            s = 'follow'
            self.print_entry("    ", entry) 
            user = User(entry['id'])

            if user.follow():
                self._update(user, 'follow')

            i += 1


    def unfollow(self):
        for entry in self.list:
            if entry['state'] != 'follow':
                continue


            id   = entry['id']
            user = User(id)            
            print(id)
            favs = MY_User.number_of_favorites(id)
            d    = entry['date']

            if not user.follow_me():
                if (datetime.today() - d).days >= 4:
                    self.print_entry("No follow after 4 days: ", entry) 

                    if user.unfollow():
                        self._update(user, 'obsolete', reason = 'NoFollow')
                        continue

                if (datetime.today() - d).days >= 1 and favs > 0:
                    self.print_entry("Favs but don't follow: ", entry) 

                    if user.unfollow():  self._update(user, 'obsolete', reason = 'NoFollowFavs')
                
                continue

            if (datetime.today() - d).days >= 3 and favs == 0:
                self.print_entry("Follows but no favs: ", entry) 

                if user.unfollow():  self._update(user, 'obsolete', reason = 'FollowNoFavs')
                continue

            if (datetime.today() - d).days >= 14 and MY_User.number_of_favorites(id, 4) == 0:
                self.print_entry("Follows but don't favs last four: ", entry) 
                if user.unfollow():  self._update(user, 'obsolete', reason = 'FollowNoLastFavs')
     

    def repair(self):
        new_list = []

        for entry in self.list:
            e = { 'id': id, 'name': n, 'state': s, 'date': d, 'lpd': lpd }
            print(e)
            new_list.append(e)

        self.list = new_list
        self._save()


    def groups(self):
        MY_User.groups()



MY_User = User(MY_USERID)


def user_in_list(user, user_list):
    for u in user_list:
        if user.id == u.id:
            return True
    return False 


def usage(ret, msg):
    error(msg)
    print("flickrctrl [-h|--help] [-v|--verbose]  --filter-user id | --filter-group-member groupid | --delete-user id | print | filter-groups | follow | unfollow | mark-friends | repair | groups")
    sys.exit(ret)


def error(msg):
    print(msg)


def main(*argv):
    from getopt import getopt, GetoptError

    try:
        (opts, args) = getopt(argv[1:], 'hv', ['help', 'verbose', 'delete-user', 'filter-user', 'filter-group-member', 'print'])
    except GetoptError, e:
        usage(1, e)

    for o, a in opts:
        if o in ('-h', '--help'):
            usage(0, "usage:")

        if o in ('-v', '--verbose'):
            verbose = True
            continue

        if o in ('--filter-user'):
            FollowList().filter_user(args[0])
            return 0

        if o in ('--filter-group-member'):
            FollowList().filter_group_member(args[0])
            return 0

        if o in ('--delete-user'):
            FollowList().delete_user(args[0])
            return 0

        if o in ('--print'):
            FollowList().print_list(args[0])
            return 0

    if len(args) == 0:
        usage(1, "no argument")

    for a in args:
        if a == 'filter-groups':
            FollowList().filter_groups()
        elif a == 'follow':
            FollowList().follow(10)
        elif a == 'mark-friends':
            FollowList().mark_friends()
        elif a == 'unfollow':
            FollowList().unfollow()
        elif a == 'repair':
            FollowList().repair()
        else:
            usage(1, "wrong argument")

    return 0


if __name__ == "__main__":
    sys.exit(main(*sys.argv))
