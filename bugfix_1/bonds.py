from datetime import datetime

def get_summary(fund_code, ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')):
    # Assume below line is writing data to DB
    print(f"BONDS -> {fund_code} is Loaded at time : {ts}")
