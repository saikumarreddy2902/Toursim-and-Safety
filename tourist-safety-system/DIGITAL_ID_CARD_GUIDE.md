# Digital ID Card - Complete Guide

## 📋 Overview
The Tourist Safety System includes a comprehensive Digital ID Card feature that displays tourist information in a professional, secure, and verifiable format.

---

## 🎯 Data Fields Used for Digital ID Card

### **1. Personal Information**
These fields are displayed on the front of the digital ID card:

| Field Name | Description | Example | Required |
|------------|-------------|---------|----------|
| `full_name` | Tourist's full legal name | "John Smith" | ✅ Yes |
| `tourist_id` | Unique ID number | "TST-20251024-1234" | ✅ Yes |
| `date_of_birth` | Date of birth | "1990-05-15" | ✅ Yes |
| `nationality` | Country of citizenship | "United States" | ✅ Yes |
| `email` | Email address | "john@example.com" | ✅ Yes |
| `phone_number` | Contact number | "+1-555-0123" | ⚠️ Optional |
| `gender` | Gender | "Male/Female/Other" | ⚠️ Optional |
| `passport_number` | Passport number | "P123456789" | ⚠️ Optional |

### **2. Profile Photo**
- **Field**: `profile_photo_path` or `profile_photo_url`
- **Format**: Image file (JPG, PNG)
- **Default**: If no photo provided, shows default avatar
- **Location**: Displayed prominently on the card front

### **3. Emergency Contacts** (Card Back)
Array of emergency contact objects:
```json
{
  "name": "Jane Smith",
  "relationship": "Wife",
  "phone": "+1-555-9999",
  "email": "jane@example.com"
}
```

### **4. Medical Information** (Card Back)
Medical data for emergency responders:
```json
{
  "blood_type": "O+",
  "allergies": ["Penicillin", "Peanuts"],
  "medications": ["Insulin"],
  "conditions": ["Diabetes Type 1"],
  "medical_notes": "Requires insulin daily"
}
```

### **5. Blockchain Verification**
Security and verification data:
- `blockchain_hash` - Immutable verification hash
- `verification_hash` - Secondary verification
- `verification_status` - Status: "verified", "pending", "unverified"
- `timestamp` - Card issue date

### **6. Card Validity**
- **Issue Date**: Automatically set to registration date
- **Expiry Date**: Automatically calculated as 5 years from issue
- **Status**: Active/Expired based on dates

---

## 🔗 How to Access Digital ID Card

### **Method 1: Direct URL**
```
http://localhost:5000/digital-id?tourist_id=<USER_ID>
```
Replace `<USER_ID>` with the actual tourist ID (e.g., from session).

### **Method 2: From User Dashboard**
Add a button to the user dashboard:
```html
<a href="/digital-id?tourist_id={{ session.user_id }}" class="btn btn-primary">
    📇 View Digital ID Card
</a>
```

### **Method 3: API Endpoint**
Get digital ID data programmatically:
```javascript
fetch('/api/get_digital_id/<tourist_id>')
  .then(response => response.json())
  .then(data => {
    console.log(data.tourist);
  });
```

---

## 📱 Digital ID Card Features

### **Front of Card**
- Large profile photo
- Full name in prominent text
- Tourist ID number with barcode/QR
- Nationality with flag
- Date of birth
- Issue and expiry dates
- Official logo and branding
- Blockchain verification badge

### **Back of Card** (Flip Card)
- Emergency contact list
  - Names, relationships, phone numbers
- Medical information
  - Blood type
  - Allergies
  - Current medications
  - Medical conditions
  - Important notes
- QR code for quick verification
- Blockchain verification details

### **Interactive Features**
1. **Card Flip Animation** - Click to flip front/back
2. **QR Code Generation** - Automatic QR with tourist data
3. **Download Card** - Export as PNG/PDF
4. **Share Card** - Generate shareable link
5. **Verify Authenticity** - Blockchain verification
6. **Print Card** - Print-friendly format

---

## 🛠️ Registration Fields Required

When registering a new tourist, collect these fields for a complete digital ID:

### **Minimum Required Fields:**
```javascript
{
  "username": "johnsmith",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Smith",
  "date_of_birth": "1990-05-15",
  "nationality": "United States"
}
```

### **Recommended Additional Fields:**
```javascript
{
  "phone_number": "+1-555-0123",
  "gender": "Male",
  "passport_number": "P123456789",
  "emergency_contacts": [
    {
      "name": "Jane Smith",
      "relationship": "Spouse",
      "phone": "+1-555-9999"
    }
  ],
  "medical_info": {
    "blood_type": "O+",
    "allergies": ["Penicillin"],
    "medications": [],
    "conditions": []
  }
}
```

---

## 🎨 Card Design Specifications

### **Dimensions**
- Width: 800px
- Height: 500px
- Border Radius: 20px
- Aspect Ratio: 16:10 (standard ID card)

### **Colors**
- **Header**: Blue gradient (#007bff to #0056b3)
- **Background**: White to light gray gradient
- **Border**: Light gray (#e9ecef)
- **Accent**: Purple gradient for page background

### **Typography**
- **Name**: 24px, Bold, Center
- **ID Number**: 18px, Monospace
- **Labels**: 14px, Regular
- **Values**: 14px, Medium

---

## 📊 Current Implementation Status

✅ **Implemented:**
- Digital ID card display page
- API endpoint for fetching tourist data
- Front and back card design
- QR code generation
- Blockchain verification display
- Emergency contacts section
- Medical information section
- Card flip animation
- Responsive design

⚠️ **Needs Integration:**
- Link from user dashboard to digital ID
- Photo upload during registration
- Emergency contact management
- Medical info update interface

---

## 🔧 Quick Setup Instructions

### **Step 1: Register a User with Complete Data**
```bash
POST /api/auth/register
Content-Type: application/json

{
  "username": "tourist1",
  "email": "tourist@example.com",
  "password": "Password123!",
  "full_name": "John Smith",
  "date_of_birth": "1990-05-15",
  "nationality": "United States",
  "phone_number": "+1-555-0123"
}
```

### **Step 2: Access Digital ID**
After registration, get the `user_id` from the response, then navigate to:
```
http://localhost:5000/digital-id?tourist_id=<user_id>
```

### **Step 3: View and Interact**
- Click card to flip between front and back
- View emergency contacts and medical info
- Download or share the card

---

## 🔐 Security Features

1. **Blockchain Verification**: Each card has a unique blockchain hash for verification
2. **Encrypted Data**: Medical information is encrypted in the database
3. **QR Code Verification**: QR codes contain cryptographic signatures
4. **Session-Based Access**: Only authenticated users can view their own cards
5. **Expiry Validation**: Cards expire after 5 years and show expired status

---

## 📞 Support

For questions or issues with the Digital ID Card feature:
- Check the MongoDB database for user data
- Verify the tourist_id parameter in the URL
- Ensure the `/api/get_digital_id/<tourist_id>` endpoint returns data
- Check browser console for JavaScript errors

---

## 📝 Example User Data Structure

Complete user object in MongoDB:
```json
{
  "_id": "ObjectId(...)",
  "user_id": "USR-20251024-1234",
  "username": "johnsmith",
  "email": "john@example.com",
  "full_name": "John Smith",
  "date_of_birth": "1990-05-15",
  "nationality": "United States",
  "phone_number": "+1-555-0123",
  "gender": "Male",
  "passport_number": "P123456789",
  "profile_photo_path": "uploads/profiles/photo.jpg",
  "emergency_contacts": [
    {
      "name": "Jane Smith",
      "relationship": "Spouse",
      "phone": "+1-555-9999",
      "email": "jane@example.com"
    }
  ],
  "medical_info": {
    "blood_type": "O+",
    "allergies": ["Penicillin"],
    "medications": ["Insulin"],
    "conditions": ["Type 1 Diabetes"],
    "medical_notes": "Requires daily insulin"
  },
  "blockchain_hash": "a1b2c3d4e5f6...",
  "verification_status": "verified",
  "created_at": "2025-10-24T10:00:00Z"
}
```

---

## 🚀 Next Steps

To fully integrate the Digital ID Card:

1. **Add Link to User Dashboard**: Add a "View Digital ID" button
2. **Profile Completion Form**: Add UI to update emergency contacts and medical info
3. **Photo Upload**: Implement profile photo upload feature
4. **Print/Download**: Enhance download functionality for PDF export
5. **Share Feature**: Implement secure card sharing via link or QR

The digital ID card system is already built and functional - it just needs user data to display!
