import validators
import time
import requests
from multiprocessing import Process, Queue, Value
from bs4 import BeautifulSoup

NUMBER_OF_THREADS=64

def load_bootstrap_links(filename):
    with open(filename, "r") as bootstrap_file:
        bootstrap = bootstrap_file.read().splitlines()
    return bootstrap



maybe_visit = Queue()
visited = Queue()
to_visit = Queue()

print("loading bootstrap list")

# to_visit starts as the bootstrap list
for link in load_bootstrap_links('bootstrap.txt'):
    to_visit.put(link)
print(to_visit)


# TODO: look for cannonical name in page
def crawler(process_number, maybe_visit, visited, to_visit, visited_count):
    while to_visit:
        current_link = to_visit.get()
        visited.put(current_link)
        try:
            page = requests.get(current_link, timeout=10)
            soup = BeautifulSoup(page.text, 'html.parser')
            all_links = [link.get('href') for link in soup.find_all('a') if link.get('href')] # remove Nones
            valid_links = [link for link in all_links if validators.url(link)]
            for link in valid_links:
                maybe_visit.put(link)
            visited_count.value += 1
            # print(f'{process_number}: finised parsing {current_link}')
        except:
            continue


# makes sure visited queue is consistent
def uniquifier(maybe_visit, visited, to_visit):
    seen = set()
    while True:
        while not visited.empty():
            seen.add(visited.get())

        # checks if links in maybe_visit were visited (if not put in to_visit)
        lookup_link = maybe_visit.get()
        if lookup_link not in seen:
            to_visit.put(lookup_link)
            seen.add(lookup_link)


visited_count = Value('i', 0)
Process(target=uniquifier, args=(maybe_visit, visited, to_visit)).start()
for thread_number in range(NUMBER_OF_THREADS):
    Process(target=crawler, args=(thread_number, maybe_visit, visited, to_visit, visited_count)).start()
    # Thread(target=extract_links, args=(thread_number,)).start()

while True:
    print(f'visited {visited_count.value} links, still {to_visit.qsize()} to visit')
    time.sleep(1)

# while to_visit:
#     current_link = to_visit.pop()
#     visited.add(current_link)

#     page_links = extract_links(current_link)
#     new_links = set(lnk for lnk in page_links if lnk not in visited)
#     to_visit |= new_links
#     # time.sleep(1)
