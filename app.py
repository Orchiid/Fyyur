#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort, session
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    venue = {}
    venues = Venue.query.all()
    for data in venues:
      id= data.id
      name= data.name
      city= data.city
      state=data.state
      area = (city, state)
      if area not in venue:
          venue[area] = {
              'city': city,
              'state': state,
              'venues': []
          }
      venue[area]['venues'].append({
          'id': id,
          'name': name,
      })
    return render_template('pages/venues.html', areas=[venue[k] for k in venue.keys()])

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seacrh for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  terms = Venue.query
  search_term = request.form.get('search_term', '')
  term = terms.filter(Venue.name.ilike('%' + search_term + '%'))
  results = {
    'count': term.count(),
    'data': term
  }
  return render_template('pages/search_venues.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue =  Venue.query.get_or_404(venue_id)
  print(venue)
  show = Show.query.filter_by(venue_id=venue_id).all()
  past_shows = []
  upcoming_shows = []
  
    # time_now = datetime.now()
    # upcoming_show = []
    # past_show = []
    # if info.start_time < time_now:
    #   past_show.append(tag)
    # else:
    #   upcoming_show.append(tag)

  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent_looking,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link,
    'past_shows': past_shows,
    'upcoming shows': upcoming_shows
  }

  for info in show:
    tag={
      "venue_id": info.venue_id,
      'venue_name': info.venue.name,
      "artist_id": info.artist_id,
      'artist_name': info.artist.name,
      'artist_image_link': info.artist.image_link,
      "start_time": format_datetime(str(info.start_time))
    }
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time<datetime.now()).all()   

  for show in past_shows_query:
    past_shows.append(tag)
  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show. start_time>datetime.now()).all()   
  
  for show in upcoming_shows_query:
    upcoming_shows.append(tag)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  venue_data = {}
  form = VenueForm()
  # TODO: insert form data as a new Venue record in the db, instead
  if form.validate_on_submit():
    try:
      name = request.get_json()['name']
      city = request.get_json()['city']
      state = request.get_json()['state']
      address = request.get_json()['address']
      phone = request.get_json()['phone']
      image_link = request.get_json()['image_link']
      facebook_link = request.get_json()['facebook_link']
      genres = request.form.getlist('genres')
      website_link = request.get_json()['website_link']
      talent_looking = request.get_json()['seeking_talent']
      seeking_desc = request.get_json()['seeking_description']
      # shows = request.get_json()['shows']

      print (talent_looking)
      #   # TODO: modify data to be the data object returned from db insertion
      new_venue = Venue(name=name, city=city, state=state, address=address, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres, website_link=website_link, talent_looking=bool(talent_looking), seeking_desc=seeking_desc)
      print (new_venue)
      db.session.add(new_venue)
      db.session.commit()
      venue_data['name'] = new_venue.name
      venue_data['city'] = new_venue.city
      venue_data['state'] = new_venue.state
      venue_data['address'] = new_venue.address
      venue_data['phone'] = new_venue.phone
      venue_data['image_link'] = new_venue.image_link
      venue_data['facebook_link'] = new_venue.facebook_link
      venue_data['genres'] = new_venue.genres
      venue_data['website_link'] = new_venue.website_link
      venue_data['talent_looking'] = new_venue.talent_looking
      venue_data['seeking_desc'] = new_venue.seeking_desc
      
    except:
      error = True
      db.session.rollback()
      print(sys.exc_info())
      flash('An error occurred. Venue ' + request.get_json()['name'] + ' could not be listed.')
    finally:
      db.session.close()
    if error:
      abort (400)
    else:
      flash('Venue ' + request.get_json()['name'] + ' was successfully listed!')
      # return jsonify(venue_data)
      return render_template('pages/home.html') 
  else:
        for field, message in form.errors.items():
            flash(field + ' - ' + str(message), 'danger')
  return render_template('forms/new_venue.html', form=form)    
  
@app.route('/delete_venues/<int:venue_id>')
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  delete_venue = Venue.query.get_or_404(venue_id)
  name: delete_venue.name
  try:
    db.session.delete(delete_venue)
    db.session.commit()
    print('deleted')
    return redirect(url_for("venues"))
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + name + 'could not be deleted. Please try again later.')
    print('not deleted')
    print(sys.exc_info())
  finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for("index"))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artist = Artist.query.all()
  return render_template('pages/artists.html', artists=artist)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seacrh for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  terms = Artist.query
  search_term = request.form.get('search_term', '')
  term = terms.filter(Artist.name.ilike('%' + search_term + '%'))
  results = {
    'count': term.count(),
    'data': term
  }
  return render_template('pages/search_artists.html', results=results, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # artist = artist_id.query.all()
  # data={}
  artist =  Artist.query.get_or_404(artist_id)
  show = Show.query.filter_by(artist_id=artist_id).all()
  past_shows = []
  upcoming_shows = []
    # time_now = datetime.now()
    # upcoming_show = []
    # past_show = []
    
    # if info.start_time < time_now:
    #   past_show.append(tag)
    # else:
    #   upcoming_show.append(tag)
  print(artist)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.venue_looking,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link,
    'past_shows':past_shows,
    'upcoming_shows':upcoming_shows
  }

  past_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time<datetime.now()).all()   
  upcoming_shows_query = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show. start_time>datetime.now()).all()   

  for info in show:
    tag={
      "venue_id": info.venue_id,
      'venue_name': info.venue.name,
      "artist_id": info.artist_id,
      'artist_name': info.artist.name,
      'venue_image_link': info.venue.image_link,
      "start_time": format_datetime(str(info.start_time))
    }
  
  for show in past_shows_query:
    past_shows.append(tag)
 
  for show in upcoming_shows_query:
    upcoming_shows.append(tag)
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist =  Artist.query.get_or_404(artist_id)
  print(artist)
  data = {
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.venue_looking,
    "seeking_description": artist.seeking_desc,
    "image_link": artist.image_link
  }
 
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=data)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  update_artist = Artist.query.get_or_404(artist_id)
  

  if request.method == 'POST':
    update_artist.name = request.form.get('name')
    update_artist.genres = request.form.getlist('genres')
    update_artist.city = request.form.get('city')
    update_artist.state = request.form.get('state')
    update_artist.phone = request.form.get('phone')
    update_artist.website = request.form.get('website')
    update_artist.facebook_link = request.form.get('facebook_link')
    update_artist.seeking_venue = request.form.get('seeking_venue')
    update_artist.seeking_description = request.form.get('seeking_description')
    update_artist.image_link = request.form.get('image_link')
    try:
      db.session.commit()
      return redirect('/artists')
    except:
          flash('An error occurred. Changes could not be made for Artist ' + request.form.get('name') + '. Please try again later.')
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue =  Venue.query.get_or_404(venue_id)
  print(venue)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "city": venue.city,
    "state": venue.state,
    "address": venue.address,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.talent_looking,
    "seeking_description": venue.seeking_desc,
    "image_link": venue.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  update_venue = Venue.query.get_or_404(venue_id)
  

  if request.method == 'POST':
    update_venue.name = request.form.get('name')
    update_venue.genres = request.form.getlist('genres')
    update_venue.city = request.form.get('city')
    update_venue.state = request.form.get('state')
    update_venue.phone = request.form.get('phone')
    update_venue.website = request.form.get('website')
    update_venue.address = request.form.get('address')
    update_venue.facebook_link = request.form.get('facebook_link')
    update_venue.seeking_talent = request.form.get('seeking_talent')
    update_venue.seeking_description = request.form.get('seeking_description')
    update_venue.image_link = request.form.get('image_link')
    try:
      db.session.commit()
      return redirect('/venues')
    except:
          flash('An error occurred. Changes could not be made for Artist ' + request.form.get('name') + '. Please try again later.')
  else:
    return redirect(url_for('show_venue', artist_id=venue_id))

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  error = False
  artist_data = {}
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.get_json()['name']
    city = request.get_json()['city']
    state = request.get_json()['state']
    phone = request.get_json()['phone']
    image_link = request.get_json()['image_link']
    facebook_link = request.get_json()['facebook_link']
    genres = request.form.getlist('genres')
    website_link = request.get_json()['website_link']
    venue_looking = request.get_json()['seeking_venue']
    seeking_desc = request.get_json()['seeking_description']
    # shows = request.get_json()['shows']

    print (genres)
    #   # TODO: modify data to be the data object returned from db insertion
    new_artist = Artist(name=name, city=city, state=state, phone=phone, image_link=image_link, facebook_link=facebook_link, genres=genres, website_link=website_link, venue_looking=bool(venue_looking), seeking_desc=seeking_desc)
    print (new_artist)
    db.session.add(new_artist)
    db.session.commit()
    artist_data['name'] = new_artist.name
    artist_data['city'] = new_artist.city
    artist_data['state'] = new_artist.state
    artist_data['phone'] = new_artist.phone
    artist_data['image_link'] = new_artist.image_link
    artist_data['facebook_link'] = new_artist.facebook_link
    artist_data['genres'] = new_artist.genres
    artist_data['website_link'] = new_artist.website_link
    artist_data['venue_looking'] = new_artist.venue_looking
    artist_data['seeking_desc'] = new_artist.seeking_desc
    # venue_data['shows'] = new_venue.shows
    return render_template('pages/home.html')
    
    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + request.get_json()['name'] + ' could not be listed.')
  finally:
    db.session.close()
  if error:
    abort (400)
  else:
    flash('Artist ' + request.get_json()['name'] + ' was successfully listed!')
    return jsonify(artist_data),
    

    
   
    

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows =  Show.query.all()
  data = []
  # print(artist)

  for info in shows:
    tag={
      "venue_id": info.venue_id,
      'venue_name': info.venue.name,
      "artist_id": info.artist_id,
      'artist_name': info.artist.name,
      'artist_image_link': info.artist.image_link,
      "start_time": format_datetime(str(info.start_time))
    }
    data.append(tag)
  print(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  error = False
  show_data = {}
  # TODO: insert form data as a new Venue record in the db, instead
  try:
    venue_id = request.get_json()['venue_id']
    artist_id = request.get_json()['artist_id']
    start_time = request.get_json()['start_time']
    print (venue_id)
    new_show = Show(venue_id=venue_id,artist_id=artist_id,start_time=start_time)
    print(new_show)
    db.session.add(new_show)
    db.session.commit()
    flash('Show was successfully listed!')
    show_data['venue_id'] = new_show.venue_id
    show_data['artist_id'] = new_show.artist_id
    show_data['start_time'] = new_show.start_time
  
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Show could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html') 
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
