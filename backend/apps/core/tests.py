from django.test import TestCase,Client,override_settings
from django.contrib.auth.models import User
from django.urls import reverse
from apps.core.models import Project,Prospect,Conversation,Message,ProjectKnowledge,KnowledgeChunk,AIConfiguration
from apps.core.services.knowledge import chunk_text,process_document,retrieve

class AuthTest(TestCase):
 def setUp(self):
  self.user=User.objects.create_user(username='regular',password='TestPassword123!')
  self.admin=User.objects.create_superuser(username='chief',email='chief@example.test',password='TestPassword123!')
 def test_guest_redirect(self):self.assertEqual(self.client.get('/').status_code,302)
 def test_non_admin_denied(self):
  self.client.force_login(self.user)
  self.assertNotEqual(self.client.get('/').status_code,200)
  self.assertEqual(self.client.get('/api/v1/projects/').status_code,403)
 def test_admin_access(self):
  self.client.force_login(self.admin)
  self.assertEqual(self.client.get('/').status_code,200)
  self.assertEqual(self.client.get('/api/v1/projects/').status_code,200)
 def test_csrf_api(self):
  c=Client(enforce_csrf_checks=True)
  c.force_login(self.admin)
  response=c.post('/api/v1/projects/',data='{"name":"ABC","slug":"abc"}',content_type='application/json')
  self.assertEqual(response.status_code,403)

class ProjectWorkflowTest(TestCase):
 def setUp(self):
  admin=User.objects.create_superuser(username='root',email='root@example.test',password='SecurePassword123!')
  self.client.force_login(admin)
  self.one=Project.objects.create(name='One',slug='one')
  self.two=Project.objects.create(name='Two',slug='two')
 def test_projects_isolated_knowledge(self):
  a=ProjectKnowledge.objects.create(project=self.one,title='Details',source_text='Our offer includes a catalog and price lists.')
  process_document(a.pk)
  self.assertTrue(retrieve(self.one.pk,'catalog'))
  self.assertEqual(retrieve(self.two.pk,'catalog'),[])
 def test_project_api_crud(self):
  r=self.client.post('/api/v1/projects/',{'name':'Three','slug':'three'},content_type='application/json')
  self.assertEqual(r.status_code,201)
  self.assertTrue(Project.objects.filter(slug='three').exists())
 def test_cross_project_lead_rejected(self):
  p=Prospect.objects.create(project=self.one,company_name='Shop')
  r=self.client.post('/api/v1/leads/',{'project':self.two.pk,'prospect':p.pk},content_type='application/json')
  self.assertEqual(r.status_code,400)
 def test_opt_out(self):
  p=Prospect.objects.create(project=self.one,company_name='Opt out',public_contact='@example')
  r=self.client.post(f'/api/v1/prospects/{p.pk}/opt_out/')
  self.assertEqual(r.status_code,200)
  p.refresh_from_db();self.assertTrue(p.opted_out)
 def test_approval_guard(self):
  self.one.status='testing';self.one.save()
  r=self.client.post(f'/api/v1/projects/{self.one.pk}/approve/')
  self.assertEqual(r.status_code,400)
 def test_handoff(self):
  p=Prospect.objects.create(project=self.one,company_name='Buyer')
  c=Conversation.objects.create(project=self.one,prospect=p)
  r=self.client.post(f'/api/v1/conversations/{c.pk}/handoff/',{'reason':'human request'},content_type='application/json')
  self.assertEqual(r.status_code,200)
  c.refresh_from_db();self.assertEqual(c.status,'handoff')
 def test_no_fake_ai_without_key(self):
  AIConfiguration.objects.create(project=self.one)
  with override_settings():
   import os
   old=os.environ.pop('GEMINI_API_KEY',None)
   try:r=self.client.post('/api/v1/ai/test/',{'project':self.one.pk,'question':'Price?'},content_type='application/json')
   finally:
    if old is not None:os.environ['GEMINI_API_KEY']=old
  self.assertEqual(r.status_code,503)
 def test_scoring(self):
  p=Prospect.objects.create(project=self.one,company_name='Shop',industry='retail',website='https://example.com')
  r=self.client.post(f'/api/v1/prospects/{p.pk}/score/')
  self.assertEqual(r.status_code,200)
  self.assertLessEqual(r.json()['qualification'],100)
 def test_empty_analytics(self):
  result=self.client.get('/api/v1/analytics/overview/').json()
  self.assertEqual(result['conversion_rate'],0)

class KnowledgeTest(TestCase):
 def test_chunking(self):
  self.assertEqual(chunk_text(''),[])
  self.assertEqual(len(chunk_text('Hello')),1)
  self.assertGreater(len(chunk_text('abc '*1200)),1)
