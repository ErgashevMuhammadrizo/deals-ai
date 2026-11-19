"""Helpers for future official Meta webhook integration."""
import hashlib,hmac
def validate_signature(payload:bytes,header:str,app_secret:str)->bool:
 if not app_secret or not header.startswith('sha256='):return False
 expected=hmac.new(app_secret.encode(),payload,hashlib.sha256).hexdigest()
 return hmac.compare_digest(header[7:],expected)

import json
import os
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from apps.core.models import WebhookEvent


@csrf_exempt
@require_http_methods(['GET','POST'])
def webhook(request):
 if request.method=='GET':
  token=os.getenv('META_WEBHOOK_VERIFY_TOKEN')
  if token and request.GET.get('hub.mode')=='subscribe' and hmac.compare_digest(token,request.GET.get('hub.verify_token','')):
   return HttpResponse(request.GET.get('hub.challenge',''),content_type='text/plain')
  return HttpResponse(status=403)
 payload=request.body
 if not validate_signature(payload,request.headers.get('X-Hub-Signature-256',''),os.getenv('META_APP_SECRET','')):
  return HttpResponse(status=403)
 try:
  body=json.loads(payload)
  for entry in body['entry']:
   for event in entry.get('messaging',[]):
    mid=event.get('message',{}).get('mid')
    if mid:
     key=hashlib.sha256(f"{entry['id']}:{mid}".encode()).hexdigest()
     WebhookEvent.objects.get_or_create(provider='instagram',event_id=key,defaults={'raw_sha256':hashlib.sha256(payload).hexdigest()})
 except (KeyError,ValueError,TypeError,AttributeError):
  return HttpResponse(status=400)
 return HttpResponse(status=200)
