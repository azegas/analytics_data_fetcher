def extract_after_last_slash(url):
    parts = url.split("/")
    return parts[-1]
