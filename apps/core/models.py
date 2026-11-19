from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator,MaxValueValidator

class Timestamp(models.Model):
 created_at=models.DateTimeField(auto_now_add=True,db_index=True)
 updated_at=models.DateTimeField(auto_now=True)
 class Meta: abstract=True

class Project(Timestamp):
 STATUS=[(s,s) for s in ('draft','processing','training','testing','approved','active','paused','archived')]
 name=models.CharField(max_length=180)
 slug=models.SlugField(unique=True)
 company_name=models.CharField(max_length=180,blank=True)
 description=models.TextField(blank=True)
 website=models.URLField(blank=True)
 industry=models.CharField(max_length=120,blank=True)
 country=models.CharField(max_length=100,default='Uzbekistan')
 language=models.CharField(max_length=2,choices=[('uz','UZ'),('ru','RU')],default='uz')
 timezone=models.CharField(max_length=64,default='Asia/Tashkent')
 contact_email=models.EmailField(blank=True)
 contact_phone=models.CharField(max_length=50,blank=True)
 status=models.CharField(max_length=24,choices=STATUS,default='draft',db_index=True)
 approved_at=models.DateTimeField(null=True,blank=True)
 def __str__(self): return self.name

class ProjectMember(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='members')
 user=models.ForeignKey('auth.User',on_delete=models.CASCADE)
 role=models.CharField(max_length=24,default='operator')
 class Meta: constraints=[models.UniqueConstraint(fields=['project','user'],name='unique_project_member')]

class ProjectKnowledge(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='documents')
 title=models.CharField(max_length=255)
 file=models.FileField(upload_to='knowledge/%Y/%m/',blank=True)
 source_text=models.TextField(blank=True)
 file_type=models.CharField(max_length=12,default='text')
 file_size=models.PositiveIntegerField(default=0)
 version=models.PositiveIntegerField(default=1)
 status=models.CharField(max_length=24,default='pending')
 chunks_count=models.PositiveIntegerField(default=0)
 error=models.TextField(blank=True)

class KnowledgeChunk(Timestamp):
 document=models.ForeignKey(ProjectKnowledge,on_delete=models.CASCADE,related_name='chunks')
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='chunks')
 position=models.PositiveIntegerField()
 content=models.TextField()
 class Meta: constraints=[models.UniqueConstraint(fields=['document','position'],name='unique_chunk_position')]

class AIConfiguration(Timestamp):
 project=models.OneToOneField(Project,on_delete=models.CASCADE,related_name='ai_config')
 name=models.CharField(max_length=100,default='DEALS AI')
 tone=models.CharField(max_length=50,default='professional')
 role=models.CharField(max_length=160,default='Sales assistant')
 instructions=models.TextField(blank=True)
 forbidden_statements=models.TextField(blank=True)
 max_response_length=models.PositiveIntegerField(default=700)
 daily_budget_usd=models.DecimalField(max_digits=9,decimal_places=2,default=1)
 temperature=models.FloatField(default=0.3)

class SalesPlaybook(Timestamp):
 project=models.OneToOneField(Project,on_delete=models.CASCADE,related_name='playbook')
 initial=models.TextField(blank=True)
 discovery=models.TextField(blank=True)
 qualification=models.TextField(blank=True)
 value_proposition=models.TextField(blank=True)
 objection_handling=models.TextField(blank=True)
 closing=models.TextField(blank=True)
 handoff=models.TextField(blank=True)

class AITrainingTest(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='training_tests')
 question=models.TextField()
 expected=models.TextField(blank=True)
 actual=models.TextField(blank=True)
 passed=models.BooleanField(default=False)
 reviewed=models.BooleanField(default=False)

class Prospect(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='prospects')
 company_name=models.CharField(max_length=190)
 instagram_username=models.CharField(max_length=100,blank=True)
 website=models.URLField(blank=True)
 public_contact=models.CharField(max_length=200,blank=True)
 industry=models.CharField(max_length=100,blank=True)
 location=models.CharField(max_length=120,blank=True)
 description=models.TextField(blank=True)
 source=models.CharField(max_length=120,default='manual')
 status=models.CharField(max_length=24,default='new')
 fit_score=models.PositiveSmallIntegerField(default=0,validators=[MaxValueValidator(100)])
 need_score=models.PositiveSmallIntegerField(default=0,validators=[MaxValueValidator(100)])
 qualification_score=models.PositiveSmallIntegerField(default=0,validators=[MaxValueValidator(100)])
 score_reason=models.TextField(blank=True)
 notes=models.TextField(blank=True)
 opted_out=models.BooleanField(default=False)

class Campaign(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='campaigns')
 name=models.CharField(max_length=180)
 target_industry=models.CharField(max_length=120,blank=True)
 target_location=models.CharField(max_length=120,blank=True)
 target_language=models.CharField(max_length=2,default='uz')
 daily_prospect_limit=models.PositiveIntegerField(default=50)
 daily_message_limit=models.PositiveIntegerField(default=0)
 start_date=models.DateField(null=True,blank=True)
 end_date=models.DateField(null=True,blank=True)
 status=models.CharField(max_length=24,default='draft')
 approval_required=models.BooleanField(default=True)

class CampaignActivity(Timestamp):
 campaign=models.ForeignKey(Campaign,on_delete=models.CASCADE,related_name='activities')
 prospect=models.ForeignKey(Prospect,on_delete=models.CASCADE)
 kind=models.CharField(max_length=32)
 class Meta: indexes=[models.Index(fields=['campaign','kind','created_at'])]

class Conversation(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='conversations')
 prospect=models.ForeignKey(Prospect,on_delete=models.CASCADE,related_name='conversations')
 channel=models.CharField(max_length=24,default='test')
 external_conversation_id=models.CharField(max_length=190,blank=True)
 status=models.CharField(max_length=24,default='new')
 stage=models.CharField(max_length=30,default='initial')
 assigned_operator=models.ForeignKey('auth.User',on_delete=models.SET_NULL,null=True,blank=True)
 last_message_at=models.DateTimeField(null=True,blank=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['project','channel','external_conversation_id'],condition=~models.Q(external_conversation_id=''),name='unique_external_conversation')]

class Message(Timestamp):
 conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='messages')
 sender_type=models.CharField(max_length=20,choices=[(x,x) for x in ('customer','ai','operator','system')])
 content=models.TextField()
 message_type=models.CharField(max_length=30,default='text')
 external_message_id=models.CharField(max_length=190,blank=True)
 ai_model=models.CharField(max_length=100,blank=True)
 token_usage=models.PositiveIntegerField(default=0)
 class Meta: constraints=[models.UniqueConstraint(fields=['conversation','external_message_id'],condition=~models.Q(external_message_id=''),name='unique_external_message')]

class Lead(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='leads')
 prospect=models.ForeignKey(Prospect,on_delete=models.CASCADE,related_name='leads')
 stage=models.CharField(max_length=24,default='new')
 budget=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True)
 expected_value=models.DecimalField(max_digits=14,decimal_places=2,null=True,blank=True)
 need=models.TextField(blank=True)
 priority=models.CharField(max_length=15,default='normal')
 source=models.CharField(max_length=80,default='manual')
 assigned_operator=models.ForeignKey('auth.User',on_delete=models.SET_NULL,null=True,blank=True)
 next_action=models.CharField(max_length=250,blank=True)
 notes=models.TextField(blank=True)

class Handoff(Timestamp):
 conversation=models.ForeignKey(Conversation,on_delete=models.CASCADE,related_name='handoffs')
 reason=models.TextField()
 summary=models.TextField(blank=True)
 operator=models.ForeignKey('auth.User',on_delete=models.SET_NULL,null=True,blank=True)
 resolved=models.BooleanField(default=False)

class IntegrationAccount(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='integrations')
 provider=models.CharField(max_length=30)
 status=models.CharField(max_length=30,default='disconnected')
 external_account_id=models.CharField(max_length=180,blank=True)
 # Secrets are not stored here. OAuth token vault must be configured before real connection.
 class Meta: constraints=[models.UniqueConstraint(fields=['project','provider'],name='unique_integration_provider')]

class WebhookEvent(Timestamp):
 provider=models.CharField(max_length=30)
 event_id=models.CharField(max_length=200)
 processed=models.BooleanField(default=False)
 raw_sha256=models.CharField(max_length=64,blank=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['provider','event_id'],name='unique_webhook_event')]

class AIUsage(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE,related_name='ai_usage')
 model=models.CharField(max_length=120)
 input_tokens=models.PositiveIntegerField(default=0)
 output_tokens=models.PositiveIntegerField(default=0)
 cost_usd=models.DecimalField(max_digits=10,decimal_places=6,default=0)
 elapsed_ms=models.PositiveIntegerField(default=0)

class AIResponseLog(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE)
 conversation=models.ForeignKey(Conversation,on_delete=models.SET_NULL,null=True,blank=True)
 prompt_version=models.CharField(max_length=50,default='v1')
 model=models.CharField(max_length=120)
 knowledge_ids=models.JSONField(default=list)
 quality_flags=models.JSONField(default=list)
 error=models.TextField(blank=True)

class AuditLog(models.Model):
 at=models.DateTimeField(auto_now_add=True,db_index=True)
 user=models.ForeignKey('auth.User',on_delete=models.SET_NULL,null=True,blank=True)
 project=models.ForeignKey(Project,on_delete=models.SET_NULL,null=True,blank=True)
 action=models.CharField(max_length=100)
 entity=models.CharField(max_length=80,blank=True)
 entity_id=models.CharField(max_length=80,blank=True)
 info=models.JSONField(default=dict)

class Notification(Timestamp):
 user=models.ForeignKey('auth.User',on_delete=models.CASCADE)
 title=models.CharField(max_length=200)
 text=models.TextField(blank=True)
 read=models.BooleanField(default=False)

class OptOutRecord(Timestamp):
 project=models.ForeignKey(Project,on_delete=models.CASCADE)
 contact_hash=models.CharField(max_length=64)
 reason=models.CharField(max_length=250,blank=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['project','contact_hash'],name='unique_optout')]


class ChunkVector(models.Model):
 chunk=models.OneToOneField(KnowledgeChunk,on_delete=models.CASCADE,related_name='vector')
 weights=models.JSONField(default=dict)
