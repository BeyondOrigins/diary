class User:
    def __init__(self, user_data : tuple | list):
        (
            self.user_id, 
            self.login, 
            self.password,
            self.password,
            self.first_name,
            self.middle_name,
            self.last_name,
            self.user_type
        ) = user_data