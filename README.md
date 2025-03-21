# Network Diagnostic Tool
A comprehensive network diagnostics and analysis tool with a modern, user-friendly interface.

## Features

- **Ping Test**: Measure network latency and packet loss with visual graphs
- **Trace Route**: Trace the network path to any destination with visual highlighting of network issues
- **Network Information**: View detailed information about your network interfaces and configuration
- **Speed Test**: Measure your internet connection speed with quality assessment
- **Modern UI**: Clean, intuitive interface with visual indicators for network quality

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/network-diagnostic-tool.git
cd network-diagnostic-tool
```

2. Create a virtual environment (recommended):
```
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install the required dependencies:
```
pip install -r requirements.txt
```

## Usage

Run the application:
```
python main.py
```

### Ping Test

1. Enter an IP address or hostname to ping, or select from the dropdown
2. Adjust ping count and interval as needed
3. Click "Start Test"
4. View the results with latency graph and quality assessment

### Trace Route

1. Enter an IP address or hostname to trace
2. Adjust maximum hops if needed
3. Click "Start Trace"
4. View the network path with highlighted high-latency hops

### Network Information

View detailed information about your network configuration, including:
- Hostname and IP addresses
- DNS resolvers
- Network interfaces
- Default gateway

Click "Refresh" to update the information.

### Speed Test

1. Click "Start Test"
2. Wait for the test to complete
3. View your download and upload speeds with quality assessment

## Requirements

- Python 3.7+
- wxPython 4.2.0
- Other dependencies listed in requirements.txt

## License

This software is provided under the MIT License.

## Developer

Created by 3λΞĐ

---

<div dir="rtl">

# ابزار عیب‌یابی شبکه

یک ابزار جامع عیب‌یابی و تحلیل شبکه با رابط کاربری مدرن و کاربرپسند.

## ویژگی‌ها

- **تست پینگ**: اندازه‌گیری تأخیر شبکه و از دست رفتن بسته‌ها با نمودارهای بصری
- **ردیابی مسیر**: ردیابی مسیر شبکه به هر مقصدی با برجسته‌سازی بصری مشکلات شبکه
- **اطلاعات شبکه**: مشاهده اطلاعات دقیق درباره رابط‌های شبکه و پیکربندی آن‌ها
- **تست سرعت**: اندازه‌گیری سرعت اتصال اینترنت با ارزیابی کیفیت
- **رابط کاربری مدرن**: رابط تمیز و شهودی با نشانگرهای بصری برای کیفیت شبکه

## نصب

1. کلون کردن این مخزن:
```
git clone https://github.com/yourusername/network-diagnostic-tool.git
cd network-diagnostic-tool
```

2. ایجاد محیط مجازی (توصیه می‌شود):
```
python -m venv venv
source venv/bin/activate  # لینوکس/مک
venv\Scripts\activate     # ویندوز
```

3. نصب وابستگی‌های مورد نیاز:
```
pip install -r requirements.txt
```

## استفاده

اجرای برنامه:
```
python main.py
```

### تست پینگ

1. آدرس IP یا نام میزبان را برای پینگ وارد کنید یا از منوی کشویی انتخاب کنید
2. تعداد پینگ و فاصله زمانی را در صورت نیاز تنظیم کنید
3. روی "Start Test" کلیک کنید
4. نتایج را با نمودار تأخیر و ارزیابی کیفیت مشاهده کنید

### ردیابی مسیر

1. آدرس IP یا نام میزبان را برای ردیابی وارد کنید
2. حداکثر تعداد گام‌ها را در صورت نیاز تنظیم کنید
3. روی "Start Trace" کلیک کنید
4. مسیر شبکه را با برجسته‌سازی گام‌های با تأخیر بالا مشاهده کنید

### اطلاعات شبکه

مشاهده اطلاعات دقیق درباره پیکربندی شبکه شما، شامل:
- نام میزبان و آدرس‌های IP
- سرورهای DNS
- رابط‌های شبکه
- دروازه پیش‌فرض

برای به‌روزرسانی اطلاعات روی "Refresh" کلیک کنید.

### تست سرعت

1. روی "Start Test" کلیک کنید
2. منتظر بمانید تا تست کامل شود
3. سرعت‌های دانلود و آپلود خود را با ارزیابی کیفیت مشاهده کنید

## نیازمندی‌ها

- پایتون 3.7+
- wxPython 4.2.0
- سایر وابستگی‌ها در فایل requirements.txt ذکر شده‌اند

## مجوز

این نرم‌افزار تحت مجوز MIT ارائه شده است.

## توسعه‌دهنده

ساخته شده توسط 3λΞĐ

</div> 