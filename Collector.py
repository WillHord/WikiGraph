import requests
import threading
from queue import Queue
from lxml import html
import time

class Collector():
    itemsToCheck = ['#', 'File:', '_(disambiguation)', 'Template:', 'Category:', 'Wikipedia_talk:']

    def __init__(self, url):
        self.startUrl = url
        self.seen = []
        self.queue = Queue()
        self.counter = 0
        self.threads = []

    def startCollection(self, thread_amount):
        self.initialCollection(self.startUrl)
        time.sleep(5)

        self.createThreads(thread_amount)
        # self.startThreads()

        print(f'{thread_amount} threads have started')

    def initialCollection(self, url):
        self.queue.put(url)

        curr = self.queue.get()
        self.counter += 1
        print(f"\r{self.counter}", end="")
        
        try:
            res = requests.get(curr, headers={'Accept': 'application/json'})
        except Exception:
            print(f'Error at URL: {curr}')
            self.queue.put(curr)
        self.seen.append(curr)

        webpage = html.fromstring(res.content)
        roughLinks = webpage.xpath("//div[@id='mw-content-text']//preceding::span[@id='See_also']/preceding::a/@href")
        if len(roughLinks) == 0:
            roughLinks = webpage.xpath("//div[@id='mw-content-text']//a/@href")
        
        cleanedLinks = []
        for i in roughLinks:
            if not i.startswith('/wiki/') or any(x in i for x in self.itemsToCheck):
                continue
            else:
                link = 'https://en.wikipedia.org' + i
                cleanedLinks.append(link)
                if link not in self.seen:
                    self.queue.put('https://en.wikipedia.org' + i)
        f = open('WikiPages', 'a')
        f.write(curr + ' ' + ' '.join(link for link in cleanedLinks)[:-1] + '\n')
        f.close()

    def collectPages(self):
        while not self.queue.empty():
            curr = self.queue.get()
            if curr in self.seen:
                continue
            self.counter += 1
            print(f"\r{self.counter}", end="")
            
            try:
                res = requests.get(curr, headers={'Accept': 'application/json'})
            except Exception:
                print(f'Error at URL: {curr}')
                self.queue.put(curr)
            self.seen.append(curr)

            webpage = html.fromstring(res.content)
            roughLinks = webpage.xpath("//div[@id='mw-content-text']//preceding::span[@id='See_also']/preceding::a/@href")
            if len(roughLinks) == 0:
                roughLinks = webpage.xpath("//div[@id='mw-content-text']//a/@href")
            
            cleanedLinks = []
            for i in roughLinks:
                if not i.startswith('/wiki/') or any(x in i for x in self.itemsToCheck):
                    continue
                else:
                    link = 'https://en.wikipedia.org' + i
                    cleanedLinks.append(link)
                    if link not in self.seen:
                        self.queue.put('https://en.wikipedia.org' + i)
            f = open('WikiPages', 'a')
            f.write(curr + ' ' + ' '.join(link for link in cleanedLinks)[:-1] + '\n')
            f.close()

    def createThreads(self, amount):
        print(f'Creating {amount} Threads')
        for i in range(amount):
            t = threading.Thread(target=self.collectPages())
            t.daemon = True
            self.threads.append(t)
        print(f'Starting {len(self.threads)} Threads')
        for i in range(amount):
            self.threads[i].start()
        for i in range(amount):
            self.threads[i].join()

if __name__ == '__main__':
    startURL = 'https://en.wikipedia.org/wiki/Bread'
    print(f"Starting Collector at URL: {startURL}")
    BreadCollector = Collector(startURL)
    BreadCollector.startCollection(10)