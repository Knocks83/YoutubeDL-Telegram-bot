from yt_dlp import YoutubeDL


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

    except Exception as e:
        print("Error!", e)
        return False


def getChannelVideos(url):
    options = {
        'quiet': True
    }
    try:
        with YoutubeDL(options) as ydl:
            channelVideos = ydl.extract_info(
                url,
                download=False  # We just want to extract the info
            )
            videos = []
            for entry in channelVideos['entries']:
                infosToReturn = {}
                infosToReturn['webpage_url'] = entry['webpage_url']
                if 'title' in entry:
                    infosToReturn['title'] = entry['title']
                if 'uploader' in entry:
                    infosToReturn['uploader'] = entry['uploader']
                if 'thumbnail' in entry:
                    infosToReturn['thumbnail'] = entry['thumbnail']
                
                videos.append(infosToReturn)

            return videos

    except Exception as e:
        print("Error!", e)
        return False


def download(url: str, filename: str) -> bool:
    options = {
        'format': 'mp4',
        'outtmpl':  filename,
        'quiet': True
    }
    with YoutubeDL(options) as ydl:
        ydl.download([url])
