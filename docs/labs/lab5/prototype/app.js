'use strict';
const $=s=>document.querySelector(s), params=new URLSearchParams(location.search);
const palettes={blue:['#345fd1','#2449ab','#edf2ff'],green:['#167658','#105740','#e8f5ee'],plum:['#8050a5','#663789','#f3edf8']};
(palettes[params.get('theme')]||palettes.blue).forEach((v,i)=>document.documentElement.style.setProperty(['--accent','--accent-dark','--tint'][i],v));
if(params.has('mobile'))document.body.classList.add('mobile-mode');
const fixture=()=>({folders:['Учёба','Проект GremlinDrive','Личное'],files:[
{id:1,name:'Отчёт_ЛР4.pdf',size:'1,8 МБ',folder:'Учёба',type:'doc',favorite:true},
{id:2,name:'Требования.docx',size:'248 КБ',folder:'Проект GremlinDrive',type:'doc',shared:true},
{id:3,name:'Макеты.png',size:'3,2 МБ',folder:'Проект GremlinDrive',type:'img'},
{id:4,name:'Материалы.zip',size:'12,4 МБ',folder:'Учёба',type:'zip'},
{id:5,name:'План проекта.docx',size:'86 КБ',folder:'Личное',type:'doc'}]});
let state;try{state=JSON.parse(localStorage.getItem('gremlindrive-lab5'))||fixture()}catch{state=fixture()}
if(!Array.isArray(state.files)||!Array.isArray(state.folders))state=fixture();
let view='files',folder='',toastTimer;
function save(){localStorage.setItem('gremlindrive-lab5',JSON.stringify(state));render()}
function node(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function button(text,label,fn,cls=''){const b=node('button',cls,text);b.type='button';if(label)b.setAttribute('aria-label',label);b.onclick=fn;return b}
function toast(text){$('#toast').textContent=text;$('#toast').classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),4000)}
const titles={files:'Мои файлы',recent:'Недавние',favorites:'Избранное',shared:'Общий доступ',trash:'Корзина'};
function render(){
 document.querySelectorAll('[data-view]').forEach(b=>b.classList.toggle('active',b.dataset.view===view));
 $('#view-title').textContent=folder||titles[view];$('#crumb').textContent=folder||titles[view];
 $('#list-title').textContent=view==='trash'?'Удалённые файлы':'Все файлы';
 $('#subtitle').textContent=view==='trash'?'Файлы можно восстановить в прежнюю папку.':'Всё, над чем вы работаете, всегда под рукой.';
 const q=$('#search').value.toLocaleLowerCase('ru');
 $('#folders').replaceChildren();const folders=state.folders.filter(f=>f.toLocaleLowerCase('ru').includes(q));
 $('#folder-section').hidden=view!=='files'||!!folder;
 folders.forEach(f=>{const b=button('',null,()=>{folder=f;$('#search').value='';render()});b.className='folder';b.append(node('span','folder-icon','▰'),node('strong','',f),node('small','',state.files.filter(x=>x.folder===f&&!x.trash).length+' файлов'));$('#folders').append(b)});
 $('#folder-count').textContent=folders.length+' папки';
 let files=state.files.filter(f=>(view==='trash'?f.trash:!f.trash)&&(!folder||f.folder===folder)&&(!q||f.name.toLocaleLowerCase('ru').includes(q)));
 if(view==='favorites')files=files.filter(f=>f.favorite);if(view==='shared')files=files.filter(f=>f.shared);
 $('#files').replaceChildren();$('#file-count').textContent=files.length+' файлов';$('#empty').hidden=files.length>0;
 files.forEach(f=>{
  const row=node('div','file-row'),name=node('div','file-name');name.append(node('span','file-icon '+f.type,f.type==='img'?'▧':f.type==='zip'?'▤':'▥'));
  const label=node('div','file-labels');label.append(button(f.name,'Открыть '+f.name,()=>details(f),'filename'),node('small','',f.folder+(f.shared?' · По ссылке':'')));name.append(label);
  row.append(name,node('span','file-date','24 окт. 2026'),node('span','file-size',f.size));const actions=node('div','row-actions');
  if(f.trash)actions.append(button('↶','Восстановить '+f.name,()=>{f.trash=false;save();toast('Файл восстановлен')}));
  else actions.append(button(f.favorite?'★':'☆','Избранное: '+f.name,()=>{f.favorite=!f.favorite;save()},'favorite-action'),button('↗','Поделиться '+f.name,()=>share(f)),button('⌫','Удалить '+f.name,()=>remove(f)));
  row.append(actions);$('#files').append(row);
 });
}
function modal(title,body,submit,label='Сохранить'){
 $('#modal-title').textContent=title;$('#modal-body').replaceChildren(body);$('#modal-actions').replaceChildren(button('Отмена',null,()=>$('#modal').close(),'outline'));
 if(submit){const b=node('button','primary',label);b.type='submit';$('#modal-actions').append(b)}
 $('#modal-form').onsubmit=e=>{e.preventDefault();if(submit)submit(new FormData(e.currentTarget))};$('#modal').showModal();
}
function field(text,name,value='',type='text'){const l=node('label','',text),i=node('input');i.name=name;i.value=value;i.type=type;l.append(i);return l}
function details(f){const box=node('div');box.append(button(f.favorite?'Убрать из избранного':'В избранное',null,()=>{f.favorite=!f.favorite;save();modalClose();toast('Избранное обновлено')},'outline')); box.append(node('p','',f.folder+' · '+f.size),node('h3','','История версий'),node('p','','Версия 2 · 24 октября 2026'+(f.version===1?'':' · текущая')),node('p','','Версия 1 · 22 октября 2026'+(f.version===1?' · текущая':'')));
 box.append(button('Восстановить версию 1',null,()=>{f.version=1;$('#modal').close();toast('Версия 1 восстановлена (демо)')},'outline'));modal(f.name,box)}
function share(f){const box=node('div');box.append(node('p','muted','Получатель сможет скачать файл. Ссылка работает только в учебном прототипе.'));
 const pass=field('Пароль ссылки (необязательно)','link-password','','password');pass.querySelector('input').minLength=8;
 const expiry=node('label','','Срок действия'),select=node('select');select.name='expiry';for(const [v,t] of [['7','7 дней'],['1','1 день'],['30','30 дней']]){const o=node('option','',t);o.value=v;select.append(o)}expiry.append(select);box.append(expiry,pass);
 modal('Поделиться файлом',box,data=>{f.shared=true;f.expiry=data.get('expiry');save();const result=node('div');result.append(node('p','','Ссылка создана. Доступ: скачивание. Срок: '+f.expiry+' дней.'));const link=field('Демонстрационная ссылка','demo-link','https://gremlindrive.example/s/demo-'+f.id);link.querySelector('input').readOnly=true;result.append(link);modalClose();modal('Ссылка готова',result)},'Создать ссылку');
}
function modalClose(){$('#modal').close()}
function remove(f){modal('Переместить в корзину?',node('p','',f.name+' можно будет восстановить.'),()=>{f.trash=true;f.shared=false;save();modalClose();toast('Файл перемещён в корзину')},'В корзину')}
$('#close-modal').onclick=modalClose;
$('#new-folder').onclick=()=>{const f=field('Название папки','folder');f.querySelector('input').required=true;f.querySelector('input').maxLength=80;modal('Новая папка',f,data=>{const value=data.get('folder').trim(),i=f.querySelector('input');if(!value||state.folders.some(x=>x.toLocaleLowerCase('ru')===value.toLocaleLowerCase('ru'))){i.setCustomValidity('Введите новое название папки');i.reportValidity();i.oninput=()=>i.setCustomValidity('');return}state.folders.push(value);save();modalClose();toast('Папка создана')},'Создать папку')};
$('#search').oninput=render;document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>{view=b.dataset.view;folder='';$('#search').value='';render()});
$('.brand').onclick=e=>{e.preventDefault();view='files';folder='';render()};
$('#grid-toggle').onclick=()=>{$('.content').classList.toggle('grid-view');$('#grid-toggle').setAttribute('aria-pressed',$('.content').classList.contains('grid-view'))};
$('#upload').onclick=()=>$('#file-input').click();$('#file-input').onchange=e=>{const f=e.target.files[0];if(!f)return;state.files.push({id:Date.now(),name:f.name,size:Math.max(1,Math.round(f.size/1024))+' КБ',folder:folder||'Личное',type:'doc'});save();toast('Добавлен демонстрационный файл');e.target.value=''};
$('#reset').onclick=()=>{state=fixture();folder='';view='files';$('#search').value='';save();toast('Учебные данные восстановлены')};
function enter(){$('#login').hidden=true;$('#app').hidden=false;render()}
$('#login-form').onsubmit=e=>{e.preventDefault();enter()};$('#logout').onclick=()=>{$('#login').hidden=false;$('#app').hidden=true};
if(params.get('screen')==='files')enter();
