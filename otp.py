import pyotp
from otp_config import SECRET

totp = pyotp.TOTP(SECRET)

print("Current OTP:")
print(totp.now())
