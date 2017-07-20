from flask import request, abort
from flask_restplus import Namespace, Resource

from datetime import datetime

from erhi.models import Event

api = Namespace('events', description='')

EVENTS_PER_PAGE = 15


@api.route('/')
class Events(Resource):
    def get(self):
        page = int(request.args.get('page') or 1)

        events = Event.objects.paginate(page=page, per_page=EVENTS_PER_PAGE)

        return [event.to_json() for event in events.items]

    def post(self):
        data = request.get_json()

        title = data.get('title')
        description = data.get('description')
        creator = data.get('creator')
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

        oid = data.get('oid')
        # if valid oid provided, do update instead of creating
        if oid:
            ev = Event.objects(id=oid).first()
            if not ev:
                abort(400, 'invalid object id provided')
            status = ev.update(**{
                'title': title,
                'description': description,
                'time': time,
                'location': location,
                'creator': creator,
                'keywords': keywords,
                'updated': datetime.utcnow()
            })

            if not status:
                abort(500, 'event update failed')
        else:
            ev = Event(
                title=title,
                description=description,
                time=time,
                location=location,
                creator=creator,
                keywords=keywords,
                created=datetime.utcnow())

            ev.save()

        return ev.to_json()
