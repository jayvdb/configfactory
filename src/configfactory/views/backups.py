from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import DeleteView, DetailView, ListView, TemplateView
from django.views.generic.base import TemplateResponseMixin
from django.views.generic.edit import FormMixin, ProcessFormView

from configfactory.forms.backup import BackupImportForm
from configfactory.mixins import SuperuserRequiredMixin
from configfactory.models import Backup
from configfactory.services.backups import create_backup, load_backup


class BackupListView(LoginRequiredMixin, ListView):

    template_name = 'backups/list.html'

    queryset = Backup.objects.select_related('user')

    context_object_name = 'backups'

    paginate_by = 25


class BackupCreateView(LoginRequiredMixin, TemplateView):

    template_name = 'backups/create.html'

    def post(self, request):

        create_backup(user=request.user, comment='User backup')

        messages.success(request, _('Backup successfully created.'))

        return redirect(to=reverse('backups'))


class BackupLoadView(SuperuserRequiredMixin, DetailView):

    template_name = 'backups/load.html'

    queryset = Backup.objects.select_related('user')

    def post(self, request, **kwargs):

        backup = self.get_object()

        load_backup(backup)

        messages.success(request, _('Backup `%s` successfully loaded.') % backup)

        return redirect(to=reverse('backups'))


class BackupExportView(SuperuserRequiredMixin, View):

    def get(self, request, pk):

        backup = get_object_or_404(Backup, pk=pk)

        with backup.data_file.open() as fp:
            response = HttpResponse(fp.read(), content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename={backup.data_file.name}'

        return response


class BackupImportView(SuperuserRequiredMixin,
                       TemplateResponseMixin,
                       FormMixin,
                       ProcessFormView):

    template_name = 'backups/import.html'

    form_class = BackupImportForm

    success_url = reverse_lazy('backups')

    def form_valid(self, form):

        response = super().form_valid(form)

        data_file = form.cleaned_data['file']

        backup = Backup()
        backup.data_file = data_file
        backup.user = self.request.user
        backup.comment = data_file.name
        backup.save()

        load_backup(backup, user=self.request.user)

        messages.success(self.request, _('Backup `%s` successfully imported.') % 'file')

        return response


class BackupDeleteView(SuperuserRequiredMixin, DeleteView):

    template_name = 'backups/delete.html'

    queryset = Backup.objects.select_related('user')

    success_url = reverse_lazy('backups')

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        backup = self.object
        messages.success(request, _('Backup `%s` successfully deleted.') % backup)
        return response
