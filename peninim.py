from sys import argv
from termcolor import colored
import json
from ebooklib import epub


def log_info(info: str) -> None:
    print(colored(f'[+] {info}', 'green'))


# Also exits
def error(info: str) -> None:
    print(colored(f'[!] {info}', 'red'))
    exit(1)


def get_json(input_file: str) -> dict:
    f = open(input_file, 'r', encoding="utf8")
    json_str = f.read()
    log_info('Converting file to a json object...')
    try:
        return json.loads(json_str)
    except json.decoder.JSONDecodeError:
        error('Invalid JSON file')


def create_introduction(json_obj: dict) -> dict:
    introduction = json_obj["text"]["Introduction"]
    html = '<h1>מבוא</h1>'
    log_info('Converting introduction to HTML...')
    for paragraph in introduction:
        html += f'<p>{paragraph}</p>'
    return {"title": 'מבוא', "html": html}


def create_chapters(json_obj: dir) -> list:
    htmls = []
    for index, chapter in enumerate(json_obj["text"][""]):
        title = chapter[0][0].removeprefix('<strong>').removesuffix('</strong>').split('/')[0].strip().replace('"',
                                                                                                               "''")
        html = f'<h1>{title}</h1>'
        log_info(f'Converting {title} to HTML...')
        for sub_chapter in chapter:
            for paragraph in sub_chapter:
                html += f'<p>{paragraph}</p>'
            html += '<br>'
        htmls.append({"title": title, "html": html})

    return htmls


def create_htmls(json_obj: dict) -> list:
    htmls = []

    htmls.append(create_introduction(json_obj))
    htmls += create_chapters(json_obj)

    return htmls


def create_epub(json_obj: dict) -> str:
    book = epub.EpubBook()

    # Set metadata
    book.set_title(json_obj["heTitle"])
    book.set_language(json_obj["language"])
    book.add_author("הרב אליעזר מלמד")
    book.set_direction("rtl")

    # Setup CSS
    style = ".footnote {text-decoration: underline;}"
    default_css = epub.EpubItem(uid="css_default",
                                file_name="style/default.css",
                                media_type="text/css",
                                content=style)
    book.add_item(default_css)

    # Create the chapters
    htmls = create_htmls(json_obj)
    for html in htmls:
        title = html["title"]
        chapter = epub.EpubHtml(title=title, file_name=f'{title}.xhtml', lang=json_obj["language"], direction='rtl')
        chapter.content = html["html"]

        # Add the CSS
        chapter.add_item(default_css)

        # Add the chapter to the book
        book.add_item(chapter)
        book.spine.append(chapter)
        book.toc.append(chapter)

    # Add default NCX and Nav file
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Write!
    file_name = f'{json_obj["heTitle"]}.epub'
    log_info(f'Creating output file "{file_name}"...')
    epub.write_epub(file_name, book, {"spine_direction": "rtl"})
    return file_name


def process(input_file: str) -> None:
    log_info(f'Processing file "{input_file}"...')
    json_obj = get_json(input_file)
    try:
        create_epub(json_obj)
    except KeyError:
        error('Invalid JSON file')

    log_info("Done!")


def main() -> None:
    if len(argv) < 2:
        print(f'Usage: {argv[0]} <input.json>')
    else:
        process(argv[1])


if __name__ == '__main__':
    main()
