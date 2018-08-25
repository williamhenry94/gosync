import pandas as pd
from pymongo import MongoClient
from datetime import datetime
from app.models.GocardHistory import GocardHistory
import time
from app.database import sqla
import hashlib


def parser(x):
    return datetime.strptime(x, '%d/%b/%Y')


def import_csv():

    csv = pd.read_csv('/Users/williamhenry/Documents/GoCard/app/storage/histories/Travel_history.csv',
                      header=0, squeeze=True, date_parser=parser).fillna(value=0)

    date = (csv[' Date'])
    from_station = (csv['From']).tolist()
    to_station = (csv['To']).tolist()
    fare = (csv['Fare']).tolist()
    balance = (csv['Balance']).tolist()
    credit = (csv['Credit']).tolist()
    time0 = (csv["Time"]).tolist()
    time1 = (csv["Time.1"]).tolist()

    for i in range(len(date)):

        if not credit[i] or (str(credit[i])).strip() == '':
            _credit = None
        else:
            _credit = float((credit[i]).strip('$').strip())

        if not fare[i] or (str(fare[i])).strip() == '':
            _fare = None
        else:
            _fare = float((fare[i]).strip('$').strip())

        if not balance[i] or (str(balance[i])).strip() == '':
            _balance = None
        else:
            _balance = float((balance[i]).strip('$').strip())

        from_datetime = (date[i]).strip() + ' ' + (time0[i]).strip()

        if not time1[i]:
            time1[i] = time0[i]
        else:
            time1[i] = time1[i]

        to_datetime = (date[i]).strip() + ' ' + (time1[i]).strip()

        if not to_station[i]:
            to_station[i] = None
        else:
            to_station[i] = (to_station[i]).strip()

        row_id = (hashlib.sha256(
            ((from_station[i]).strip() + '_' + from_datetime).encode())).hexdigest()

        from_datetime = datetime.strptime(from_datetime, '%d/%b/%Y %H:%M %p')
        to_datetime = datetime.strptime(to_datetime, '%d/%b/%Y %H:%M %p')

        hist_data = GocardHistory.query.filter_by(hashed_id=row_id).first()
        if not hist_data:
            history = GocardHistory(from_station=(from_station[i]).strip(), to_station=to_station[i], fare=_fare,
                                    credit=_credit, from_datetime=from_datetime, to_datetime=to_datetime, balance=_balance, deleted_at=None, hashed_id=row_id)

            sqla.session.add(history)
            sqla.session.commit()
            sqla.session.refresh(history)
