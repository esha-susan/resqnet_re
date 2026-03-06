def get_user_profile(user):
    """
    Returns a clean user profile dictionary.
    """
    return {
        "id": user.id,
        "email": user.email,
        "created_at": str(user.created_at)
    }