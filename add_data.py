import pymysql
import random

conn = pymysql.connect(host='localhost', port=3306, user='root', password='12345678', db=f'前台数据')
cursor = conn.cursor(pymysql.cursors.DictCursor)
status_list = ['occupation', 'unoccupied']

for floor in range(1, 11):
    for room in range(1, 16):
        if room // 10 >= 1:
            room_name = f'{floor}{room}'
        else:
            room_name = f'{floor}0{room}'

        try:
            status = status_list[random.choice([0, 1])]
            if status== 'occupation':
                cursor.execute(
                    f"INSERT INTO `rooms` (`floor_number`,`room_number`, `status`, `water_fee`, `electricity_fee`, `name`, `phone`, `checkin`, `checkout`) "
                    f"VALUES (%s,%s, %s, %s, %s,%s, %s,%s, %s);",
                    (floor, room_name, status, round(random.uniform(10.5, 500.5), 1),
                     round(random.uniform(10.5, 500.5), 1), 'hzh', 13456545676, '2024-12-09 16:00', '2024-12-20 12:00'))
            else:
                cursor.execute(
                    f"INSERT INTO `rooms` (`floor_number`,`room_number`, `status`, `water_fee`, `electricity_fee`) "
                    f"VALUES (%s,%s, %s, %s, %s);",
                    (floor, room_name, status, round(random.uniform(10.5, 500.5), 1),
                     round(random.uniform(10.5, 500.5), 1)))


        except:
            print((room_name, status_list[random.choice([0, 1])], round(random.uniform(10.5, 500.5), 1),
                   round(random.uniform(10.5, 500.5), 1)))

conn.commit()
conn.close()
