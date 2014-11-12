from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from djblets.db.fields import JSONField
from multiselectfield import MultiSelectField

from reviewboard.notifications.managers import WebHookTargetManager
from reviewboard.scmtools.models import Repository
from reviewboard.site.models import LocalSite


@python_2_unicode_compatible
class WebHookTarget(models.Model):
    """A target for a webhook.

    A webhook target is a URL which will receive a POST request when the
    corresponding event occurs.
    """
    ALL_EVENTS = '*'

    EVENT_CHOICES = (
        (ALL_EVENTS, _('All events')),
        ('review_request_closed', _('Review request closed')),
        ('review_request_published', _('Review request published')),
        ('review_request_reopened', _('Review request reopened')),
        ('review_published', _('Review published')),
        ('reply_published', _('Reply published')),
    )

    ENCODING_JSON = 'application/json'
    ENCODING_XML = 'application/xml'
    ENCODING_FORM_DATA = 'application/x-www-form-urlencoded'

    ENCODINGS = (
        (ENCODING_JSON, _('JSON')),
        (ENCODING_XML, _('XML')),
        (ENCODING_FORM_DATA, _('Form Data')),
    )

    APPLY_TO_ALL = 'A'
    APPLY_TO_NO_REPOS = 'N'
    APPLY_TO_SELECTED_REPOS = 'S'

    APPLY_TO_CHOICES = (
        (APPLY_TO_ALL, _('All review requests')),
        (APPLY_TO_SELECTED_REPOS,
         _('Only review requests on selected repositories')),
        (APPLY_TO_NO_REPOS,
         _('Only review requests not associated with a repository (file '
           'attachments only)')),
    )

    # Standard information
    enabled = models.BooleanField(default=True)
    events = MultiSelectField(
        _('events'),
        choices=EVENT_CHOICES,
        help_text=_('Select any or all events that should trigger this '
                    'Webhook.'))

    url = models.URLField(
        'URL',
        help_text=_('When the event is triggered, HTTP requests will be '
                    'made against this URL.'))

    encoding = models.CharField(
        _('encoding'),
        choices=ENCODINGS,
        default=ENCODING_JSON,
        max_length=40,
        help_text=_('Payload contents will be encoded in this format.'))

    # Custom content
    use_custom_content = models.BooleanField(
        _('use custom payload content'),
        default=False)

    custom_content = models.TextField(
        _('custom content'),
        blank=True,
        null=True,
        help_text=_('You can override what is sent to the URL above. If '
                    'left blank, the default payload will be sent.'))

    # HMAC payload signing
    secret = models.CharField(
        _('HMAC secret'),
        max_length=128, blank=True,
        help_text=_('If specified, the HMAC digest for the Webhook payload '
                    'will be signed with the given secret.'))

    # Apply to
    apply_to = models.CharField(
        _('apply to'),
        max_length=1,
        blank=False,
        default=APPLY_TO_ALL,
        choices=APPLY_TO_CHOICES)

    repositories = models.ManyToManyField(
        Repository,
        blank=True,
        null=True,
        related_name='webhooks',
        help_text=_('If set, this Webhook will be limited to these '
                    'repositories.'))

    local_site = models.ForeignKey(
        LocalSite,
        blank=True,
        null=True,
        related_name='webhooks',
        help_text=_('If set, this Webhook will be limited to this site.'))

    extra_data = JSONField(
        null=True,
        help_text=_('Extra JSON data that can be tied to this Webhook '
                    'registration. It will not be sent with the Webhook '
                    'request.'))

    objects = WebHookTargetManager()

    def __str__(self):
        return 'Webhook for events %s, url %s' % (','.join(self.events),
                                                  self.url)

    class Meta:
        verbose_name = _('webhook')
