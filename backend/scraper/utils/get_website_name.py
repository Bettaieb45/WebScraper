from urllib.parse import urlparse

def get_website_name(domain):
    """Extracts the name of the website from the domain and formats it."""
    parsed_url = urlparse(domain)
    hostname = parsed_url.hostname or domain.replace("https://", "").replace("http://", "")
    parts = hostname.split(".")
    
    # Check if the first part is "www" and return the next part instead
    return parts[1] if parts[0] == "www" and len(parts) > 1 else parts[0]