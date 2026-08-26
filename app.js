let contacts=[];
const $=id=>document.getElementById(id);

function log(msg){
  const d=$('log');
  const e=document.createElement('div');
  e.textContent='['+new Date().toLocaleTimeString()+'] '+msg;
  d.appendChild(e);
  d.scrollTop=d.scrollHeight;
}

async function callScript(action,data){
  const url=$('scriptUrl').value.trim();
  if(!url){
    alert('Google Apps Script URL daalo');
    return null;
  }
  try{
    const response=await fetch(url,{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({action,...data})
    });
    return await response.json();
  }catch(e){
    log('Error: '+e.message);
    return null;
  }
}

async function startScrape(){
  const city=$('city').value.trim();
  const category=$('category').value.trim();
  const limit=$('limit').value;
  const serpApiKey=$('serpApiKey').value.trim();
  const hunterApiKey=$('hunterApiKey').value.trim();
  
  if(!city||!category){
    alert('City aur Business Type daalo');
    return;
  }
  if(!serpApiKey){
    alert('SerpAPI Key daalo');
    return;
  }
  if(!hunterApiKey){
    alert('Hunter API Key daalo');
    return;
  }
  
  const btn=$('scrapeBtn');
  btn.disabled=true;
  btn.textContent='⏳ Scraping...';
  
  log('🔍 Starting: '+category+' in '+city);
  
  const result=await callScript('scrape',{
    city,
    category,
    limit,
    serpApiKey,
    hunterApiKey
  });
  
  if(result&&result.success){
    contacts=result.data||[];
    renderResults();
    log('✅ Found '+contacts.length+' contacts');
    $('saveBtn').disabled=false;
  }else{
    log('❌ Failed: '+(result?result.message:'Unknown error'));
  }
  
  btn.disabled=false;
  btn.textContent='🔍 Start Scraping';
}

function renderResults(){
  const tbody=$('results');
  tbody.innerHTML='';
  
  if(!contacts.length){
    tbody.innerHTML='<tr><td colspan="7" class="empty">No results</td></tr>';
  }else{
    contacts.forEach((c,i)=>{
      const statusBadge=c.email_status==='valid'?'<span class="badge badge-valid">Valid</span>':c.email_status==='invalid'?'<span class="badge badge-invalid">Invalid</span>':'<span class="badge badge-unknown">Unknown</span>';
      const tr=document.createElement('tr');
      tr.innerHTML='<td>'+(i+1)+'</td><td>'+(c.business_name||'—')+'</td><td>'+(c.business_email||'—')+'</td><td>'+statusBadge+'</td><td>'+(c.business_phone||'—')+'</td><td>'+(c.website||'—').substring(0,40)+'</td><td>'+(c.source||'—')+'</td>';
      tbody.appendChild(tr);
    });
  }
  
  $('statContacts').textContent=contacts.length;
  $('statEmails').textContent=contacts.filter(c=>c.business_email).length;
  $('statPhones').textContent=contacts.filter(c=>c.business_phone).length;
  $('statVerified').textContent=contacts.filter(c=>c.email_status==='valid').length;
}

async function saveData(){
  if(!contacts.length)return;
  const result=await callScript('save',{data:contacts});
  if(result&&result.success){
    log('✅ Saved '+result.count+' records');
  }
}

async function loadData(){
  const result=await callScript('load');
  if(result&&result.success){
    contacts=result.data||[];
    renderResults();
    log('📊 Loaded '+contacts.length+' records');
  }
}
