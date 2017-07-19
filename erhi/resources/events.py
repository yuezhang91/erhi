from flask import request
from flask_restplus import Namespace, Resource

from datetime import datetime

from erhi.models import Event

api = Namespace('events', description='')

EVENTS_PER_PAGE = 15


@api.route('/')
class Events(Resource):
    def get(self):
        page = int(request.args.get('page') or 1)

        Event.objects().delete()
        for i in range(20):
            point = {
                'type': 'Point',
                'coordinates': [i, i]}
            ev = Event(
                title='event {}'.format(i),
                description='whatever {}'.format(i),
                time=datetime.now(),
                location=point)
            ev.save()

        events = Event.objects.paginate(page=page, per_page=EVENTS_PER_PAGE)

        return [event.to_json() for event in events.items]
