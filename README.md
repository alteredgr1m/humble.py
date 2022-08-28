# humble.py
Humble Bundle Book Downloader

### Instructions

- install dependencies
```
    pip3 install requests selenium webdriver_manager
```
- clone the repo
```
git clone https://github.com/alteredgr1m/humble.py.git
```
- create drivers directory in repo
```
cd humble.py
mkdir drivers
```
- run the script like so:
```
python humble.py -b {BROWSER} -u {BUNDLE_URL} -p {DOWNLOAD_PATH} -f {FORMAT} 
```

### Settings
- `-b {chrome, firefox}` or `--browser {chrome, firefox}` Currently supports Chrome and Firefox, sets the browser you want the script to use for downloading the books. (REQUIRED)
- `-p {download_path}` or `--path {download_path}` Sets the path that the script will store details on the bundle (name and book links) in JSON as well as the destination it will download the books to in a folder named after the bundle.
- `-u {url}` or `--url {url}` Sets URL to the bundle you want to download books from.
- `-f {format}` or `--format {format}` Sets the format you want to download the books in. Depending on the bundle, that can be PDF, EPUB, MOBI, or CBZ.

By default, it will run the browser in headless mode. To do otherwise, run it with `-hl false` or `--headless false`.
