from googlesearch import search as search_google
from urllib.parse import urlparse, unquote
import math
import itertools
import re
from collections import Counter
from duckduckgo_search import DDGS


class SearchEngine:
    def __init__(self, brand, model, num_results=20, operator="ddg"):
        self.brand = brand.lower()
        self.model = model
        self.num_results = num_results
        self.search_results = []  # urls
        self.parsed_urls = []
        self.filtered_strings = []
        self.split_words = []
        self.result_string = ""
        self.operator = operator

    def search(self):
        """
        Perform a Google search and store the result URLs.
        """
        try:
            query = f"{self.brand} {self.model}"
            if self.operator == "ddg":
                results = DDGS().text(
                    query, max_results=self.num_results, region="ue-es"
                )
                # results [{title, href, body}]
                results = [result["href"].lower() for result in results]

                self.search_results = results
            else:
                self.search_results = [
                    url for url in search_google(query, num_results=self.num_results)
                ]
        except Exception as e:
            print(f"An error occurred during search: {e}")
            self.search_results = []

    def parse_urls(self):
        """
        Parse and decode the URLs from the search results.
        """
        self.parsed_urls = [unquote(urlparse(url).path) for url in self.search_results]

    def filter_by_brand(self):
        """
        Filter parsed URLs by the brand name.
        """
        self.filtered_strings = [
            string for string in self.parsed_urls if self.brand in string.lower()
        ]

    def split_strings(self):
        """
        Split filtered strings into individual words.
        """
        split_words = [
            re.split(r"[^a-zA-Z0-9_]+", string) for string in self.filtered_strings
        ]
        self.split_words = list(itertools.chain(*split_words))

    def remove_empty_strings(self):
        """
        Remove empty strings from the list of split words.
        """
        self.split_words = [word for word in self.split_words if word]

    def calculate_frequency_threshold(self):
        """
        Calculate the threshold for word frequency filtering.
        """
        total_matches = len(self.filtered_strings)
        threshold_floor = math.floor(total_matches / 10)
        return max(1, int(threshold_floor / 2 * 10))

    def count_and_filter_frequent_words(self, threshold):
        """
        Count word occurrences and filter by frequency threshold.
        """
        word_count = Counter(self.split_words)
        return [word for word, count in word_count.most_common() if count >= threshold]

    def generate_result_string(self):
        """
        Generate the final result string by joining frequent words.
        """
        frequency_threshold = self.calculate_frequency_threshold()
        frequent_words = self.count_and_filter_frequent_words(frequency_threshold)
        self.result_string = " ".join(frequent_words)

    def run(self) -> str:
        """
        Execute the full process from search to result generation.
        """
        try:
            self.search()
            self.parse_urls()
            self.filter_by_brand()
            self.split_strings()
            self.remove_empty_strings()
            self.generate_result_string()
            return self.result_string
        except:
            return None


# Example usage
# if __name__ == "__main__":
#     brand_search = GoogleBrandSearch(brand="xiaomi", model="RB02")
#     result = brand_search.run()
#     print(result)
#     result22 = GoogleBrandSearch(brand="xiaomi", model="MDZ-28-AA").run()
#     print(result22)
#     result22 = GoogleBrandSearch(brand="poco", model="m2004j11g").run()
#     print(result22)

# a = "xiaomi poco pro f2 m2004j11g en xiaomi_poco_f2_pro 10220 php phone where to buy compare x5 5g device data devices 58413939"
# # re.split(r"\W+", string)
# print(re.split(r"\W+", a))
