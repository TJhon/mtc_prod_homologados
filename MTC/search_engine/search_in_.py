from urllib.parse import urlparse, unquote
import math
import itertools
import re
from collections import Counter
from ddgs import DDGS
from rich import print


class SearchEngine:
    def __init__(self, brand, model, num_results=20, operator="ddg"):
        self.brand = brand.lower()
        self.model = model.lower()
        self.num_results = num_results
        self.search_results = []  # Lista de diccionarios con href y title
        self.parsed_urls = []
        self.parsed_titles = []
        self.filtered_strings = []
        self.split_words = []
        self.result_string = ""
        self.operator = operator

    def search(self):
        """
        Perform a search and store the result URLs and titles.
        """
        try:
            query = f"{self.brand} {self.model}"
            if self.operator == "ddg":
                results = DDGS().text(
                    query, max_results=self.num_results, region="ue-es"
                )
                # Guardar tanto href como title
                self.search_results = [
                    {"href": result["href"].lower(), "title": result["title"].lower()}
                    for result in results
                ]
        except Exception as e:
            print(f"An error occurred during search: {e}")
            self.search_results = []

    def parse_urls(self):
        """
        Parse and decode the URLs from the search results.
        """
        self.parsed_urls = [
            unquote(urlparse(result["href"]).path) for result in self.search_results
        ]

    def parse_titles(self):
        """
        Extract titles from search results.
        """
        self.parsed_titles = [result["title"] for result in self.search_results]

    def filter_by_brand(self):
        """
        Filter parsed URLs and titles by the brand name.
        Combine both sources for analysis.
        """
        # Filtrar URLs que contengan la marca
        filtered_urls = [
            string for string in self.parsed_urls if self.brand in string.lower()
        ]
        
        # Filtrar títulos que contengan la marca
        filtered_titles = [
            string for string in self.parsed_titles if self.brand in string.lower()
        ]
        
        # Combinar ambas fuentes
        self.filtered_strings = filtered_urls + filtered_titles

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
        if total_matches == 0:
            return 1
        threshold_floor = math.floor(total_matches / 10)
        return max(1, int(threshold_floor / 2 * 5))

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
            self.parse_titles()  # Nueva función
            self.filter_by_brand()
            self.split_strings()
            self.remove_empty_strings()
            self.generate_result_string()
            return self.result_string
        except Exception as e:
            print(f"Error: {e}")
            return None


if __name__ == "__main__":
    # result = SearchEngine(brand='GOOGLE', model='GB7N6').run()
    # print(f"Google GB7N6: {result}")
    
    result = SearchEngine(brand='xiaomi', model='mdz-28-aa').run()
    print(f"Xiaomi mdz-28-aa: {result}")
    
    # result22 = SearchEngine(brand="poco", model="m2004j11g").run()
    # print(f"POCO m2004j11g: {result22}")