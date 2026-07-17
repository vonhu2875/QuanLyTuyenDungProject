# FINAL PROJECT SOFTWARE TESTING - RECRUITMENT MANAGEMENT SYSTEM
## Mô tả 

Quản lý tuyển dụng là một website giúp kết nối nhà tuyển dụng và ứng viên, hỗ trợ toàn bộ quy trình tuyển dụng từ đăng tin tuyển dụng đến nộp hồ sơ ứng tuyển. Hệ thống được phát triển với Django REST Framework cho backend và React Native cho frontend, cung cấp các RESTful API để quản lý người dùng, tin tuyển dụng và hồ sơ ứng tuyển.

Trang web hỗ trợ ba vai trò chính:

- Quản trị viên (Admin): Quản lý người dùng, doanh nghiệp, tin tuyển dụng và phê duyệt doanh nghiệp.
- Nhà tuyển dụng (Employer): Quản lý thông tin doanh nghiệp, đăng tin tuyển dụng, theo dõi và xử lý hồ sơ ứng tuyển.
- Ứng viên (Candidate): Tìm kiếm việc làm, xem chi tiết tin tuyển dụng, lưu việc làm và nộp hồ sơ ứng tuyển.

Trang web có 3 nghiệp vụ chính:

1.	Đăng tin tuyển dụng.
2.	Nộp hồ sơ.
3.	Xem và cập nhật trạng thái hồ sơ.
## Thành viên nhóm 
| MSSV | Họ tên | Vai trò | 
|------|--------|---------| 
|2351050127|Võ Thị Bích Như | Project Manager, Developer (Nghiệp vụ 1), Tester (Nghiệp vụ 2)|
| 2351050037 | Nguyễn Diệp Thái Hà | Developer (Nghiệp vụ 2), Tester (Nghiệp vụ 3) | 
| 2351050183 | Nguyễn Đức Nhu Toàn | Developer (Nghiệp vụ 3), Tester (Nghiệp vụ 1) | 
## Công nghệ
| Category | Technologies |
|----------|--------------|
| Backend | Python, Flask, SQLAlchemy |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript |
| Database | MySQL |
| Testing | Manual Testing, Postman, Selenium, Locust |
| Version Control | Git, GitHub |

## Cài đặt và chạy 
* Máy tính đã cài đặt sẵn **Python (phiên bản 3.8 trở lên)**.
* Máy tính đã cài đặt và khởi động sẵn **MySQL Server**.
### 1. Yêu cầu hệ thống
* Máy tính đã cài đặt sẵn **Python (phiên bản 3.8 trở lên)**.
* Máy tính đã cài đặt và khởi động sẵn **MySQL Server**.
### 2. Tải mã nguồn
Mở terminal (hoặc Git Bash) và chạy lệnh sau để clone dự án về máy:
git clone [https://github.com/vonhu2875/QuanLyTuyenDungProject.git](https://github.com/vonhu2875/QuanLyTuyenDungProject.git)

cd QuanLyTuyenDungProject
### 3. Tạo môi trường ảo
#### Tạo môi trường ảo có tên là 'venv'
python -m venv venv

#### Kích hoạt môi trường ảo (Đối với Windows)
- venv\Scripts\activate

#### Kích hoạt môi trường ảo (Đối với macOS/Linux)
- source venv/bin/activate
### 4. Cài đặt các thư viện
- pip install -r requirements.txt
### 5. Cấu hình cơ sở dữ liệu
- Mở MySQL Client (hoặc Workbench/DBeaver) và tạo một database mới: `CREATE DATABASE recruitmentdb;`

- Hãy cập nhật lại thông tin cấu hình kết nối Database (Host, User, Password, Database Name) trong file `__init__.py` cho khớp với máy của bạn.

## Nộp bài
- Báo cáo: test-case-quan-ly-tuyen-dung-project.xlsx
