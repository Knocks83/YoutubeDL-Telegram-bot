from youtube_dl import YoutubeDL


def getDownloadLink(url):
    options = {
#        'format': 'bestvideo[ext=mp4]',
        'quiet': True
    }
    try:
        with YoutubeDL(options) as ydl:
            videoInfos = ydl.extract_info(
                url,
                download=False  # We just want to extract the info
            )
            infosToReturn = {}
            infosToReturn['url'] = videoInfos['url']
            if 'title' in videoInfos:
                infosToReturn['title'] = videoInfos['title']
            if 'uploader' in videoInfos:
                infosToReturn['uploader'] = videoInfos['uploader']
            if 'thumbnail' in videoInfos:
                infosToReturn['thumbnail'] = videoInfos['thumbnail']

            return infosToReturn

    except Exception:
        print("Error!")
        return False


def download(url: str, filename: str) -> bool:
    options = {
        'format': 'mp4',
        'outtmpl':  filename,
        'quiet': True
    }
    with YoutubeDL(options) as ydl:
        ydl.download([url])
