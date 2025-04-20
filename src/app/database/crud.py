



def register_user(username, email, password):
    print(f"Registere new user {username} with email {email} and password {password}")

    return {
        'user_id': '1',
        'username': username,
        'email': email
    }


def login_user(username, password):
    print(f"Login user {username} with password {password}")

    return {
        'user_id': '1',
        'username': username,
        'email': 'patsteitor3000'
    }

def get_user(user_id):
    print(f"Get user {user_id}")

    return {
        'user_id': user_id,
        'username': 'patsteitor3000',
        'email': 'patsteitor3000@gmail.com'
    }