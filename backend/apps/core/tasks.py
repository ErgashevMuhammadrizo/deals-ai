from celery import shared_task
from apps.core.services.knowledge import process_document
@shared_task(bind=True,max_retries=2,default_retry_delay=30)
def process_knowledge(self,document_id):
 return {'document_id':process_document(document_id).id}
