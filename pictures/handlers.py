import os
import logging
import mimetypes

from tornado.web import asynchronous
from tornado.httpclient import HTTPError, AsyncHTTPClient, HTTPRequest
from tornado.escape import json_decode, json_encode
from couchdbkit.exceptions import ResourceNotFound
from PIL import Image

from newebe.profile.models import UserManager
from newebe.core.handlers import NewebeAuthHandler, NewebeHandler

from newebe.contacts.models import ContactManager
from newebe.pictures.models import PictureManager, Picture
from newebe.lib.date_util import get_date_from_db_date, \
                                 get_db_date_from_url_date


logger = logging.getLogger("newebe.pictures")


class PicturesHandler(NewebeAuthHandler):
    '''
    This handler handles requests that retrieve last posted pictures.
    
    * GET: Retrieves all pictures ordered by title.
    * POST: Create a picture.
    '''


    def get(self, startKey=None):
        '''
        Returns last posted pictures.  If *startKey* is provided, it returns 
        last picture posted until *startKey*.
        '''
        
        pictures = list()

        if startKey:
            dateString = get_db_date_from_url_date(startKey)
            pictures = PictureManager.get_last_pictures(startKey=dateString)

        else:
            pictures = PictureManager.get_last_pictures()

        self.return_documents(pictures)


    @asynchronous
    def post(self):
        '''
        Creates a picture and corresponding activity. Then picture is 
        propagated to all trusted contacts.

        Errors are stored inside activity.
        '''

        file = self.request.files['picture'][0]

        if file:
            filebody = file["body"]
            filename = file['filename']

            picture = Picture(
                title = "New Picture", 
                path=file['filename'],
                contentType=file["content_type"], 
                authorKey = UserManager.getUser().key,
                author = UserManager.getUser().name,
                isFile = True
            )
            picture.save()

            picture.put_attachment(filebody, filename)
            thumbnail = self.get_thumbnail(filebody, filename, (200, 200))     
            thbuffer = thumbnail.read()
            picture.put_attachment(thbuffer, "th_" + filename)
            os.remove("th_" + filename)           
            preview = self.get_thumbnail(filebody, filename, (1000, 1000))
            picture.put_attachment(preview.read(), "prev_" + filename)
            os.remove("th_" + filename)           
            picture.save()
        
            self.create_creation_activity(UserManager.getUser().asContact(),
                    picture, "publishes", "picture")

            self.send_files_to_contacts("pictures/contact/", 
                        fields = { "json": str(picture.toJson()) },
                        files = [("picture", str(picture.path), thbuffer)])
                        
            logger.info("Picture %s successfuly posted." % filename)
            self.return_json(picture.toJson(), 201)

        else:
            self.return_failure("No picture posted.", 400)


    def get_thumbnail(self, filebody, filename, size):            
        file = open(filename, "w")
        file.write(filebody)  
        file.close()
        image = Image.open(filename)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save("th_" + filename)
        file = open(filename)
        os.remove(filename)
        return open("th_" + filename)


class PicturesMyHandler(NewebeAuthHandler):
    '''
    This handler handles requests that retrieve last pictures posted by
    Newebe owner.
    
    * GET: Retrieves last pictures posted by newebe owner.
    * POST: Creates a picture.
    '''


    def get(self, startKey=None):
        '''
        Returns last posted pictures.
        '''
        pictures = PictureManager.get_owner_last_pictures()
        

        if startKey:
            dateString = get_db_date_from_url_date(startKey)
            pictures = PictureManager.get_owner_last_pictures(
                    startKey=dateString)
        else:
            pictures = PictureManager.get_owner_last_pictures()

        self.return_documents(pictures)


class PicturesQQHandler(PicturesHandler):
    '''
    This handler handles requests from QQ uploader to post new pictures.
    
    * POST: Create a picture.
    '''

    @asynchronous
    def post(self):
        '''
        Creates a picture and corresponding activity. Then picture is 
        propagated to all trusted contacts.

        Errors are stored inside activity.
        '''

        filebody = self.request.body
        filename = self.get_argument("qqfile")
        filetype = mimetypes.guess_type(filename)[0] or \
                'application/octet-stream'

        if filebody:

            picture = Picture(
                title = "New Picture", 
                path=filename,
                contentType=filetype, 
                authorKey = UserManager.getUser().key,
                author = UserManager.getUser().name,
                isMine = True,
                isFile = True
            )
            picture.save()

            picture.put_attachment(content=filebody, name=filename)            
            thumbnail = self.get_thumbnail(filebody, filename, (200, 200))
            thbuffer = thumbnail.read()        
            picture.put_attachment(thbuffer, "th_" + filename)
            os.remove("th_" + filename)           
            preview = self.get_thumbnail(filebody, filename, (1000, 1000))
            picture.put_attachment(preview.read(), "prev_" + filename)
            os.remove("th_" + filename)
            picture.save()

            self.create_creation_activity(UserManager.getUser().asContact(),
                    picture, "publishes", "picture")

            self.send_files_to_contacts("pictures/contact/", 
                        fields = { "json": str(picture.toJson()) },
                        files = [("picture", str(picture.path), thbuffer)])
            
            logger.info("Picture %s successfuly posted." % filename)
            self.return_json(picture.toJson(), 201)

        else:
            self.return_failure("No picture posted.", 400)


class PictureContactHandler(NewebeHandler):
    '''
    This handler handles requests coming from contacts.

    * POST : Creates a new picture.
    * PUT :  Delete a picture.
    '''

    def post(self):
        '''
        Extract picture and file linked to the picture from request, then 
        creates a picture in database for the contact who sends it. An 
        activity is created too.

        If author is not inside trusted contacts, the request is rejected.
        '''

        file = self.request.files['picture'][0]
        data = json_decode(self.get_argument("json"))

        if file and data:
            contact = ContactManager.getTrustedContact(
                    data.get("authorKey", ""))
            
            if contact:
                date = get_date_from_db_date(data.get("date", ""))

                picture = Picture(
                    title = data.get("title", ""),
                    path = data.get("path", ""),
                    contentType = data.get("contentType", ""),
                    authorKey = data.get("authorKey", ""),
                    author = data.get("author", ""),
                    date = date,
                    isMine = False,
                    isFile = False
                )
                picture.save()
                picture.put_attachment(content=file["body"], 
                                       name="th_" + file['filename'])
                picture.save()

                self.create_creation_activity(contact,
                        picture, "publishes", "picture")

                self.return_success("Creation succeeds", 201)

            else:
                self.return_failure("Author is not trusted.", 400)                
        else:
            self.return_failure("No data sent.", 405)


    def put(self):
        '''
        Delete picture of which data are given inside request.
        Picture is found with contact key and creation date.

        If author is not inside trusted contacts, the request is rejected.
        '''

        data = self.get_body_as_dict()

        if data:
            contact = ContactManager.getTrustedContact(
                    data.get("authorKey", ""))
            
            if contact:
                picture = PictureManager.get_contact_picture(
                        contact.key, data.get("date", ""))

                if picture:
                    self.create_deletion_activity(contact, 
                            picture, "deletes", "picture")
                    picture.delete()

                self.return_success("Deletion succeeds")

            else:
                self.return_failure("Author is not trusted.", 400)      


        else:
            self.return_failure("No data sent.", 405)


class PictureObjectHandler(NewebeAuthHandler):

    def get(self, id):
        '''
        Retrieves picture corresponding to id. Returns a 404 response if
        picture is not found.
        '''

        picture = PictureManager.get_picture(id)
        if picture:
            self.on_picture_found(picture, id)
        else:
            self.return_failure("Picture not found.", 404)


    def on_picture_found(self, picture, id):
        pass


class PictureFileHandler(NewebeAuthHandler):
    '''
    Returns file linked to a given picture document.
    '''
    
    def get(self, id, filename):
        '''
        Retrieves picture corresponding to id. Returns a 404 response if
        picture is not found.
        '''

        picture = PictureManager.get_picture(id)
        if picture:
            self.filename = filename
            self.on_picture_found(picture, id)
        else:
            self.return_failure("Picture not found.", 404)


    def on_picture_found(self, picture, id):
        '''
        Returns file linked to given picture.
        '''
        try:
            file = picture.fetch_attachment(self.filename)
            self.set_header("Content-Type", picture.contentType)
            self.write(file)
            self.finish()
        except ResourceNotFound:
            self.return_failure("Picture not found.", 404)



class PictureHandler(PictureObjectHandler):
    '''
    Handles operations on a single picture.

    * GET : Retrieves picture corresponding to id given in URL.
    * DELETE : Deletes picture corresponding to id given in URL.
    '''


    def on_picture_found(self, picture, id):        
        '''
        Retrieves picture corresponding to id.
        '''

        self.return_document(picture)


    @asynchronous
    def delete(self, id):
        '''
        Deletes picture corresponding to id.
        '''

        picture = PictureManager.get_picture(id)
        if picture:
            user = UserManager.getUser()
            
            if picture.authorKey == user.key:
                self.create_owner_deletion_activity(
                        picture, "deletes", "picture")
                self.send_deletion_to_contacts("pictures/contact/", picture)
          
            picture.delete()
            self.return_success("Picture deleted.")
        else:
            self.return_failure("Picture not found.", 404)


class PictureDownloadHandler(PictureObjectHandler):
    '''
    Handler that allows newebe owner to download original file of the picture 
    inside its newebe to make it available through UI. 
    '''

    
    @asynchronous
    def on_picture_found(self, picture, id):        
        '''
        '''

        self.picture = picture

        data = dict()
        data["picture"] = picture.toDict()
        data["contact"] = UserManager.getUser().asContact().toDict()

        contact = ContactManager.getTrustedContact(picture.authorKey)
        
        url = contact.url + u"pictures/contact/download/"
        client = AsyncHTTPClient()
        request = HTTPRequest(url, method="POST", body=json_encode(data))       
        
        try:
            logger.info(url)
            client.fetch(request, self.on_download_finished)
        except HTTPError:
            self.return_failure("Cannot download picture from contact.")


    def on_download_finished(self, response):
        logger.info(self.picture)
        self.picture.put_attachment(response.body, self.picture.path)
        thumbnail = self.get_thumbnail(
                response.body, self.picture.path, (1000, 1000))
        thbuffer = thumbnail.read()
        self.picture.put_attachment(thbuffer, "prev_" + self.picture.path)
        os.remove("th_" + self.picture.path)
        self.picture.isFile = True
        self.picture.save()
        self.return_success("Picture successfuly downloaded.")



    def get_thumbnail(self, filebody, filename, size):            
        file = open(filename, "w")
        file.write(filebody)  
        file.close()
        image = Image.open(filename)
        image.thumbnail(size, Image.ANTIALIAS)
        image.save("th_" + filename)
        file = open(filename)
        os.remove(filename)
        return open("th_" + filename)


class PictureContactDownloadHandler(NewebeHandler):


    @asynchronous
    def post(self):
        '''
        '''

        data = self.get_body_as_dict()

        contact = ContactManager.getTrustedContact(data["contact"]["key"])

        if contact:
            date = data["picture"]["date"]
     
            picture = PictureManager.get_owner_last_pictures(date).first()

            if picture:
                self.on_picture_found(picture, id)
            else:
                logger.info("Picture no more available.")
                self.return_failure("Picture not found.", 404)
        else:
            logger.info("Contact unknown")
            self.return_failure("Picture not found", 404)

    @asynchronous
    def on_picture_found(self, picture, id):
        file = picture.fetch_attachment(picture.path)
        
        self.set_status(200)        
        self.set_header("Content-Type", picture.contentType)
        self.write(file)
        self.finish()
        

class PictureTHandler(PictureObjectHandler):
    '''
    This handler allows to retrieve picture at HTML format.
    * GET: Return for given id the HTML representation of corresponding 
           picture.
    '''
    

    def on_picture_found(self, picture, id):
        '''
        Returns for given id the HTML representation of corresponding 
        picture.
        '''

        if picture.isFile:
            self.render("templates/picture.html", picture=picture)
        else:
            self.render("templates/picture_empty.html", picture=picture)        



# Template handlers

class PicturesTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/pictures.html")

class PicturesTestsTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/pictures_tests.html")

class PicturesContentTHandler(NewebeAuthHandler):
    def get(self):
        self.render("templates/pictures_content.html")

