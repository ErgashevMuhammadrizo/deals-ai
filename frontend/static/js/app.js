let createSection=null;const $=s=>document.querySelector(s);
const fields={projects:[['name','text',true],['slug','text',true],['company_name','text'],['description','textarea'],['industry','text'],['website','url']],prospects:[['project','project',true],['company_name','text',true],['industry','text'],['instagram_username','text'],['website','url'],['public_contact','text'],['description','textarea']],campaigns:[['project','project',true],['name','text',true],['target_industry','text'],['target_location','text'],['daily_prospect_limit','number']],leads:[['project','project',true],['prospect','prospect',true],['need','textarea'],['priority','text']],knowledge:[['project','project',true],['title','text',true],['source_text','textarea'],['file','file']]};
function showToast(message){const x=$('#toast');x.textContent=message;x.classList.add('show');setTimeout(()=>x.classList.remove('show'),3900)}
function csrf(){return document.querySelector('meta[name="csrf-token"]')?.content||''}
async function api(path,{method='GET',body=null}={}){let opts={method,credentials:'same-origin',headers:{'X-CSRFToken':csrf()}};if(body instanceof FormData){opts.body=body}else if(body){opts.headers['Content-Type']='application/json';opts.body=JSON.stringify(body)}const r=await fetch('/api/v1/'+path,opts);let data=await r.json().catch(()=>({error:'Invalid server response'}));if(!r.ok)throw new Error(JSON.stringify(data));return data}
function fieldLabel(key){const d={name:['Nomi','Название'],slug:['URL slug','URL slug'],company_name:['Kompaniya nomi','Название компании'],description:['Tavsif','Описание'],industry:['Soha','Сфера'],website:['Veb-sayt','Веб-сайт'],project:['Loyiha','Проект'],instagram_username:['Instagram akkaunt','Instagram аккаунт'],public_contact:['Ochiq biznes kontakti','Публичный контакт'],target_industry:['Maqsadli soha','Целевая отрасль'],target_location:['Hudud','Регион'],daily_prospect_limit:['Kunlik tahlil limiti','Лимит анализа в день'],prospect:['Mijoz','Клиент'],need:['Ehtiyoj','Потребность'],priority:['Muhimlik','Приоритет'],title:['Hujjat nomi','Название документа'],source_text:['Matn (yoki fayl)','Текст (или файл)'],file:['Fayl','Файл']};return(d[key]||[key,key])[language()==='ru'?1:0]}
async function openCreate(section){createSection=section;const modal=$('#createDialog'),box=$('#modalFields');box.innerHTML='';for(const [key,type,required] of fields[section]||[]){const wrap=document.createElement('div'),label=document.createElement('label');label.textContent=fieldLabel(key);wrap.append(label);let el;if(type==='project'||type==='prospect'){el=document.createElement('select');const blank=document.createElement('option');blank.value='';blank.textContent=t('choose');el.append(blank);try{const data=await api(type==='project'?'projects/?page_size=100':'prospects/?page_size=100');for(const item of data.results||[]){const opt=document.createElement('option');opt.value=item.id;opt.textContent=item.name||item.company_name;el.append(opt)}}catch(e){showToast(e.message)}}else if(type==='textarea'){el=document.createElement('textarea');el.rows=3}else{el=document.createElement('input');el.type=type}el.name=key;el.required=!!required;if(key==='daily_prospect_limit')el.value=50;wrap.append(el);box.append(wrap)}applyLanguage();modal.showModal()}
async function submitCreate(e){e.preventDefault();let form=e.target,fd=new FormData(form),body={};for(const [key,val] of fd){if(val instanceof File){if(val.size)body[key]=val}else if(val!=='')body[key]=['project','prospect','daily_prospect_limit'].includes(key)?Number(val):val}try{const endpoint=createSection+'/';if(createSection==='knowledge'){let multipart=new FormData();for(const [key,val] of Object.entries(body))multipart.append(key,val);await api(endpoint,{method:'POST',body:multipart})}else await api(endpoint,{method:'POST',body});$('#createDialog').close();location.reload()}catch(err){showToast(err.message)}return false}
async function handleAI(e,section){e.preventDefault();const project=Number($('#aiProject').value),output=$('#aiResult');output.hidden=false;output.textContent=language()==='ru'?'Обработка...':'Tekshirilmoqda...';try{let result;if(section==='testing')result=await api('ai/test/',{method:'POST',body:{project,question:$('#aiQuestion').value}});else{let endpoint=section==='training'?'ai-config/':'playbooks/';const existing=await api(endpoint+'?project='+project);const found=existing.results?.[0];const body=section==='training'?{project,name:$('#aiName').value,instructions:$('#aiInstructions').value}:{project,discovery:$('#aiInstructions').value};result=await api(endpoint+(found?found.id+'/':''),{method:found?'PATCH':'POST',body})}output.textContent=section==='testing'?JSON.stringify(result,null,2):language()==='ru'?'Сохранено успешно.':'Muvaffaqiyatli saqlandi.'}catch(err){output.textContent=err.message}return false}
document.addEventListener('DOMContentLoaded',()=>{$('#date-label').textContent=new Date().toLocaleDateString(language()==='ru'?'ru-RU':'uz-UZ',{day:'numeric',month:'long',year:'numeric'});});

async function workflow(path) {
  try { await api(path,{method:'POST'}); location.reload() }
  catch (error) { showToast(error.message) }
}
const projectSelector = document.querySelector('#aiProject');
if (projectSelector) projectSelector.addEventListener('change', async () => {
  const name = document.querySelector('#aiName');
  const instructions = document.querySelector('#aiInstructions');
  if (!instructions) return;
  const project = projectSelector.value;
  instructions.value = '';
  if (name) name.value = 'DEALS AI';
  if (!project) return;
  try {
    const page = await api((name ? 'ai-config/' : 'playbooks/') + '?project=' + project);
    if (projectSelector.value !== project || !page.results.length) return;
    const record = page.results[0];
    if (name) name.value = record.name;
    instructions.value = name ? record.instructions : record.discovery;
  } catch (err) { showToast(err.message) }
});
