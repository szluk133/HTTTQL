CREATE TABLE [users] (
    id INT IDENTITY(1,1) PRIMARY KEY,
    username NVARCHAR(50) NOT NULL UNIQUE,
    password NVARCHAR(255) NOT NULL,
    phone NVARCHAR(15) NULL,
    role NVARCHAR(20) NOT NULL DEFAULT 'user'
);
INSERT INTO [user] (username, password, phone, role)  
VALUES  
    ('banhang', '1', '0901234567', 'banhang'),  
    ('quanly', '1', '0912345678', 'quanly'),  
    ('thukho', '1', '0923456789', 'thukho'),  


CREATE TABLE KhachHang (
    maKhachHang NVARCHAR(10) PRIMARY KEY,
    tenKhachHang NVARCHAR(100) NOT NULL,
    sdt NVARCHAR(15) NOT NULL UNIQUE
);
INSERT INTO KhachHang (maKhachHang, tenKhachHang, sdt)  
VALUES  
    ('KH001', 'A', '0901123456'),  
    ('KH002', 'B', '0912233445'),  
    ('KH003', 'C', '0923344556'),  
    ('KH004', 'D', '0934455667'),  
    ('KH005', 'E', '0945566778'),  
    ('KH006', 'F', '0956677889'),  
    ('KH007', 'G', '0967788990'),  
    ('KH008', 'H', '0978899001'),  
    ('KH009', 'I', '0989900112'),  
    ('KH010', 'J', '0990011223'); 
ALTER TABLE KhachHang
ADD diaChi NVARCHAR(255);

UPDATE KhachHang
SET diaChi = N'x'
WHERE diaChi IS NULL;

CREATE TABLE ChiNhanh (
    maChiNhanh NVARCHAR(10) PRIMARY KEY,
    tenChiNhanh NVARCHAR(100) NOT NULL
);
INSERT INTO ChiNhanh (maChiNhanh, tenChiNhanh)  
VALUES  
    ('CN001', N'Hà Nội'),  
    ('CN002', N'Bắc Giang'),  
    ('CN003', N'Đà Nẵng'),  
    ('CN004', N'Hải Phòng'),  
    ('CN005', N'Cần Thơ'),  
    ('CN006', N'Nghệ An'),  
    ('CN007', N'Bình Dương'),  
    ('CN008', N'Đồng Nai'),  
    ('CN009', N'Quảng Ninh'),  
    ('CN010', N'Thanh Hóa');  

-- Tạo bảng DienThoai
CREATE TABLE DienThoai (
    maDienThoai NVARCHAR(10) PRIMARY KEY,
    tenDienThoai NVARCHAR(100) NOT NULL,
    giaTien DECIMAL(18,2) NOT NULL,
    moTa NVARCHAR(500) NULL,
    img NVARCHAR(255) NULL
);

INSERT INTO DienThoai (maDienThoai, tenDienThoai, giaTien, moTa, img)  
VALUES  
    ('DT01', '600 LG Velvet', 33990000, 'ok', '600-lg-velvet.jpg'),  
    ('DT02', '600 LG Wing', 28990000, 'ok', '600-lg-wing.jpg'),  
    ('DT03', 'Iphone 14 Pro Max', 21990000, 'ok', 'ip-14-pro-max.jpg'),  
    ('DT04', 'Iphone 15 Pro Max', 25990000, 'ok', 'iphone-15-pro-max.png'),  
    ('DT05', 'Iphone 16 Pro Max', 19990000, 'ok', 'ip-16-pro-max.jpeg')

 
-- T?o b?ng NhanVien
CREATE TABLE NhanVien (
    maNhanVien NVARCHAR(10) PRIMARY KEY,
    tenNhanVien NVARCHAR(100) NOT NULL,
    maChiNhanh NVARCHAR(10) NOT NULL,
    FOREIGN KEY (maChiNhanh) REFERENCES ChiNhanh(maChiNhanh) ON DELETE CASCADE
);

-- Chèn 10 d? li?u m?u
INSERT INTO NhanVien (maNhanVien, tenNhanVien, maChiNhanh)  
VALUES  
    ('NV001', 'Nguyen Van An', 'CN001'),  
    ('NV002', 'Tran Thi Bich', 'CN002'),  
    ('NV003', 'Le Van Cuong', 'CN003'),  
    ('NV004', 'Pham Thi Dung', 'CN004'),  
    ('NV005', 'Hoang Van Duc', 'CN005'),  
    ('NV006', 'Dang Thi Huong', 'CN006'),  
    ('NV007', 'Bui Van Khoa', 'CN007'),  
    ('NV008', 'Ngo Thi Lan', 'CN008'),  
    ('NV009', 'Vu Van Minh', 'CN009'),  
    ('NV010', 'Do Thi Nhu', 'CN010');  

ALTER TABLE NhanVien
ADD luong DECIMAL(18, 2);

UPDATE NhanVien
SET luong = 10000000
WHERE luong IS NULL;


-- T?o b?ng HoaDonBanHang
CREATE TABLE HoaDonBanHang (
    maHoaDon NVARCHAR(10) PRIMARY KEY,
    maKhachHang NVARCHAR(10) NOT NULL,
    maNhanVien NVARCHAR(10) NOT NULL,
    ngayThanhToan DATE NOT NULL,
    tongTien DECIMAL(18,2) NOT NULL,
    maChiNhanh NVARCHAR(10) NOT NULL,
    FOREIGN KEY (maKhachHang) REFERENCES KhachHang(maKhachHang) ON DELETE NO ACTION,
    FOREIGN KEY (maNhanVien) REFERENCES NhanVien(maNhanVien) ON DELETE NO ACTION,
    FOREIGN KEY (maChiNhanh) REFERENCES ChiNhanh(maChiNhanh) ON DELETE NO ACTION
);


-- Chèn 10 d? li?u m?u
INSERT INTO HoaDonBanHang (maHoaDon, maKhachHang, maNhanVien, ngayThanhToan, tongTien, maChiNhanh)  
VALUES  
    ('HD001', 'KH001', 'NV001', '2024-03-01', 15000000, 'CN001'),  
    ('HD002', 'KH002', 'NV002', '2024-03-02', 28990000, 'CN002'),  
    ('HD003', 'KH003', 'NV003', '2024-03-03', 21990000, 'CN003'),  
    ('HD004', 'KH004', 'NV004', '2024-03-04', 25990000, 'CN004'),  
    ('HD005', 'KH005', 'NV005', '2024-03-05', 19990000, 'CN005'),  
    ('HD006', 'KH006', 'NV006', '2024-03-06', 20990000, 'CN006'),  
    ('HD007', 'KH007', 'NV007', '2024-03-07', 18990000, 'CN007'),  
    ('HD008', 'KH008', 'NV008', '2024-03-08', 15990000, 'CN008'),  
    ('HD009', 'KH009', 'NV009', '2024-03-09', 24990000, 'CN009'),  
    ('HD010', 'KH010', 'NV010', '2024-03-10', 27990000, 'CN010');  


-- T?o b?ng HangBan
CREATE TABLE HangBan (
    maHangBan NVARCHAR(10) PRIMARY KEY,
    maHoaDon NVARCHAR(10) NOT NULL,
    maDienThoai NVARCHAR(10) NOT NULL,
    soLuong INT NOT NULL CHECK (soLuong > 0),
    tongTien DECIMAL(18,2) NOT NULL,
    FOREIGN KEY (maHoaDon) REFERENCES HoaDonBanHang(maHoaDon) ON DELETE CASCADE,
    FOREIGN KEY (maDienThoai) REFERENCES DienThoai(maDienThoai) ON DELETE CASCADE
);

-- Chèn 10 d? li?u m?u
INSERT INTO HangBan (maHangBan, maHoaDon, maDienThoai, soLuong, tongTien)  
VALUES  
    ('HB001', 'HD001', 'DT01', 1, 15000000),  
    ('HB002', 'HD002', 'DT02', 2, 28990000),  
    ('HB003', 'HD003', 'DT03', 1, 21990000),  
    ('HB004', 'HD004', 'DT04', 3, 25990000),  
    ('HB005', 'HD005', 'DT05', 2, 19990000),  
    ('HB006', 'HD006', 'DT06', 1, 20990000),  
    ('HB007', 'HD007', 'DT07', 2, 18990000),  
    ('HB008', 'HD008', 'DT08', 1, 15990000),  
    ('HB009', 'HD009', 'DT09', 3, 24990000),  
    ('HB010', 'HD010', 'DT10', 2, 27990000);  

CREATE TABLE LichLamViec (
    maNhanVien VARCHAR(10),
    ngay DATE,
    ca NVARCHAR(10) -- Dùng NVARCHAR để lưu dữ liệu tiếng Việt
);

INSERT INTO LichLamViec (maNhanVien, ngay, ca) VALUES
('NV001', '2025-03-01', N'sang'),
('NV002', '2025-03-01', N'chieu'),
('NV003', '2025-03-02', N'sang'),
('NV004', '2025-03-02', N'chieu'),
('NV005', '2025-03-03', N'sang'),
('NV006', '2025-03-03', N'chieu'),
('NV007', '2025-03-04', N'sang'),
('NV008', '2025-03-04', N'chieu'),
('NV009', '2025-03-05', N'sang'),
('NV010', '2025-03-05', N'chieu');
