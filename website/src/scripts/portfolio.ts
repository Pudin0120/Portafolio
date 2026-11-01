const filterButtons=Array.from(document.querySelectorAll<HTMLButtonElement>('[data-filter]'));
const projectCards=Array.from(document.querySelectorAll<HTMLElement>('[data-project-card]'));
const projectSearch=document.querySelector<HTMLInputElement>('#project-search');
const emptyState=document.querySelector<HTMLElement>('#projects-empty');
let activeFilter='all',searchQuery='';
function updateProjects():void{
 let visible=0;
 projectCards.forEach(card=>{
  const category=card.dataset.category??'';
  const searchable=card.dataset.search??card.textContent?.toLowerCase()??'';
  const show=(activeFilter==='all'||category===activeFilter)&&searchable.includes(searchQuery);
  card.hidden=!show;if(show)visible++;
 });
 if(emptyState)emptyState.hidden=visible>0;
}
filterButtons.forEach(button=>button.addEventListener('click',()=>{
 activeFilter=button.dataset.filter??'all';
 filterButtons.forEach(item=>{const active=item===button;item.classList.toggle('active',active);item.setAttribute('aria-pressed',String(active));});
 updateProjects();
}));
projectSearch?.addEventListener('input',()=>{searchQuery=projectSearch.value.trim().toLowerCase();updateProjects();});
const overlay=document.querySelector<HTMLElement>('#command-overlay');
const commandInput=document.querySelector<HTMLInputElement>('#command-input');
const commandResults=document.querySelector<HTMLElement>('#command-results');
const commandTrigger=document.querySelector<HTMLButtonElement>('#command-trigger');
function filterCommandResults(query:string):void{
 if(!commandResults)return;
 const items=Array.from(commandResults.querySelectorAll<HTMLElement>('[data-search-item]'));
 let first:HTMLElement|null=null;
 items.forEach(item=>{const match=item.textContent?.toLowerCase().includes(query)??false;item.hidden=!match;item.classList.remove('first-result');if(match&&!first)first=item;});
 first?.classList.add('first-result');
}
function openSearch():void{if(!overlay||!commandInput)return;overlay.hidden=false;commandInput.value='';filterCommandResults('');commandInput.focus();}
function closeSearch():void{if(!overlay)return;overlay.hidden=true;commandTrigger?.focus();}
commandTrigger?.addEventListener('click',openSearch);
commandInput?.addEventListener('input',()=>filterCommandResults(commandInput.value.trim().toLowerCase()));
overlay?.querySelectorAll('[data-close-search]').forEach(element=>element.addEventListener('click',closeSearch));
document.addEventListener('keydown',(event:KeyboardEvent)=>{
 const shortcut=(event.ctrlKey||event.metaKey)&&event.key.toLowerCase()==='k';
 if(shortcut){event.preventDefault();if(overlay?.hidden)openSearch();else closeSearch();}
 if(event.key==='Escape'&&overlay&&!overlay.hidden)closeSearch();
 if(event.key==='Enter'&&overlay&&!overlay.hidden)commandResults?.querySelector<HTMLAnchorElement>('[data-search-item]:not([hidden])')?.click();
});
const terminalForm=document.querySelector<HTMLFormElement>('#terminal-form');
const terminalInput=document.querySelector<HTMLInputElement>('#terminal-input');
const terminalOutput=document.querySelector<HTMLElement>('#terminal-output');
function writeTerminalLine(content:string,className='response'):void{
 if(!terminalOutput)return;const line=document.createElement('p');line.className=className;line.textContent=content;terminalOutput.append(line);terminalOutput.scrollTop=terminalOutput.scrollHeight;
}
const commands:Record<string,string>={
 help:'Comandos: about · stack · projects · contact · clear',
 about:'Joseff Laverde | Desarrollador orientado a Backend y Full Stack | UPTC.',
 stack:'Backend: Java, Spring Boot, Python, FastAPI | Frontend: TypeScript, React, Next.js | Data: PostgreSQL, MySQL, Supabase | Tools: Docker, Git.',
 projects:'Destacados: Huffman Compressor Pro, Banking Portal API, Inventory Management System. Abre Proyectos para ver las fichas.',
 contact:'Email: joseffflaverde@gmail.com | GitHub: github.com/Pudin0120'
};
terminalForm?.addEventListener('submit',event=>{
 event.preventDefault();const command=terminalInput?.value.trim().toLowerCase()??'';if(!command)return;
 writeTerminalLine(`$ ${command}`,'terminal-command');
 if(command==='clear')terminalOutput?.replaceChildren();
 else writeTerminalLine(commands[command]??`Comando no reconocido: ${command}. Escribe help para ver las opciones.`);
 if(terminalInput)terminalInput.value='';
});