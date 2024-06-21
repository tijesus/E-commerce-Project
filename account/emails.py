"""
contains html mails as string

for verification mail
    password_reset mail
    sucessful reset mail
"""


verification_email_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Verify Your Email - Dalle Stores</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #333;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            margin-top: 20px;
            background-color: #ff6347;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
        }}
        .footer {{
            background-color: #f4f4f4;
            color: #666666;
            padding: 10px;
            text-align: center;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Dalle Stores!</h1>
        </div>
        <div class="content">
            <h2>Verify Your Email Address</h2>
            <p>Thank you for signing up! Please click the button below to verify your email address and complete your registration.</p>
            <a href="{}" class="button">Verify Email</a>
        </div>
        <div class="footer">
            <p>If you didn't create an account, please ignore this email.</p>
            <p>For support, contact us at <a href="mailto:praisechinonso21@gmail.com">praisechinonso21@gmail.com</a></p>
            <p>&copy; 2024 Dalle Stores. All rights reserved.</p>
            
        </div>
    </div>
</body>
</html>"""

reset_password_email_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Reset Your Password - Dalle Stores</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #333;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            margin-top: 20px;
            background-color: #ff6347;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
        }}
        .footer {{
            background-color: #f4f4f4;
            color: #666666;
            padding: 10px;
            text-align: center;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Reset Your Password</h1>
        </div>
        <div class="content">
            <h2>Password Reset Request</h2>
            <p>We received a request to reset your password. Click the button below to reset it.</p>
            <a href="{}" class="button">Reset Password</a>
        </div>
        <div class="footer">
            <p>If you didn't request a password reset, please ignore this email.</p>
            <p>&copy; 2024 Dalle Stores. All rights reserved.</p>
            <p>For support, contact us at <a href="mailto:praisechinonso21@gmail.com">praisechinonso21@gmail.com</a></p>
            
        </div>
    </div>
</body>
</html>
"""

successful_reset_email_html = """
<!DOCTYPE html>
<html>
<head>
    <title>Password Reset Successful - Dalle Stores</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }}
        .container {{
            width: 100%;
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background-color: #333;
            color: #ffffff;
            padding: 20px;
            text-align: center;
        }}
        .content {{
            padding: 20px;
            text-align: center;
        }}
        .button {{
            display: inline-block;
            padding: 10px 20px;
            margin-top: 20px;
            background-color: #ff6347;
            color: #ffffff;
            text-decoration: none;
            border-radius: 5px;
        }}
        .footer {{
            background-color: #f4f4f4;
            color: #666666;
            padding: 10px;
            text-align: center;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Password Reset Successful</h1>
        </div>
        <div class="content">
            <h2>Your password has been successfully reset.</h2>
            <p>You can now use your new password to log in to your account.</p>
        </div>
        <div class="footer">
            <p>If you didn't request a password reset, please ignore this email.</p>
            <p>&copy; 2024 Dalle Stores. All rights reserved.</p>
            <p>For support, contact us at <a href="mailto:praisechinonso21@gmail.com">praisechinonso21@gmail.com</a></p>
        </div>
    </div>
</body>
</html>

"""