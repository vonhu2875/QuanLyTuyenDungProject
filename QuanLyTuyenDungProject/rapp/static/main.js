//// 1. Phải để hàm này ở NGOÀI CÙNG của file để HTML gọi được
//function updateFileName(input) {
//    const display = document.getElementById('file-name-display');
//    if (input.files && input.files[0]) {
//        display.innerHTML = `<i class="bi bi-check-circle-fill me-1"></i> Đã chọn: ${input.files[0].name}`;
//    }
//}
//
//document.addEventListener("DOMContentLoaded", function() {
//    // 2. Xử lý lỗi ảnh avatar
//    document.querySelectorAll('.user-avatar').forEach(img => {
//        img.addEventListener('error', function() {
//            this.style.display = 'none';
//            if (this.nextElementSibling) {
//                this.nextElementSibling.style.display = 'block';
//            }
//        });
//    });
//
//    // 3. Tự động đóng TẤT CẢ Alert sau 3 giây (Đã sửa lỗi không hoạt động)
//    setTimeout(function() {
//        var alerts = document.querySelectorAll('.alert');
//        alerts.forEach(function(alertElement) {
//            if (typeof bootstrap !== 'undefined') {
//                // Sử dụng getOrCreateInstance để đảm bảo đóng được mọi loại thông báo
//                var bsAlert = bootstrap.Alert.getOrCreateInstance(alertElement);
//                if (bsAlert) bsAlert.close();
//            }
//        });
//    }, 3000);
//});
