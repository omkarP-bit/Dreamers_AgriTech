# FasalMitra Frontend

React-based frontend for the FasalMitra AI farming assistant application.

## Features

- **Authentication**: User registration and login with email/password
- **Chat Interface**: Real-time chat with AI farming assistant
- **No Prerequisites**: Users can start chatting immediately after login
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Setup

### Prerequisites

- Node.js 16+ and npm/yarn

### Installation

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file (if needed):
```
VITE_API_URL=http://localhost:8000/api
```

### Running the Application

**Development mode:**
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

**Build for production:**
```bash
npm run build
```

**Preview production build:**
```bash
npm run preview
```

## Project Structure

```
src/
├── api.js                 # API client setup and calls
├── App.jsx               # Main app component and routing
├── main.jsx              # React entry point
├── index.css             # Global styles with Tailwind
├── context/
│   └── AuthContext.jsx   # Authentication context and hooks
├── components/
│   └── ProtectedRoute.jsx # Route protection wrapper
└── pages/
    ├── LoginPage.jsx     # Login page
    ├── RegisterPage.jsx  # Registration page
    └── ChatPage.jsx      # Main chat interface
```

## Technologies Used

- **React 18**: UI framework
- **React Router**: Client-side routing
- **Axios**: HTTP client
- **Tailwind CSS**: Styling
- **Vite**: Build tool
- **Lucide React**: Icon library

## Features Explained

### Authentication Flow
- Users register with name, email, and password
- JWT token is stored in localStorage for session management
- Protected routes ensure only authenticated users can access the chat

### Chat Interface
- Displays all messages with timestamps
- Shows user and bot messages in different styles
- Auto-scrolls to latest message
- Loads chat history on page load
- No prerequisites needed to start chatting

### API Integration
- All API calls include Bearer token authentication
- Automatic token refresh on requests
- Error handling with user-friendly messages

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_API_URL=http://localhost:8000/api
```

## Troubleshooting

**CORS errors**: Make sure backend is running on port 8000 and CORS_ORIGINS includes your frontend URL

**Login issues**: Verify backend is running and MongoDB is connected

**Chat not working**: Check network tab in browser devtools for API errors

## Contributing

Feel free to submit pull requests and issues.
