
from registration.signals import user_activated
from medialibrary.models import MediaLibrary



def registration_user_activated_signal(sender, **kwargs):
    """
    receive signal from django-registration for when a new user
    has activated their account. Upon activation you will want to 
    create a default UserProfile (model in django-profiles app).  
    """
    if 'user' in kwargs:       
        user = kwargs['user']
        
        if not MediaLibrary.objects.filter(user=user).count():
            pml = MediaLibrary(user=user)
            pml.save()


user_activated.connect(registration_user_activated_signal)

