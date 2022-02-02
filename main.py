#!/usr/bin/env python
import asyncio
import dataclasses
import io
import os
import re

from tqdm.asyncio import tqdm

from PIL import Image
from dotenv import load_dotenv
from ebooklib import epub
from telethon import TelegramClient

load_dotenv()


@dataclasses.dataclass
class Dialog(object):
    id: int
    name: str


def message_to_html(msg, image_path):
    html_body = ''
    if image_path:
        html_body += f'<img src="{image_path}"/>'

    if msg:
        msg = re.sub(r'\n', r'<br>', msg)
        html_body += msg

    return html_body


async def main():
    api_id = os.getenv('API_ID')
    api_hash = os.getenv('API_HASH')
    client = TelegramClient('session', api_id, api_hash)
    client.parse_mode = 'html'

    async with client:
        dialogs = []
        for d in sorted(await client.get_dialogs(), key=lambda d: d.id):
            if not d.is_channel:
                continue

            dialog = Dialog(id=d.entity.id, name=d.entity.title)
            dialogs.append(dialog)

        for i, d in enumerate(dialogs):
            print(i+1, d)
        print()

        idx = int(input('Choose dialog to convert: '))
        assert (0 <= idx-1 < len(dialogs)), 'Dialog index should be correct'

        d = dialogs[idx-1]

        os.makedirs

        book = epub.EpubBook()
        book.set_identifier(str(d.id))
        book.set_title(d.name)
        book.set_language('ru')

        # FIXME: Not working
        # cover_image = await client.download_profile_photo(d.id, file=bytes)
        # if cover_image:
        #     book.set_cover('cover.jpeg', cover_image)

        limit = None
        msg_cnt = limit or sum([1 async for _ in client.iter_messages(d.id)])

        chapters = []
        msg_iter = client.iter_messages(d.id, reverse=True, limit=limit)
        async for msg in tqdm(msg_iter, total=msg_cnt):
            if not (msg.text or msg.photo):
                continue

            image_path = None
            if msg.photo and not msg.web_preview:
                image_bytes = await msg.download_media(file=bytes)
                await asyncio.sleep(0.1)
                pil_image = Image.open(io.BytesIO(image_bytes))

                compressed_image = io.BytesIO()
                pil_image.save(
                    compressed_image,
                    format='JPEG',
                    quality=35,
                    optimize=True,
                    progressive=True,
                )

                image_path = f'images/msg_{msg.id}.jpeg'
                image = epub.EpubItem(
                    uid=f'msg_{msg.id}',
                    file_name=image_path,
                    media_type='image/jpeg',
                    content=compressed_image.getvalue(),
                )
                book.add_item(image)

            chapter = epub.EpubHtml(
                title=msg.date.strftime(r'%Y-%m-%d %H:%M:%S'),
                file_name=f'msg_{msg.id}.xhtml',
                lang='ru',
            )
            html = message_to_html(msg.text, image_path)
            chapter.set_content(html)

            book.add_item(chapter)
            chapters.append(chapter)

        book.toc = chapters

        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())

        book.spine = ['nav'] + chapters

        os.makedirs('results', exist_ok=True)
        epub.write_epub(f'./results/{d.name}.epub', book)


if __name__ == '__main__':
    asyncio.run(main())

