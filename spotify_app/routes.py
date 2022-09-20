import requests, json, datetime
from flask import render_template, redirect, url_for, request
from spotify_app import app

from spotify_app.cred import SPOTIPY_CLIENT_ID,SPOTIPY_CLIENT_SECRET


def get_request(access_token, endpoint):
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    response = requests.get(endpoint, headers=authorization_header)
    if response.status_code == 200:
        response_data = json.loads(response.text)
        return response_data
    if response.status_code != 401 and response.status_code!= 200:
        return None

def get_artist(access_token, endpoint):
    authorization_header = {"Authorization": "Bearer {}".format(access_token)}
    response = requests.get(endpoint, headers=authorization_header)
    if response.status_code == 200:
        response_artists = json.loads(response.text)
        return response_artists
    if response.status_code != 401 and response.status_code!= 200:
        return None

def getToken():
    body = {    
        'Content-Type': 'application/x-www-form-urlencoded',
        "grant_type" : "client_credentials"
    }
    req = requests.post('https://accounts.spotify.com/api/token', auth=(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET), data=body)
    if req.status_code == 200:
        req_response = req.json()
        access_token = req_response['access_token']
        return access_token
    return None

def query_artist(access_token, artist):
    payload = {'q': artist, 'type': 'artist', 'limit': '1'}
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    req = requests.get('https://api.spotify.com/v1/search', params=payload, headers=headers)
    return req

def query_track(access_token, track):
    payload = {'q': track, 'type': 'track', 'limit': '1'}
    headers = {
        'Authorization': f"Bearer {access_token}",
        'Accept': 'application/json',
        'Content-Type': 'application/json',
    }

    req = requests.get('https://api.spotify.com/v1/search', params=payload, headers=headers)
    return req


@app.route('/')
@app.route('/top-tracks')
def top_tracks():
    access_token = getToken()
    if access_token != None:
        
        top_tracks = get_request(access_token, "https://api.spotify.com/v1/tracks?ids=0WtM2NBVQNNJLh6scP13H8,5ycsqezujKrwviU3VFhci1,3eR23VReFzcdmS7TYCrhCe,4T3c3YmtREIOyflo9ytTAL,0TDLuuLlV54CkRRUOahJb4,6bERF1Siw7KAbUtjg0LSas,0pqnGHJpmpxLKifKRmU6WP,0u2P5u6lvoDfwTYjAADbn4,6ocbgoVGwYJhOv1GgI9NsF,0dIoGTQXDh1wVnhIiSyYEa,0QBzMgT7NIeoCYy3sJCof1,5wANPM4fQCJwkGd4rN57mH,7kdmDLwyzFL8jYLzfMvPwQ,6RUKPb4LETWmmr3iAEQktW,6OcCk1dbAb7XNHsC098oEM")

        if top_tracks != None:
            for top_track in top_tracks['tracks']:
                raw_time = int(top_track['duration_ms'])
                ms = raw_time / 1000
                MinutesGet, SecondsGet = divmod(ms, 60)
                MinutesGet = round(MinutesGet)
                SecondsGet = round(SecondsGet)
                MinutesGet = str(MinutesGet).zfill(2)
                SecondsGet = str(SecondsGet).zfill(2)
                pr_time = f"{MinutesGet}:{SecondsGet}"
                top_track['duration_ms'] = pr_time
            return render_template('tracks.html', top_tracks=top_tracks)
        return render_template('search_error.html', error = '403, Spotify denied access')
        
    return render_template('search_error.html', error = 'Try reloading the previous page')


@app.route('/artists')
def home():
    access_token = getToken()
    if access_token != None:
        top_artists  = get_artist(access_token, "https://api.spotify.com/v1/artists?ids=66CXWjxzNUsdJxJ2JdwvnR,0C8ZW7ezQVs4URX5aX7Kqx,6qMGjGD3lmDJtzALZ8uS2z,4kYSro6naA4h99UJvo89HB,1hNaHKp2Za5YdOAG0WnRbc,7n2wHs1TKAczGzO7Dd2rGr,6vWDO969PvNqNYHIOW5v0m,4Ns55iOSe1Im2WU2e1Eym0,7dGJo4pcD2V6oG8kP0tJRR,1XavfPKBpNjkOfxHINlMHF,7vk5e3vY1uw9plTHJAMwjN,246dkjvS1zLTtiykXe5h60,6qqNVTkY8uBg9cP3Jd7DAH")
        for artist in top_artists['artists']:
            raw_genre = artist['genres']
            new_genre = ", ".join(map(str,raw_genre))
            artist['genres'] = new_genre
            return render_template('home.html', top_artists=top_artists)
        return render_template('search_error.html', error = '403, Spotify denied access')
        
    return render_template('search_error.html', error = 'Try reloading the previous page')


@app.route('/track/<id>')
def track(id):
    access_token = getToken()
    if access_token != None:
        track = get_request(access_token, "https://api.spotify.com/v1/tracks/{}".format(id))
        if track != None:
            items = []
            for item in track['album']['artists']:
                item = item['name']
                items.append(item)
                new_items = ", ".join(map(str,items))

            raw_time = int(track['duration_ms'])
            ms = raw_time / 1000
            MinutesGet, SecondsGet = divmod(ms, 60)
            MinutesGet = round(MinutesGet)
            SecondsGet = round(SecondsGet)
            MinutesGet = str(MinutesGet).zfill(2)
            SecondsGet = str(SecondsGet).zfill(2)
            pr_time = f"{MinutesGet}:{SecondsGet}"
            track['duration_ms'] = pr_time

            r_date_list =  (track['album']['release_date']).split('-')
            dt = datetime.datetime(int(r_date_list[0]), int(r_date_list[1]),int(r_date_list[2]))
            r_date = dt.strftime("%B, %Y")
            track['album']['release_date'] = r_date

            return render_template('search.html',topic='Top result (Song)', track=track, all_artists=new_items)
        return render_template('search_error.html', error = '403, Spotify denied access')
    return render_template('search_error.html', error = 'Try reloading the previous page')

@app.route('/artist/<id>')
def artist(id):
    access_token = getToken()
    if access_token != None:
        artist = get_request(access_token, "https://api.spotify.com/v1/artists/{}".format(id))
        if artist != None:
            f_genre = ", ".join(map(str,artist['genres']))
            artist['genres'] = f_genre

            followers = "{:,}".format(int(artist['followers']['total']))
            artist['followers']['total'] = followers
            return render_template('search.html',topic='Top result (Artist)', artist=artist)
        return render_template('search_error.html', error = '403, Spotify denied access')
    return render_template('search_error.html', error = 'Try reloading the previous page')

@app.route('/search-artist', methods=['GET', 'POST'])
def search_artist():
    access_token = getToken()
    if access_token != None:
        if request.method == 'POST':
            artist = request.form.get('artist')
            if artist:
                res = query_artist(access_token, artist)
                if res.status_code != 200:
                    return render_template('search_error.html', error = '{}'.format(res.status_code))
                if res.status_code == 200:
                    artist_search = res.json()
                    if len(artist_search['artists']['items']) >= 1:
                        f_genre = ", ".join(map(str,artist_search['artists']['items'][0]['genres']))
                        artist_search['artists']['items'][0]['genres'] = f_genre

                        followers = "{:,}".format(int(artist_search['artists']['items'][0]['followers']['total']))
                        artist_search['artists']['items'][0]['followers']['total'] = followers
                        return render_template('search.html',topic='Top result (Artist)', artist_search=artist_search)
                    return  render_template('search_error.html', artist_search=artist_search, error='Your search returned no results. Do Check for proper spellings')
            return redirect(url_for('home'))          
    return render_template('search_error.html', error = 'Try reloading the previous page')

@app.route('/search-track', methods=['GET', 'POST'])
def search_track():
    access_token = getToken()
    if access_token != None:
        if request.method == 'POST':
            track = request.form.get('track')
            if track:
                res = query_track(access_token, track)
                if res.status_code != 200:
                    return render_template('search_error.html', error = '{}'.format(res.status_code))
                if res.status_code == 200:
                    track_search = res.json()
                    if len(track_search['tracks']['items']) >= 1:
                        items = []
                        for item in track_search['tracks']['items'][0]['album']['artists']:
                            item = item['name']
                            items.append(item)
                            new_items = ", ".join(map(str,items))
                        raw_time = int(track_search['tracks']['items'][0]['duration_ms'])
                        ms = raw_time / 1000
                        MinutesGet, SecondsGet = divmod(ms, 60)
                        MinutesGet = round(MinutesGet)
                        SecondsGet = round(SecondsGet)
                        MinutesGet = str(MinutesGet).zfill(2)
                        SecondsGet = str(SecondsGet).zfill(2)
                        pr_time = f"{MinutesGet}:{SecondsGet}"
                        track_search['tracks']['items'][0]['duration_ms'] = pr_time

                        r_date_list =  (track_search['tracks']['items'][0]['album']['release_date']).split('-')
                        dt = datetime.datetime(int(r_date_list[0]), int(r_date_list[1]),int(r_date_list[2]))
                        r_date = dt.strftime("%B, %Y")
                        track_search['tracks']['items'][0]['album']['release_date'] = r_date
                        return render_template('search.html',topic='Top result (Song)', track_search=track_search, all_artists=new_items)
                    return  render_template('search_error.html', track_search=track_search, error='Your search returned no results. Do Check for proper spellings')
            return redirect(url_for('top_tracks'))          
    return render_template('search_error.html', error = 'Try reloading the previous page')