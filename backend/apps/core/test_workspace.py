from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from unittest.mock import patch
from .models import Project, Prospect, Conversation


class WorkspaceTests(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.create_superuser('admin'))
        self.project = Project.objects.create(name='VITRIX',slug='vitrix')
        self.prospect = Prospect.objects.create(company_name='Shop',project=self.project)

    def test_all_sections_with_records(self):
        for section in 'dashboard projects knowledge training testing playbook prospects campaigns conversations leads operators analytics integrations settings audit'.split():
            with self.subTest(section=section):
                self.assertEqual(self.client.get(f'/app/{section}/').status_code,200)

    def test_operator_flow(self):
        self.client.post('/inbox/',{'prospect':self.prospect.pk})
        dialog = Conversation.objects.get()
        url = f'/inbox/{dialog.pk}/'
        self.client.post(url,{'action':'customer','message':'operator kerak'})
        self.assertTrue(dialog.handoffs.exists())
        self.client.post(url,{'action':'take'})
        self.client.post(url,{'action':'reply','message':'Assalomu alaykum!'})
        self.assertTrue(dialog.messages.filter(sender_type='operator').exists())
        self.client.post(url,{'action':'resume'})
        with patch('apps.core.workspace.generate',return_value={'answer':'Salom','model':'test'}):
            self.client.post(url,{'action':'customer','message':'Salom'})
        self.assertTrue(dialog.messages.filter(sender_type='ai').exists())
        self.assertEqual(self.client.get(url).status_code,200)

    def test_csv_and_excel(self):
        upload=SimpleUploadedFile('import.csv',b'company_name,industry\nGarden,Flowers')
        self.client.post('/prospects/import/',{'project':self.project.pk,'file':upload})
        self.assertTrue(self.project.prospects.filter(company_name='Garden').exists())
        self.assertEqual(self.client.get('/api/v1/analytics/prospects.xlsx').content[:2],b'PK')

    def test_file_upload_and_gemini_adapter(self):
        import os
        import tempfile
        import httpx
        from django.test import override_settings
        from .models import AIConfiguration, AIUsage, AITrainingTest
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            result=self.client.post('/api/v1/knowledge/',{'project':self.project.pk,'title':'Tarif','file':SimpleUploadedFile('tarif.txt',b'Catalog price is 12 USD.')})
            self.assertEqual(result.status_code,201)
            self.assertEqual(result.json()['status'],'ready')
        AIConfiguration.objects.create(project=self.project)
        provider=httpx.Response(200,request=httpx.Request('POST','https://example.test'),json={
            'candidates':[{'content':{'parts':[{'text':'Catalog price is 12 USD.'}]}}],
            'usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':20}
        })
        with patch.dict(os.environ,{'GEMINI_API_KEY':'test','AI_INPUT_USD_PER_MILLION':'1','AI_OUTPUT_USD_PER_MILLION':'2'}), patch('httpx.Client.post',return_value=provider):
            response=self.client.post('/api/v1/ai/test/',{'project':self.project.pk,'question':'Catalog price?'})
        self.assertEqual(response.status_code,200)
        self.assertGreater(AIUsage.objects.get().cost_usd,0)
        self.assertEqual(AITrainingTest.objects.get().actual,'Catalog price is 12 USD.')

    def test_all_document_formats(self):
        from io import BytesIO
        import tempfile
        from django.test import override_settings
        from docx import Document
        from openpyxl import Workbook
        from reportlab.pdfgen.canvas import Canvas

        doc = Document()
        doc.add_paragraph('Business catalog')
        word = BytesIO()
        doc.save(word)
        workbook = Workbook()
        workbook.active.append(['Business catalog'])
        excel = BytesIO()
        workbook.save(excel)
        pdf = BytesIO()
        canvas = Canvas(pdf)
        canvas.drawString(10, 700, 'Business catalog')
        canvas.save()
        samples={'pdf':pdf.getvalue(),'docx':word.getvalue(),'xlsx':excel.getvalue(),'txt':b'Business catalog','md':b'# Business catalog','csv':b'name\nBusiness catalog'}
        with tempfile.TemporaryDirectory() as media, override_settings(MEDIA_ROOT=media):
            for extension,content in samples.items():
                with self.subTest(format=extension):
                    res=self.client.post('/api/v1/knowledge/',{'project':self.project.pk,'title':'Catalog','file':SimpleUploadedFile('catalog.'+extension,content)})
                    self.assertEqual(res.json()['status'],'ready')
                    self.assertGreater(res.json()['chunks_count'],0)
