import sys
sys.path.append("../")

from newebe.apps.contacts import handlers as contacts
from newebe.apps.profile import handlers as profile
from newebe.apps.auth import handlers as auth
from newebe.apps.news import handlers as news
from newebe.apps.activities import handlers as activities
from newebe.apps.notes import handlers as notes
from newebe.apps.pictures import handlers as pictures
from newebe.apps.commons import handlers as commons
from newebe.apps.core import handlers as core
from newebe.apps.sync import handlers as sync


routes = [
    ('/', core.IndexTHandler),
    ('/login/', auth.LoginHandler),
    ('/login/json/', auth.LoginJsonHandler),
    ('/logout/', auth.LogoutHandler),
    ('/register/', auth.RegisterTHandler),
    ('/register/password/', auth.RegisterPasswordTHandler),
    ('/register/password/content/', auth.RegisterPasswordContentTHandler),
    ('/user/password/', auth.UserPasswordHandler),
    ('/user/state/', auth.UserStateHandler),

    ('/user/$', profile.UserHandler),
    ('/user/picture$', profile.ProfilePictureHandler),
    ('/user/picture.jpg$', profile.ProfilePictureHandler),

    ('/contacts/update-profile/$', contacts.ContactUpdateHandler),
    ('/contacts/update-profile/picture/$',
        contacts.ContactPictureUpdateHandler),
    ('/contacts/pending/$', contacts.ContactsPendingHandler),
    ('/contacts/requested/$', contacts.ContactsRequestedHandler),
    ('/contacts/trusted/$', contacts.ContactsTrustedHandler),
    ('/contacts/confirm/$', contacts.ContactConfirmHandler),
    ('/contacts/request/$', contacts.ContactPushHandler),
    ('/contacts/publisher/', contacts.ContactPublishingHandler),
    ('/contacts/tags/$', contacts.ContactTagsHandler),
    ('/contacts/tags/([0-9A-Za-z-]+)$', contacts.ContactTagsHandler),
    ('/contacts/$', contacts.ContactsHandler),
    ('/contacts/([0-9A-Za-z-]+)/retry/$', contacts.ContactRetryHandler),
    ('/contacts/([0-9A-Za-z-]+)/tags/$', contacts.ContactTagHandler),
    ('/contacts/([0-9A-Za-z-]+)$', contacts.ContactHandler),

    ('/activities/', activities.ActivityPageHandler),
    ('/activities/content/', activities.ActivityContentHandler),
    ('/activities/all/', activities.ActivityHandler),
    ('/activities/all/([0-9\-]+)/', activities.ActivityHandler),
    ('/activities/mine/', activities.MyActivityHandler),
    ('/activities/mine/([0-9\-]+)/', activities.MyActivityHandler),

    ('/synchronize/', sync.SynchronizeHandler),
    ('/synchronize/contact/', sync.SynchronizeContactHandler),

    ('/microposts/all/$', news.NewsHandler),
    ('/microposts/all/([0-9\-]+)/$', news.NewsHandler),
    ('/microposts/all/([0-9\-]+)/tags/([0-9a-z]+)/$', news.NewsHandler),
    ('/microposts/mine/([0-9\-]+)/$', news.MyNewsHandler),
    ('/microposts/mine/([0-9\-]+)/tags/([0-9a-z]+)/$', news.MyNewsHandler),
    ('/microposts/mine/$', news.MyNewsHandler),
    ('/microposts/contacts/$', news.NewsContactHandler),
    ('/microposts/contacts/attach/$', news.MicropostContactAttachedFileHandler),
    ('/microposts/$', news.NewsTHandler),
    ('/microposts/publisher/', news.MicropostPublishingHandler),
    ('/microposts/content/$', news.NewsContentTHandler),
    ('/microposts/tutorial/1/$', news.NewsTutorial1THandler),
    ('/microposts/tutorial/2/$', news.NewsTutorial2THandler),
    ('/microposts/search/$', news.NewsSearchHandler),
    ('/microposts/([0-9a-z]+)/retry/$', news.NewsRetryHandler),
    ('/microposts/([0-9a-z]+)/$', news.MicropostHandler),
    ('/microposts/([0-9a-z]+)/html/$', news.MicropostTHandler),
    ('/microposts/([0-9a-z]+)/attach/download/$',
        news.MicropostDlAttachedFileHandler),
    ('/microposts/([0-9a-z]+)/attach/(.+)$',
        news.MicropostAttachedFileHandler),

    ('/notes/all/', notes.NotesHandler),
    ('/notes/all/order-by-title/', notes.NotesHandler),
    ('/notes/all/order-by-date/', notes.NotesByDateHandler),
    ('/notes/all/([0-9a-z]+)', notes.NoteHandler),

    ('/pictures/all/$', pictures.PicturesHandler),
    ('/pictures/all/([0-9\-]+)/$', pictures.PicturesHandler),
    ('/pictures/all/([0-9\-]+)/tags/([0-9a-z]+)/$', pictures.PicturesHandler),
    ('/pictures/mine/$', pictures.PicturesMyHandler),
    ('/pictures/mine/([0-9\-]+)/$', pictures.PicturesMyHandler),
    ('/pictures/mine/([0-9\-]+)/tags/([0-9a-z]+)/$',
        pictures.PicturesMyHandler),
    ('/pictures/fileuploader/$', pictures.PicturesQQHandler),
    ('/pictures/contact/$', pictures.PictureContactHandler),
    ('/pictures/contact/download/$', pictures.PictureContactDownloadHandler),
    ('/pictures/([0-9a-z]+)$', pictures.PictureHandler),
    ('/pictures/([0-9a-z]+)/retry/$', pictures.PictureRetryHandler),
    ('/pictures/([0-9a-z]+)/download/$', pictures.PictureDownloadHandler),
    ('/pictures/([0-9a-z]+)/rotate/$', pictures.PictureRotateHandler),
    ('/pictures/([0-9a-z]+)/(.+)', pictures.PictureFileHandler),

    ('/commons/all/([0-9\-]+)/tags/([0-9a-z]+)/$', commons.CommonsHandler),
    ('/commons/all/$', commons.CommonsHandler),
    ('/commons/all/html/$', commons.CommonRowsTHandler),
    ('/commons/all/([0-9\-]+)/$', commons.CommonsHandler),
    ('/commons/mine/$', commons.CommonsMyHandler),
    ('/commons/mine/([0-9\-]+)/$', commons.CommonsMyHandler),
    ('/commons/mine/([0-9\-]+)/tags/([0-9a-z]+)/$',
        commons.CommonsMyHandler),
    ('/commons/fileuploader/$', commons.CommonsQQHandler),
    ('/commons/contact/$', commons.CommonContactHandler),
    ('/commons/contact/download/$', commons.CommonContactDownloadHandler),
    ('/commons/content/$', commons.CommonsContentTHandler),
    ('/commons/([0-9a-z]+)/$', commons.CommonHandler),
    ('/commons/([0-9a-z]+)/retry/$', commons.CommonRetryHandler),
    ('/commons/([0-9a-z]+)/download/$', commons.CommonDownloadHandler),
    ('/commons/([0-9a-z]+)/(.+)', commons.CommonFileHandler),
    ('/commons/$', commons.CommonsTHandler),
]
