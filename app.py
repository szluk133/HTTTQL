from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import pyodbc
from datetime import datetime, timedelta
import json
from flask_socketio import SocketIO
from decimal import Decimal

app = Flask(__name__)
socketio = SocketIO(app)
app.config['SECRET_KEY'] = 'key'

# app.config['MSSQL_SERVER'] = 'DESKTOP-P61169L\HIHI'
# app.config['MSSQL_DATABASE'] = 'HTTTQL'
# app.config['MSSQL_USER'] = 'sa'
# app.config['MSSQL_PASSWORD'] = 'sa'

app.config['MSSQL_SERVER'] = 'DESKTOP-UAFD9T6'
app.config['MSSQL_DATABASE'] = 'BTL_HTTTQL'
app.config['MSSQL_USER'] = 'sa'
app.config['MSSQL_PASSWORD'] = '123'

# Setup MSSQL connection
def get_db_connection():
    conn = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={app.config['MSSQL_SERVER']};"
        f"DATABASE={app.config['MSSQL_DATABASE']};"
        f"UID={app.config['MSSQL_USER']};"
        f"PWD={app.config['MSSQL_PASSWORD']}"
    )
    return conn

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, username, phone, role):
        self.id = id
        self.username = username
        self.phone = phone
        self.role = role

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, phone, role FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(id=user[0], username=user[1], phone=user[2], role=user[3])
    return None

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, phone, role FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()
        if user:
            user_obj = User(user[0], user[1], user[2], user[3])
            login_user(user_obj)
            if user_obj.role == 'banhang':
                return redirect(url_for('nvbanhang'))
            elif user_obj.role == 'quanly':
                return redirect(url_for('quanly'))
            elif user_obj.role == 'thukho':
                return redirect(url_for('nvthukho'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)

@app.route("/nvbanhang")
@login_required
def nvbanhang():
    return render_template('nvbanhang.html')

@app.route('/get_dien_thoai_options')
def get_dien_thoai_options():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maDienThoai, tenDienThoai, giaTien FROM DienThoai")
    dien_thoai_options = [{'maDienThoai': row[0], 'tenDienThoai': row[1], 'giaTien': row[2]} for row in cursor.fetchall()]
    return jsonify(dien_thoai_options)

@app.route('/get_chi_nhanh')
def get_chi_nhanh():
    conn = get_db_connection()
    cursor = conn.cursor()
    maNhanVien = request.args.get('maNhanVien')
    cursor.execute("SELECT maChiNhanh FROM NhanVien WHERE maNhanVien = ?", maNhanVien)
    row = cursor.fetchone()
    return jsonify({'maChiNhanh': row[0] if row else None})

@app.route('/submit_invoice', methods=['POST'])
def submit_invoice():
    conn = get_db_connection()
    cursor = conn.cursor()
    data = request.json
    maHoaDon = data.get('maHoaDon')
    maKhachHang = data.get('maKhachHang')
    maNhanVien = data.get('maNhanVien')
    maDienThoai = data.get('maDienThoai')
    soLuong = data.get('soLuong')
    tongTien = data.get('tongTien')
    ngayThanhToan = data.get('ngayThanhToan')
    maChiNhanh = data.get('maChiNhanh')

    try:
        cursor.execute("SELECT TOP 1 maHangBan FROM HangBan ORDER BY maHangBan DESC")
        mahbcu = cursor.fetchone()

        if mahbcu:
            mahbcuall = mahbcu[0]  # Lấy toàn bộ chuỗi mã hàng bán
            # Tách phần số từ mã hàng bán và tăng lên 1
            mahbcu_num = int(mahbcuall[2:]) + 1
            # Tạo mã hàng bán mới với định dạng HB + 8 chữ số
            maHangBan = f"HB{mahbcu_num:07d}"
        cursor.execute("""
            INSERT INTO HoaDonBanHang (maHoaDon, maKhachHang, maNhanVien, ngayThanhToan, tongTien, maChiNhanh)
            VALUES (?, ?, ?, ?, ?, ?)
        """, maHoaDon, maKhachHang, maNhanVien, ngayThanhToan, tongTien, maChiNhanh)
        conn.commit()
        cursor.execute("""
            INSERT INTO HangBan (maHangBan, maHoaDon, maDienThoai, soLuong, tongTien)
            VALUES (?, ?, ?, ?, ?)
        """, maHangBan, maHoaDon, maDienThoai, soLuong, tongTien)
        conn.commit()
        return jsonify(success=True)
    except pyodbc.Error as e:
        print("Error:", e)
        return jsonify(success=False, error=str(e))
    finally:
        cursor.close()
        conn.close()
    
@app.route('/get_next_ma_hoa_don')
def get_next_ma_hoa_don():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 1 maHoaDon FROM HoaDonBanHang ORDER BY maHoaDon DESC")
    last_ma_hoa_don = cursor.fetchone()
    if last_ma_hoa_don:
        last_ma_hoa_don = last_ma_hoa_don[0]
        prefix = last_ma_hoa_don[:3]
        number = int(last_ma_hoa_don[3:]) + 1
        next_ma_hoa_don = f"{prefix}{number:06d}"
    else:
        next_ma_hoa_don = "HDB000001"
    return jsonify({'next_ma_hoa_don': next_ma_hoa_don})

@app.route("/quanly")
@login_required
def quanly():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tenDienThoai, moTa, giaTien, img FROM DienThoai")
    dien_thoai_list = cursor.fetchall()
    conn.close()
    return render_template('trangchu.html',dien_thoai_list=dien_thoai_list)

@app.route("/lichlamviec", methods=['GET', 'POST'])
def lichlamviec():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if request.method == 'POST':
        maNhanVien = request.form['maNhanVien']
        ngay = request.form['ngay']
        ca = request.form['ca']
        cursor.execute(
            "INSERT INTO LichLamViec (maNhanVien, ngay, ca) VALUES (?, ?, ?)",
            (maNhanVien, ngay, ca)
        )
        conn.commit()

    cursor.execute("SELECT maNhanVien, tenNhanVien FROM NhanVien")
    employees = cursor.fetchall()

    # Get the current week's schedule
    # start_of_week = datetime.now() - timedelta(days=datetime.now().weekday())
    # weekly_schedule = {}
    # for i in range(7):
    #     current_day = start_of_week + timedelta(days=i)
    #     formatted_date = current_day.strftime('%Y-%m-%d')
    #     weekly_schedule[current_day.strftime('%A')] = {'sáng': [], 'chiều': []}
    #     cursor.execute("SELECT nv.tenNhanVien, llv.ca FROM LichLamViec llv JOIN NhanVien nv ON llv.maNhanVien = nv.maNhanVien WHERE llv.ngay = ?", (formatted_date,))
    #     shifts = cursor.fetchall()
    #     for shift in shifts:
    #         weekly_schedule[current_day.strftime('%A')][shift[1]].append(shift[0])
    today = datetime.today()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    cursor.execute("""
        SELECT llv.ngay, llv.ca, nv.tenNhanVien 
        FROM LichLamViec llv
        JOIN NhanVien nv ON llv.maNhanVien = nv.maNhanVien
        WHERE llv.ngay BETWEEN ? AND ?
        ORDER BY llv.ngay, llv.ca
    """, (start_of_week, end_of_week))
    
    schedule = cursor.fetchall()
    
    # Tạo cấu trúc lịch làm việc cho tuần hiện tại
    weekly_schedule = {}
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        weekly_schedule[day.strftime('%Y-%m-%d')] = {'sáng': [], 'chiều': []}
    
    for entry in schedule:
        day = entry.ngay.strftime('%Y-%m-%d')
        shift = entry.ca
        employee_name = entry.tenNhanVien
        weekly_schedule[day][shift].append(employee_name)

    conn.close()
    return render_template('QuanLy/QLLLV.html', employees=employees, weekly_schedule=weekly_schedule)

@app.route("/tkdoanhthunv")
def tkdoanhthunv():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT nv.maNhanVien, nv.tenNhanVien, SUM(hdbh.tongTien) AS doanhThu
        FROM HoaDonBanHang hdbh
        JOIN NhanVien nv ON hdbh.maNhanVien = nv.maNhanVien
        GROUP BY nv.maNhanVien, nv.tenNhanVien
        ORDER BY doanhThu DESC
    """)
    rows = cursor.fetchall()
    
    # Loại bỏ khoảng trắng thừa trong maNhanVien
    doanhthu_data = [
        {'maNhanVien': row.maNhanVien.strip(), 'tenNhanVien': row.tenNhanVien.strip(), 'doanhThu': row.doanhThu}
        for row in rows
    ]
    
    conn.close()
    return render_template('QuanLy/TKDTNV.html', doanhthu_data=doanhthu_data)


@app.route("/tkdoanhthunv/<maNhanVien>")
def doanhthu_chitiet(maNhanVien):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT maHoaDon, maKhachHang, ngayThanhToan, tongTien
        FROM HoaDonBanHang
        WHERE maNhanVien = ?
        ORDER BY ngayThanhToan DESC
    """, (maNhanVien.strip(),))
    hoadon_data = cursor.fetchall()

    cursor.execute("SELECT tenNhanVien FROM NhanVien WHERE maNhanVien = ?", (maNhanVien.strip(),))
    nhanvien = cursor.fetchone()
    
    conn.close()
    return render_template('QuanLy/ChiTietDoanhThuNV.html', hoadon_data=hoadon_data, nhanvien=nhanvien)



@app.route("/quanlyluong")
def quanlyluong():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Truy vấn để lấy danh sách nhân viên và mức lương của họ
    cursor.execute("""
        SELECT ROW_NUMBER() OVER (ORDER BY maNhanVien) AS stt, maNhanVien, tenNhanVien, luong
        FROM NhanVien

    """)
        #  WHERE maChiNhanh = 'CN001'
    luong_data = cursor.fetchall()
    
    conn.close()
    return render_template('QuanLy/QLLuong.html', luong_data=luong_data)

@app.route('/delete_luong/<maNhanVien>', methods=['DELETE'])
def delete_luong(maNhanVien):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM BangLuong WHERE maNhanVien = ?", maNhanVien)
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/update_luong', methods=['POST'])
def update_luong():
    data = request.get_json()
    maNhanVien = data['maNhanVien']
    tenNhanVien = data['tenNhanVien']
    luong = data['luong']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE NhanVien SET tenNhanVien = ?, luong = ? WHERE maNhanVien = ?", (tenNhanVien, luong, maNhanVien))
    conn.commit()
    conn.close()
    return jsonify(success=True)

@app.route('/delete_shift', methods=['POST'])
def delete_shift():
    data = request.get_json()
    day = data['day']
    shift = data['shift']
    employee = data['employee']
    
    # Chuyển đổi ngày từ chuỗi sang datetime.date
    day_date = datetime.strptime(day, '%Y-%m-%d').date()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        DELETE FROM LichLamViec 
        WHERE maNhanVien = (
            SELECT maNhanVien FROM NhanVien WHERE tenNhanVien = ?
        ) AND ngay = ? AND ca = ?
    """, (employee, day_date, shift))
    
    conn.commit()
    conn.close()
    
    return jsonify(success=True)


@app.route("/nvthukho")
@login_required
def nvthukho():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tenDienThoai, moTa, giaTien, img FROM DienThoai")
    dien_thoai_list = cursor.fetchall()
    conn.close()
    return render_template('nvthukho.html',dien_thoai_list=dien_thoai_list)

@app.route('/get_dien_thoai_in_stock')
def get_dien_thoai_in_stock():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 10 maDienThoai, tenDienThoai, moTa, giaTien, img FROM DienThoai")
    dien_thoai_list = [{'maDienThoai': row[0], 'tenDienThoai': row[1], 'moTa': row[2], 'giaTien': row[3], 'img': row[4]} for row in cursor.fetchall()]
    return jsonify(dien_thoai_list)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('login'))

# Trang nv ban hang

added_products = []

@app.route('/')
def index():
    return redirect(url_for('login'))



@app.route('/add_product', methods=['POST'])
def add_product():
    product_code = request.json.get('product_code')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT maDienThoai, tenDienThoai, giaTien FROM DienThoai WHERE maDienThoai = ?", (product_code,))
    product = cursor.fetchone()
    conn.close()

    if product:
        product_info = {"maDienThoai": product[0], "tenDienThoai": product[1], "giaTien": product[2]}
        added_products.append(product_info)
        return jsonify({"success": True, "product": product_info}), 200
    else:
        return jsonify({"success": False, "message": "Product not found"}), 404



@app.route('/process_payment', methods=['POST'])
def process_payment():
    customer_phone = request.json.get('customer_phone')  # Sử dụng 'customer_phone' thay vì 'customer_code'

    if added_products:
        total_amount = sum(product['giaTien'] for product in added_products)
        
        # Tìm id của khách hàng dựa trên số điện thoại
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT maKhachHang FROM KhachHang WHERE sdt = ?", (customer_phone,))
        customer_id = cursor.fetchone()
        
        if customer_id:
            customer_id = customer_id[0]  # Lấy id của khách hàng

            # Tạo mã hóa đơn theo định dạng HDB000001
            cursor.execute("SELECT MAX(RIGHT(maHoaDon, 6)) FROM HoaDonBanHang")
            max_id = cursor.fetchone()[0]
            next_id = 1 if max_id is None else int(max_id) + 1
            maHoaDon = f'HDB{next_id:06d}'  # Format mã hóa đơn

            # Lưu hóa đơn bán hàng vào cơ sở dữ liệu
            cursor.execute("INSERT INTO HoaDonBanHang (maHoaDon, maKhachHang, maNhanVien, ngayThanhToan, tongTien) VALUES (?, ?, ?, GETDATE(), ?)", (maHoaDon, customer_id, current_user.id, total_amount))
            conn.commit()
            conn.close()

            return jsonify({"success": True, "total_amount": total_amount}), 200
        else:
            conn.close()
            return jsonify({"success": False, "message": "Customer not found"}), 404
    else:
        return jsonify({"success": False, "message": "No products to process"}), 400


@app.route('/employee_management')
def employee_management():
    # Xử lý logic cho trang quản lý nhân viên ở đây
    return render_template('QuanLy/QLNhanVien.html')


# Quan ly khach hang
############################################
@app.route('/add_customer', methods=['POST'])
def add_customer():
    try:
        # Lấy dữ liệu khách hàng từ yêu cầu POST
        customer_data = request.json
        name = customer_data['name']
        address = customer_data['address']
        phone = customer_data['phone']
        
        # Tạo ID mới cho khách hàng
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(RIGHT(maKhachHang, 4)) FROM KhachHang")
        last_id = cursor.fetchone()[0]
        next_id = 1 if last_id is None else int(last_id) + 1
        new_customer_id = f'KH{next_id:04d}'
        
        # Thêm khách hàng vào cơ sở dữ liệu
        cursor.execute("INSERT INTO KhachHang (maKhachHang, tenNhanVien, diaChi, sdt) VALUES (?, ?, ?, ?)", (new_customer_id, name, address, phone))
        conn.commit()
        conn.close()

        return jsonify({"success": True, "message": "Customer added successfully"}), 200

    except Exception as e:

        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/get_purchase_history', methods=['POST'])
def get_purchase_history():
    try:
        # Lấy số điện thoại của khách hàng từ yêu cầu POST
        customer_phone = request.json.get('customer_phone')

        # Tạo truy vấn SQL để lấy lịch sử mua hàng của khách hàng
        query = """
        SELECT HoaDonBanHang.maHoaDon, HoaDonBanHang.tongTien 
        FROM HoaDonBanHang 
        JOIN KhachHang ON HoaDonBanHang.maKhachHang = KhachHang.maKhachHang 
        WHERE KhachHang.sdt = ?
        """

        # Thực thi truy vấn và lấy kết quả
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, customer_phone)
        purchase_history = cursor.fetchall()

        # Chuyển kết quả sang định dạng phù hợp để trả về cho client
        formatted_purchase_history = [{'maHoaDon': row[0], 'tongTien': row[1]} for row in purchase_history]

        # Trả về lịch sử mua hàng dưới dạng JSON
        return jsonify({"success": True, "purchase_history": formatted_purchase_history}), 200

    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    
    
@app.route('/customer_management', methods=['GET'])
def customer_management():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    connection = get_db_connection()
    cursor = connection.cursor()
    
    if search:
        search_query = f"""
        SELECT * FROM KhachHang
        WHERE maKhachHang LIKE ? OR tenKhachHang LIKE ? OR sdt LIKE ?
        """
        search_param = f"%{search}%"
        cursor.execute(search_query, (search_param, search_param, search_param))
    else:
        cursor.execute("SELECT * FROM KhachHang")
    
    customers = cursor.fetchall()
    total_customers = len(customers)
    
    # Pagination logic
    start = (page - 1) * per_page
    end = start + per_page
    paginated_customers = customers[start:end]
    total_pages = (total_customers + per_page - 1) // per_page
    
    return render_template(
        'QuanLy/QLKhachHang.html',
        customers=paginated_customers,
        current_page=page,
        total_pages=total_pages,
        search=search
    )

@app.route('/update_customer', methods=['POST'])
def update_customer():
    data = request.json
    maKhachHang = data['maKhachHang']
    tenKhachHang = data['tenKhachHang']
    diaChi = data['diaChi']
    sdt = data['sdt']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        print("Received data for update:", data)
        cursor.execute("""
            UPDATE KhachHang
            SET tenKhachHang = ?, diaChi = ?, sdt = ?
            WHERE maKhachHang = ?
        """, tenKhachHang, diaChi, sdt, maKhachHang)
        conn.commit()
        print("Customer updated successfully.")
        return jsonify(success=True)
    except pyodbc.Error as e:
        print("Error:", e)
        return jsonify(success=False, error=str(e))
    finally:
        conn.close()

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    data = request.json
    maKhachHang = data['maKhachHang']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "DELETE FROM KhachHang WHERE maKhachHang = ?"
    cursor.execute(query, (maKhachHang,))
    conn.commit()
    conn.close()
    
    return jsonify(success=True)

@app.route('/update_phone/<string:phone_id>', methods=['POST'])
def update_phone(phone_id):
    data = request.get_json()
    tenDienThoai = data.get('tenDienThoai')
    moTa = data.get('moTa')
    giaTien = data.get('giaTien')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE DienThoai
        SET tenDienThoai = ?, moTa = ?, giaTien = ?
        WHERE maDienThoai = ?
    """, tenDienThoai, moTa, giaTien, phone_id)
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/delete_phone/<string:phone_id>', methods=['POST'])
def delete_phone(phone_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM DienThoai WHERE maDienThoai = ?", phone_id)
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/finance_management_detail')
def finance_management_detail():
    # Xử lý logic cho trang quản lý tài chính ở đây
    return render_template('QuanLy/QLTaiChinh.html')


@app.route('/finace_management')
def finance_management():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Lấy dữ liệu của tháng 4 năm 2024 từ bảng HangBan và HoaDonBanHang
    query = """
    SELECT h.maDienThoai, d.tenDienThoai, SUM(h.soLuong) AS total_quantity, SUM(h.tongTien) AS total_revenue
    FROM HangBan h
    JOIN HoaDonBanHang hd ON h.maHoaDon = hd.maHoaDon
    JOIN DienThoai d ON h.maDienThoai = d.maDienThoai
    WHERE MONTH(hd.ngayThanhToan) = 3 AND YEAR(hd.ngayThanhToan) = 2024
    GROUP BY h.maDienThoai, d.tenDienThoai
    ORDER BY total_quantity DESC
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    top_products = results[:3]
    total_revenue = sum(float(row.total_revenue) for row in results)

    # Dữ liệu cho biểu đồ cột
    top_products_chart_data = {
        'labels': [row.tenDienThoai for row in top_products],
        'quantities': [row.total_quantity for row in top_products]
    }

    # Dữ liệu cho biểu đồ tròn
    total_revenue_chart_data = {
        'labels': [row.tenDienThoai for row in results],
        'revenues': [float(row.total_revenue) for row in results]
    }

    return render_template('QuanLy/QLTK.html', top_products_chart_data=json.dumps(top_products_chart_data), total_revenue_chart_data=json.dumps(total_revenue_chart_data))

@socketio.on('connect')
def handle_connect():
    data = fetch_chart_data()
    socketio.emit('update_chart_data', data)

def fetch_chart_data():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Truy vấn 3 sản phẩm bán chạy nhất
    top_products_query = '''
    SELECT TOP 3 DienThoai.tenDienThoai, SUM(HangBan.soLuong) as total_quantity
    FROM HangBan
    JOIN DienThoai ON HangBan.maDienThoai = DienThoai.maDienThoai
    WHERE HangBan.maHoaDon IN (
        SELECT maHoaDon
        FROM HoaDonBanHang
        WHERE MONTH(ngayThanhToan) = 3 AND YEAR(ngayThanhToan) = 2024
    )
    GROUP BY DienThoai.tenDienThoai
    ORDER BY total_quantity DESC
    '''
    
    # Truy vấn tổng doanh thu theo tên điện thoại
    total_revenue_query = '''
    SELECT DienThoai.tenDienThoai, SUM(HangBan.tongTien) as total_revenue
    FROM HangBan
    JOIN DienThoai ON HangBan.maDienThoai = DienThoai.maDienThoai
    WHERE HangBan.maHoaDon IN (
        SELECT maHoaDon
        FROM HoaDonBanHang
        WHERE MONTH(ngayThanhToan) = 3 AND YEAR(ngayThanhToan) = 2024
    )
    GROUP BY DienThoai.tenDienThoai
    '''
    
    cursor.execute(top_products_query)
    top_products_data = cursor.fetchall()
    top_products_chart_data = {
        'labels': [row[0] for row in top_products_data],
        'quantities': [float(row[1]) for row in top_products_data]  # ✅ Chuyển Decimal -> float
    }

    cursor.execute(total_revenue_query)
    total_revenue_data = cursor.fetchall()
    total_revenue_chart_data = {
        'labels': [row[0] for row in total_revenue_data],
        'revenues': [float(row[1]) for row in total_revenue_data]  # ✅ Chuyển Decimal -> float
    }

    conn.close()
    
    return {
        'top_products_chart_data': top_products_chart_data,
        'total_revenue_chart_data': total_revenue_chart_data
    }
    
if __name__ == '__main__':
    socketio.run(app, debug=True)
