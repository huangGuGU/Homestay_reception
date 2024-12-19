CREATE DATABASE 前台数据;
use 前台数据;
CREATE TABLE rooms (
    room_id INT AUTO_INCREMENT PRIMARY KEY,
    floor_number INT NOT NULL,
    room_number VARCHAR(10) NOT NULL,  -- 房间号
    status VARCHAR(20),  -- 房间状态（空闲、入住等）
    water_fee DECIMAL(10, 2),
    electricity_fee DECIMAL(10, 2),
    name VARCHAR(20),
    phone VARCHAR(20),
    checkin DATETIME,
    checkout DATETIME

);


SELECT * FROM `rooms`;
INSERT INTO `rooms` (`room_number`, `status`, `water_fee`, `electricity_fee`)
VALUES ('105', 'occupation', 201.00, 100.00);