from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk
from django.conf import settings
from django.core.management.base import BaseCommand

from conduit.apps.articles.models import Article


class Command(BaseCommand):
    help = "My shiny new management command."

    def handle(self, *args, **options):
        self.recreate_index()
        self.push_db_to_indx()

    def recreate_index(self):
        indices_client = IndicesClient(client=settings.ES_CLIENT)
        index_name = Article._meta.es_index_name

        if indices_client.exists(index_name):
            indices_client.delete(index=index_name)

        indices_client.create(index=index_name)
        indices_client.put_mapping(
            doc_type=Article._meta.es_type_name,
            body=Article._meta.es_mapping,
            index=index_name
        )

    def push_db_to_indx(self):
        data = [
            self.convert_for_bulk(s, 'create') for s in Article.objects.all()
        ]
        print(data)
        bulk(client=settings.ES_CLIENT, actions=data, stats_only=True)

    def convert_for_bulk(self, django_obj, action=None):
        data = django_obj.es_repr()
        metadata = {
            '_op_type': action,
            "_index": django_obj._meta.es_index_name,
            "_type": django_obj._meta.es_type_name,
        }
        data.update(**metadata)
        return data
