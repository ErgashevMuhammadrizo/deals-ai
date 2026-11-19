from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from . import models as m
from .services.ai import AIUnavailable, generate
from .views import admin_only


class ConversationForm(forms.Form):
    prospect = forms.ModelChoiceField(queryset=m.Prospect.objects.filter(opted_out=False))
    prospect.label_from_instance = lambda p: f"{p.project.name} · {p.company_name}"


@user_passes_test(admin_only)
def inbox(request, pk=None):
    form = ConversationForm(request.POST or None)
    if pk is None:
        if request.method == 'POST' and form.is_valid():
            prospect = form.cleaned_data['prospect']
            dialog = m.Conversation.objects.create(project=prospect.project, prospect=prospect)
            return redirect('inbox-detail', pk=dialog.pk)
        return render(request, 'inbox.html', {'form': form, 'dialogs': m.Conversation.objects.select_related('prospect','project').order_by('-updated_at')})
    dialog = get_object_or_404(m.Conversation, pk=pk)
    if request.method == 'POST':
        with transaction.atomic():
            dialog = m.Conversation.objects.select_for_update().get(pk=pk)
            action = request.POST.get('action')
            body = request.POST.get('message','').strip()
            if action == 'take':
                dialog.status = 'operator_active'
                dialog.assigned_operator = request.user
                dialog.handoffs.filter(resolved=False).update(operator=request.user)
            elif action == 'resume' and dialog.assigned_operator_id == request.user.pk:
                dialog.status = 'ai_active'
                dialog.assigned_operator = None
                dialog.handoffs.update(resolved=True)
            elif action == 'reply' and dialog.assigned_operator_id == request.user.pk and dialog.status == 'operator_active' and 0 < len(body) <= 5000:
                dialog.messages.create(sender_type='operator',content=body)
            elif action == 'customer' and dialog.channel == 'test' and not dialog.prospect.opted_out and 0 < len(body) <= 2000:
                dialog.messages.create(sender_type='customer',content=body)
                if dialog.status not in ('operator_active','handoff'):
                    try:
                        if any(word in body.casefold() for word in ('operator','оператор','inson bilan')):
                            raise AIUnavailable('Mijoz operator so‘radi.')
                        result = generate(dialog.project, body, dialog)
                        dialog.messages.create(sender_type='ai',content=result['answer'],ai_model=result['model'])
                        if result.get('handoff_recommended'):
                            dialog.status = 'handoff'
                            dialog.handoffs.create(reason='AI javobini tekshirish kerak', summary=body)
                        else:
                            dialog.status = 'waiting_customer'
                    except AIUnavailable as exc:
                        dialog.status = 'handoff'
                        dialog.handoffs.create(reason=str(exc),summary=body)
            else:
                messages.error(request, 'Bu amal hozir mavjud emas.')
                return redirect('inbox-detail', pk=pk)
            dialog.last_message_at = timezone.now()
            dialog.save()
            m.AuditLog.objects.create(user=request.user,project=dialog.project,action=action,entity='Conversation',entity_id=str(pk))
        return redirect('inbox-detail', pk=pk)
    return render(request,'inbox.html',{'dialog':dialog,'history':dialog.messages.order_by('pk')})


@user_passes_test(admin_only)
def import_prospects(request):
    import csv
    import io
    from django.core.exceptions import ValidationError

    projects = m.Project.objects.order_by('name')
    if request.method == 'POST':
        project = get_object_or_404(m.Project, pk=request.POST.get('project'))
        upload = request.FILES.get('file')
        try:
            if not upload or upload.size > 2 * 1024 * 1024:
                raise ValueError('2 MB gacha CSV fayl tanlang.')
            reader = csv.DictReader(io.StringIO(upload.read().decode('utf-8-sig')))
            if 'company_name' not in (reader.fieldnames or []):
                raise ValueError('company_name ustuni kerak.')
            allowed = {'company_name','instagram_username','website','public_contact','industry','location','description','notes'}
            with transaction.atomic():
                count = 0
                for count, row in enumerate(reader, 1):
                    if count > 2000:
                        raise ValueError('Bir importda 2000 qatorgacha ruxsat etiladi.')
                    prospect = m.Prospect(project=project, source='csv', **{key:(row.get(key) or '').strip() for key in allowed})
                    prospect.full_clean()
                    prospect.save()
                m.AuditLog.objects.create(project=project,user=request.user,action='csv_import',info={'count':count})
            messages.success(request,f'{count} ta mijoz import qilindi.')
            return redirect('prospect-import')
        except (ValueError, csv.Error, ValidationError) as exc:
            messages.error(request,str(exc))
    return render(request,'import.html',{'projects':projects})
