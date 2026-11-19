"""Bounded document extraction and project-scoped sparse vector retrieval."""
import csv,io,re
from pathlib import Path
from .vectors import embed,similarity
from apps.core.models import ChunkVector
from django.db import transaction
from apps.core.models import KnowledgeChunk,ProjectKnowledge
ALLOWED={'.txt','.md','.csv','.pdf','.docx','.xlsx'}
def extract_document(doc:ProjectKnowledge)->str:
 if doc.source_text: return doc.source_text[:250000]
 if not doc.file: return ''
 ext=Path(doc.file.name).suffix.lower()
 if ext not in ALLOWED: raise ValueError('Unsupported file type')
 with doc.file.open('rb') as f: raw=f.read(10*1024*1024+1)
 if len(raw)>10*1024*1024: raise ValueError('File too large')
 if ext in ('.xlsx','.docx'):
  from zipfile import ZipFile
  with ZipFile(io.BytesIO(raw)) as archive:
   entries=archive.infolist()
   required='word/document.xml' if ext=='.docx' else 'xl/workbook.xml'
   if required not in archive.namelist() or len(entries)>3000 or sum(entry.file_size for entry in entries)>48*1024*1024:
    raise ValueError('Invalid or oversized Office document')
 if ext=='.pdf' and not raw.startswith(b'%PDF-'):raise ValueError('Invalid PDF header')
 if ext in ('.txt','.md','.csv') and b'\x00' in raw:raise ValueError('Binary data in a text file')
 if ext in ('.txt','.md'): return raw.decode('utf-8-sig')[:250000]
 if ext=='.csv': return '\n'.join(' | '.join(row) for row in csv.reader(io.StringIO(raw.decode('utf-8-sig'))))[:250000]
 if ext=='.pdf':
  from pypdf import PdfReader
  pdf=PdfReader(io.BytesIO(raw),strict=True)
  if len(pdf.pages)>100: raise ValueError('Too many pages')
  return '\n'.join((page.extract_text() or '') for page in pdf.pages)[:250000]
 if ext=='.docx':
  from docx import Document
  return '\n'.join(p.text for p in Document(io.BytesIO(raw)).paragraphs)[:250000]
 if ext=='.xlsx':
  from openpyxl import load_workbook
  wb=load_workbook(io.BytesIO(raw),read_only=True,data_only=True,keep_links=False)
  try:
   if len(wb.sheetnames)>20: raise ValueError('Too many sheets')
   return '\n'.join(' | '.join(str(c)[:400] if c is not None else '' for c in row) for sh in wb for row in sh.iter_rows(max_row=2000,max_col=30,values_only=True))[:250000]
  finally: wb.close()
 return ''

def chunk_text(text:str,size:int=1100,overlap:int=150)->list[str]:
 text=re.sub(r'\s+',' ',text).strip()
 if not text:return []
 chunks=[]
 for i in range(0,len(text),size-overlap):
  part=text[i:i+size]
  if part: chunks.append(part)
  if i+size>=len(text):break
 return chunks[:300]

@transaction.atomic
def process_document(doc_id:int):
 doc=ProjectKnowledge.objects.select_for_update().get(pk=doc_id)
 doc.status='processing';doc.error='';doc.save(update_fields=['status','error','updated_at'])
 try:
  doc.file_type=Path(doc.file.name).suffix.lower().lstrip('.') if doc.file else 'text'
  doc.file_size=doc.file.size if doc.file else len(doc.source_text.encode())
  text=extract_document(doc)
  pieces=chunk_text(text)
  if not pieces: raise ValueError('Document is empty or text is not extractable')
  doc.chunks.all().delete()
  KnowledgeChunk.objects.bulk_create([KnowledgeChunk(project_id=doc.project_id,document=doc,position=i,content=part) for i,part in enumerate(pieces)])
  ChunkVector.objects.bulk_create([ChunkVector(chunk=c,weights=embed(c.content)) for c in doc.chunks.all()])
  doc.chunks_count=len(pieces);doc.status='ready';doc.error=''
 except Exception as exc:
  doc.chunks_count=0;doc.status='failed';doc.error=str(exc)[:500]
 doc.save(update_fields=['status','chunks_count','error','file_type','file_size','updated_at'])
 return doc

def retrieve(project_id:int,question:str,limit:int=5):
 words=set(re.findall(r'\w{3,}',question.lower()))
 if not words:return []
 query=embed(question)
 chunks=KnowledgeChunk.objects.filter(project_id=project_id,document__status='ready').select_related('document','vector').iterator(chunk_size=100)
 scored=[]
 for item in chunks:
  s=sum(item.content.lower().count(word) for word in words)
  vector=getattr(item,'vector',None)
  cosine=similarity(query,vector.weights if vector else embed(item.content))
  if s or cosine>=0.2:scored.append((cosine+min(s,3)*0.05,item))
 return [item for _,item in sorted(scored,key=lambda row:row[0],reverse=True)[:limit]]
