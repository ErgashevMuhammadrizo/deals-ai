from rest_framework import serializers
from . import models as m
class ProjectSerializer(serializers.ModelSerializer):
 def validate_status(self,value):
  if value in ('approved','active') and value!=getattr(self.instance,'status',None):
   raise serializers.ValidationError('Use approval and activation actions.')
  return value
 class Meta:
  model=m.Project
  fields='__all__'
  read_only_fields=['created_at','updated_at','approved_at']
class ProspectSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.Prospect; fields='__all__';read_only_fields=['created_at','updated_at']
class CampaignSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.Campaign;fields='__all__';read_only_fields=['created_at','updated_at']
class LeadSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.Lead;fields='__all__';read_only_fields=['created_at','updated_at']
class ConversationSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.Conversation; fields='__all__';read_only_fields=['created_at','updated_at']
class MessageSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.Message; fields='__all__';read_only_fields=['created_at','updated_at']
class KnowledgeSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.ProjectKnowledge;fields='__all__';read_only_fields=['created_at','updated_at','status','chunks_count','error','version']
 def validate_file(self,file):
  from pathlib import Path
  from .services.knowledge import ALLOWED
  if file.size>10*1024*1024: raise serializers.ValidationError('Maximum file size: 10MB')
  if Path(file.name).suffix.lower() not in ALLOWED: raise serializers.ValidationError('File extension not allowed')
  return file
class AIConfigSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.AIConfiguration;fields='__all__'
class PlaybookSerializer(serializers.ModelSerializer):
 class Meta:
  model=m.SalesPlaybook;fields='__all__'
