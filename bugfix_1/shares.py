from datetime import datetime

def get_summary(fund_code, ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    print(f"SHARS -> {fund_code} is Loaded at time : {ts}")
