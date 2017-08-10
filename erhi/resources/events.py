from flask import abort, g, request
from flask_restplus import Namespace, Resource
from mongoengine.errors import ValidationError

from datetime import datetime

from erhi.models import auth, Event

api = Namespace('events', description='')

EVENTS_PER_PAGE = 15


def processEventDetail(data):
    title = data.get('title')
    description = data.get('description')
    keywords = data.get('keywords')

    # expect utc time ?
    epoch_time = data.get('time')
    location_coordinates = data.get('location')
    if epoch_time is None or location_coordinates is None:
        abort(400, 'time and location of event are required')

    time = datetime.fromtimestamp(epoch_time)
    location = {
        'type': 'Point',
        'coordinates': location_coordinates
    }

    return {
        'title': title,
        'description': description,
        'keywords': keywords,
        'time': time,
        'location': location
    }


@api.route('/')
class Events(Resource):
    def get(self):
        page = int(request.args.get('page') or 1)

        events = Event.objects.paginate(page=page, per_page=EVENTS_PER_PAGE)

        return [event.to_json() for event in events.items]

    @auth.login_required
    def post(self):
        creator = g.user
        if creator is None:
            abort(500, 'user logged in but no user instance found')

        data = request.get_json()

        eventDetail = processEventDetail(data)

        oid = data.get('oid')
        # if valid oid provided, do update instead of creating
        if oid:
            try:
                ev = Event.objects(id=oid).first()
            except ValidationError:
                abort(400, 'invalid event object id, it must be a 12-byte'
                           ' input or a 24-character hex string')

            if ev is None:
                abort(400, 'could not locate the event from object id')
            status = ev.update(**{
                'title': eventDetail['title'],
                'description': eventDetail['description'],
                'time': eventDetail['time'],
                'location': eventDetail['location'],
                'creator': creator,
                'keywords': eventDetail['keywords'],
                'updated': datetime.utcnow()
            })

            if not status:
                abort(500, 'event update failed')
        else:
            ev = Event(
                title=eventDetail['title'],
                description=eventDetail['description'],
                time=eventDetail['time'],
                location=eventDetail['location'],
                creator=creator,
                keywords=eventDetail['keywords'],
                created=datetime.utcnow())

            ev.save()

            # append the event into user created list
            creator.update(add_to_set__created=ev)

        return ev.to_json()


@api.route('/remove')
class EventsDelete(Resource):
    @auth.login_required
    def post(self):
        oid = request.args.get('oid')

        if not oid:
            abort(400, 'event object is required to remove event')

        try:
            ev = Event.objects(id=oid).first()
        except ValidationError:
            abort(400, 'invalid event object id, it must be a 12-byte'
                       ' input or a 24-character hex string')

        if ev is None:
            abort(400, 'could not locate the event from object id')

        ev.delete()

        return {"message": "event {} was deleted".format(oid)}


@api.route('/batch')
class EventsBatch(Resource):
    @auth.login_required
    def post(self):
        creator = g.user
        if creator is None:
            abort(500, 'user logged in but no user instance found')

        batchedEvents = request.get_json()

        if not batchedEvents or type(batchedEvents) is not list:
            abort(400, 'batched events have to be a list')

        count = 0

        for event in batchedEvents:
            eventDetail = processEventDetail(event)

            ev = Event(
                title=eventDetail['title'],
                description=eventDetail['description'],
                time=eventDetail['time'],
                location=eventDetail['location'],
                creator=creator,
                keywords=eventDetail['keywords'],
                created=datetime.utcnow())

            ev.save()

            creator.update(add_to_set__created=ev)

            count += 1

        return '{} events are created'.format(count)
