import logging

from threading import Timer

from tornado.escape import json_decode
from tornado.httpclient import HTTPClient, HTTPRequest

from newebe.core.handlers import NewebeAuthHandler
from newebe.profile.models import UserManager
from newebe.contacts.models import ContactManager

from newebe.activities.models import Activity

logger = logging.getLogger("newebe.core")


class ProfileUpdater:
    '''
    Utility class to handle profile forwarding to contacts. Set error
    log inside acitivity when error occurs.
    '''

    sending_data = False
    contact_requests = {}


    def send_profile_to_contacts(self):
        '''
        External methods to not send too much times the changed profile. 
        A timer is set to wait for other modifications before running this
        function that sends modification requests to every contacts.
        '''

        client = HTTPClient()
        self.sending_data = False

        user = UserManager.getUser()
        jsonbody = user.toJson()

        activity = Activity(
            authorKey = user.key,
            author = user.name,
            verb = "modifies",
            docType = "profile",
            method = "PUT",
            docId = "none",
            isMine = True
        )
        activity.save()     

        for contact in ContactManager.getTrustedContacts():
            request = HTTPRequest("%scontacts/update-profile/" % contact.url, 
                         method="PUT", body=jsonbody)

            response = client.fetch(request)

            if response.error:
                logger.error("""
                    Profile sending to a contact failed, error infos are 
                    stored inside activity.
                """)
                activity.add_error(contact)
                activity.save()    
            logger.info("Profile update successfully sent.")


    def forward_profile(self):
        '''
        Because profile modification occurs a lot in a short time. The 
        profile is forwarded only every ten minutes. It avoids to create
        too much activities for this profile modification.
        '''
        t = Timer(1.0 * 60 * 10, self.send_profile_to_contacts)
        if not self.sending_data:
            self.sending_data = True
            t.start()


profile_updater = ProfileUpdater()



class UserHandler(NewebeAuthHandler):
    '''
    This resource allows :
     * GET : retrieve current user (newebe owner) data.
     * POST : create a new user (if user exists, error response is returned).
     * PUT : modify current user data. Send profile to every contacts
     after a pre-defined time.
    '''


    def get(self):
        '''
        Retrieves current user (newebe owner) data at JSON format.
        '''

        users = list()
        user = UserManager.getUser()
        users.append(user)

        self.return_documents(users)


    def put(self):
        '''
        Modifies current user data with sent data (user object at JSON format).
        Then forwards it to contacts after a pre-defined time.
        '''

        user = UserManager.getUser()
    
        data = self.request.body

        if data:
            postedUser = json_decode(data)
            user.name = postedUser["name"]
            user.url = postedUser["url"]
            user.description = postedUser["description"]
            user.save()

            profile_updater.forward_profile()

            self.return_success("User successfully Modified.")
        else:
            self.return_failure("No data were sent.")



# Template handlers.

class ProfileContentTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/profile_content.html")

class ProfileMenuContentTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/profile_menu_content.html")

class ProfileTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/profile.html",
                    isTheme=self.is_file_theme_exists())

class ProfileTutorial1THandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/tutorial_1.html")

class ProfileTutorial2THandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/tutorial_2.html")

