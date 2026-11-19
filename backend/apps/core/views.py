import csv,hashlib,io
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
from django.utils import timezone
from rest_framework import viewsets,status
from rest_framework.decorators import action,api_view,permission_classes
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from .services.analytics import chart_data
from . import models as m
from . import serializers as s
from .services.ai import generate,AIUnavailable
from .services.knowledge import process_document,retrieve

def admin_only(user):return user.is_authenticated and user.is_active and user.is_superuser
class AdminLogin(LoginView):
 template_name='login.html'
 def form_valid(self,form):
  if not form.get_user().is_superuser:
   form.add_error(None,'Administrator access only')
   return self.form_invalid(form)
  response=super().form_valid(form)
  self.request.session.set_expiry(60*60*24*14 if self.request.POST.get('remember') else 0)
  return response

@login_required
@user_passes_test(admin_only)
def dashboard(request,section='dashboard'):
 stats={'projects':m.Project.objects.count(),'active':m.Project.objects.filter(status='active').count(),'prospects':m.Prospect.objects.count(),'leads':m.Lead.objects.count(),'conversations':m.Conversation.objects.count(),'campaigns':m.Campaign.objects.count(),'documents':m.ProjectKnowledge.objects.count(),'handoffs':m.Handoff.objects.filter(resolved=False).count()}
 routes={'projects':m.Project.objects.order_by('-created_at')[:30],'prospects':m.Prospect.objects.select_related('project').order_by('-created_at')[:30],'campaigns':m.Campaign.objects.select_related('project').order_by('-created_at')[:30],'leads':m.Lead.objects.select_related('project').order_by('-created_at')[:30],'conversations':m.Conversation.objects.select_related('project','prospect').order_by('-created_at')[:30],'knowledge':m.ProjectKnowledge.objects.select_related('project').order_by('-created_at')[:30],'audit':m.AuditLog.objects.order_by('-at')[:30]}
 allowed=['dashboard','projects','knowledge','training','testing','playbook','prospects','campaigns','conversations','leads','operators','analytics','integrations','settings','audit']
 if section not in allowed:
  from django.http import Http404
  raise Http404
 return render(request,'dashboard.html',{'charts':chart_data() if section in ('dashboard','analytics') else [],'section':section,'stats':stats,'rows':routes.get(section,[]),'projects':m.Project.objects.order_by('name'),'recent':m.AuditLog.objects.order_by('-at')[:7],'admin_model':{'projects':'project','prospects':'prospect','campaigns':'campaign','leads':'lead','knowledge':'projectknowledge','conversations':'conversation'}.get(section,'')})

class AuditMixin:
 def perform_create(self,serializer):
  obj=serializer.save()
  m.AuditLog.objects.create(user=self.request.user,project=obj if isinstance(obj,m.Project) else getattr(obj,'project',None),action='create',entity=obj.__class__.__name__,entity_id=str(obj.pk))
 def perform_update(self,serializer):
  obj=serializer.save()
  m.AuditLog.objects.create(user=self.request.user,project=obj if isinstance(obj,m.Project) else getattr(obj,'project',None),action='update',entity=obj.__class__.__name__,entity_id=str(obj.pk))
 def perform_destroy(self,obj):
  m.AuditLog.objects.create(user=self.request.user,project=obj if isinstance(obj,m.Project) else getattr(obj,'project',None),action='delete',entity=obj.__class__.__name__,entity_id=str(obj.pk))
  obj.delete()

class ProjectViewSet(AuditMixin,viewsets.ModelViewSet):
 queryset=m.Project.objects.all().order_by('-created_at');serializer_class=s.ProjectSerializer
 @action(detail=True,methods=['post'])
 def approve(self,request,pk=None):
  project=self.get_object()
  if project.status not in ('testing','approved') or not project.training_tests.filter(reviewed=True,passed=True).exists() or project.training_tests.exclude(reviewed=True,passed=True).exists():
   return Response({'error':'Reviewed and passing AI tests are required before approval'},status=400)
  project.status='approved';project.approved_at=timezone.now();project.save()
  m.AuditLog.objects.create(user=request.user,project=project,action='approve')
  return Response({'status':project.status})
 @action(detail=True,methods=['post'])
 def activate(self,request,pk=None):
  p=self.get_object()
  if p.status!='approved':return Response({'error':'Approve tested AI first'},status=400)
  p.status='active';p.save();m.AuditLog.objects.create(user=request.user,project=p,action='activate')
  return Response({'status':p.status})

class ProjectScopeMixin:
 def get_queryset(self):
  q=super().get_queryset()
  project=self.request.query_params.get('project')
  if project:
   if not project.isdecimal():raise ValidationError({'project':'Invalid project ID'})
   q=q.filter(project_id=int(project))
  return q
 def validate_cross_project(self,serializer):
  project=serializer.validated_data.get('project') or getattr(self.get_object(),'project',None)
  if not project:return
  for field in ('prospect','campaign'):
   related=serializer.validated_data.get(field,getattr(serializer.instance,field,None))
   if related and related.project_id!=project.pk:raise ValidationError({field:'Related object belongs to another project'})

class ProspectViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.Prospect.objects.all().order_by('-created_at');serializer_class=s.ProspectSerializer
 @action(detail=True,methods=['post'])
 def score(self,request,pk=None):
  p=self.get_object()
  # Deterministic evidence-based heuristic; not a claim of conversion probability.
  p.fit_score=min(100,20+int(bool(p.industry))*35+int(bool(p.description))*25+int(bool(p.website))*20)
  p.need_score=min(100,int(bool(p.description))*40+int(bool(p.notes))*30+int(bool(p.public_contact))*20)
  p.qualification_score=round((p.fit_score+p.need_score)/2)
  p.score_reason='Heuristic: industry, public web presence, description, notes and contact availability.'
  p.save();return Response({'fit':p.fit_score,'need':p.need_score,'qualification':p.qualification_score,'reason':p.score_reason})
 @action(detail=True,methods=['post'])
 def opt_out(self,request,pk=None):
  p=self.get_object();p.opted_out=True;p.save()
  contact=(p.public_contact or p.instagram_username or str(p.pk)).lower()
  m.OptOutRecord.objects.get_or_create(project=p.project,contact_hash=hashlib.sha256(contact.encode()).hexdigest())
  m.AuditLog.objects.create(user=request.user,project=p.project,action='opt_out',entity='Prospect',entity_id=str(p.id))
  return Response({'opted_out':True})

class CampaignViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.Campaign.objects.all().order_by('-created_at');serializer_class=s.CampaignSerializer
 @action(detail=True,methods=['post'])
 def pause(self,request,pk=None):
  c=self.get_object();c.status='paused';c.save();return Response({'status':'paused'})
 @action(detail=True,methods=['post'])
 def record_analysis(self,request,pk=None):
  with transaction.atomic():
   c=m.Campaign.objects.select_for_update().get(pk=self.get_object().pk)
   if c.status!='running':return Response({'error':'Campaign not running'},status=400)
   prospect=get_object_or_404(m.Prospect,pk=request.data.get('prospect'),project=c.project,opted_out=False)
   today=timezone.localdate()
   if c.activities.filter(kind='analysis',created_at__date=today).count()>=c.daily_prospect_limit:
    return Response({'error':'Daily analysis limit reached'},status=429)
   m.CampaignActivity.objects.create(campaign=c,prospect=prospect,kind='analysis')
  return Response({'status':'recorded'})

class LeadViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.Lead.objects.all().order_by('-created_at');serializer_class=s.LeadSerializer
 def perform_create(self,serializer):self.validate_cross_project(serializer);super().perform_create(serializer)
 def perform_update(self,serializer):self.validate_cross_project(serializer);super().perform_update(serializer)
class ConversationViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.Conversation.objects.all().order_by('-created_at');serializer_class=s.ConversationSerializer
 def perform_create(self,serializer):self.validate_cross_project(serializer);super().perform_create(serializer)
 def perform_update(self,serializer):self.validate_cross_project(serializer);super().perform_update(serializer)
 @action(detail=True,methods=['post'])
 def handoff(self,request,pk=None):
  c=self.get_object();c.status='handoff';c.save()
  obj=m.Handoff.objects.create(conversation=c,reason=str(request.data.get('reason','Human assistance requested'))[:2000],summary='\n'.join(f'{a.sender_type}: {a.content[:400]}' for a in c.messages.order_by('-created_at')[:12]))
  return Response({'handoff':obj.pk})
 @action(detail=True,methods=['post'])
 def take_over(self,request,pk=None):
  c=self.get_object();c.status='operator_active';c.assigned_operator=request.user;c.save()
  return Response({'status':c.status})
 @action(detail=True,methods=['post'])
 def reply(self,request,pk=None):
  c=self.get_object()
  if c.status!='operator_active' or c.assigned_operator_id!=request.user.pk:return Response({'error':'Take over this conversation first'},status=409)
  txt=str(request.data.get('content','')).strip()
  if not txt or len(txt)>5000:return Response({'error':'Content required (max 5000)'},status=400)
  # Local record only: no external delivery without official provider implementation.
  msg=m.Message.objects.create(conversation=c,sender_type='operator',content=txt)
  return Response({'id':msg.pk,'delivery':'local_only'})
class KnowledgeViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.ProjectKnowledge.objects.all().order_by('-created_at');serializer_class=s.KnowledgeSerializer
 def perform_create(self,serializer):
  super().perform_create(serializer)
  obj=serializer.instance
  process_document(obj.id)
  obj.refresh_from_db()
 @transaction.atomic
 def perform_update(self,serializer):
  obj=serializer.save(version=serializer.instance.version+1)
  process_document(obj.pk)
  obj.refresh_from_db()
  m.AuditLog.objects.create(user=self.request.user,project=obj.project,action='update',entity='ProjectKnowledge',entity_id=str(obj.pk))
 @action(detail=True,methods=['post'])
 def reprocess(self,request,pk=None):
  obj=self.get_object();process_document(obj.id);obj.refresh_from_db()
  return Response({'status':obj.status,'chunks':obj.chunks_count,'error':obj.error})

class AIConfigViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.AIConfiguration.objects.all();serializer_class=s.AIConfigSerializer
class PlaybookViewSet(ProjectScopeMixin,AuditMixin,viewsets.ModelViewSet):
 queryset=m.SalesPlaybook.objects.all();serializer_class=s.PlaybookSerializer

@api_view(['POST'])
def test_ai(request):
 project=get_object_or_404(m.Project,pk=request.data.get('project'))
 question=str(request.data.get('question','')).strip()
 if not question or len(question)>2000:return Response({'error':'Question required (max 2000)'},status=400)
 try:
  result=generate(project,question)
  test=m.AITrainingTest.objects.create(project=project,question=question,actual=result['answer'])
  return Response({**result,'test_id':test.pk})
 except AIUnavailable as exc:return Response({'error':str(exc),'handoff_recommended':True},status=503)

@api_view(['GET'])
def overview(request):
 project=request.query_params.get('project')
 data={}
 for name,model in [('projects',m.Project),('prospects',m.Prospect),('campaigns',m.Campaign),('conversations',m.Conversation),('leads',m.Lead),('documents',m.ProjectKnowledge)]:
  qs=model.objects.all()
  if project and name!='projects':qs=qs.filter(project_id=project)
  data[name]=qs.count()
 data['won']=m.Lead.objects.filter(stage='won',**({'project_id':project} if project else {})).count()
 data['conversion_rate']=round(data['won']*100/data['leads'],1) if data['leads'] else 0
 return Response(data)

@api_view(['GET'])
def export_prospects(request):
 response=HttpResponse(content_type='text/csv; charset=utf-8');response['Content-Disposition']='attachment; filename="prospects.csv"'
 response.write('\ufeff');w=csv.writer(response);w.writerow(['id','project','company','industry','status','score'])
 qs=m.Prospect.objects.all().select_related('project')
 if request.query_params.get('project'):qs=qs.filter(project_id=request.query_params['project'])
 for p in qs.iterator():w.writerow([p.pk,spreadsheet_text(p.project.name),spreadsheet_text(p.company_name),spreadsheet_text(p.industry),spreadsheet_text(p.status),p.qualification_score])
 return response

@api_view(['GET'])
def export_excel(request):
 from openpyxl import Workbook
 workbook=Workbook(write_only=True)
 sheet=workbook.create_sheet('Prospects')
 sheet.append(['ID','Project','Company','Industry','Status','Score'])
 for prospect in m.Prospect.objects.select_related('project').iterator():
  sheet.append([prospect.pk,*[spreadsheet_text(value) for value in (prospect.project.name,prospect.company_name,prospect.industry,prospect.status)],prospect.qualification_score])
 response=HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
 response['Content-Disposition']='attachment; filename="prospects.xlsx"'
 workbook.save(response)
 return response

def spreadsheet_text(value):
 return "'"+value if value.lstrip().startswith(('=','+','-','@')) else value
