//Có 1 số trang tui không cần phải tự động tắt sa
//u 3 giây -> Hà có cần thì đặt tên 1 selector khác để set lại 3 giây ngen
//document.addEventListener("DOMContentLoaded", function() {
//        // Tự tắt thông báo sau 3 giây cho toàn bộ các trang
//        setTimeout(function() {
//            const alerts = document.querySelectorAll('.alert');
//            alerts.forEach(function(a) {
//                if (typeof bootstrap !== 'undefined') {
//                    const bsA = bootstrap.Alert.getOrCreateInstance(a);
//                    if (bsA) bsA.close();
//                } else {
//                    a.style.display = 'none';
//                }
//            });
//        }, 3000);