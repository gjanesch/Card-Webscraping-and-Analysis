from bs4 import BeautifulSoup
import urllib.request


def get_soup(url):
    html = urllib.request.urlopen(section_url).read()
    soup = BeautifulSoup(html, "lxml")
    return soup

def append_to_file(object, target_file):
    with open(target_file, "a") as file:
        file.write(object + "\n")

def read_text_file(filename):
    with open(filename, "r") as file:
        lines = file.readlines()
    return lines