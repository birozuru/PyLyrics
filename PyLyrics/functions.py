import json, sys, codecs
import requests
from bs4 import BeautifulSoup, Comment


class Track(object):
    def __init__(self, trackName, album, artist):
        self.name = trackName
        self.album = album
        self.artist = artist

    def __repr__(self):
        return self.name

    def link(self):
        return 'http://lyrics.wikia.com/{0}:{1}'.format(self.artist.replace(' ', '-'), self.name.replace(' ', '-'))


class Artist(object):
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name.encode('utf-8')


class Album(object):
    def __init__(self, name, link, singer):
        self.year = name.split(' ')[-1]
        self.name = name.replace(self.year, ' ').rstrip()
        self.url = link
        self.singer = singer

    def link(self):
        return self.url

    def __repr__(self):
        if sys.version_info[0] == 2:
            return self.name.encode('utf-8', 'replace')
        return self.name


class PyLyrics:
    @staticmethod
    def getAlbums(singer):
        singer = singer.replace(' ', '_')
        s = BeautifulSoup(requests.get('http://lyrics.wikia.com/{0}'.format(singer)).text)
        spans = s.findAll('span', {'class': 'mw-headline'})

        als = []

        for tag in spans:
            try:
                a = tag.findAll('a')[0]
                als.append(Album(a.text, 'http://lyrics.wikia.com' + a['href'], singer))
            except:
                pass

        if not als:
            raise ValueError("Unknown Artist Name given")
            return None
        return als

    @staticmethod
    def getTracks(current_album, singer):
        #Lists all the tracks of the value current_album and forms a dictionary

        singer = singer.replace(' ', '_')
        current_album = current_album

        url = "http://lyrics.wikia.com/api.php?action=lyrics&artist={0}&fmt=xml".format(singer)
        soup = BeautifulSoup(requests.get(url).text)
        songs = soup.findAll('songs')
        album_names = soup.findAll('album')
        years = soup.findAll('year')
        data = {}

        for song, album, year in zip(songs, album_names, years):
            temp_songs = [x.text for x in song.findAll('item')]
            temp_album = album.text + '|' + year.text

            data[temp_album] = temp_songs

        data = json.loads(json.dumps(data))

        for album in data.keys():
            album_name = album.lower()
            current_album = current_album.lower()
            if current_album in album_name:
                return {album.split('|')[0]: data[album]}

            try:
                if album not in data.keys():
                    raise ValueError("Unknown album found")
            except:
                pass

    @staticmethod
    def getLyrics(singer, song):
        # Replace spaces with _
        singer = singer.replace(' ', '_')
        song = song.replace(' ', '_')
        r = requests.get('http://lyrics.wikia.com/{0}:{1}'.format(singer, song))
        s = BeautifulSoup(r.text)
        # Get main lyrics holder
        lyrics = s.find("div", {'class': 'lyricbox'})
        if lyrics is None:
            raise ValueError("Song or Singer does not exist or the API does not have Lyrics")
            return None
        # Remove Scripts
        [s.extract() for s in lyrics('script')]

        # Remove Comments
        comments = lyrics.findAll(text=lambda text: isinstance(text, Comment))
        [comment.extract() for comment in comments]

        # Remove unnecessary tags
        for tag in ['div', 'i', 'b', 'a']:
            for match in lyrics.findAll(tag):
                match.replaceWithChildren()
        # Get output as a string and remove non unicode characters and replace <br> with newlines
        output = str(lyrics).encode('utf-8', errors='replace')[22:-6:].decode("utf-8").replace('\n', '').replace(
            '<br/>', '\n')
        try:
            return output
        except:
            return output.encode('utf-8')


def main():
    albums = PyLyrics.getAlbums('Drake')
    print(albums) #Prints out all listed albums of an artist
    tracks = PyLyrics.getTracks('Nothing was the same', 'Drake')
    print(tracks) #Prints out all the tracks in an album of an artist
    lyrics = PyLyrics.getLyrics('Drake', 'Worst Behaviour')
    print(lyrics) #Prints out the lyrics of a particular song by an artist


if __name__ == '__main__':
    main()
