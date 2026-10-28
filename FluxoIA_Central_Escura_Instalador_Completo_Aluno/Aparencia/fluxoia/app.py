"""FluxoIA: painel demonstrativo totalmente offline após a etapa preparar.py."""
from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from modelo_utils import preparar_calendario

BASE=Path(__file__).resolve().parent
ARTEFATOS=BASE/'artefatos'

st.set_page_config(page_title='FluxoIA | Central de Controle',page_icon='🚦',layout='wide')
# Somente estilo: não altera modelos, dados, parâmetros, previsões ou YOLO.
CSS = BASE / 'estilo_central.css'
if CSS.exists():
    st.markdown('<style>' + CSS.read_text(encoding='utf-8') + '</style>', unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def carregar_modelo():
    return joblib.load(ARTEFATOS/'modelo_fluxo.joblib')

@st.cache_data(show_spinner=False)
def carregar_dados():
    resumo=json.loads((ARTEFATOS/'metricas.json').read_text(encoding='utf-8'))
    teste=pd.read_csv(ARTEFATOS/'demonstracao_teste.csv',parse_dates=['date_time'])
    return resumo,teste


def pt(valor,casas=0):
    return f'{valor:,.{casas}f}'.replace(',','_').replace('.',',').replace('_','.')


def prever_data(modelo,datas):
    entrada=preparar_calendario(pd.Series(pd.to_datetime(datas)))
    return np.maximum(0,modelo['modelo'].predict(entrada))


def grafico_padrao(fig,height=310):
    # Paleta escura; preserva integralmente as séries e seus valores.
    fig.update_layout(height=height,margin=dict(l=8,r=12,t=21,b=24),
                      plot_bgcolor='#0f2031',paper_bgcolor='#0f2031',
                      font=dict(color='#b4c9dc',size=12),showlegend=True,
                      legend=dict(orientation='h',y=-.26,x=0,font=dict(size=11)),
                      hoverlabel=dict(bgcolor='#1a3349',font_color='#eefaff',bordercolor='#32718d'))
    fig.update_xaxes(showgrid=False,linecolor='#35506a',tickfont=dict(color='#93aec4'))
    fig.update_yaxes(gridcolor='#243a4e',zeroline=False,minor=dict(showgrid=False),tickfont=dict(color='#93aec4'))
    return fig


# Identidade e enquadramento do protótipo; links e botões da aplicação permanecem nativos.
with st.sidebar:
    st.markdown('''<div class="side-logo"><div class="side-logo-icon">≋</div>
      <div><div class="side-logo-name">FluxoIA</div><div class="side-logo-caption">TRAFFIC INTELLIGENCE</div></div></div>
      <div class="side-heading">CENTRAL DE CONTROLE</div>
      <div class="side-item"><em>01</em> Previsões e validação <strong>ML</strong></div>
      <div class="side-item"><em>02</em> Planejamento e dados <strong>UCI</strong></div>
      <div class="side-item"><em>03</em> Supervisão inteligente <strong>YOLO</strong></div>
      <div class="side-note"><b>Fonte de dados</b><br>Rodovia I-94, Minnesota (EUA). O sistema é um protótipo educacional, não monitora o trânsito de Cuiabá ao vivo.</div>
      <div class="side-heading">PROJETO ACADÊMICO</div>
      <div class="side-footer">SENAC · UC9 · GRUPO 6</div>''',unsafe_allow_html=True)

st.markdown('''<div class="top-ribbon"><div class="ribbon-title"><span class="fx-dot"></span> FLUXOIA / SISTEMA DE ANÁLISE VIÁRIA</div><div class="ribbon-meta">CENTRAL DE CONTROLE · VERSÃO DEMONSTRATIVA</div></div>
<div class="mission-hero">
  <div><div class="hero-eyebrow">▣ &nbsp; MACHINE LEARNING + VISÃO COMPUTACIONAL</div>
    <h1>Dados que antecipam.<br><span>IA que observa.</span></h1>
    <p>Previsão de fluxo por horário, apoio ao planejamento viário e supervisão de vídeos em uma única plataforma.</p>
    <div class="hero-tags"><span>● RANDOM FOREST</span><span>◈ STREAMLIT</span><span>▣ YOLO11n</span></div>
  </div>
  <div class="radar"><div class="radar-center"><b>03</b><span>MÓDULOS</span></div></div>
</div>
<div class="status-strip">
 <div class="status-tile"><i>⌁</i><div><small>MODELO PREDITIVO</small><strong>Random Forest · treinado</strong></div></div>
 <div class="status-tile"><i>◫</i><div><small>BASE DE REFERÊNCIA</small><strong>UCI · Tráfego histórico I-94</strong></div></div>
 <div class="status-tile"><i>▣</i><div><small>SUPERVISÃO</small><strong>Análise de arquivos MP4</strong></div></div>
</div>''',unsafe_allow_html=True)

faltando=[p for p in ['modelo_fluxo.joblib','metricas.json','demonstracao_teste.csv'] if not (ARTEFATOS/p).exists()]
if faltando:
    st.warning('O modelo ainda não foi treinado neste computador. Nenhum resultado foi inventado.')
    st.code('python preparar.py\nstreamlit run app.py',language='bash')
    st.info('A preparação obtém a base pública da UCI uma vez, treina e compara os modelos, salva as métricas e os exemplos. Depois o painel funciona offline.')
    st.stop()

try:
    pacote=carregar_modelo(); meta,dados=carregar_dados()
except Exception as e:
    st.error(f'Erro ao abrir os arquivos treinados: {e}')
    st.stop()

selecionado=meta['selecionado']
met=meta['resultados'][selecionado]['teste']
base=meta['resultados']['Baseline por dia/hora']['teste']

st.markdown('<div class="module-kicker">PAINÉIS OPERACIONAIS</div><div class="module-description">Escolha um módulo para explorar os modelos, validar os resultados ou analisar um vídeo de trânsito.</div>',unsafe_allow_html=True)

# Navegação permanece nativa e operacional: todos os controles e cálculos originais são mantidos.
aba_previsoes, aba_planejamento, aba_supervisao = st.tabs([
    '📈 Previsões e validação',
    '🛠️ Planejamento e dados',
    '📹 Supervisão inteligente',
])

with aba_previsoes:
    st.markdown('<div class="module-kicker">01 / ANÁLISE PREDITIVA</div><div class="module-description">Estimativas baseadas em padrões temporais e confronto com dados históricos de teste.</div>',unsafe_allow_html=True)
    c1,c2,c3,c4=st.columns(4)
    c1.metric('Modelo selecionado',selecionado)
    c2.metric('MAE no teste',f"{pt(met['mae'])} veículos")
    c3.metric('Baseline MAE',f"{pt(base['mae'])} veículos")
    c4.metric('Registros históricos',pt(meta['origem_linhas']))
    st.write('')

    # PREVISÃO LIVRE: usa somente atributos conhecidos do calendário, sem API e sem novo treino.
    st.subheader('Previsão de volume · data e horário')
    st.markdown('<div class="section-banner">Informe um horário para estimar o volume de veículos por hora. <b>Não é um monitoramento em tempo real:</b> o resultado usa padrões históricos de calendário.</div>',unsafe_allow_html=True)
    hoje = datetime.now()
    cl1, cl2 = st.columns([1, 1], gap='medium')
    with cl1:
        data_livre = st.date_input('Data da previsão', value=hoje.date(), key='data_livre', format='DD/MM/YYYY')
    with cl2:
        hora_livre = st.selectbox('Hora da previsão', options=list(range(24)), index=hoje.hour,
                                 format_func=lambda h: f'{h:02d}:00', key='hora_livre')

    # Calcula o ponto escolhido e uma curva de 24 h com as mesmas variáveis do treinamento.
    instante = pd.Timestamp(data_livre) + pd.Timedelta(hours=int(hora_livre))
    horas_livres = pd.date_range(pd.Timestamp(data_livre), periods=24, freq='h')
    previsoes_livres = prever_data(pacote, horas_livres)
    prev_livre = float(previsoes_livres[int(hora_livre)])
    # Baseline não depende de rede: médias históricas salvas durante a etapa preparar.py.
    grupo_base = pacote.get('baseline_grupo', {})
    hora_base = pacote.get('baseline_hora', {})
    geral_base = float(pacote.get('baseline_geral', 0))
    def media_simples_calendario(dia_semana, hora):
        return float(grupo_base.get((int(dia_semana), int(hora)),
                                    hora_base.get(int(hora), geral_base)))
    comparacao_livre = [media_simples_calendario(dia_l.weekday(), dia_l.hour)
                        for dia_l in horas_livres]

    m1,m2,m3 = st.columns(3)
    m1.metric('Previsão do Random Forest', f'{pt(prev_livre)} veículos/h')
    m2.metric('Média histórica de referência', f'{pt(comparacao_livre[hora_livre])} veículos/h')
    m3.metric('Data e horário escolhidos', instante.strftime('%d/%m/%Y · %Hh'))

    fig_livre = go.Figure()
    fig_livre.add_trace(go.Scatter(x=horas_livres, y=previsoes_livres, mode='lines+markers',
                                  name='Previsão do Random Forest', line=dict(color='#51dce8', width=3)))
    fig_livre.add_trace(go.Scatter(x=horas_livres, y=comparacao_livre, mode='lines',
                                  name='Baseline histórico', line=dict(color='#7296ff', width=2, dash='dash')))
    fig_livre.add_vline(x=instante, line_dash='dot', line_color='#f6bc69', line_width=2)
    fig_livre.update_yaxes(title_text='Veículos por hora')
    st.plotly_chart(grafico_padrao(fig_livre, 315), use_container_width=True)

    opcoes_operacao = range(9, 19)
    mais_tranquilo = min(opcoes_operacao, key=lambda h: float(previsoes_livres[h]))

    st.divider()
    st.subheader('Validação histórica · previsão × observado')
    st.caption('Este painel exibe exemplos separados do treinamento (conjunto de teste).')
    dados['data']=dados['date_time'].dt.date
    datas=dados['data'].drop_duplicates().to_list()
    if not datas:st.error('Conjunto de teste vazio.');st.stop()

    esq,dir=st.columns([1,2],gap='large')
    with esq:
        data=st.selectbox('Dia observado (teste)',datas,index=min(len(datas)-1,max(0,len(datas)//3)),format_func=lambda d:pd.Timestamp(d).strftime('%d/%m/%Y'))
        desse_dia=dados[dados['data']==data].copy().sort_values('date_time')
        hora=st.selectbox('Horário',list(desse_dia['date_time'].dt.strftime('%H:%M').values),index=min(10,len(desse_dia)-1))
        registro=desse_dia.loc[desse_dia['date_time'].dt.strftime('%H:%M')==hora].iloc[0]
        st.metric('Previsão do modelo',f"{pt(registro['pred_modelo'])} veículos/h")
        st.metric('Volume real observado',f"{pt(registro['traffic_volume'])} veículos/h")
        st.caption(f"Erro absoluto neste exemplo: {pt(abs(registro['pred_modelo']-registro['traffic_volume']))} veículos/h.")
        st.write('**Para que serve?** Um gestor pode comparar períodos e avaliar quando uma intervenção teria menor exposição ao tráfego.')
    with dir:
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=desse_dia['date_time'],y=desse_dia['traffic_volume'],name='Volume observado',mode='lines+markers',line=dict(color='#6c91f8',width=3)))
        fig.add_trace(go.Scatter(x=desse_dia['date_time'],y=desse_dia['pred_modelo'],name='Previsão IA',mode='lines+markers',line=dict(color='#54d5dc',width=2,dash='dash')))
        fig.update_yaxes(title_text='Veículos por hora')
        st.plotly_chart(grafico_padrao(fig,330),use_container_width=True)
        st.caption('Os dois valores correspondem a horários históricos; não se trata de previsão em tempo real.')


with aba_planejamento:
    st.markdown('<div class="module-kicker">02 / PLANEJAMENTO OPERACIONAL</div><div class="module-description">Explore os padrões de demanda e avalie um cenário hipotético de manutenção viária.</div>',unsafe_allow_html=True)
    st.subheader('Planejamento de manutenção · simulação')
    st.markdown('<div class="section-banner">O custo por veículo é <b>hipotético</b>. Os resultados são simulações históricas e <b>não representam economia operacional comprovada</b>.</div>',unsafe_allow_html=True)
    candidatos=desse_dia[desse_dia['date_time'].dt.hour.between(9,18)].copy()
    if not candidatos.empty:
        escolhido=candidatos.loc[candidatos['pred_modelo'].idxmin()]
        fixo=candidatos[candidatos['date_time'].dt.hour==16]
        if not fixo.empty:
            custo_por_carro=st.slider('Custo hipotético por veículo exposto à intervenção (R$)',0.0,1.0,0.10,step=0.05)
            baseline_obs=float(fixo.iloc[0]['traffic_volume']);sugerido_obs=float(escolhido['traffic_volume'])
            a,b,c=st.columns(3)
            a.metric('Horário com menor previsão',escolhido['date_time'].strftime('%Hh'))
            b.metric('Volume real nesse horário',f'{pt(sugerido_obs)} veículos')
            c.metric('Diferença hipotética de custo',f'R$ {pt((baseline_obs-sugerido_obs)*custo_por_carro,2)}')
        else:
            st.info('Este dia não contém registro de 16h para comparação.')
    else:
        st.info('Não há horas entre 9h e 18h suficientes para esta demonstração.')

    st.subheader('Panorama de tráfego · padrões históricos')
    l,r=st.columns(2,gap='medium')
    eda=meta['eda']
    with l:
        fig=px.bar(pd.DataFrame(eda['media_por_hora']),x='hora',y='volume',labels={'hora':'Hora do dia','volume':'Veículos/h (média)'},color_discrete_sequence=['#5b95f6'])
        st.plotly_chart(grafico_padrao(fig,300),use_container_width=True)
    with r:
        df=pd.DataFrame(eda['media_por_dia_semana'])
        df['dia']=df['dia'].map({0:'Seg',1:'Ter',2:'Qua',3:'Qui',4:'Sex',5:'Sáb',6:'Dom'})
        fig=px.bar(df,x='dia',y='volume',labels={'dia':'Dia da semana','volume':'Veículos/h (média)'},color_discrete_sequence=['#49cadb'])
        st.plotly_chart(grafico_padrao(fig,300),use_container_width=True)
        st.caption('Padrão semanal da rodovia monitorada nos Estados Unidos.')




with aba_supervisao:
    st.markdown('<div class="module-kicker">03 / VISÃO COMPUTACIONAL</div><div class="module-description">Central de supervisão para vídeos MP4: detecção, identificação, cruzamentos de linha e sinais de parada prolongada.</div>',unsafe_allow_html=True)
    st.markdown('<div class="section-banner">O módulo YOLO processa um <b>vídeo enviado pelo usuário</b>. Alertas de parada são indícios para verificação humana, <b>não confirmação de acidentes</b>.</div>',unsafe_allow_html=True)
    from supervisao import mostrar_supervisao
    mostrar_supervisao()

