from arttrip.application.domain.auth.exceptions import AuthError
from arttrip.application.domain.user.user import User
from arttrip.application.port.output.user_port import UserPort


def load_current_user(
    users: UserPort, user_id: int, *, for_update: bool = False
) -> User:
    user = (
        users.find_by_id_for_update(user_id)
        if for_update
        else users.find_by_id(user_id)
    )
    if user is None:
        raise AuthError.invalid_access_token()
    return user
