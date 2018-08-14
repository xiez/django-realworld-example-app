from django.core.management.base import BaseCommand
from model_mommy import mommy

from conduit.apps.articles.models import Article
from conduit.apps.authentication.models import User

class Command(BaseCommand):
    help = "My shiny new management command."

    # def add_arguments(self, parser):
    #     parser.add_argument('sample', nargs='+')

    def handle(self, *args, **options):
        # self.clear()
        # self.make_articles()
        self.make_users()

    def make_users(self):
        for i in range(10):
            mommy.make(User,
                       email='test-%s@test.com' % i,
                       username='test-%s' % i,
                       password='12345678')

    # def make_articles(self):
    #     for i in range(10):
    #         article = mommy.make(Article, )
    #     pass

    # def clear(self):
    #     Article.objects.all().delete()
