from flask_login import UserMixin

class User(UserMixin):
    def __init__(self,id_user,name,surname,email,password):
        self.id_user=id_user
        self.name=name
        self.surname=surname
        self.email=email
        self.password=password
    
    def get_id(self):
           return (self.id_user)