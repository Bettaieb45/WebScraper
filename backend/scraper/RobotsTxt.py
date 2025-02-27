import requests
class RobotsTxt:
    """Fetches all URLs from a robot.txt"""
    def __init__(self,domain):
        self.domain = domain

    def get_robot_paths(self):
        """Fetches all URLs from a robot.txt"""
        headers = {"User-Agent": "Mozilla/5.0"}

        try:
            response = requests.get(f"{self.domain}/robots.txt", headers=headers, timeout=10)
            if response.status_code != 200:
                print(f"⚠️ Failed to fetch robots.txt: {self.domain}")
                return []

            urls = []
            for line in response.text.split("\n"):
                if line.startswith("Disallow:"):
                    parts = line.split(" ",1)
                    if len(parts)>1 and parts[1].strip():
                        urls.append(f"{self.domain}{parts[1].strip()}")
            print(f"✅ Found {len(urls)} URLs in robots.txt")
            print(f"robots.txt: {urls}")
            return urls

        except Exception as e:
            print(f"⚠️ Error fetching robots.txt: {e}")
            return []
        