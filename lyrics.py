# Import packages
import csv
import requests as r
import pandas as pd
from bs4 import BeautifulSoup as bs
from collections import Counter
from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize
import nltk
nltk.download('stopwords')

# Storage list
out_list = []

# Returns all songs 
# n elements (dictionary) -- {"artist", "album", "song_title", "url"}
def get_songs(artist):
    url = 'https://www.lyrics.com/artist/' + str(artist)
    page = r.get(url)
    soup = bs(page.content, 'html.parser')
    song_list = []
    for content in soup.findAll('div', {"class" : "tdata-ext"}):
        for section in content.findAll('div', {"class" : "clearfix"}):
            entry = {"artist": artist}
            for album in section.findAll('h3', {"class" : "artist-album-label"}):
                entry['album'] = album.text
            for songs in section.findAll('td', {"class" : "tal qx"}):
                for song in songs.findAll('strong'):
                    entry['song title'] = song.text
                    for link in song.findAll('a', href=True):
                        entry['url'] = 'https://www.lyrics.com' + link['href']
            song_list.append(entry)
    out_list = song_list
    
    return song_list

# Returns lyrics of all songs
def get_all_lyrics(out_list):
    this_list = out_list
    for entry in this_list:
        entry.update(get_lyrics(entry))
    out_list = this_list
    
    return this_list

# Returns a string of all lyrics of the given song
def get_lyrics(entry):
    url = entry.get('url')
    page = r.get(url)
    soup = bs(page.content, 'html.parser')
    lyrics = ""
    for w in soup.findAll('pre', {"id" : "lyric-body-text"}):
        lyrics = lyrics + w.text + "\n"
    
    clean_lyrics = lyrics.replace(".","")
    clean_lyrics = clean_lyrics.replace(",","")
    clean_lyrics = clean_lyrics.replace(":","")
    clean_lyrics = clean_lyrics.replace("\"","")
    clean_lyrics = clean_lyrics.replace("!","")
    clean_lyrics = clean_lyrics.replace("*","")
    clean_lyrics = clean_lyrics.split()
    stop_words = set(stopwords.words('english')) 
    filtered = [w for w in clean_lyrics if not w.lower() in stop_words]
    most_common, num_most_common = Counter(filtered).most_common(1)[0]

    entry['lyrics'] = lyrics
    entry['number of words'] = len(lyrics.split())
    entry['most common non-stop word'] = most_common, num_most_common

    return entry

# Save data to a .csv file
# Column 1: artist
# Column 2: album
# Column 3: song title
# Column 4: URL of song lyrics
# Column 5: song lyrics (all of the lyrics in one column)
# Column 6: Number of words in the song
# Column 7: Most common non-stop word in the song
def save_lyrics(out_list):
    df = pd.DataFrame(out_list)
    df.to_csv('sample_output.csv', index=False, columns=["artist","album","song title", "url", "lyrics", "number of words", "most common non-stop word"])

