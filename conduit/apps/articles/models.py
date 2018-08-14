from django.db import models
import django.db.models.options as options

from conduit.apps.core.models import TimestampedModel

options.DEFAULT_NAMES = options.DEFAULT_NAMES + (
    'es_index_name', 'es_type_name', 'es_mapping'
)


class Article(TimestampedModel):
    slug = models.SlugField(db_index=True, max_length=255, unique=True)
    title = models.CharField(db_index=True, max_length=255)

    description = models.TextField()
    body = models.TextField()

    # Every article must have an author. This will answer questions like "Who
    # gets credit for writing this article?" and "Who can edit this article?".
    # Unlike the `User` <-> `Profile` relationship, this is a simple foreign
    # key (or one-to-many) relationship. In this case, one `Profile` can have
    # many `Article`s.
    author = models.ForeignKey(
        'profiles.Profile', on_delete=models.CASCADE, related_name='articles'
    )

    tags = models.ManyToManyField(
        'articles.Tag', related_name='articles'
    )

    def __str__(self):
        return self.title

    class Meta:
        es_index_name = 'conduit'
        es_type_name = 'article'
        es_mapping = {
            'properties': {
                'slug': {
                    'type': 'keyword',
                },
                'title': {
                    'type': 'string',
                    'analyzer': 'simple',
                },
                'description': {
                    'type': 'text',
                    'analyzer': 'simple',
                },
                'body': {
                    'type': 'text',
                    'analyzer': 'simple',
                },
                'tagList': {
                    'type': 'string',
                },
                'createdAt': {
                    'type': 'date',
                },
                'updatedAt': {
                    'type': 'date',
                },
            }
        }

    def es_repr(self):
        data = {}
        mapping = self._meta.es_mapping
        data['_id'] = self.pk
        for field_name in mapping['properties'].keys():
            data[field_name] = self.field_es_repr(field_name)
        return data

    def field_es_repr(self, field_name):
        config = self._meta.es_mapping['properties'][field_name]

        if hasattr(self, 'get_es_%s' % field_name):
            field_es_value = getattr(self, 'get_es_%s' % field_name)()
        else:
            if config['type'] == 'object':
                related_object = getattr(self, field_name)
                field_es_value = {}
                field_es_value['_id'] = related_object.pk
                for prop in config['properties'].keys():
                    field_es_value[prop] = getattr(related_object, prop)
            else:
                field_es_value = getattr(self, field_name)
        return field_es_value

    def get_es_createdAt(self):
        return self.created_at

    def get_es_updatedAt(self):
        return self.updated_at

    def get_es_tagList(self):
        return [x.tag for x in self.tags.all()]


class Comment(TimestampedModel):
    body = models.TextField()

    article = models.ForeignKey(
        'articles.Article', related_name='comments', on_delete=models.CASCADE
    )

    author = models.ForeignKey(
        'profiles.Profile', related_name='comments', on_delete=models.CASCADE
    )


class Tag(TimestampedModel):
    tag = models.CharField(max_length=255)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return self.tag
