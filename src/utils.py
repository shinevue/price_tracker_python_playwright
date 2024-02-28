def read_urls(filepath: str = 'urls.txt') -> list[str]:
    with open(filepath, 'r') as file:
        urls = [line.rstrip() for line in file]
        return urls


def compare_list_elements(input_list) -> bool:
    return all(item == input_list[0] for item in input_list)
