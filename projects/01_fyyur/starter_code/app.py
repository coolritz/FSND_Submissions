#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import collections
import collections.abc
collections.Callable = collections.abc.Callable
import psycopg2
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database - Ritesh done
Migrate = Migrate(app, db)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(200))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='Venue', lazy='joined', cascade="all, delete") 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate 

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venues = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    show = db.relationship('Show', backref='Artist', lazy='joined', cascade="all, delete")    

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer,db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

db.create_all()

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

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
  venues = Venue.query.all()
  data = []
  for venue in venues:
      num_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).count()
      venue_values = {'id':venue.id, 'name': venue.name, 'num_upcoming_shows': num_upcoming_shows}
      NewData =[(d) for d in data if (d['city'] == venue.city and d['state'] == venue.state)]

      if not (NewData):
          CityState_values ={'city': venue.city, 'state': venue.state, 'venues': [venue_values]}
          data.append(CityState_values)
      else:
          venues_list = NewData[0]['venues']
          venues_list.append(venue_values)
          data[data.index(NewData[0])]['venues'] = venues_list
  return render_template('pages/venues.html', areas=data);

#  ----------------------------------------------------------------
@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_key = request.form['search_term']
  searched_venues = Venue.query.filter(Venue.name.ilike('%{}%'.format(search_key))).all()
  response={
    "count": len(searched_venues),
    "data": []
    }
  for venues in searched_venues:
      response["data"].append({
          "id" : venues.id,
          "name" : venues.name,
      })
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  shows = venue.show
  past_shows = db.session.query(Show).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time>datetime.now()).all()
  past_shows_var1 = []
  upcoming_shows_var2 = []

  if not past_shows == []:
      for x in past_shows:
          artist_details= {
              'artist_id': x.Artist.id,
              'artist_name': x.Artist.name,
              'artist_image_link': x.Artist.image_link,
              'start_time': x.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
          past_shows_var1.append(artist_details)
  else:
      flash('No Previous Show History for this Venue', Show.venue_id)   

  if not upcoming_shows == []:
      for show in upcoming_shows:
          artist_details= {
              'artist_id': show.Artist.id,
              'artist_name': show.Artist.name,
              'artist_image_link': show.Artist.image_link,
              'start_time': show.start_time.strftime("%Y-%m-%d %H:%M:%S")
            }
          upcoming_shows_var2.append(artist_details)
  else:
      flash('No Upcoming Shows Available for this Venue', venue.id)
  
  data={
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres.split(','),
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows_var1,
    "upcoming_shows": upcoming_shows_var2,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
        form = VenueForm(request.form)
        form.validate()
        new_venue = Venue(
           name=form.name.data,
           city=form.city.data,
           state=form.state.data,
           address=form.address.data,
           phone=form.phone.data,
           genres=form.genres.data,
           facebook_link=form.facebook_link.data,
           image_link=form.image_link.data,
           seeking_talent=form.seeking_talent.data,
           seeking_description=form.seeking_description.data
        )
        db.session.add(new_venue)
        db.session.commit()
  # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
         db.session.rollback()
         db.session.close()
         flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  finally:
         db.session.close()  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>/delete', methods=['DELETE', 'GET'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  delete_venue = Venue.query.get(venue_id)
  try:
      db.session.delete(delete_venue)
      db.session.commit()
      flash('Deleted from DB Successfully')
  except:
      db.session.rollback()
      flash('Unable to Delete from DB')
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
  data=Artist.query.with_entities(Artist.id, Artist.name).all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_key = request.form['search_term']
  search_result = Artist.query.filter(Artist.name.ilike('%{}%'.format(search_key))).all()
  response={
    "count": len(search_result),
    "data": []
  }
  for artist in search_result:
      response["data"].append({
         "id": artist.id,
         "name":artist.name, 
      })
  
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist=Artist.query.get(artist_id)
  shows = Artist.show
  past_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time<datetime.now()).all()
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id==artist_id).filter(Show.start_time>datetime.now()).all()
  past_shows_var1 = []
  upcoming_shows_var2 = [] 
  if not past_shows == []:
      for shows in past_shows:
          Venue_detail= {
              'venue_id': shows.Venue.id,
              'venue_name': shows.Venue.name,
              'venue_image_link': shows.Venue.image_link,
              'start_time': shows.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            }
      past_shows_var1.append(Venue_detail)
  else:
      flash('No Previous Show History for this Artist', artist_id)   

  if not upcoming_shows == []:
      for shows in upcoming_shows:
          Venue_detail= {
              'venue_id': shows.Venue.id,
              'venue_name': shows.Venue.name,
              'venue_image_link': shows.Venue.image_link,
              'start_time': shows.start_time.strftime("%Y-%m-%d %H:%M:%S"),              
            }
      upcoming_shows_var2.append(Venue_detail)
  else:
      flash('No Upcoming Shows Available for this Artist', artist_id)   
 
  data={
    "id": artist.id,
    "name": artist.name,
    "genres": artist.genres.split(','),
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website_link,
    "facebook_link": artist.facebook_link,
    "seeking_venue": artist.seeking_venues,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows_var1,
    "upcoming_shows": upcoming_shows_var2,
    "past_shows_count": len(past_shows_var1),
    "upcoming_shows_count": len(upcoming_shows_var2),      
  }
  
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_details=Artist.query.get(artist_id)
  
  form.name.data = artist_details.name
  form.city.data = artist_details.city
  form.state.data = artist_details.state 
  form.phone.data = artist_details.phone
  form.genres.data = artist_details.genres
  form.facebook_link.data = artist_details.facebook_link
  form.image_link.data = artist_details.image_link
  form.website_link.data = artist_details.website_link
  form.seeking_venue.data = artist_details.seeking_venues
  form.seeking_description.data = artist_details.seeking_description

  artist={
    "id": artist_details.id,
    "name": artist_details.name,
    "genres": artist_details.genres.split(','),
    "city": artist_details.city,
    "state": artist_details.state,
    "phone": artist_details.phone,
    "website_link": artist_details.website_link,
    "facebook_link": artist_details.facebook_link,
    "seeking_venue": artist_details.seeking_venues,
    "seeking_description": artist_details.seeking_description,
    "image_link": artist_details.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist=db.session.query(Artist).filter_by(id=artist_id).first()
  form = ArtistForm(request.form)
  try:
      artist.name=form.name.data
      artist.city=form.city.data
      artist.state=form.state.data
      artist.phone=form.phone.data
      artist.genres=form.genres.data
      artist.facebook_link=form.facebook_link.data
      artist.image_link=form.image_link.data
      artist.website_link=form.website_link.data
      artist.seeking_venue=form.seeking_venue.data
      artist.seeking_description=form.seeking_description.data
      db.session.commit()
      flash('Artist '+ request.form['name'] + ' was successfully updated')
  except:
      db.session.rollback()
      flash('Artist '+ request.form['name'] + ' could not be updated')
  finally:
      db.session.commit()
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  Venue_details=Venue.query.get(venue_id)
  
  form.name.data = Venue_details.name
  form.city.data = Venue_details.city
  form.state.data = Venue_details.state 
  form.phone.data = Venue_details.phone
  form.address.data = Venue_details.address
  form.genres.data = Venue_details.genres
  form.facebook_link.data = Venue_details.facebook_link
  form.image_link.data = Venue_details.image_link
  form.website_link.data = Venue_details.website_link
  form.seeking_talent.data = Venue_details.seeking_talent
  form.seeking_description.data = Venue_details.seeking_description

  venue_data = {
      "id": Venue_details.id,
      "name": Venue_details.name,
      "genres": Venue_details.genres.split(','),
      "address": Venue_details.address,
      "city": Venue_details.city,
      "state": Venue_details.state,
      "phone" : Venue_details.phone,
      "website_link": Venue_details.website_link,
      "facebook_link": Venue_details.facebook_link,
      "seeking_talent": Venue_details.seeking_talent,
      "seeking_description": Venue_details.seeking_description,
  }
  return render_template('forms/edit_venue.html', form=form, venue=venue_data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  form.validate()
  venue=db.session.query(Venue).filter_by(id=venue_id).first()
  try:
      venue.name=form.name.data
      venue.city=form.city.data
      venue.state=form.state.data
      venue.phone=form.phone.data
      venue.address=form.address.data
      venue.genres=form.genres.data
      venue.facebook_link=form.facebook_link.data
      venue.image_link=form.image_link.data
      venue.website_link=form.website_link.data
      venue.seeking_talent=form.seeking_talent.data
      venue.seeking_description=form.seeking_description.data
      db.session.commit()
      flash('Venue '+ request.form['name'] + ' was successfully updated')
  except:
      db.session.rollback()
      flash('Venue '+ request.form['name'] + ' could not be updated')
  finally:
      db.session.commit() 

  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  try:
        form = ArtistForm(request.form)
        form.validate()
        new_artist = Artist(
           name=form.name.data,
           city=form.city.data,
           state=form.state.data,
           phone=form.phone.data,
           genres=form.genres.data,
           facebook_link=form.facebook_link.data,
           image_link=form.image_link.data,
           website_link=form.website_link.data,
           seeking_venues=form.seeking_venue.data,
           seeking_description=form.seeking_description.data
        )
        db.session.add(new_artist)
        db.session.commit()
  # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
         db.session.rollback()
         db.session.close()
         flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  finally:
         db.session.close()  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')
  
#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  shows = Show.query.all()
  data = []

  for show in shows:
      show_data = {
          "name": show.name,
          "venue_id": show.venue_id,
          "venue_name": Venue.query.get(show.venue_id).name,
          "artist_id": show.artist_id,
          "artist_name": Artist.query.get(show.artist_id).name,
          "artist_image_link": Artist.query.get(show.artist_id).image_link,
          "start_time": show.start_time.strftime("%Y-%m-%d %H:%M:%S"),
      }
      data.append(show_data)
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
  try:
        form = ShowForm(request.form)
        form.validate()
        new_show = Show(
           name = form.name.data,
           artist_id=form.artist_id.data,
           venue_id=form.venue_id.data,
           start_time=form.start_time.data.strftime("%Y-%m-%d %H:%M:%S")
        )
        db.session.add(new_show)
        db.session.commit()
  # on successful db insert, flash success
        flash('Show ' + request.form['name'] + ' on ' + request.form['start_time'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  except:
         db.session.rollback()
         db.session.close()
         flash('An error occurred. Show ' + request.form['name'] + ' on ' + request.form['start_time'] + ' could not be listed.')
  finally:
         db.session.close()  
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

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
