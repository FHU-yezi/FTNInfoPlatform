def user_URL_to_URL_scheme(user_url: str):
    return "jianshu://u/" + user_url.split("/")[-1]
