"""BRICAS Day 3 interactive risk analysis dashboard."""
import pandas as pd
import streamlit as st
from anomaly_day3 import build_findings, export_findings

st.set_page_config(page_title='BRICAS | Risk & Audit', layout='wide')
st.title('BRICAS | Risk Intelligence & Audit Evidence')
st.caption('Synthetic banking data. Illustrative screening rules and robust statistics; alerts are not confirmed fraud.')
try:
    df = build_findings()
except (FileNotFoundError, ValueError) as exc:
    st.error(str(exc))
    st.stop()

st.sidebar.header('Audit filters')
regions = st.sidebar.multiselect('Customer region', sorted(df.region.unique()), default=sorted(df.region.unique()))
severity = st.sidebar.multiselect('Risk severity', ['LOW','MEDIUM','HIGH','CRITICAL'], default=['LOW','MEDIUM','HIGH','CRITICAL'])
filtered = df[df.region.isin(regions) & df.severity.isin(severity)].copy()
flagged = filtered[filtered.review_status == 'REVIEW_REQUIRED']
c1,c2,c3,c4 = st.columns(4)
c1.metric('Transactions in scope', f'{len(filtered):,}')
c2.metric('Review-required alerts', f'{len(flagged):,}')
c3.metric('Statistical anomalies', f'{int(filtered.statistical_anomaly.sum()):,}')
c4.metric('Total amount (BDT)', f'{filtered.amount_bdt.sum():,.0f}')
st.subheader('Severity distribution')
st.bar_chart(filtered.severity.value_counts().reindex(['LOW','MEDIUM','HIGH','CRITICAL'],fill_value=0))
st.subheader('Daily review-required alerts')
if not flagged.empty:
    st.line_chart(flagged.groupby('tx_day').size().rename('Alerts'))
else:
    st.info('No alerts match the selected filters.')
st.subheader('Audit evidence — flagged transactions')
cols = ['transaction_id','timestamp','account_id','region','amount_bdt','direction','risk_score','severity','robust_z','risk_reasons','review_status']
st.dataframe(flagged[cols], hide_index=True, width='stretch')
st.download_button('Download filtered audit evidence', flagged[cols].to_csv(index=False).encode('utf-8'), file_name='bricas_day3_filtered_evidence.csv', mime='text/csv')
st.subheader('Statistical anomalies')
st.dataframe(filtered[filtered.statistical_anomaly == 1][cols], hide_index=True, width='stretch')
st.caption('Severity thresholds and statistical cutoff are demonstrative and not calibrated against labeled fraud outcomes.')
