from repositories import UserRepository

class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def login(self, email, password):
        user = self.repository.get_user_by_credentials(email, password)
        if user:
            return {
                'role': user.role,
                'email': user.email,
                'name': user.name
            }
        return None