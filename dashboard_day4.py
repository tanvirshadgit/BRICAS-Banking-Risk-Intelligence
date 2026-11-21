"""BRICAS Day 4 executive dashboard."""
import pandas as pd
import streamlit as st
from anomaly_day3 import build_findings
from executive_day4 import summarize, export_reports

st.set_page_config(page_title='BRICAS | Executive Audit',layout='wide')
st.title('BRICAS | Executive Risk & Continuous Audit')
st.caption('Synthetic data • Illustrative risk indicators • Alerts require human review; not proven fraud or regulatory breaches')
try:
    df=build_findings()
except (FileNotFoundError,ValueError) as exc:
    st.error(str(exc)); st.stop()
regions=st.sidebar.multiselect('Customer region',sorted(df.region.unique()),default=sorted(df.region.unique()))
severities=st.sidebar.multiselect('Risk severity',['LOW','MEDIUM','HIGH','CRITICAL'],default=['LOW','MEDIUM','HIGH','CRITICAL'])
filtered=df[df.region.isin(regions)&df.severity.isin(severities)].copy()
metrics=summarize(filtered)
c1,c2,c3,c4=st.columns(4)
c1.metric('Transactions',f"{metrics['transactions']:,}")
c2.metric('Review-required alerts',f"{metrics['alerts']:,}")
c3.metric('Alert rate',f"{metrics['alert_rate_pct']:.2f}%")
c4.metric('Amount (BDT)',f"{metrics['amount_bdt']:,.0f}")
c5,c6,c7=st.columns(3)
c5.metric('Accounts in scope',f"{metrics['accounts']:,}")
c6.metric('Statistical anomalies',f"{metrics['statistical_anomalies']:,}")
c7.metric('Critical review alerts',f"{metrics['critical_alerts']:,}")
left,right=st.columns(2)
with left:
    st.subheader('Severity distribution')
    st.bar_chart(filtered.severity.value_counts().reindex(['LOW','MEDIUM','HIGH','CRITICAL'],fill_value=0))
with right:
    st.subheader('Regional alert counts')
    region_alerts=filtered.assign(is_alert=filtered.review_status.eq('REVIEW_REQUIRED').astype(int)).groupby('region')['is_alert'].sum()
    st.bar_chart(region_alerts)
st.subheader('Daily monitoring')
if not filtered.empty:
    daily=filtered.assign(is_alert=filtered.review_status.eq('REVIEW_REQUIRED').astype(int)).groupby('tx_day').agg(transactions=('transaction_id','size'),alerts=('is_alert','sum'))
    st.line_chart(daily)
else:
    st.info('No records match current filters.')
st.subheader('Audit evidence — review required')
evidence=filtered.loc[filtered.review_status.eq('REVIEW_REQUIRED'),['transaction_id','timestamp','account_id','region','amount_bdt','risk_score','severity','risk_reasons']].sort_values(['risk_score','amount_bdt'],ascending=False)
st.dataframe(evidence,hide_index=True,width='stretch')
st.download_button('Download filtered evidence CSV',evidence.to_csv(index=False).encode(),file_name='bricas_filtered_evidence.csv',mime='text/csv')
st.subheader('Account review priorities')
if not evidence.empty:
    accounts=evidence.groupby('account_id').agg(alerts=('transaction_id','size'),max_risk_score=('risk_score','max')).sort_values(['alerts','max_risk_score'],ascending=False).head(20)
    st.dataframe(accounts,width='stretch')
else:
    st.info('No review-required records in this selection.')
st.info('Generate the complete executive report and Power BI-ready CSV files by running: python executive_day4.py')
st.caption('Severity categories are illustrative and not validated against actual banking outcomes.')
