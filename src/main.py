import browser

urls = ["https://en.wikipedia.org/wiki/Security_orchestration",
        "https://en.wikipedia.org/wiki/Security_information_and_event_management",
        "https://en.wikipedia.org/wiki/Security_architecture",
        "https://en.wikipedia.org/wiki/Python",
        ]
if __name__ == "__main__":
    b = browser.Browser()
    for url in urls:
        page = b.visit_url(url)
        if not page:
            print(b.response_error)
            continue
        print(page.url)
        print(page.status_code)
        print(page.raw_html[:100])

