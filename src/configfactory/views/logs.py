from django.views.generic import DetailView
from django_filters.views import FilterView

from configfactory.filters import LogEntryFilterSet
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import LogEntry


class LogEntryListView(SuperuserRequiredMixin, FilterView):

    template_name = 'logs/list.html'

    filterset_class = LogEntryFilterSet

    queryset = LogEntry.objects.select_related('user', 'content_type')

    context_object_name = 'logs'

    paginate_by = 1


class LogEntryDetailView(SuperuserRequiredMixin, DetailView):

    template_name = 'logs/detail.html'

    queryset = LogEntry.objects.all()

    context_object_name = 'log'
