const API_URL = "http://127.0.0.1:8000/api";

const adminToken = localStorage.getItem("adminToken");
const adminUsername = localStorage.getItem("adminUsername");

async function fetchAdmin(url, options = {}) {
    const headers = new Headers(options.headers || {});
    headers.set("Authorization", `Token ${adminToken || ""}`);
    return window.fetch(url, { ...options, headers });
}

if (!adminToken) {
    window.location.href = "admin-login.html";
}

const usuarioLogado = document.getElementById("usuarioLogado");

if (usuarioLogado) {
    usuarioLogado.textContent = `Bem-vindo, ${adminUsername}`;
}

const campoBuscaReserva = document.getElementById("campoBuscaReserva");

const listaReservas = document.getElementById("listaReservas");

const totalReservas = document.getElementById("totalReservas");
const totalConfirmadas = document.getElementById("totalConfirmadas");
const totalCanceladas = document.getElementById("totalCanceladas");
const totalAlteracoes = document.getElementById("totalAlteracoes");
const totalCancelamentos = document.getElementById("totalCancelamentos");

let todasReservas = [];
let filtroAtual = "TODAS";
let clientesEncontrados = [];

async function carregarReservas() {

    try {

    const resposta = await fetchAdmin(`${API_URL}/reservas/`, {
        method: "GET",
        headers: {
            "Authorization": `Token ${adminToken}`
        }
    });

        if (!resposta.ok) {
            throw new Error("Erro ao carregar reservas.");
        }

        todasReservas = await resposta.json();

        atualizarDashboard();

        carregarProximaReserva();

        renderizarReservas();

    } catch (erro) {

        console.error(erro);

        listaReservas.innerHTML = `

            <div class="painel-reserva">

                <h3>Erro ao carregar reservas.</h3>

            </div>

        `;

    }

}

function atualizarDashboard() {

    totalReservas.textContent =
        todasReservas.length;

    totalConfirmadas.textContent =
        todasReservas.filter(
            r => r.status_nome === "CONFIRMADA"
        ).length;

    totalCanceladas.textContent =
        todasReservas.filter(
            r => r.status_nome === "CANCELADA"
        ).length;

    totalAlteracoes.textContent =
        todasReservas.filter(
            r => r.status_nome === "ALTERACAO_SOLICITADA"
        ).length;

    totalCancelamentos.textContent =
        todasReservas.filter(
            r => r.status_nome === "CANCELAMENTO_SOLICITADO"
        ).length;

}

function criarCardReserva(reserva) {
 const el=(tag,cls,text,parent)=>{const x=document.createElement(tag);if(cls)x.className=cls;if(text!==undefined)x.textContent=text;parent?.appendChild(x);return x;};
 const cls={CONFIRMADA:'status-confirmada',ALTERACAO_SOLICITADA:'status-alteracao',CANCELAMENTO_SOLICITADO:'status-cancelamento'}[reserva.status_nome]||'';
 const card=el('div',`painel-reserva ${cls}`), head=el('div','cabecalho-reserva',undefined,card);
 el('h3','',`👤 ${reserva.cliente_nome||''}`,head);el('span','badge-status',reserva.status_nome||'',head);
 const info=el('div','info-reserva',undefined,card);const row=(label,value)=>{const p=el('p','',undefined,info);el('strong','',label,p);p.appendChild(document.createTextNode(' '+(value??'')));};
 row('📌 Código:',reserva.codigo_reserva);row('📅 Data:',reserva.data_reserva);row('🕒 Horário:',`${reserva.hora_inicio||''} às ${reserva.hora_fim||''}`);row('💰 Total:',`R$ ${reserva.valor_total??''}`);
 const actions=el('div','acoes-reserva',undefined,card), view=el('button','btn-ver','👁 Ver',actions);view.addEventListener('click',()=>abrirReserva(reserva.codigo_reserva));
 const funcs=reserva.status_nome==='ALTERACAO_SOLICITADA'?[['aprovarAlteracao','✅ Aprovar'],['rejeitarAlteracao','❌ Rejeitar']]:reserva.status_nome==='CANCELAMENTO_SOLICITADO'?[['aprovarCancelamento','✅ Aprovar'],['rejeitarCancelamento','❌ Rejeitar']]:[];
 funcs.forEach(([name,label])=>{const button=el('button','',label,actions);button.addEventListener('click',()=>window[name](reserva.codigo_reserva));});return card;
}
function renderizarReservas() {

    listaReservas.replaceChildren();

    let reservas = todasReservas;

    if (filtroAtual !== "TODAS") {

        reservas = reservas.filter(
            r => r.status_nome === filtroAtual
        );

    }

    reservas.forEach(reserva => {

        listaReservas.appendChild(criarCardReserva(reserva));

    });

}

async function executarAcaoReserva(codigo, rota, acao) {
    if (!confirm(`Confirma ${acao} da reserva ${codigo}?`)) return;
    try {
        const resposta = await fetchAdmin(`${API_URL}/${rota}/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ codigo_reserva: codigo })
        });
        const dados = await resposta.json().catch(() => ({}));
        if (resposta.status === 401) {
            localStorage.removeItem("adminToken");
            window.location.href = "admin-login.html";
            return;
        }
        const mensagem = dados.erro || dados.detail || dados.mensagem || "Operação concluída.";
        if (!resposta.ok) {
            alert(mensagem);
            return;
        }
        alert(mensagem);
        await carregarReservas();
    } catch (erro) {
        alert(erro.message || "Não foi possível concluir a operação.");
    }
}

function aprovarAlteracao(codigo) { return executarAcaoReserva(codigo, "aprovar-alteracao", "a aprovação"); }
function rejeitarAlteracao(codigo) { return executarAcaoReserva(codigo, "rejeitar-alteracao", "a rejeição"); }
function aprovarCancelamento(codigo) { return executarAcaoReserva(codigo, "aprovar-cancelamento", "a aprovação"); }
function rejeitarCancelamento(codigo) { return executarAcaoReserva(codigo, "rejeitar-cancelamento", "a rejeição"); }
window.aprovarAlteracao = aprovarAlteracao;
window.rejeitarAlteracao = rejeitarAlteracao;
window.aprovarCancelamento = aprovarCancelamento;
window.rejeitarCancelamento = rejeitarCancelamento;

const modal = document.getElementById("modalReserva");
const botaoFecharModal = document.getElementById("fecharModal");

botaoFecharModal.onclick = function () {

    modal.style.display = "none";

}

window.onclick = function (event) {

    if (event.target === modal) {

        modal.style.display = "none";

    }

}

document.addEventListener("keydown", function (event) {

    if (event.key === "Escape") {

        modal.style.display = "none";

    }

});

function logoutAdmin() {

    localStorage.removeItem("adminToken");
    localStorage.removeItem("adminUsername");

    window.location.href = "admin-login.html";

}

function buscarReservaPorCodigo() {

    const codigo = campoBuscaReserva.value
        .trim()
        .toLowerCase();

    if (!codigo) {

        renderizarReservas();

        return;

    }

    const cards = document.querySelectorAll(".painel-reserva");

    cards.forEach(card => {

        const texto = card.textContent.toLowerCase();

        if (texto.includes(codigo)) {

            card.style.display = "";

        } else {

            card.style.display = "none";

        }

    });

}

function limparBuscaReserva() {

    campoBuscaReserva.value = "";

    renderizarReservas();

}
/* ===========================
   FILTROS
=========================== */

const botoesFiltro =
    document.querySelectorAll(".filtro");

botoesFiltro.forEach(botao => {

    botao.addEventListener("click", () => {

        botoesFiltro.forEach(btn =>
            btn.classList.remove("ativo")
        );

        botao.classList.add("ativo");

        filtroAtual =
            botao.dataset.status;

        renderizarReservas();

    });

});


/* ===========================
   DASHBOARD
=========================== */

const cardsDashboard =
    document.querySelectorAll(".dashboard-card");

cardsDashboard.forEach(card => {

    card.addEventListener("click", () => {

        filtroAtual =
            card.dataset.status;

        botoesFiltro.forEach(btn =>
            btn.classList.remove("ativo")
        );

        const filtro =
            document.querySelector(
                `.filtro[data-status="${filtroAtual}"]`
            );

        if (filtro) {

            filtro.classList.add("ativo");

        }

        renderizarReservas();

        listaReservas.scrollIntoView({

            behavior: "smooth"

        });

    });

});


/* ===========================
   BUSCA COM ENTER
=========================== */

campoBuscaReserva.addEventListener("keypress", (e) => {

    if (e.key === "Enter") {

        buscarReservaPorCodigo();

    }

});
/* ===========================
   INICIALIZAÇÃO
=========================== */

document.addEventListener("DOMContentLoaded", () => {

    carregarReservas();

});

/* ===========================
   Area de pesquisa do cliente
=========================== */

async function abrirModalClientes() {

    const modal = document.getElementById("modalClientes");
    const resultado = document.getElementById("resultadoClientes");
    const campo = document.getElementById("campoBuscaCliente");

    if (!modal || !resultado) {
        return;
    }

    modal.style.display = "flex";

    if (campo) {
        campo.value = "";
    }

    resultado.innerHTML = `
        <p class="mensagem-clientes">
            Carregando clientes...
        </p>
    `;

    try {

    const resposta = await fetchAdmin(`${API_URL}/clientes/`, {
        method: "GET",
        headers: {
            "Authorization": `Token ${adminToken}`
        }
    });

        if (!resposta.ok) {
            throw new Error("Erro ao carregar clientes.");
        }

        clientesEncontrados = await resposta.json();

        mostrarClientes(clientesEncontrados);

    } catch (erro) {

        console.error(erro);

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar os clientes.
            </p>
        `;

    }

}

function renderizarClientes(resultado, clientes, classe='cliente-resultado') {
    resultado.replaceChildren();
    clientes.forEach(cliente => {
        const row=document.createElement('div'); row.className=classe;
        const details=document.createElement('div'); const nome=document.createElement('strong'); nome.textContent=cliente.nome||''; details.appendChild(nome);
        [['CPF',cliente.cpf],['Telefone',cliente.telefone],['E-mail',cliente.email]].forEach(([label,value])=>{const p=document.createElement('p');p.textContent=label+': '+(value||'');details.appendChild(p);});
        const button=document.createElement('button');button.className='btn-ver-cliente';button.textContent='Ver cliente';button.addEventListener('click',()=>verCliente(cliente.id));row.append(details,button);resultado.appendChild(row);
    });
}
function mostrarClientes(clientes) {
    const resultado=document.getElementById('resultadoClientes'); if(!resultado)return;
    if(!clientes.length){const p=document.createElement('p');p.className='mensagem-clientes';p.textContent='Nenhum cliente cadastrado.';resultado.replaceChildren(p);return;}
    renderizarClientes(resultado,clientes);
}

function fecharModalClientes() {

    const modal = document.getElementById("modalClientes");

    if (modal) {
        modal.style.display = "none";
    }

}

async function buscarClientes() {


    const campo = document.getElementById("campoBuscaCliente");
    const resultado = document.getElementById("resultadoClientes");

    const busca = campo.value.trim().toLowerCase();

    if (!busca) {

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Digite o nome, CPF ou telefone do cliente.
            </p>
        `;

        return;
    }

    try {

        const resposta = await fetchAdmin(`${API_URL}/clientes/`, {
            method: "GET",
            headers: {
                "Authorization": `Token ${adminToken}`
            }
        });

        if (!resposta.ok) {
            throw new Error("Erro ao buscar clientes.");
        }

        const clientes = await resposta.json();

        clientesEncontrados = clientes.filter(cliente => {

            return (
                cliente.nome.toLowerCase().includes(busca) ||
                cliente.cpf.includes(busca) ||
                cliente.telefone.includes(busca)
            );

        });

        if (clientesEncontrados.length === 0) {

            resultado.innerHTML = `
                <p class="mensagem-clientes">
                    Nenhum cliente encontrado.
                </p>
            `;

            return;
        }

renderizarClientes(resultado, clientesEncontrados, "cliente-encontrado");

    } catch (erro) {

        console.error(erro);

        resultado.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar os clientes.
            </p>
        `;

    }

}

function verCliente(id) {
    const cliente=clientesEncontrados.find(item=>item.id===id);
    if(!cliente){alert('Cliente não encontrado.');return;}
    const resultado=document.getElementById('resultadoClientes');
    const el=(tag,cls,text,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;parent?.appendChild(n);return n;};
    const detalhes=el('div','detalhes-cliente',undefined,resultado);const cab=el('div','cabecalho-cliente',undefined,detalhes);const inner=el('div','',undefined,cab);
    el('span','modal-subtitulo','Cliente selecionado',inner);el('h2','','👤 '+(cliente.nome||''),inner);
    const grid=el('div','grid-modal',undefined,detalhes);let box=el('div','info-box',undefined,grid);el('h3','','👤 Informações pessoais',box);
    const field=(parent,label,value)=>{const p=el('p','',undefined,parent);el('strong','',label,p);p.appendChild(document.createTextNode(' '+(value||'')));};
    field(box,'Nome',cliente.nome);field(box,'CPF',cliente.cpf);box=el('div','info-box',undefined,grid);el('h3','','📞 Contato',box);field(box,'Telefone',cliente.telefone);field(box,'E-mail',cliente.email);
    box=el('div','info-box info-box-full',undefined,grid);el('h3','','📅 Cadastro',box);field(box,'Cadastrado em',new Date(cliente.criado_em).toLocaleDateString('pt-BR'));
    const actions=el('div','acoes-cliente',undefined,detalhes);const back=el('button','btn-voltar-cliente','Voltar',actions);back.addEventListener('click',voltarBuscaClientes);const edit=el('button','btn-editar-cliente','Editar cliente',actions);edit.addEventListener('click',()=>editarCliente(cliente.id));
}

function voltarBuscaClientes() {

    const resultado = document.getElementById("resultadoClientes");

    if (!resultado) {
        return;
    }

    if (clientesEncontrados.length === 0) {

        resultado.innerHTML = `
            <p class="nenhum-cliente">
                Nenhum cliente encontrado.
            </p>
        `;

        return;

    }

    renderizarClientes(resultado, clientesEncontrados, "cliente-encontrado");

}

function editarCliente(id) {
    const cliente=clientesEncontrados.find(item=>item.id===id);if(!cliente){alert('Cliente não encontrado.');return;}
    const resultado=document.getElementById('resultadoClientes');const el=(tag,cls,text,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;parent?.appendChild(n);return n;};
    const detalhes=el('div','detalhes-cliente',undefined,resultado);const cab=el('div','cabecalho-cliente',undefined,detalhes);const inner=el('div','',undefined,cab);el('span','modal-subtitulo','Editando cliente',inner);el('h2','','👤 '+(cliente.nome||''),inner);
    const grid=el('div','grid-modal',undefined,detalhes);let box=el('div','info-box',undefined,grid);el('h3','','👤 Informações pessoais',box);
    const input=(parent,label,id,type,value)=>{el('label','',label,parent);const field=el('input','',undefined,parent);field.type=type;field.id=id;field.value=value||'';};
    input(box,'Nome','editarNome','text',cliente.nome);input(box,'CPF','editarCpf','text',cliente.cpf);box=el('div','info-box',undefined,grid);el('h3','','📞 Contato',box);input(box,'Telefone','editarTelefone','text',cliente.telefone);input(box,'E-mail','editarEmail','email',cliente.email);
    const actions=el('div','acoes-cliente',undefined,detalhes);const cancel=el('button','btn-voltar-cliente','Cancelar',actions);cancel.addEventListener('click',()=>verCliente(cliente.id));const save=el('button','btn-editar-cliente','Salvar alterações',actions);save.addEventListener('click',()=>salvarCliente(cliente.id));
}

async function salvarCliente(id) {

    const nome = document.getElementById("editarNome").value.trim();
    const cpf = document.getElementById("editarCpf").value.trim();
    const telefone = document.getElementById("editarTelefone").value.trim();
    const email = document.getElementById("editarEmail").value.trim();

    if (!nome || !cpf || !telefone || !email) {

        alert("Preencha todos os campos.");
        return;

    }

    try {

        const resposta = await fetchAdmin(
            `http://127.0.0.1:8000/api/clientes/${id}/`,
            {
                method: "PATCH",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    nome: nome,
                    cpf: cpf,
                    telefone: telefone,
                    email: email
                })
            }
        );

        const clienteAtualizado = await resposta.json();

        if (!resposta.ok) {

            console.error(clienteAtualizado);

            alert(
                "Não foi possível atualizar o cliente."
            );

            return;

        }

        // Atualiza o cliente na lista que já carregamos
        const indice = clientesEncontrados.findIndex(
            cliente => cliente.id === id
        );

        if (indice !== -1) {

            clientesEncontrados[indice] = clienteAtualizado;

        }

        alert("Cliente atualizado com sucesso!");

        // Volta para a tela de detalhes
        verCliente(id);

    } catch (erro) {

        console.error(erro);

        alert(
            "Erro ao conectar com o servidor."
        );

    }

}


function abrirConfiguracoes() {

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "flex";
    }

}


function fecharConfiguracoes() {

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "none";
    }

}

function carregarProximaReserva() {
    const conteudo=document.getElementById('conteudoProximaReserva');if(!conteudo)return;
    const hoje=new Date();hoje.setHours(0,0,0,0);
    const futuras=todasReservas.filter(r=>r.status_nome==='CONFIRMADA'&&new Date(r.data_reserva+'T00:00:00')>=hoje).sort((a,b)=>new Date(a.data_reserva+'T00:00:00')-new Date(b.data_reserva+'T00:00:00'));
    const el=(tag,cls,text,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;parent?.appendChild(n);return n;};
    if(!futuras.length){const box=el('div','sem-proxima-reserva',undefined,conteudo);const icon=el('i','fa-solid fa-calendar-xmark',undefined,box);el('p','','Nenhuma próxima reserva confirmada.',box);return;}
    const r=futuras[0], card=el('div','proxima-reserva-card',undefined,conteudo), customer=el('div','proxima-cliente',undefined,card);
    el('h3','','👤 '+(r.cliente_nome||''),customer);el('p','','Código: '+(r.codigo_reserva||''),customer);const info=el('div','proxima-info',undefined,customer);
    const span=(iconClass,text)=>{const item=el('span','',undefined,info);el('i',iconClass,undefined,item);item.appendChild(document.createTextNode(' '+text));};
    span('fa-solid fa-calendar',new Date(r.data_reserva+'T00:00:00').toLocaleDateString('pt-BR'));span('fa-solid fa-clock',(r.hora_inicio||'').slice(0,5)+' às '+(r.hora_fim||'').slice(0,5));span('fa-solid fa-circle-check','Confirmada');
    const button=el('button','btn-ver-proxima-reserva','Ver Reserva',card);button.addEventListener('click',()=>abrirReserva(r.codigo_reserva));
}

/*modal das informaçoes da laje */

function abrirInformacoesLaje() {

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Configurações
            </span>

            <h2>
                <i class="fa-solid fa-house"></i>
                Informações da Laje
            </h2>

            <p>
                Gerencie as informações principais da Laje do Modesto.
            </p>

        </div>

        <div class="form-configuracoes">

            <div class="info-box">

                <h3>
                    🏠 Informações
                </h3>

                <label>Nome</label>

                <input
                    type="text"
                    id="configNomeLaje"
                    value="Laje do Modesto"
                >

                <label>Telefone</label>

                <input
                    type="text"
                    id="configTelefoneLaje"
                    placeholder="(00) 00000-0000"
                >

                <label>E-mail</label>

                <input
                    type="email"
                    id="configEmailLaje"
                    placeholder="email@exemplo.com"
                >

                <label>Endereço</label>

                <input
                    type="text"
                    id="configEnderecoLaje"
                    placeholder="Digite o endereço"
                >

            </div>

            <div class="acoes-configuracoes">

                <button
                    class="btn-salvar-config"
                    onclick="salvarInformacoesLaje()"
                >
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar alterações
                </button>

            </div>

        </div>

    `;

}

function voltarConfiguracoes() {

    console.log("Tela de configurações carregada");

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Administração
            </span>

            <h2>
                <i class="fa-solid fa-gear"></i>
                Configurações
            </h2>

            <p>
                Gerencie as configurações da Laje do Modesto.
            </p>

        </div>

        <div class="grid-configuracoes">

            <button
                class="card-configuracao"
                onclick="abrirInformacoesLaje()"
            >
                <i class="fa-solid fa-house"></i>

                <div>
                    <strong>Informações da Laje</strong>
                    <span>Nome, telefone, e-mail e endereço</span>
                </div>
            </button>

            <button
                class="card-configuracao"
                onclick="abrirValoresReserva()"
            >
                <i class="fa-solid fa-money-bill-wave"></i>

                <div>
                    <strong>Valores da Reserva</strong>
                    <span>Valor base e hora extra</span>
                </div>
            </button>

            <button class="card-configuracao">
                <i class="fa-solid fa-clock"></i>

                <div>
                    <strong>Horários</strong>
                    <span>Configure os horários das reservas</span>
                </div>
            </button>



            <button
                class="card-configuracao"
                onclick="abrirDiasBloqueados()"
            >
                <i class="fa-solid fa-calendar-xmark"></i>

                <div>
                    <strong>Dias Bloqueados</strong>
                    <span>Gerencie datas indisponíveis</span>
                </div>
            </button>




            <button
                class="card-configuracao"
                onclick="abrirAdicionais()"
            >
                <i class="fa-solid fa-champagne-glasses"></i>

                <div>
                    <strong>Adicionais</strong>
                    <span>Crie e gerencie serviços adicionais</span>
                </div>
            </button>


            <button
                class="card-configuracao"
                onclick="abrirCupons()"
            >
                <i class="fa-solid fa-ticket"></i>

                <div>
                    <strong>Cupons</strong>
                    <span>Crie e gerencie cupons de desconto</span>
                </div>
            </button>

        </div>

    `;

}

/*Configirações das reservas */

function abrirValoresReserva() {

    const conteudo =
        document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    conteudo.innerHTML = `

        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">

            <span class="modal-subtitulo">
                Configurações
            </span>

            <h2>
                <i class="fa-solid fa-money-bill-wave"></i>
                Valores da Reserva
            </h2>

            <p>
                Configure os valores utilizados nas reservas.
            </p>

        </div>

        <div class="form-configuracoes">

            <div class="info-box">

                <h3>
                    💰 Valores
                </h3>

                <label>
                    Valor base da reserva
                </label>

                <input
                    type="number"
                    id="configValorBase"
                    min="0"
                    step="0.01"
                    placeholder="Ex: 500.00"
                >

                <label>
                    Valor da hora extra
                </label>

                <input
                    type="number"
                    id="configValorHoraExtra"
                    min="0"
                    step="0.01"
                    value="60.00"
                >

            </div>

            <div class="acoes-configuracoes">

                <button
                    class="btn-salvar-config"
                    onclick="salvarValoresReserva()"
                >
                    <i class="fa-solid fa-floppy-disk"></i>
                    Salvar valores
                </button>

            </div>

        </div>

    `;

    carregarValoresReserva();

}

async function carregarValoresReserva() {

    try {

        const resposta = await fetchAdmin(
            `${API_URL}/configuracao-laje/reserva/`
        );

        if (!resposta.ok) {
            throw new Error(
                "Erro ao carregar valores da reserva."
            );
        }

        const dados = await resposta.json();

        const campoValorBase =
            document.getElementById("configValorBase");

        const campoValorHoraExtra =
            document.getElementById("configValorHoraExtra");

        if (campoValorBase) {

            campoValorBase.value =
                Number(dados.valor_base).toFixed(2);

        }

        if (campoValorHoraExtra) {

            campoValorHoraExtra.value =
                Number(dados.valor_hora_extra).toFixed(2);

        }

    } catch (erro) {

        console.error(
            "Erro ao carregar configurações:",
            erro
        );

        alert(
            "Não foi possível carregar os valores atuais."
        );

    }

}

async function salvarValoresReserva() {

    const campoValorBase =
        document.getElementById("configValorBase");

    const campoValorHoraExtra =
        document.getElementById("configValorHoraExtra");

    const valorBase =
        parseFloat(campoValorBase.value);

    const valorHoraExtra =
        parseFloat(campoValorHoraExtra.value);

    // Validação
    if (
        isNaN(valorBase) ||
        isNaN(valorHoraExtra)
    ) {

        alert("Preencha todos os valores corretamente.");
        return;

    }

    if (
        valorBase < 0 ||
        valorHoraExtra < 0
    ) {

        alert("Os valores não podem ser negativos.");
        return;

    }

    try {

        const resposta = await fetchAdmin(
            `${API_URL}/configuracao-laje/reserva/`,
            {
                method: "PUT",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    valor_base: valorBase,
                    valor_hora_extra: valorHoraExtra
                })
            }
        );

        if (!resposta.ok) {

            throw new Error(
                "Erro ao salvar os valores."
            );

        }

        const dados = await resposta.json();

        console.log(
            "Valores atualizados:",
            dados
        );

        alert("Valores da reserva atualizados com sucesso!");

    } catch (erro) {

        console.error(
            "Erro ao salvar valores:",
            erro
        );

        alert(
            "Não foi possível salvar os valores."
        );

    }

}

async function abrirDiasBloqueados() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        return;
    }

    const modal = document.getElementById("modalConfiguracoes");

    if (modal) {
        modal.style.display = "flex";
    }

    conteudo.innerHTML = `
        <button
            class="btn-voltar-config"
            onclick="voltarConfiguracoes()"
        >
            <i class="fa-solid fa-arrow-left"></i>
            Voltar
        </button>

        <div class="cabecalho-configuracoes">
            <span class="modal-subtitulo">Configurações</span>

            <h2>
                <i class="fa-solid fa-calendar-xmark"></i>
                Dias Bloqueados
            </h2>

            <p>
                Cadastre as datas em que a Laje não estará disponível
                para reservas.
            </p>
        </div>

        <div class="form-configuracoes">
            <div class="info-box">
                <h3>📅 Bloquear uma data</h3>

                <label for="dataBloqueio">Data</label>
                <input
                    type="date"
                    id="dataBloqueio"
                    required
                >

                <label for="motivoBloqueio">Motivo (opcional)</label>
                <input
                    type="text"
                    id="motivoBloqueio"
                    maxlength="255"
                    placeholder="Ex.: manutenção ou evento particular"
                >

                <div class="acoes-configuracoes">
                    <button
                        class="btn-salvar-config"
                        onclick="salvarDiaBloqueado()"
                    >
                        <i class="fa-solid fa-lock"></i>
                        Bloquear data
                    </button>
                </div>
            </div>

            <div class="info-box">
                <h3>🗓️ Datas cadastradas</h3>
                <div id="listaDiasBloqueados">
                    Carregando datas...
                </div>
            </div>
        </div>
    `;

    await carregarDiasBloqueados();
}

window.abrirDiasBloqueados = abrirDiasBloqueados;


function abrirAdicionais() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        console.error("Elemento conteudoConfiguracoes não encontrado.");
        return;
    }

    conteudo.innerHTML = `
        <div class="cabecalho-configuracoes">
            <button
                class="btn-voltar-config"
                onclick="voltarConfiguracoes()"
            >
                <i class="fa-solid fa-arrow-left"></i>
                Voltar
            </button>

            <h2>Gerenciar Adicionais</h2>
        </div>

        <div class="form-configuracoes">
            <h3>Cadastrar adicional</h3>

            <label for="adicionalNome">Nome</label>
            <input
                type="text"
                id="adicionalNome"
                placeholder="Ex.: Churrasqueira"
            >

            <label for="adicionalDescricao">Descrição</label>
            <textarea
                id="adicionalDescricao"
                placeholder="Descrição do adicional"
            ></textarea>

            <label for="adicionalValor">Valor (R$)</label>
            <input
                type="number"
                id="adicionalValor"
                min="0"
                step="0.01"
                placeholder="0,00"
            >

            <button
                class="btn-salvar-config"
                onclick="salvarAdicional()"
            >
                Salvar adicional
            </button>
        </div>

        <div class="acoes-configuracoes">
            <h3>Adicionais cadastrados</h3>
            <div id="listaAdicionais">
                Carregando adicionais...
            </div>
        </div>
    `;

    carregarAdicionais();
}

window.abrirAdicionais = abrirAdicionais;


function abrirCupons() {
    const conteudo = document.getElementById("conteudoConfiguracoes");

    if (!conteudo) {
        console.error("Elemento conteudoConfiguracoes não encontrado.");
        return;
    }

    conteudo.innerHTML = `
        <div class="cabecalho-configuracoes">
            <button
                class="btn-voltar-config"
                onclick="voltarConfiguracoes()"
            >
                <i class="fa-solid fa-arrow-left"></i>
                Voltar
            </button>

            <h2>Gerenciar Cupons</h2>
        </div>

        <div class="form-configuracoes">
            <h3>Cadastrar cupom</h3>

            <label for="cupomCodigo">Código do cupom</label>
            <input
                type="text"
                id="cupomCodigo"
                placeholder="Ex.: LAJE10"
            >

            <label for="cupomTipo">Tipo de desconto</label>
            <select id="cupomTipo">
                <option value="percentual">Percentual (%)</option>
                <option value="fixo">Valor fixo (R$)</option>
            </select>

            <label for="cupomValor">Valor do desconto</label>
            <input
                type="number"
                id="cupomValor"
                min="0.01"
                step="0.01"
                placeholder="Ex.: 10"
            >

            <label for="cupomUsoMaximo">Limite de utilizações</label>
            <input
                type="number"
                id="cupomUsoMaximo"
                min="1"
                step="1"
                placeholder="Ex.: 50"
            >

            <label for="cupomValidade">Data de validade</label>
            <input
                type="date"
                id="cupomValidade"
            >

            <button
                class="btn-salvar-config"
                onclick="salvarCupom()"
            >
                Salvar cupom
            </button>
        </div>

        <div class="acoes-configuracoes">
            <h3>Cupons cadastrados</h3>
            <div id="listaCupons">
                Carregando cupons...
            </div>
        </div>
    `;
    carregarCupons();
}

window.abrirCupons = abrirCupons;



async function salvarCupom() {
    const codigo = document.getElementById("cupomCodigo").value.trim().toUpperCase();
    const tipo = document.getElementById("cupomTipo").value;
    const valor = document.getElementById("cupomValor").value;
    const usoMaximo = document.getElementById("cupomUsoMaximo").value;
    const validade = document.getElementById("cupomValidade").value;

    const campoId = document.getElementById("cupomIdEdicao");
    const idEdicao = campoId?.value;
    const editando = Boolean(idEdicao);

    if (!codigo || !valor || !usoMaximo || !validade) {
        alert("Preencha todos os campos do cupom.");
        return;
    }

    if (Number(valor) <= 0 || Number(usoMaximo) < 1) {
        alert("O desconto e o limite de utilizações devem ser maiores que zero.");
        return;
    }

    if (!Number.isInteger(Number(usoMaximo))) {
        alert("O limite de utilizações deve ser um número inteiro.");
        return;
    }

    if (tipo === "percentual" && Number(valor) > 100) {
        alert("O desconto percentual não pode ultrapassar 100%.");
        return;
    }

    const cupom = {
        codigo: codigo,
        tipo_desconto: tipo,
        valor: Number(valor).toFixed(2),
        uso_maximo: Number(usoMaximo),
        validade: validade
    };

    if (!editando) {
        cupom.uso_atual = 0;
        cupom.ativo = true;
    }

    try {
        const url = editando
            ? `${API_URL}/cupons/${idEdicao}/`
            : `${API_URL}/cupons/`;

        const resposta = await fetchAdmin(url, {
            method: editando ? "PATCH" : "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(cupom)
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            console.error("Erro ao salvar cupom:", dados);
            alert(
                "Não foi possível salvar o cupom.\n" +
                JSON.stringify(dados, null, 2)
            );
            return;
        }

        alert(
            editando
                ? "Cupom atualizado com sucesso!"
                : "Cupom cadastrado com sucesso!"
        );

        document.getElementById("cupomCodigo").value = "";
        document.getElementById("cupomTipo").value = "percentual";
        document.getElementById("cupomValor").value = "";
        document.getElementById("cupomUsoMaximo").value = "";
        document.getElementById("cupomValidade").value = "";

        if (campoId) {
            campoId.value = "";
        }

        const titulo = document.querySelector(".form-configuracoes h3");
        const botaoSalvar = document.querySelector(
            ".form-configuracoes .btn-salvar-config"
        );

        if (titulo) {
            titulo.textContent = "Cadastrar cupom";
        }

        if (botaoSalvar) {
            botaoSalvar.textContent = "Salvar cupom";
        }

        await carregarCupons();

    } catch (erro) {
        console.error("Erro ao conectar com a API:", erro);
        alert("Não foi possível conectar ao servidor Django.");
    }
}

window.salvarCupom = salvarCupom;



async function carregarAdicionais() {
    const lista = document.getElementById("listaAdicionais");

    if (!lista) return;

    lista.textContent = "Carregando adicionais...";

    try {
        const resposta = await fetchAdmin(`${API_URL}/adicionais/`);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados) || dados.length === 0) {
            lista.textContent = "Nenhum adicional cadastrado.";
            return;
        }

        lista.replaceChildren();

        dados.forEach((adicional) => {
            const item = document.createElement("div");
            item.className = "cliente-resultado";

            const nome = document.createElement("strong");
            nome.textContent = adicional.nome;

            const descricao = document.createElement("p");
            descricao.textContent =
                adicional.descricao || "Sem descrição";

            const valor = document.createElement("p");
            valor.textContent = `Valor: ${Number(adicional.valor).toLocaleString(
                "pt-BR",
                { style: "currency", currency: "BRL" }
            )}`;

            const status = document.createElement("p");
            status.textContent = adicional.ativo
                ? "Status: Ativo"
                : "Status: Inativo";


            const acoes = document.createElement("div");
            acoes.style.display = "flex";
            acoes.style.gap = "10px";
            acoes.style.marginTop = "10px";


            const botaoEditar = document.createElement("button");
            botaoEditar.textContent = "Editar";
            botaoEditar.className = "btn-salvar-config";
            botaoEditar.onclick = () => editarAdicional(adicional);

            const botaoStatus = document.createElement("button");
            botaoStatus.textContent = adicional.ativo ? "Desativar" : "Ativar";
            botaoStatus.className = "btn-salvar-config";

            botaoStatus.onclick = () => alterarStatusAdicional(adicional);


            const botaoExcluir = document.createElement("button");
            botaoExcluir.textContent = "Excluir";
            botaoExcluir.className = "btn-salvar-config";

            botaoExcluir.style.backgroundColor = "#dc3545";

            botaoExcluir.onclick = () => excluirAdicional(adicional);

            acoes.append(botaoEditar, botaoStatus, botaoExcluir);



            item.append(nome, descricao, valor, status, acoes);
            lista.appendChild(item);

        });
    } catch (erro) {
        console.error("Erro ao carregar adicionais:", erro);
        lista.textContent =
            "Não foi possível carregar os adicionais. Verifique se o Django está rodando e se a API está acessível.";
    }
}


async function salvarAdicional() {
    const nome = document.getElementById("adicionalNome").value.trim();
    const descricao = document.getElementById("adicionalDescricao").value.trim();
    const valor = document.getElementById("adicionalValor").value;

    if (!nome) {
        alert("Informe o nome do adicional.");
        return;
    }

    if (valor === "" || !Number.isFinite(Number(valor)) || Number(valor) < 0) {
        alert("Informe um valor válido para o adicional.");
        return;
    }

    const botao = document.querySelector(
        "#conteudoConfiguracoes .btn-salvar-config"
    );

    if (botao) {
        botao.disabled = true;
        botao.textContent = "Salvando...";
    }

    try {
        const resposta = await fetchAdmin(`${API_URL}/adicionais/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome: nome,
                descricao: descricao,
                valor: Number(valor).toFixed(2),
                ativo: true
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            const mensagem = Object.entries(dados)
                .map(([campo, erro]) => {
                    const detalhe = Array.isArray(erro)
                        ? erro.join(", ")
                        : typeof erro === "string"
                            ? erro
                            : JSON.stringify(erro);

                    return `${campo}: ${detalhe}`;
                })
                .join("\n");

            throw new Error(
                mensagem || `Erro ao cadastrar. Código: ${resposta.status}`
            );
        }

        alert("Adicional cadastrado com sucesso!");

        document.getElementById("adicionalNome").value = "";
        document.getElementById("adicionalDescricao").value = "";
        document.getElementById("adicionalValor").value = "";

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao salvar adicional:", erro);
        alert("Não foi possível cadastrar o adicional:\n" + erro.message);
    } finally {
        if (botao) {
            botao.disabled = false;
            botao.textContent = "Salvar adicional";
        }
    }
}

window.salvarAdicional = salvarAdicional;


async function alterarStatusAdicional(adicional) {
    const novoStatus = !adicional.ativo;

    const acao = novoStatus ? "ativar" : "desativar";

    const confirmar = confirm(
        `Deseja realmente ${acao} o adicional "${adicional.nome}"?`
    );

    if (!confirmar) return;

    try {
        const resposta = await fetchAdmin(
            `${API_URL}/adicionais/${adicional.id}/`,
            {
                method: "PATCH",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    ativo: novoStatus
                })
            }
        );

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            throw new Error(
                JSON.stringify(dados) || `Erro HTTP ${resposta.status}`
            );
        }

        alert(
            `Adicional ${novoStatus ? "ativado" : "desativado"} com sucesso!`
        );

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao alterar status do adicional:", erro);

        alert(
            "Não foi possível alterar o status do adicional.\n" +
            erro.message
        );
    }
}

window.alterarStatusAdicional = alterarStatusAdicional;


async function excluirAdicional(adicional) {
    const confirmar = confirm(
        `Tem certeza que deseja excluir o adicional "${adicional.nome}"?\n\nEssa ação não poderá ser desfeita.`
    );

    if (!confirmar) return;

    try {
        const resposta = await fetchAdmin(
            `${API_URL}/adicionais/${adicional.id}/`,
            {
                method: "DELETE"
            }
        );

        if (!resposta.ok) {
            const mensagem = await resposta.text();

            throw new Error(
                mensagem || `Erro HTTP ${resposta.status}`
            );
        }

        alert("Adicional excluído com sucesso!");

        await carregarAdicionais();

    } catch (erro) {
        console.error("Erro ao excluir adicional:", erro);

        alert(
            "Não foi possível excluir o adicional.\n" +
            erro.message
        );
    }
}

window.excluirAdicional = excluirAdicional;


function editarAdicional(adicional) {
    const conteudo=document.getElementById('conteudoConfiguracoes');if(!conteudo)return;
    const el=(tag,cls,text,parent)=>{const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=text;parent?.appendChild(n);return n;};
    const head=el('div','cabecalho-configuracoes',undefined,conteudo);const back=el('button','btn-voltar-config','Voltar',head);back.addEventListener('click',abrirAdicionais);el('h2','','Editar Adicional',head);
    const form=el('div','form-configuracoes',undefined,conteudo);
    const field=(label,id,tag,value)=>{el('label','',label,form);const n=el(tag,'',undefined,form);n.id=id;if(tag==='textarea')n.value=value||'';else n.value=value??'';return n;};
    field('Nome','editarAdicionalNome','input',adicional.nome);field('Descrição','editarAdicionalDescricao','textarea',adicional.descricao);field('Valor (R$)','editarAdicionalValor','input',Number(adicional.valor));
    const save=el('button','btn-salvar-config','Salvar alterações',form);save.addEventListener('click',()=>salvarEdicaoAdicional(Number(adicional.id)));
}

window.editarAdicional = editarAdicional;

async function salvarEdicaoAdicional(id) {
    const nome = document
        .getElementById("editarAdicionalNome")
        .value.trim();

    const descricao = document
        .getElementById("editarAdicionalDescricao")
        .value.trim();

    const valor = document
        .getElementById("editarAdicionalValor")
        .value;

    if (!nome) {
        alert("Informe o nome do adicional.");
        return;
    }

    if (
        valor === "" ||
        !Number.isFinite(Number(valor)) ||
        Number(valor) < 0
    ) {
        alert("Informe um valor válido.");
        return;
    }

    try {
        const resposta = await fetchAdmin(`${API_URL}/adicionais/${id}/`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nome: nome,
                descricao: descricao,
                valor: Number(valor).toFixed(2)
            })
        });

        const dados = await resposta.json().catch(() => ({}));

        if (!resposta.ok) {
            const mensagem = Object.entries(dados)
                .map(([campo, erro]) => {
                    const detalhe = Array.isArray(erro)
                        ? erro.join(", ")
                        : typeof erro === "string"
                            ? erro
                            : JSON.stringify(erro);

                    return `${campo}: ${detalhe}`;
                })
                .join("\n");

            throw new Error(
                mensagem || `Erro HTTP ${resposta.status}`
            );
        }

        alert("Adicional atualizado com sucesso!");

        abrirAdicionais();
    } catch (erro) {
        console.error("Erro ao editar adicional:", erro);
        alert("Não foi possível atualizar o adicional:\n" + erro.message);
    }
}

window.salvarEdicaoAdicional = salvarEdicaoAdicional;


async function carregarDiasBloqueados() {
    const lista = document.getElementById("listaDiasBloqueados");

    if (!lista) {
        return;
    }

    try {
        const resposta = await fetchAdmin(
            `${API_URL}/dias-bloqueados/`
        );

        if (!resposta.ok) {
            throw new Error("Erro ao carregar dias bloqueados.");
        }

        const dias = await resposta.json();

        if (dias.length === 0) {
            lista.innerHTML = `
                <p class="mensagem-clientes">
                    Nenhum dia bloqueado cadastrado.
                </p>
            `;
            return;
        }

        lista.replaceChildren();
        dias.forEach(dia => {
            const [ano, mes, numero] = (dia.data||'').split('-');
            const row=document.createElement('div');row.className='cliente-resultado';const details=document.createElement('div');
            const date=document.createElement('strong');date.textContent='👤 '+[numero,mes,ano].join('/');details.appendChild(date);
            const reason=document.createElement('p');reason.textContent='Motivo: '+(dia.motivo||'Não informado');details.appendChild(reason);
            const button=document.createElement('button');button.className='btn-voltar-cliente';button.textContent='Remover';button.addEventListener('click',()=>excluirDiaBloqueado(dia.id));row.append(details,button);lista.appendChild(row);
        });

    } catch (erro) {
        console.error("Erro ao carregar dias bloqueados:", erro);

        lista.innerHTML = `
            <p class="mensagem-clientes">
                Não foi possível carregar as datas bloqueadas.
            </p>
        `;
    }
}

window.carregarDiasBloqueados = carregarDiasBloqueados;


async function salvarDiaBloqueado() {
    const campoData = document.getElementById("dataBloqueio");
    const campoMotivo = document.getElementById("motivoBloqueio");

    const data = campoData.value;
    const motivo = campoMotivo.value.trim();

    if (!data) {
        alert("Selecione a data que deseja bloquear.");
        return;
    }

    try {
        const resposta = await fetchAdmin(
            `${API_URL}/dias-bloqueados/`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    data: data,
                    motivo: motivo
                })
            }
        );

        const dados = await resposta.json();

        if (!resposta.ok) {
            if (dados.data) {
                alert(
                    "Não foi possível bloquear essa data. " +
                    "Ela pode já estar cadastrada."
                );
            } else {
                alert("Erro ao cadastrar o bloqueio.");
            }

            console.error("Erro da API:", dados);
            return;
        }

        alert("Dia bloqueado com sucesso!");

        campoData.value = "";
        campoMotivo.value = "";

        await carregarDiasBloqueados();

    } catch (erro) {
        console.error("Erro ao salvar dia bloqueado:", erro);
        alert("Não foi possível conectar ao servidor.");
    }
}

window.salvarDiaBloqueado = salvarDiaBloqueado;


async function excluirDiaBloqueado(id) {
    const confirmar = confirm(
        "Tem certeza de que deseja remover este bloqueio?"
    );

    if (!confirmar) {
        return;
    }

    try {
        const resposta = await fetchAdmin(
            `${API_URL}/dias-bloqueados/${id}/`,
            {
                method: "DELETE"
            }
        );

        if (!resposta.ok) {
            throw new Error("Erro ao remover o bloqueio.");
        }

        alert("Bloqueio removido com sucesso!");

        await carregarDiasBloqueados();

    } catch (erro) {
        console.error("Erro ao remover dia bloqueado:", erro);

        alert("Não foi possível remover o bloqueio.");
    }
}

window.excluirDiaBloqueado = excluirDiaBloqueado;


async function carregarCupons() {
    const lista = document.getElementById("listaCupons");

    if (!lista) {
        console.error("Elemento listaCupons não encontrado.");
        return;
    }

    lista.textContent = "Carregando cupons...";

    try {
        const resposta = await fetchAdmin(`${API_URL}/cupons/`);

        if (!resposta.ok) {
            throw new Error(`Erro HTTP ${resposta.status}`);
        }

        const dados = await resposta.json();

        if (!Array.isArray(dados) || dados.length === 0) {
            lista.textContent = "Nenhum cupom cadastrado.";
            return;
        }

        lista.replaceChildren();

        dados.forEach((cupom) => {
            const item = document.createElement("div");
            item.className = "cliente-resultado";

            const codigo = document.createElement("strong");
            codigo.textContent = cupom.codigo;

            const desconto = document.createElement("p");
            desconto.textContent =
                cupom.tipo_desconto === "percentual"
                    ? `Desconto: ${cupom.valor}%`
                    : `Desconto: R$ ${Number(cupom.valor).toFixed(2)}`;

            const usos = document.createElement("p");
            usos.textContent =
                `Utilizações: ${cupom.uso_atual}/${cupom.uso_maximo}`;

            const validade = document.createElement("p");
            validade.textContent =
                `Validade: ${new Date(
                    cupom.validade + "T12:00:00"
                ).toLocaleDateString("pt-BR")}`;

            const status = document.createElement("p");
            status.textContent = cupom.ativo
                ? "Status: Ativo"
                : "Status: Inativo";

            const botaoEditar = document.createElement("button");
            botaoEditar.type = "button";
            botaoEditar.textContent = "Editar";

            botaoEditar.addEventListener("click", () => {
                editarCupom(cupom);
            });

            const botao = document.createElement("button");
            botao.type = "button";
            botao.textContent = cupom.ativo
                ? "Desativar cupom"
                : "Ativar cupom";

            botao.addEventListener("click", () => {
                alterarStatusCupom(cupom.id, !cupom.ativo);
            });

            item.append(
                codigo,
                desconto,
                usos,
                validade,
                status,
                botaoEditar,
                botao
            );

            lista.appendChild(item);
        });

    } catch (erro) {
        console.error("Erro ao carregar cupons:", erro);
        lista.textContent =
            "Erro ao carregar cupons. Confira o Console (F12).";
    }
}

window.carregarCupons = carregarCupons;


function editarCupom(cupom) {
    document.getElementById("cupomCodigo").value = cupom.codigo;
    document.getElementById("cupomTipo").value = cupom.tipo_desconto;
    document.getElementById("cupomValor").value = cupom.valor;
    document.getElementById("cupomUsoMaximo").value = cupom.uso_maximo;
    document.getElementById("cupomValidade").value = cupom.validade;

    // Guarda o ID do cupom que será editado
    let campoId = document.getElementById("cupomIdEdicao");

    if (!campoId) {
        campoId = document.createElement("input");
        campoId.type = "hidden";
        campoId.id = "cupomIdEdicao";

        const formulario = document.querySelector(".form-configuracoes");

        if (formulario) {
            formulario.appendChild(campoId);
        }
    }

    campoId.value = cupom.id;

    // Altera o título e o texto do botão
    const titulo = document.querySelector(".form-configuracoes h3");
    const botaoSalvar = document.querySelector(
        ".form-configuracoes .btn-salvar-config"
    );

    if (titulo) {
        titulo.textContent = "Editar cupom";
    }

    if (botaoSalvar) {
        botaoSalvar.textContent = "Salvar alterações";
    }

    // Leva a tela até o formulário
    document.querySelector(".form-configuracoes")?.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}

window.editarCupom = editarCupom;
