from flask import abort, g, request
from flask_restplus import Namespace, Resource, reqparse, fields
from mongoengine.errors import ValidationError

from datetime import datetime

from erhi.models import auth, Event, User

api = Namespace('events', description='')

# argument parsing
parser = reqparse.RequestParser()
parser.add_argument('geo', type=str, required=True,
                    help='geo location in format of \'long,lat\'')
parser.add_argument('dis', type=int, help='query events radius (miles)')
parser.add_argument('page', type=int, help='events page number')


class UserField(fields.Raw):
    def format(self, obj):
        if isinstance(obj, User) and hasattr(obj, 'id'):
            return str(obj.id)
        # TODO: errors or logs here
        return None


event_fields = api.model('Event', {
    'id': fields.String,
    'title': fields.String,
    'description': fields.String,
    'time': fields.DateTime(dt_format='rfc822'),
    'location': fields.Raw,
    # Non-nested field for creator to prevent infinite loop
    'creator': UserField,
    'keywords': fields.List(fields.String),
    'created_on': fields.DateTime(dt_format='rfc822', attribute='created'),
    'updated_on': fields.DateTime(dt_format='rfc822', attribute='updated')
})


EVENTS_PER_PAGE = 15
# miles / 3963.2 applied for geo_within
MONGO_RADIUS_CONSTANT = 3963.2
DEFAULT_EVENT_RADIUS = 100 / MONGO_RADIUS_CONSTANT


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
    @api.marshal_with(event_fields)
    @api.expect(parser)
    def get(self):
        args = parser.parse_args()
        page = args['page'] or 1
        # sanity check for geo
        geo = args['geo']
        radius = args['dis'] / MONGO_RADIUS_CONSTANT or DEFAULT_EVENT_RADIUS

        longitude, latitude = [float(e) for e in geo.split(',')]

        events = Event \
            .objects(location__geo_within_sphere=[(longitude, latitude),
                     radius]) \
            .order_by('time') \
            .paginate(page=page, per_page=EVENTS_PER_PAGE)

        # return [json.loads(event.to_json()) for event in events.items]
        return events.items

    # don't use validation here for api, because we expect epoch time
    # from client, but to use decorator marshal_with we have to specify
    # DateTime field for time
    @auth.login_required
    @api.expect(event_fields)
    def post(self):
        creator = g.user
        if creator is None:
            abort(500, 'user logged in but no user instance found')

        data = request.get_json()

        eventDetail = processEventDetail(data)

        id = data.get('id')
        # if valid id provided, do update instead of creating
        if id:
            try:
                ev = Event.objects(id=id).first()
            except ValidationError:
                abort(400, 'invalid event object id, it must be a 12-byte'
                           ' input or a 24-character hex string')

            if ev is None:
                abort(400, 'can not locate the event from object id')
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
    @api.expect(event_fields)
    def post(self):
        data = request.get_json()
        id = data.get('id')

        if not id:
            abort(400, 'event object is required to remove event')

        try:
            ev = Event.objects(id=id).first()
        except ValidationError:
            abort(400, 'invalid event object id, it must be a 12-byte'
                       ' input or a 24-character hex string')

        if ev is None:
            abort(400, 'can not locate the event from object id')

        ev.delete()

        return {"message": "event {} was deleted".format(id)}


@api.route('/batch')
class EventsBatch(Resource):
    # we want to be able to insert array of events
    # don't use validation here for api
    @auth.login_required
    @api.expect(event_fields)
    def post(self):
        creator = g.user
        if creator is None:
            abort(500, 'user logged in but no user instance found')

        batchedEvents = request.get_json()

        if not batchedEvents or type(batchedEvents) is not list:
            abort(400, 'batched events have to be a list of events')

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
