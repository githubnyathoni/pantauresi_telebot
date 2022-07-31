from app import apiTracking, serveData
from database import conn, cursor

def check_waybill():
    cursor.execute("SELECT * FROM waybill WHERE NOT status = 'DELIVERED'")
    data = cursor.fetchall()
    for item in data:
        payload = {
            "resi": item[2],
            "kurir": item[3]
        }
        packet = apiTracking(payload)
        print(packet["result"]["summary"]["status"])
        if(str(packet["result"]["manifest"]) == item[4]):
            cursor.execute("UPDATE waybill SET status = ?, manifest = ? WHERE waybill = ?",
            (packet["result"]["summary"]["status"], str(packet["result"]["manifest"]), item[2],))
            conn.commit()
            print("Updated")
            serveData(item[1], packet)

check_waybill()