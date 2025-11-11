# 🚀 Quick Hosting Guide - Tourist Safety System

## ⚡ Instant Setup (Choose One)

### Option 1: One-Click Setup (Windows)
```bash
# Double-click this file:
host.bat
```

### Option 2: Quick Local Server
```bash
cd backend
pip install -r requirements.txt
python app.py
```
**Access:** http://localhost:5000

### Option 3: Docker (Recommended)
```bash
docker-compose up -d
```
**Access:** http://localhost:5000

## 🌐 Live URLs After Hosting

- **🏠 Home Page:** `http://your-domain.com/`
- **👨‍💼 Admin Dashboard:** `http://your-domain.com/admin`
- **🆘 SOS System:** Integrated in tourist dashboard
- **📊 Reports:** Admin-only access at `/admin`
- **🔍 Health Check:** `http://your-domain.com/health`

## 🔑 Key Features Available

✅ **User Authentication:** SOS requires user login
✅ **Admin Reports:** Post-incident reports (admin-only)
✅ **Real-time GPS:** Location tracking and geofencing
✅ **Multi-language:** 12+ Indian languages supported
✅ **AI Monitoring:** Advanced threat detection
✅ **Blockchain:** Secure incident logging

## 📋 Default Login

- **Admin Access:** Built-in admin authentication
- **Tourist Login:** Registration required via main page

## 🔧 Production Checklist

- [ ] Change admin password
- [ ] Set secure SECRET_KEY
- [ ] Configure HTTPS
- [ ] Set up domain name
- [ ] Enable monitoring

## 📞 Support

📖 **Full Guide:** See `DEPLOYMENT_README.md`
🔍 **Verify Setup:** Run `python verify_deployment.py`
🛠️ **Issues?** Check logs in `logs/app.log`

---

**Ready to host?** Run `host.bat` for guided setup! 🚀