import api
import storage
import xbmc

def get_video_url(video_id):
    manifest = api.get_video_manifest(video_id)

    urls = [(_get_vertical_resolution_from_m3u_meta(meta), url) for meta,url in manifest]
    urls = [(height, url) for height, url in urls if height is not None]
    urls.sort(key=lambda a: a[0], reverse=True)

    max_height = storage.get_setting_max_vertical_resolution()

    allowed_urls = [url for height, url in urls if height <= max_height]

    return allowed_urls[0]

def _get_vertical_resolution_from_m3u_meta(m3u_meta):
    parts = m3u_meta.split(",")

    for part in parts:
        if part.startswith("RESOLUTION="):
            resolution = part[12:].split("x")
            h = int(resolution[1])

            return h

    return None