# Profile Component Architecture

## 📐 Component Structure

```
┌─────────────────────────────────────────────────────────────┐
│                    ProfileComponent                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                Profile Information Card                │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  Username Input       [John Doe          ]      │  │  │
│  │  │  Email Input          [john@example.com  ]      │  │  │
│  │  │                                                  │  │  │
│  │  │  [Cancel]  [Update Profile]                     │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Change Password Card                      │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  🔒 Password Settings        [▼ Expand]         │  │  │
│  │  │  ┌───────────────────────────────────────────┐  │  │  │
│  │  │  │  Current Password    [••••••••]           │  │  │  │
│  │  │  │  New Password        [••••••••] 💪 Strong │  │  │  │
│  │  │  │  Confirm Password    [••••••••]           │  │  │  │
│  │  │  │                                            │  │  │  │
│  │  │  │  [Cancel]  [Change Password]              │  │  │  │
│  │  │  └───────────────────────────────────────────┘  │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Account Information Card                  │  │
│  │    User ID: 123e4567-e89b-12d3-a456-426614174000     │  │
│  │    Member Since: Jan 15, 2024                         │  │
│  │    Last Updated: Nov 13, 2025, 10:30 AM               │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow

```
┌──────────────┐
│   Browser    │
│  (Angular)   │
└──────┬───────┘
       │
       │ HTTP Request (GET /api/users/profile)
       │
       ▼
┌──────────────┐
│ ProfileService│──────► HttpClient
│   (Service)  │         │
└──────────────┘         │
                         ▼
                   ┌─────────────┐
                   │  ASP.NET    │
                   │  Core API   │
                   └─────┬───────┘
                         │
                         ▼
                   ┌─────────────┐
                   │ PostgreSQL  │
                   │  Database   │
                   └─────────────┘
```

## 🏗️ File Dependencies

```
profile.component.ts
├── profile.service.ts
│   ├── HttpClient (Angular)
│   ├── environment.ts (API URL)
│   └── user.model.ts (Interfaces)
│
├── MessageService (PrimeNG)
├── FormBuilder (Angular)
└── Validators (Angular)

profile.component.html
├── PrimeNG Components
│   ├── Card
│   ├── InputText
│   ├── Password
│   ├── Button
│   ├── Panel
│   ├── Message
│   └── Toast
│
└── Bootstrap Grid
    ├── container-fluid
    ├── row
    └── col-*

profile.component.scss
├── PrimeNG Theme
├── Bootstrap Utilities
└── Custom Styles
```

## 📊 Form Validation Flow

```
User Input
    │
    ▼
┌────────────────────┐
│ Reactive Form      │
│ (FormGroup)        │
└────────┬───────────┘
         │
         ▼
┌────────────────────┐      ┌──────────────────┐
│ Field Validators   │──────►│ Required         │
│                    │      ├──────────────────┤
│                    │      │ Email            │
│                    │      ├──────────────────┤
│                    │      │ MinLength        │
│                    │      ├──────────────────┤
│                    │      │ PasswordStrength │
│                    │      └──────────────────┘
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Form Validators    │──────► Password Match
└────────┬───────────┘
         │
         ▼
┌────────────────────┐
│ Valid?             │
├────────┬───────────┤
│  Yes   │    No     │
└────┬───┴───┬───────┘
     │       │
     │       ▼
     │   Show Errors
     │       │
     ▼       ▼
   Submit  [Disabled Button]
```

## 🔐 Password Validation Logic

```
Password Input: "Test@123"
         │
         ▼
┌─────────────────────────────┐
│ passwordStrengthValidator   │
└─────────────────────────────┘
         │
    ┌────┴────┬────────┬──────────┬─────────────┐
    ▼         ▼        ▼          ▼             ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐
│Length  │ │Upper   │ │Number  │ │ Special  │ │ Result │
│>= 8    │ │Case    │ │Present │ │   Char   │ │        │
│   ✅   │ │   ✅   │ │   ✅   │ │    ✅    │ │  VALID │
└────────┘ └────────┘ └────────┘ └──────────┘ └────────┘
```

## 🎭 Component States

```
┌─────────────────────────────────────────────────┐
│           ProfileComponent States                │
├─────────────────────────────────────────────────┤
│                                                  │
│  1. LOADING                                      │
│     ├─ isLoadingProfile = true                  │
│     └─ Display: Spinner                          │
│                                                  │
│  2. VIEWING                                      │
│     ├─ isLoadingProfile = false                 │
│     ├─ Form populated with user data            │
│     └─ Display: Profile form                     │
│                                                  │
│  3. EDITING                                      │
│     ├─ Form is dirty (profileForm.dirty)        │
│     ├─ Cancel button enabled                    │
│     └─ Update button enabled (if valid)         │
│                                                  │
│  4. UPDATING                                     │
│     ├─ isUpdatingProfile = true                 │
│     ├─ Buttons disabled                         │
│     └─ Display: Loading spinner on button       │
│                                                  │
│  5. CHANGING PASSWORD                            │
│     ├─ isChangingPassword = true                │
│     ├─ Password panel expanded                  │
│     └─ Display: Loading spinner on button       │
│                                                  │
│  6. ERROR                                        │
│     ├─ Toast notification shown                 │
│     ├─ Form errors displayed                    │
│     └─ User can retry                            │
│                                                  │
│  7. SUCCESS                                      │
│     ├─ Toast notification shown                 │
│     ├─ Form marked as pristine                  │
│     └─ Data refreshed                            │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 🌐 API Request/Response Flow

### Get Profile

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │ loadProfile()
       ▼
┌──────────────┐
│   Service    │ GET /api/users/profile
└──────┬───────┘ Headers: Authorization: Bearer {token}
       │
       ▼
┌──────────────┐
│   Backend    │
└──────┬───────┘
       │
       ▼
{
  "id": "uuid",
  "username": "johndoe",
  "email": "john@example.com",
  "createdAt": "2024-01-15T10:00:00Z",
  "updatedAt": "2025-11-13T10:30:00Z"
}
       │
       ▼
┌──────────────┐
│  Component   │ Form populated
└──────────────┘ isLoadingProfile = false
```

### Update Profile

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │ updateProfile()
       ▼
┌──────────────┐
│   Service    │ PUT /api/users/profile
└──────┬───────┘ Body: { username, email }
       │
       ▼
┌──────────────┐
│   Backend    │ Validate & Save
└──────┬───────┘
       │
       ├─ SUCCESS (200) ─► Toast: "Profile updated"
       │                   Form marked pristine
       │
       └─ ERROR (400/401) ─► Toast: Error message
                             Form remains dirty
```

### Change Password

```
┌─────────────┐
│  Component  │
└──────┬──────┘
       │ changePassword()
       ▼
┌──────────────┐
│   Service    │ POST /api/users/change-password
└──────┬───────┘ Body: { currentPassword, newPassword }
       │
       ▼
┌──────────────┐
│   Backend    │ Verify current, hash new
└──────┬───────┘
       │
       ├─ SUCCESS (204) ─► Toast: "Password changed"
       │                   Form reset, panel collapsed
       │
       └─ ERROR (401) ─► Toast: "Current password incorrect"
                         Form remains filled
```

## 🎨 Responsive Breakpoints

```
┌────────────────────────────────────────────────────┐
│  Extra Small (< 576px) - Mobile                    │
│  ┌──────────────────────────────────────────────┐ │
│  │  [Username Input - Full Width]                │ │
│  │  [Email Input - Full Width]                   │ │
│  │  [Cancel Button - Full Width]                 │ │
│  │  [Update Button - Full Width]                 │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Small (576px - 768px) - Tablet Portrait           │
│  ┌──────────────────────────────────────────────┐ │
│  │  [Username] [Email]                           │ │
│  │  [Cancel]   [Update]                          │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Medium (768px - 992px) - Tablet Landscape         │
│  ┌──────────────────────────────────────────────┐ │
│  │  [Username Input - 80% Width]                 │ │
│  │  [Email Input - 80% Width]                    │ │
│  │  [Cancel] [Update]                            │ │
│  └──────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Large (992px - 1200px) - Desktop                  │
│  ┌────────────────────────────────────┐           │
│  │  [Username Input - 60% Width]      │           │
│  │  [Email Input - 60% Width]         │           │
│  │         [Cancel] [Update]          │           │
│  └────────────────────────────────────┘           │
└────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────┐
│  Extra Large (> 1200px) - Large Desktop            │
│  ┌──────────────────────────┐                     │
│  │  [Username - 50% Width]  │                     │
│  │  [Email - 50% Width]     │                     │
│  │     [Cancel] [Update]    │                     │
│  └──────────────────────────┘                     │
└────────────────────────────────────────────────────┘
```

## 🧩 Module Dependencies

```
ProfileModule
├── CommonModule (Angular)
├── ReactiveFormsModule (Angular)
├── RouterModule (Angular)
│
├── PrimeNG Modules
│   ├── CardModule
│   ├── InputTextModule
│   ├── PasswordModule
│   ├── ButtonModule
│   ├── PanelModule
│   ├── MessageModule
│   └── ToastModule
│
└── Providers
    └── MessageService (PrimeNG)
```

---

**Visual Guide Version**: 1.0  
**Last Updated**: November 13, 2025
