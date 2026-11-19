from django.contrib import admin
from . import models as m
for cls in (m.ProjectMember,m.ProjectKnowledge,m.KnowledgeChunk,m.AIConfiguration,m.SalesPlaybook,m.AITrainingTest,m.Prospect,m.Campaign,m.CampaignActivity,m.Conversation,m.Message,m.Lead,m.Handoff,m.IntegrationAccount,m.WebhookEvent,m.AIUsage,m.AIResponseLog,m.AuditLog,m.Notification,m.OptOutRecord):
 admin.site.register(cls)
admin.site.site_header='DEALS AI — System Administration'

@admin.register(m.Project)
class ProjectAdmin(admin.ModelAdmin):
 readonly_fields = ('approved_at',)
 def get_form(self,request,obj=None,**kwargs):
  form=super().get_form(request,obj,**kwargs)
  form.base_fields['status'].choices=[(key,label) for key,label in m.Project.STATUS if key not in ('approved','active') or key==getattr(obj,'status',None)]
  return form

admin.site.unregister(m.AITrainingTest)

@admin.register(m.AITrainingTest)
class TestReviewAdmin(admin.ModelAdmin):
 list_display=('project','question','reviewed','passed')
 list_filter=('project','reviewed','passed')
 actions=('run_selected','accept_selected','reject_selected')
 readonly_fields=('actual','reviewed','passed')

 @admin.action(description='Gemini yordamida tanlangan savollarni sinash (5 tagacha)')
 def run_selected(self,request,queryset):
  from .services.ai import AIUnavailable,generate
  if queryset.count()>5:
   self.message_user(request,'Bir martada 5 tagacha sinovni tanlang.',level='error')
   return
  for case in queryset.select_related('project'):
   try:
    answer=generate(case.project,case.question)['answer']
   except AIUnavailable as exc:
    self.message_user(request,str(exc),level='error')
    return
   case.actual=answer
   case.passed=case.reviewed=False
   case.save()

 @admin.action(description='Ko‘rib chiqilgan javoblarni qabul qilish')
 def accept_selected(self,request,queryset):
  queryset.exclude(actual='').update(reviewed=True,passed=True)

 @admin.action(description='Ko‘rib chiqilgan javoblarni rad etish')
 def reject_selected(self,request,queryset):
  queryset.exclude(actual='').update(reviewed=True,passed=False)
