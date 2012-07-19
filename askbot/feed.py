"""
#-------------------------------------------------------------------------------
# Name:        Syndication feed class for subscription
# Purpose:
#
# Author:      Mike
#
# Created:     29/01/2009
# Copyright:   (c) CNPROG.COM 2009
# Licence:     GPL V2
#-------------------------------------------------------------------------------
"""
#!/usr/bin/env python
#encoding:utf-8
import itertools

from django.contrib.syndication.views import Feed
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist

from askbot.models import Post
from askbot.conf import settings as askbot_settings
from django.utils import translation
from django.contrib.sites.models import Site

class RssIndividualQuestionFeed(Feed):
    """rss feed class for particular questions
    """

    def title(self):
        return askbot_settings.APP_TITLE + _(' - ') + \
                _('Individual question feed')

    def feed_copyright(self):
        return askbot_settings.APP_COPYRIGHT

    def description(self):
        return askbot_settings.APP_DESCRIPTION

    def get_object(self, request, question_id):
        return Post.objects.get_questions().get(id=question_id)

    def item_link(self, item):
        """get full url to the item
        """
        return askbot_settings.APP_URL + item.get_absolute_url()

    def link(self):
        return askbot_settings.APP_URL

    def item_pubdate(self, item):
        """get date of creation for the item
        """
        return item.added_at

    def items(self, item):
        """get content items for the feed
        ordered as: question, question comments,
        then for each answer - the answer itself, then
        answer comments
        """
        chain_elements = list()
        chain_elements.append([item,])
        chain_elements.append(
            Post.objects.get_comments().filter(parent=item)
        )

        answers = Post.objects.get_answers().filter(thread = item.thread)
        for answer in answers:
            chain_elements.append([answer,])
            chain_elements.append(
                Post.objects.get_comments().filter(parent=answer)
            )

        return itertools.chain(*chain_elements)

    def item_title(self, item):
        """returns the title for the item
        """
        title = item
        if item.post_type == "question":
            self.title = item
        elif item.post_type == "answer":
            title = "Answer by %s for %s " % (item.author, self.title)
        elif item.post_type == "comment":
            title = "Comment by %s for %s" % (item.author, self.title)
        return title

    def item_description(self, item):
        """returns the description for the item
        """
        return item.text


class RssLastestQuestionsFeed(Feed):
    """rss feed class for the latest questions
    """

    def title(self):
        return askbot_settings.APP_TITLE + _(' - ') + \
                _('Individual question feed')

    def feed_copyright(self):
        return askbot_settings.APP_COPYRIGHT

    def description(self):
        return askbot_settings.APP_DESCRIPTION

    def item_link(self, item):
        """get full url to the item
        """
        return askbot_settings.APP_URL + item.get_absolute_url()

    def link(self):
        return askbot_settings.APP_URL

    def item_author_name(self, item):
        """get name of author
        """
        return item.author.username

    def item_author_link(self, item):
        """get url of the author's profile
        """
        return askbot_settings.APP_URL + item.author.get_profile_url()

    def item_pubdate(self, item):
        """get date of creation for the item
        """
        return item.added_at

    def item_guid(self, item):
        """returns url without the slug
        because the slug can change
        """
        return askbot_settings.APP_URL + item.get_absolute_url(no_slug = True)

    def item_description(self, item):
        """returns the description for the item
        """
        return item.text

    def items(self, item):
        """get questions for the feed
        """
        #initial filtering
        language_code = translation.get_language()
        site = Site.objects.get_current()
        qs = Post.objects.get_questions().filter(thread__site=site, 
                                                 thread__language_code=language_code, 
                                                 deleted=False)

        return qs.order_by('-thread__last_activity_at')[:30]



def main():
    """main function for use as a script
    """
    pass

if __name__ == '__main__':
    main()
