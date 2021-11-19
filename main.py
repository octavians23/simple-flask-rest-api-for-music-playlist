from flask import Flask
from flask_restful import Resource, Api, reqparse, abort
import json

# put - /songs/song_id -d "arg" -d "arg"... -X PUT
# delete - /songs/song_id -X DELETE

app = Flask('PlaylistAPI')
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('artist', required=True)
parser.add_argument('album', required=True)

with open('songs.json', 'r') as f:
    songs = json.load(f)


def write_changes_to_file():
    global songs
    songs = {k: v for k, v in sorted(songs.items(), key=lambda song: song[0])}
    with open('songs.json', 'w') as f:
        json.dump(songs, f)


def check_for_song(songs1, song_title, song_artist, song_id):
    for song in songs1.items():
        if song[0] == song_id:
            abort(404, message=f"Song {song_title} by {song_artist} is already in the playlist!")
        if song[1]['title'] == song_title and song[1]['artist'] == song_artist:
            abort(404, message=f"Song {song_title} by {song_artist} is already in the playlist!")


class Song(Resource):

    def get(self, song_id):
        if song_id == 'all':
            return songs
        if song_id not in songs:
            abort(404, message=f'Song {song_id} not found!')
        return songs[song_id],

    def put(self, song_id):
        args = parser.parse_args()
        check_for_song(songs, args['title'], args['artist'], song_id)
        new_song = {'title': args['title'], 'artist': args['artist'], 'album': args['album']}
        songs[song_id] = new_song
        write_changes_to_file()
        return {song_id: songs[song_id]}, 201

    def delete(self, song_id):
        if song_id not in songs:
            abort(404, message=f'Song {song_id} not found!')
        del songs[song_id]
        for k in songs.copy():
            if int(k.lstrip('song')) > int(song_id.lstrip('song')):
                new_id = 'song' + str(int(k.lstrip('song')) - 1)
                songs[new_id] = songs[k]
                del songs[k]
        write_changes_to_file()
        return '', 204


class SongWithNoId(Resource):

    def get(self):
        return songs

    def put(self):
        args = parser.parse_args()
        new_song = {'title': args['title'], 'artist': args['artist'], 'album': args['album']}
        song_id = max(int(s.lstrip('song')) for s in songs.keys()) + 1
        song_id = f"song{song_id}"
        check_for_song(songs, args['title'], args['artist'], song_id)
        songs[song_id] = new_song
        write_changes_to_file()
        return {song_id: songs[song_id]}, 201


api.add_resource(Song, '/songs/<song_id>')
api.add_resource(SongWithNoId, '/songs')

if __name__ == '__main__':
    app.run()
