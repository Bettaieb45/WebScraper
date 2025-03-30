from collections import defaultdict

class InternalLinkGraphBuilder:
    def __init__(self, scraped_metadata):
        self.scraped_metadata = scraped_metadata

    def build_internal_link_counts(self):
        incoming_links = defaultdict(int)

        for page in self.scraped_metadata:
            for linked_url in page.get("links_to", []):
                incoming_links[linked_url] += 1

        return incoming_links
