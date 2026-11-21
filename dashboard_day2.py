from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='BRICAS | Continuous Audit', layout='wide')
st.title('BRICAS | Banking Risk Intelligence')
st.caption('Synthetic data • illustrative risk rules • alerts require human review; not proof of fraud.')
DATA = Path(__file__).resolve().parent / 'data'
required = ['transactions_export.csv', 'ews_alerts.csv', 'daily_audit_summary.csv', 'account_risk_summary.csv']
missing = [name for name in required if not (DATA/name).exists()]
if missing:
    st.error('Missing files: ' + ', '.join(missing) + '. Run python main.py then python ews.py.')
    st.stop()
tx = pd.read_csv(DATA/'transactions_export.csv')
alerts = pd.read_csv(DATA/'ews_alerts.csv')
daily = pd.read_csv(DATA/'daily_audit_summary.csv')
accounts = pd.read_csv(DATA/'account_risk_summary.csv')

st.sidebar.header('Filters')
regions = st.sidebar.multiselect('Customer region', sorted(accounts.region.unique()), default=sorted(accounts.region.unique()))
allowed = set(accounts.loc[accounts.region.isin(regions),'account_id'])
filtered_tx = tx[tx.account_id.isin(allowed)].copy()
filtered_alerts = alerts[alerts.account_id.isin(allowed)]
c1,c2,c3,c4=st.columns(4)
c1.metric('Transactions', f'{len(filtered_tx):,}')
c2.metric('Risk alerts (EWS)', f'{len(filtered_alerts):,}')
c3.metric('Total amount (BDT)', f'{filtered_tx.amount_bdt.sum():,.0f}')
c4.metric('Accounts in scope', f'{len(allowed):,}')
st.subheader('Daily transaction trend')
filtered_tx['day'] = pd.to_datetime(filtered_tx.timestamp).dt.date
st.line_chart(filtered_tx.groupby('day').size().rename('Transactions'))
st.subheader('EWS alerts requiring review')
st.dataframe(filtered_alerts, width='stretch', hide_index=True)
st.download_button('Download filtered alerts CSV', filtered_alerts.to_csv(index=False).encode('utf-8'), file_name='bricas_ews_filtered.csv', mime='text/csv')
st.subheader('Account-level audit summary')
st.dataframe(accounts[accounts.region.isin(regions)].head(100), width='stretch', hide_index=True)
st.download_button('Download account summary CSV', accounts[accounts.region.isin(regions)].to_csv(index=False).encode('utf-8'), file_name='bricas_accounts_filtered.csv', mime='text/csv')
st.caption('Day 1 alert counts may differ: Day 2 adds a repeated-high-value rule.')
