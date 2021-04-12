from youtube_dl import YoutubeDL

options = {
    'format': 'mp4[protocol^=http]',
    'quiet': True
}


def getDownloadLink(url):
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
