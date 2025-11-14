# Network Access Quick Start Guide

## For Windows Users

### Step 1: Start the Server with Network Access

#### Option A: Using Batch Script (Easiest)

```batch
cd c:\Etu_student_result
.\run_network.bat
```

#### Option B: Using PowerShell

```powershell
powershell -ExecutionPolicy Bypass -File run_network.ps1
```

#### Option C: Direct Command

```powershell
python manage.py runserver 0.0.0.0:8000
```

### Step 2: Find Your Computer's IP Address

Open Command Prompt (`cmd`) and run:

```cmd
ipconfig
```

Look for **IPv4 Address** under your network adapter (e.g., `192.168.1.100` or `10.0.0.50`)

### Step 3: Access from Another Computer

On another computer on the same network, open a web browser and visit:

```text
http://YOUR_COMPUTER_IP:8000
```

**Example**: `http://192.168.1.100:8000`

---

## Access Points

Once the server is running:

| Page | Local URL | Network URL |
|------|-----------|-------------|
| **Homepage** | `http://127.0.0.1:8000` | `http://192.168.x.x:8000` |
| **Admin Portal** | `http://127.0.0.1:8000/officer/portal/` | `http://192.168.x.x:8000/officer/portal/` |
| **Student Login** | `http://127.0.0.1:8000/student/login/` | `http://192.168.x.x:8000/student/login/` |
| **Django Admin** | `http://127.0.0.1:8000/admin/` | `http://192.168.x.x:8000/admin/` |

---

## Network Hostname Access (Optional)

### Windows Hosts File Setup

To use `etusl:8000` or `result:8000` instead of IP addresses:

1. **Edit Windows Hosts File**:
   - Open: `C:\Windows\System32\drivers\etc\hosts` (as Administrator)
   - Add these lines at the end:

   ```text
   192.168.x.x    etusl
   192.168.x.x    result
   ```

   (Replace `192.168.x.x` with your computer's IP address)

2. **Save and close the file**

3. **Access using hostname**:

   ```text
   http://etusl:8000
   http://result:8000
   ```

### Linux/Mac Hosts File Setup

1. **Edit Hosts File**:

   ```bash
   sudo nano /etc/hosts
   ```

2. **Add these lines at the end**:

   ```text
   192.168.x.x    etusl
   192.168.x.x    result
   ```

   (Replace `192.168.x.x` with your computer's IP address)

3. **Save**: `Ctrl+O`, Enter, `Ctrl+X`

4. **Access using hostname**:

   ```text
   http://etusl:8000
   http://result:8000
   ```

---

## Login Credentials

### Admin Accounts

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | admin123 |
| Primary Admin | admin_main | Admin@2025 |
| HOD | hod_admin | HOD@2025 |
| DEAN | dean_admin | DEAN@2025 |

### Student Login

- Click "Student Login" on homepage
- Enter: Student ID, Student Name, Email

---

## Troubleshooting

### Issue: "Connection refused" or "Cannot reach server"

- **Solution 1**: Ensure the server is running: `python manage.py runserver 0.0.0.0:8000`
- **Solution 2**: Verify both computers are on the **same network**
- **Solution 3**: Check firewall settings - allow port 8000

### Issue: "Port 8000 already in use"

- **Solution 1**: Close other applications using port 8000
- **Solution 2**: Use a different port:

  ```powershell
  python manage.py runserver 0.0.0.0:8080
  ```

### Issue: "Page not found" after entering correct IP

- **Solution 1**: Verify you're using the correct format: `http://IP:8000`
- **Solution 2**: Make sure Django server shows "Starting development server at..."
- **Solution 3**: Try accessing `http://IP:8000/` (with trailing slash)

### Issue: Using hostname (etusl:8000) doesn't work

- **Solution**: Edit Windows Hosts file as described above in the "Network Hostname Access" section

---

## Performance Tips

### For Production/Shared Network Use

The development server is suitable for testing but not production. For better performance:

```powershell
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 Etu_student_result.wsgi:application
```

---

## Summary Commands

```powershell
# Find your IP
ipconfig

# Start server for network access
python manage.py runserver 0.0.0.0:8000

# Or use startup script
.\run_network.bat

# Access from another computer
# http://YOUR_IP:8000
```

---

**Last Updated**: November 14, 2025

