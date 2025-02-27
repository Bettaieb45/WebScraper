def get_website_name(domain):
        """Extracts the name of the website from the domain and formats it."""
        return domain.replace("https://", "").replace("http://", "").split(".")[0]