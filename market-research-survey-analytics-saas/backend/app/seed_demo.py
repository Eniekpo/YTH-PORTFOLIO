from pathlib import Path
import random
import numpy as np
import pandas as pd

random.seed(42)
np.random.seed(42)
N=850
cities=["Lagos","Abuja","Port Harcourt","Ibadan","Benin City","Enugu"]
genders=["Female","Male","Prefer not to say"]
age_groups=["18-24","25-34","35-44","45-54","55+"]
channels=["Instagram","Google Search","Referral","LinkedIn","Offline"]
products=["Starter","Professional","Enterprise"]
rows=[]
for i in range(1,N+1):
    age=np.random.choice(age_groups,p=[.18,.34,.25,.15,.08])
    plan=np.random.choice(products,p=[.43,.39,.18])
    satisfaction=int(np.clip(round(np.random.normal(4.0 if plan!="Starter" else 3.6,0.9)),1,5))
    nps=int(np.clip(round(np.random.normal(7.8 if satisfaction>=4 else 5.8,2)),0,10))
    rows.append({
        "respondent_id":f"R{i:04d}","city":np.random.choice(cities),
        "gender":np.random.choice(genders,p=[.49,.49,.02]),"age_group":age,
        "acquisition_channel":np.random.choice(channels),"subscription_plan":plan,
        "satisfaction_1_5":satisfaction,"nps_0_10":nps,
        "monthly_spend_ngn":round(max(2500,np.random.lognormal(mean=9.4 if plan=="Starter" else 10.1 if plan=="Professional" else 10.8,sigma=.45)),2),
        "would_recommend":"Yes" if nps>=7 else "No",
        "support_rating_1_5":int(np.clip(round(np.random.normal(satisfaction,0.8)),1,5)),
        "open_feedback":np.random.choice(["Easy to use","Pricing could improve","Support was helpful","Need more integrations","Good overall experience",None],p=[.18,.16,.16,.14,.28,.08])
    })
df=pd.DataFrame(rows)
out=Path(__file__).resolve().parents[2]/"data"/"demo_customer_experience_survey.csv"
out.parent.mkdir(parents=True,exist_ok=True)
df.to_csv(out,index=False)
print(f"Created {out} with {len(df):,} rows")
