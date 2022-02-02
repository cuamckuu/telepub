# TelEpub

Script to convert Telegram channels to epub e-books with images

# Installation

```bash
git clone https://github.com/cuamckuu/telepub.git
cd ./telepub
pip install -r requirements.txt
```

# Usage

1. Create `.env` with `API_ID` and `API_HASH` for [Telethon](https://github.com/LonamiWebs/Telethon) (get it [here](https://my.telegram.org))
2. Run script `python main.py`
3. Enter chat number from list of all channels
4. Wait for data to be downloaded and converted
5. Get generated epub file from `results` folder
6. If needed, validate created file [here](https://draft2digital.com/book/epubcheck/upload)

