from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title='BRICAS Risk Monitoring',layout='wide')
st.title('BRICAS | Synthetic Banking Risk Monitoring')
st.caption('Portfolio demonstration only — synthetic data, illustrative risk rules, not real fraud findings.')
path=Path(__file__).resolve().parent/'data'/'transactions_export.csv'
if not path.exists():
    st.error('Run python main.py first to generate the dataset.')
    st.stop()
df=pd.read_csv(path)
df['timestamp']=pd.to_datetime(df['timestamp'])
channels=st.multiselect('Direction',sorted(df.direction.unique()),default=sorted(df.direction.unique()))
filtered=df[df.direction.isin(channels)]
c1,c2,c3=st.columns(3)
c1.metric('Transactions',f'{len(filtered):,}')
c2.metric('Alerts (score ≥ 40)',f'{(filtered.risk_score>=40).sum():,}')
c3.metric('Total amount (BDT)',f'{filtered.amount_bdt.sum():,.0f}')
st.subheader('Daily transaction volume')
st.line_chart(filtered.groupby(filtered.timestamp.dt.date).size())
st.subheader('Flagged transactions')
st.dataframe(filtered[filtered.risk_score>=40].sort_values('risk_score',ascending=False).head(200),use_container_width=True)
