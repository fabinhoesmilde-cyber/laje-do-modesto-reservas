function abrirReserva(codigoReserva) {
    const listaReservas = typeof todasReservas !== 'undefined' ? todasReservas : (typeof reservas !== 'undefined' ? reservas : []);
    const reserva = listaReservas.find(r => r.codigo_reserva === codigoReserva);
    if (!reserva) { alert('Reserva não encontrada.'); return; }
    const modal = document.getElementById('modalReserva');
    const conteudo = document.getElementById('conteudoModal');
    const el=(tag,cls,text,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;parent?.appendChild(n);return n;};
    const section=(parent,title,full=false)=>{const box=el('div',full?'info-box info-box-full':'info-box',undefined,parent);el('h3','',title,box);return box;};
    const field=(box,label,value,cls='')=>{const p=el('p',cls,undefined,box);const strong=el('strong','',label,p);p.appendChild(document.createTextNode(' '+(value??'')));return p;};
    conteudo.replaceChildren();
    const head=el('div','cabecalho-modal',undefined,conteudo), details=el('div','',undefined,head);
    el('span','modal-subtitulo','Reserva',details);el('h2','','👤 '+(reserva.cliente_nome||''),details);el('span','codigo-modal','Código '+(reserva.codigo_reserva||''),details);
    const status=el('div','status-lateral',undefined,head);el('span','badge-status',reserva.status_nome||'',status);
    const grid=el('div','grid-modal',undefined,conteudo);
    let box=section(grid,'👤 Cliente');field(box,'Nome',reserva.cliente_nome);field(box,'CPF',reserva.cpf);field(box,'Telefone',reserva.telefone);field(box,'E-mail',reserva.email);
    box=section(grid,'📅 Reserva');field(box,'Data',reserva.data_reserva);field(box,'Horário',`${(reserva.hora_inicio||'').slice(0,5)} às ${(reserva.hora_fim||'').slice(0,5)}`);field(box,'Status',reserva.status_nome);field(box,'Código',reserva.codigo_reserva);
    const extra=Number(reserva.horas_extras)||0;box=section(grid,'💰 Financeiro');field(box,'Valor Base',`R$ ${reserva.valor_base??''}`);field(box,'Desconto',`R$ ${reserva.valor_desconto??''}`);field(box,'Horas Extras',`R$ ${(extra*60).toFixed(2)}`);field(box,'Adicionais',`R$ ${reserva.valor_adicionais??''}`);field(box,'',`R$ ${reserva.valor_total??''}`,'valor-total');
    box=section(grid,' 🕒 Tempo da Reserva');field(box,'Horas Inclusas','8 horas');field(box,'Horas Extras',`${extra} hora(s)`);field(box,'Total Contratado',`${8+extra} horas`);field(box,'Horário',`${(reserva.hora_inicio||'').slice(0,5)} às ${(reserva.hora_fim||'').slice(0,5)}`);
    box=section(grid,'🎉 Adicionais Contratados',true);if(reserva.adicionais?.length){reserva.adicionais.forEach(ad=>{const item=el('div','item-adicional',undefined,box),left=el('div','',undefined,item);el('strong','',ad.nome,left);el('p','',`Quantidade: ${ad.quantidade}`,left);const right=el('div','',undefined,item);el('strong','',`R$ ${ad.valor_total}`,right);});}else el('div','sem-adicionais','Nenhum adicional contratado.',box);
    box=section(grid,'🏷 Cupom');field(box,'',reserva.cupom_codigo||'Nenhum cupom aplicado');box=section(grid,'📌 Status da Reserva');field(box,'',reserva.status_nome);
    box=section(grid,'📝 Observações',true);field(box,'',reserva.observacao||'Nenhuma observação cadastrada.');modal.style.display='flex';
}
function fecharModal() { const modal=document.getElementById('modalReserva'); if(modal) modal.style.display='none'; }
window.abrirReserva=abrirReserva;window.fecharModal=fecharModal;
