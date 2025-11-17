import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import ChatPage from './pages/ChatPage'
import DeadlinesPage from './pages/DeadlinesPage'

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/deadlines" element={<DeadlinesPage />} />
          {/* TODO: Add more routes as we build them */}
          {/* <Route path="/notes" element={<NotesPage />} /> */}
        </Routes>
      </div>
    </Router>
  )
}

export default App
