"""
Email utility module for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from typing import Optional
from ..config import settings


def send_email(
    to_email: str,
    subject: str,
    body_html: str,
    body_text: Optional[str] = None
) -> bool:
    """
    Send email via SMTP
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_html: HTML body content
        body_text: Plain text body (optional, will be extracted from HTML if not provided)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    # Check if SMTP is configured
    if not settings.smtp_username or not settings.smtp_password:
        logger.warning("SMTP not configured - email not sent")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.smtp_from_email
        msg['To'] = to_email
        
        # Add text/plain part
        if body_text:
            part1 = MIMEText(body_text, 'plain', 'utf-8')
            msg.attach(part1)
        
        # Add text/html part
        part2 = MIMEText(body_html, 'html', 'utf-8')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {e}")
        return False


def send_new_employee_notification(
    employee_name: str,
    employee_email: str,
    employee_id: int,
    department: Optional[str] = None,
    temp_password: Optional[str] = None
) -> bool:
    """
    Send welcome email to new employee
    
    Args:
        employee_name: Employee's name
        employee_email: Employee's email address
        employee_id: Employee ID
        department: Department name (optional)
        temp_password: Temporary password if user account created (optional)
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Chào mừng bạn đến với hệ thống chấm công"
    
    # Build HTML body
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #3b82f6;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .info-box {{
                background-color: #e0f2fe;
                border-left: 4px solid #3b82f6;
                padding: 15px;
                margin: 20px 0;
            }}
            .info-row {{
                margin: 10px 0;
            }}
            .label {{
                font-weight: bold;
                color: #1e40af;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Chào mừng đến với Hệ thống Chấm công</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{employee_name}</strong>,</p>
                
                <p>Chúng tôi rất vui mừng thông báo rằng bạn đã được thêm vào hệ thống chấm công của công ty.</p>
                
                <div class="info-box">
                    <div class="info-row">
                        <span class="label">Mã nhân viên:</span> {employee_id}
                    </div>
                    <div class="info-row">
                        <span class="label">Họ tên:</span> {employee_name}
                    </div>
    """
    
    if department:
        html_body += f"""
                    <div class="info-row">
                        <span class="label">Phòng ban:</span> {department}
                    </div>
    """
    
    if temp_password:
        html_body += f"""
                    <div class="info-row">
                        <span class="label">Tài khoản:</span> {employee_email}
                    </div>
                    <div class="info-row">
                        <span class="label">Mật khẩu tạm:</span> {temp_password}
                    </div>
                    <div style="margin-top: 15px; padding: 10px; background-color: #fef3c7; border-left: 4px solid #f59e0b;">
                        <strong>⚠️ Quan trọng:</strong> Vui lòng đổi mật khẩu ngay sau lần đăng nhập đầu tiên!
                    </div>
    """
    
    html_body += """
                </div>
                
                <h3>Hướng dẫn sử dụng:</h3>
                <ol>
                    <li>Tải ứng dụng di động hoặc truy cập hệ thống web</li>
                    <li>Đăng nhập bằng tài khoản được cung cấp</li>
                    <li>Thực hiện chụp ảnh khuôn mặt để đăng ký nhận dạng (nếu chưa có)</li>
                    <li>Bắt đầu chấm công hàng ngày</li>
                </ol>
                
                <p>Nếu bạn có bất kỳ câu hỏi nào, vui lòng liên hệ với bộ phận IT hoặc HR.</p>
                
                <p>Chúc bạn làm việc hiệu quả!</p>
                
                <p>Trân trọng,<br>
                <strong>Đội ngũ Quản trị hệ thống</strong></p>
            </div>
            <div class="footer">
                <p>Email này được gửi tự động từ Hệ thống Chấm công.<br>
                Vui lòng không trả lời email này.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=employee_email,
        subject=subject,
        body_html=html_body
    )


def send_account_created_notification(
    employee_name: str,
    employee_email: str,
    username: str,
    temp_password: str,
    employee_id: int
) -> bool:
    """
    Send notification when user account is created for employee
    
    Args:
        employee_name: Employee's name
        employee_email: Employee's email address
        username: Username for login
        temp_password: Temporary password
        employee_id: Employee ID
    
    Returns:
        True if email sent successfully, False otherwise
    """
    subject = "Tài khoản hệ thống chấm công đã được tạo"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #10b981;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .credentials-box {{
                background-color: #d1fae5;
                border: 2px solid #10b981;
                padding: 20px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .warning-box {{
                background-color: #fef3c7;
                border-left: 4px solid #f59e0b;
                padding: 15px;
                margin: 20px 0;
            }}
            .credential-item {{
                margin: 10px 0;
                font-size: 16px;
            }}
            .label {{
                font-weight: bold;
                color: #065f46;
            }}
            .value {{
                font-family: 'Courier New', monospace;
                background-color: white;
                padding: 5px 10px;
                border-radius: 3px;
                display: inline-block;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✓ Tài khoản đã được tạo</h1>
            </div>
            <div class="content">
                <p>Xin chào <strong>{employee_name}</strong>,</p>
                
                <p>Tài khoản đăng nhập hệ thống chấm công của bạn đã được tạo thành công!</p>
                
                <div class="credentials-box">
                    <h3 style="margin-top: 0; color: #065f46;">Thông tin đăng nhập:</h3>
                    <div class="credential-item">
                        <span class="label">Tên đăng nhập:</span><br>
                        <span class="value">{username}</span>
                    </div>
                    <div class="credential-item">
                        <span class="label">Mật khẩu tạm thời:</span><br>
                        <span class="value">{temp_password}</span>
                    </div>
                    <div class="credential-item">
                        <span class="label">Mã nhân viên:</span><br>
                        <span class="value">{employee_id}</span>
                    </div>
                </div>
                
                <div class="warning-box">
                    <strong>⚠️ BẢO MẬT QUAN TRỌNG:</strong>
                    <ul style="margin: 10px 0;">
                        <li>Vui lòng đổi mật khẩu ngay sau lần đăng nhập đầu tiên</li>
                        <li>Không chia sẻ thông tin đăng nhập với người khác</li>
                        <li>Chọn mật khẩu mạnh (ít nhất 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt)</li>
                    </ul>
                </div>
                
                <h3>Các bước tiếp theo:</h3>
                <ol>
                    <li><strong>Đăng nhập:</strong> Sử dụng tài khoản và mật khẩu trên để đăng nhập vào hệ thống</li>
                    <li><strong>Đổi mật khẩu:</strong> Truy cập phần Cài đặt → Đổi mật khẩu</li>
                    <li><strong>Đăng ký khuôn mặt:</strong> Chụp ảnh để đăng ký nhận dạng khuôn mặt (nếu chưa có)</li>
                    <li><strong>Bắt đầu sử dụng:</strong> Chấm công hàng ngày qua ứng dụng</li>
                </ol>
                
                <p>Nếu bạn gặp khó khăn khi đăng nhập hoặc có câu hỏi, vui lòng liên hệ bộ phận IT.</p>
                
                <p>Chúc bạn có trải nghiệm tốt!</p>
                
                <p>Trân trọng,<br>
                <strong>Hệ thống Chấm công</strong></p>
            </div>
            <div style="text-align: center; margin-top: 20px; font-size: 12px; color: #666;">
                <p>Email tự động từ Hệ thống Chấm công - Không trả lời email này</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(
        to_email=employee_email,
        subject=subject,
        body_html=html_body
    )
