import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import *
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import *
import logging
import sys
import os
from datetime import datetime

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)
sys.stdout.flush()


# TODO: connect to a local postgresql database
# DONE


def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}


def format_datetime(value, format='medium'):
    #  date = dateutil.parser.parse(value)
    date = value
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'Venue'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(120))
    image_link = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE

    def __repr__(self):
        return f'<Venue {self.id} {self.name} {self.genres} {self.city} {self.state}>'


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# DONE

class Show(db.Model):
    __tablename__ = "Show"
    show_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id", ondelete="CASCADE"), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


# DONE

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String)
    genres = db.Column(db.String(120))
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    image_link = db.Column(db.String(500))
    venues = db.relationship('Venue', secondary='Show',
                             backref=db.backref('artists', lazy=True)
                             )

    def __repr__(self):
        return f'<Artist {self.id} {self.name} {self.genres} >'
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    # DONE


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


# app.jinja_env.filters['datetime'] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#
# db.create_all()


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.\
    # DONE
    # ADD try and catch and change proper variable name
    all_venue = db.session.query(func.count(
        Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state)
    data = []
    for i in all_venue:
        data.append(i._asdict())

    for venue in data:
        venue["area"] = (object_as_dict(ven) for ven in Venue.query.filter_by(
            city=venue['city']).filter_by(state=venue['state']).all())

    #     data =object_as_dict(Venue.query.filter_by(city=venue[1]).filter_by(state=venue[2]).all())
    #     venue_list.append(data)

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    # DONE

    search = request.form.get('search_term', '')
    result = db.session.query(Venue).filter(Venue.name.ilike(f'%{search}%')).all()

    response = {
        "count": len(result),
        "data": result
    }

    return render_template('pages/search_venues.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace  real venue data from the venues table, using venue_id
    # DONE

    data = db.session.query(Venue).filter(Venue.id == venue_id).first_or_404()

    data.past_shows = db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"),
                                       Artist.image_link.label(
                                           "artist_image_link"), Show.start_time).filter(
        Show.venue_id == venue_id).filter(
        Artist.id == Show.artist_id).filter(Show.start_time < datetime.now()).all()
    data.past_shows_count = len(data.past_shows)

    data.upcoming_shows = db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"),
                                           Artist.image_link.label(
                                               "artist_image_link"), Show.start_time).filter(
        Show.venue_id == venue_id).filter(
        Artist.id == Show.artist_id).filter(Show.start_time > datetime.now()).all()
    data.upcoming_shows_count = len(data.upcoming_shows)
    # data = db.session.query(Artist).join(show).join(Venue).filter(Artist.id == show.c.artist_id).filter(Venue.id == show.c.venue_id).all()
    # data3 = []

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
    # TODO: modify data to be the data object returned from db insertion'
    # DONE

    try:
        Error = False
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        phone = request.form['phone']
        address = request.form['address']
        genres = request.form['genres']
        website = request.form['website']
        facebook_link = request.form['facebook_link']

        seeking_description = request.form['seeking_description']
        image_link = request.form['image_link']
        seeking_talent = True if 'seeking_talent' in request.form else False

        data = Venue(name=name, city=city, state=state, phone=phone, address=address, genres=genres, website=website,
                     facebook_link=facebook_link, seeking_talent=seeking_talent,
                     seeking_description=seeking_description, image_link=image_link)
        db.session.add(data)
        db.session.commit()

    except Exception as Error:
        Error = True
        db.session.rollback()

    finally:
        db.session.close()

    if not Error:
        flash('Venue ' + request.form['name'] + ' was unsuccessfully !')

    if Error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    # on successful db insert, flash success

    # TODO: on unsuccessful db insert, flash an error instead.
    # DONE
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    Error = False
    try:
        data = Venue.query.get(venue_id)
        db.session.delete(data)
        db.session.commit()
    except:
        Error = True
        db.session.rollback()

    finally:
        db.session.close()

    if error:
        flash(f' Venue {venue_id} was not deleted.')

    if not error:
        flash(f'Venue {venue_id} was successfully deleted.')

    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    # DONE
    data = Artist.query.all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # DONE
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search = request.form.get('search_term', '')
    result = db.session.query(Artist).filter(Artist.name.ilike(f'%{search}%')).all()
    response = {
        "count": len(result),
        "data": result
    }
    return render_template('pages/search_artists.html', results=response,
                           search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist_id = artist_id
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    # DONE
    data = Artist.query.filter(Artist.id == artist_id).first_or_404()
    data.past_shows = db.session.query(Venue.id.label("venue_id"), Venue.name.label("venue_name"),
                                       Venue.image_link.label("venue_image_link"), Show.start_time).filter(
        Show.artist_id == artist_id).filter(Show.venue_id == Venue.id).filter(
        Show.start_time < datetime.now()).all()
    data.past_shows_count = len(data.past_shows)

    data.upcoming_shows = db.session.query(Venue.id.label("venue_id"), Venue.name.label("venue_name"),
                                           Venue.image_link.label(
                                               "venue_image_link"), Show.start_time).filter(
        Show.artist_id == artist_id).filter(
        Show.venue_id == Venue.id).filter(Show.start_time > datetime.now()).all()
    data.upcoming_shows_count = len(data.upcoming_shows)

    return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    data = Artist.query.get(artist_id)

    if data:
        form.name.data = data.name
        form.city.data = data.city
        form.state.data = data.state
        form.phone.data = data.phone
        form.genres.data = data.genres
        form.facebook_link.data = data.facebook_link
        form.image_link.data = data.image_link




    return render_template('forms/edit_artist.html', form=form, artist=data)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing

    artist = Artist.query.get(artist_id)

    try:
        Error = False
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')

        artist.facebook_link = request.form['facebook_link']
        db.session.commit()

    except:
        Error = True
        db.session.rollback()

    finally:
        db.session.close()

    if Error:
        flash('Artist Info was not updated.')
    if not Error:
        flash('Artist Info was successfully updated!')

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    data = Venue.query.get(venue_id)
    if data:
        form.name.data = data.name
        form.genres.data = data.genres
        form.address.data = data.address
        form.city.data = data.city
        form.state.data = data.state
        form.phone.data = data.phone
        form.website.data = data.website
        form.facebook_link.data = data.facebook_link
        form.seeking_talent.data = data.seeking_talent
        form.image_link.data = data.image_link
        form.seeking_description.data = data.seeking_description

    return render_template('forms/edit_venue.html', form=form, venue=data)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    venue = Venue.query.get(venue_id)

    try:
        Error = False
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.image_link = request.form['image_link']

        venue.website = request.form['website']
        venue.seeking_talent = True if 'seeking_talent' in request.form else False
        venue.seeking_description = request.form['seeking_description']

        db.session.commit()
    except e:

        Error = True
        db.session.rollback()

    finally:
        db.session.close()

    if Error:
        flash(f' Venue did not changed.')
    if not Error:
        flash(f'Venue updated successfully')
    return redirect(url_for('show_venue', venue_id=venue_id))
    #return render_template('pages/show_venue.html', venue=venue)


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
    # TODO: modify data to be the data object returned from db insertion
    try:
        name = request.form["name"]
        genres = request.form["genres"]
        city = request.form["city"]
        state = request.form["state"]
        phone = request.form["phone"]

        facebook_link = request.form["facebook_link"]
        image_link = request.form['image_link']
        data = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link,
                      facebook_link=facebook_link)
        db.session.add(data)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()

        # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = db.session.query(Artist.id.label("artist_id"), Artist.name.label("artist_name"),
                            Artist.image_link.label("artist_image_link"), Venue.id.label(
            "venue_id"), Venue.name.label("venue_name"), Show.start_time).filter(Venue.id == Show.venue_id).filter(
        Artist.id == Show.artist_id).all()

    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        start_time = request.form['start_time']

        show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
        db.session.add(show)
        db.session.commit()
    except:
        error = True
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Show could not be listed.')
    if not error:
        flash('Show was successfully listed')
    return render_template('pages/home.html', shows=show)


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run(debug=True)

    app.run()
