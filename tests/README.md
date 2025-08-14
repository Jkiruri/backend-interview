# SMS Testing Suite

This folder contains comprehensive tests for the SMS functionality using Africa's Talking.

## Test Files

### Core Tests
- `test_sms_simple.py` - Basic SMS functionality test
- `test_sms_with_logging.py` - Comprehensive SMS test with detailed logging
- `test_sms_no_sender_id.py` - Test SMS without sender ID (recommended)
- `debug_sms.py` - Debug SMS service initialization
- `test_africastalking_api.py` - Test Africa's Talking API structure
- `test_sms_response.py` - Test SMS response parsing
- `test_sms_no_sender.py` - Test SMS without sender ID

### Utilities
- `view_logs.py` - Real-time log viewer (similar to `tail -f`)
- `test_auth.py` - Test authentication endpoints
- `test_auth_simple.py` - Simple authentication test

## Running Tests

### Basic SMS Test (without sender ID)
```bash
python tests/test_sms_no_sender_id.py
```

### Comprehensive Test with Logging
```bash
python tests/test_sms_with_logging.py
```

### View Logs in Real-time
```bash
# View SMS logs (default)
python tests/view_logs.py

# View specific log file
python tests/view_logs.py logs/orderflow.log

# View last 20 lines
python tests/view_logs.py logs/sms.log 20
```

### Test Authentication
```bash
# Test authentication endpoints
python tests/test_auth.py

# Simple authentication test
python tests/test_auth_simple.py
```

## Log Files

The tests generate detailed logs in the `logs/` directory:

- `logs/sms.log` - SMS-specific activities (similar to Laravel's `laravel.log`)
- `logs/orderflow.log` - General application logs
- `logs/error.log` - Error logs only

## Log Format

SMS logs follow this format:
```
[2024-01-15 10:30:45] INFO: Sending SMS to +254700123456 - Message: Hello from OrderFlow! This is a test SMS...
[2024-01-15 10:30:46] INFO: Africa's Talking Response: {'SMSMessageData': {...}}
[2024-01-15 10:30:46] INFO: SMS sent successfully to +254700123456 - Message ID: ATXid_123456, Cost: 1.00
```

## Error Examples

Common errors you'll see in logs:
- `UserInBlacklist: 406` - Phone number is blacklisted
- `InvalidSenderId` - Sender ID not registered
- `InsufficientBalance` - Account has insufficient credits

## Before Running Tests

1. **Update Phone Number**: Replace `+254700123456` with your actual phone number in the test files
2. **Check Credentials**: Ensure Africa's Talking credentials are set in `.env`
3. **Register Sender ID**: Optional - register a sender ID with Africa's Talking

## Troubleshooting

### SMS Not Sending
- Check Africa's Talking account balance
- Verify phone number format (+254...)
- Ensure sender ID is registered (if using one)

### Logs Not Appearing
- Check if `logs/` directory exists
- Verify logging configuration in `settings.py`
- Ensure Django is properly set up

### Permission Errors
- Make sure you have write permissions to the `logs/` directory
- Check if the directory is created properly
