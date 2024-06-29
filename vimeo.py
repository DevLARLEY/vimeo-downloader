import argparse
import json
import logging
from base64 import b64decode
from os.path import join
from pathlib import Path
from urllib.parse import urljoin

import requests


class Vimeo:
    def __init__(
            self,
            playlist_url: str,
            output_path: str
    ):
        """
        Vimeo Downloader
        HLS Specification: https://www.rfc-editor.org/rfc/rfc8216
        """
        self.playlist_url = playlist_url
        self.output_path = output_path
        Path(self.output_path).mkdir(parents=True, exist_ok=True)

        self.response = None
        self.clip_id = None

        self.videos = []
        self.audios = []
        self.main_base = None

        self.video_streams = []
        self.audio_streams = []

    def send_request(self) -> bool:
        self.response = requests.get(
            url=self.playlist_url
        )

        return self.response.status_code == 200

    def parse_playlist(self) -> bool:
        try:
            parsed = json.loads(self.response.text)
        except Exception:
            return False

        self.clip_id = parsed.get('clip_id')

        self.videos = sorted(
            parsed.get('video'),
            key=lambda p: p.get('width', 1) * p.get('height', 1),
            reverse=True
        )
        self.audios = sorted(
            parsed.get('audio'),
            key=lambda p: p.get('sample_rate', 1) * p.get('bitrate', 1),
            reverse=True
        )

        self.main_base = urljoin(
            self.playlist_url,
            parsed.get('base_url', '')
        )
        return bool(self.videos or self.audios)

    def _save_playlist(
            self,
            stream: dict,
            content_type: str
    ) -> str:

        stream_base = urljoin(
            self.main_base,
            stream.get('base_url', '')
        )

        segments_to_write = []
        max_duration = 0

        for segments in stream.get('segments', []):
            duration = segments.get('end') - segments.get('start')
            if duration > max_duration:
                max_duration = duration

            segments_to_write.append(
                {
                    'url': urljoin(
                        stream_base,
                        segments.get('url')
                    ),
                    'duration': duration
                }
            )

        init = f'{stream.get('id', 'NO_ID')}_{content_type}_init.mp4'
        with open(join(self.output_path, init), 'wb') as f:
            f.write(b64decode(stream.get('init_segment')))

        playlist = f'{stream.get('id', 'NO_ID')}_{content_type}.m3u8'
        with open(join(self.output_path, playlist), 'w') as f:
            f.writelines(
                [
                    '#EXTM3U\n',
                    '#EXT-X-VERSION:4\n',
                    '#EXT-X-MEDIA-SEQUENCE:0\n',
                    '#EXT-X-PLAYLIST-TYPE:VOD\n',
                    '## Generated by vimeo-downloader (https://github.com/DevLARLEY)\n',
                    f'#EXT-X-MAP:URI="{init}"\n',
                    f'#EXT-X-TARGETDURATION:{int(round(max_duration)) + 1}\n'
                ]
            )
            for segment in segments_to_write:
                f.write(f'#EXTINF:{segment.get('duration', 0)}\n')
                f.write(f'{segment.get('url', '')}\n')
            f.write("#EXT-X-ENDLIST\n")

        return playlist

    def _save_video_stream(
            self,
            video: dict
    ) -> dict:

        playlist_url = self._save_playlist(video, 'video')

        return {
            'url': playlist_url,
            'resolution': f'{video.get('width')}x{video.get('height')}',
            'bandwidth': video.get('bitrate'),
            'average_bandwidth': video.get('avg_bitrate'),
            'codecs': video.get('codecs')
        }

    def _save_audio_stream(
            self,
            audio: dict
    ) -> dict:

        playlist_url = self._save_playlist(audio, 'audio')

        return {
            'url': playlist_url,
            'channels': audio.get('channels'),
            'bitrate': audio.get('bitrate'),
            'sample_rate': audio.get('sample_rate')
        }

    def _save_master(
            self,
            video_streams: list,
            audio_streams: list
    ) -> str:
        master = f'master_{self.clip_id}.m3u8'
        with open(join(self.output_path, master), 'w') as f:
            f.writelines(
                [
                    '#EXTM3U\n',
                    '## Generated by vimeo-downloader (https://github.com/DevLARLEY)\n',
                ]
            )
            stream = 0
            for audio_stream in audio_streams:
                f.write(
                    '#EXT-X-MEDIA:'
                    'TYPE=AUDIO,'
                    f'URI="{audio_stream.get('url')}",'
                    'GROUP-ID="default-audio-group",'
                    f'NAME="{audio_stream.get('bitrate', 0)/1000}_{audio_stream.get('sample_rate')}_{stream}",'
                    f'CHANNELS="{audio_stream.get('channels')}"\n'
                )
                stream += 1
            for video_stream in video_streams:
                f.write(
                    '#EXT-X-STREAM-INF:'
                    f'BANDWIDTH={video_stream.get('bandwidth')},'
                    f'AVERAGE-BANDWIDTH={video_stream.get('average_bandwidth')},'
                    f'CODECS="{video_stream.get('codecs')}",'
                    f'RESOLUTION={video_stream.get('resolution')},'
                    'AUDIO="default-audio-group"\n'
                )
                f.write(f'{video_stream.get('url')}\n')

        return master

    def save_media(self):
        self.video_streams = list(
            map(
                self._save_video_stream,
                self.videos
            )
        )

        self.audio_streams = list(
            map(
                self._save_audio_stream,
                self.audios
            )
        )

        return self._save_master(
            self.video_streams,
            self.audio_streams
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", action="store")
    parser.add_argument("--output", action="store", default=".")
    args = parser.parse_args()

    logging.basicConfig(format='[%(levelname)s]: %(message)s', level=logging.INFO)

    if not args.url:
        logging.error("No url provided")
        parser.print_help()
        exit(-1)

    dl = Vimeo(
        playlist_url=args.url,
        output_path=args.output
    )
    if not dl.send_request():
        logging.error("Unable to send request")
        exit(-1)
    if not dl.parse_playlist():
        logging.error("Unable to parse playlist")
        exit(-1)
    if (master_file := dl.save_media()) is None:
        logging.error("Unable to save media")

    logging.info(f"Master Playlist => {master_file}")
