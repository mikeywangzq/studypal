import { BookOpen, MessageSquare, Calendar } from 'lucide-react'
import { Link } from 'react-router-dom'

function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-3xl font-bold text-gray-900">
            StudyPal - AI Learning Assistant
          </h1>
          <p className="mt-1 text-sm text-gray-600">
            Your intelligent companion for managing notes, studying, and staying organized
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Welcome to Your Personal Learning Hub
          </h2>
          <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
            Manage your course notes, get AI-powered answers from your knowledge base,
            and never miss a deadline again.
          </p>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {/* Notes Feature */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg mb-4">
              <BookOpen className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Smart Note Management
            </h3>
            <p className="text-gray-600 mb-4">
              Upload and organize your course notes, code snippets, and study materials.
              Automatic categorization and tagging powered by AI.
            </p>
            <button className="text-blue-600 hover:text-blue-800 font-medium">
              Manage Notes →
            </button>
          </div>

          {/* Chat Feature */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-green-100 rounded-lg mb-4">
              <MessageSquare className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              AI Q&A Assistant
            </h3>
            <p className="text-gray-600 mb-4">
              Ask questions and get intelligent answers based on your personal knowledge base.
              Context-aware and always learning from your notes.
            </p>
            <Link to="/chat" className="text-green-600 hover:text-green-800 font-medium inline-block">
              Start Chatting →
            </Link>
          </div>

          {/* Deadlines Feature */}
          <div className="bg-white rounded-lg shadow-lg p-6 hover:shadow-xl transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-purple-100 rounded-lg mb-4">
              <Calendar className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Deadline Tracker
            </h3>
            <p className="text-gray-600 mb-4">
              Keep track of assignments, exams, and project deadlines.
              Get timely reminders so you never miss an important date.
            </p>
            <button className="text-purple-600 hover:text-purple-800 font-medium">
              View Calendar →
            </button>
          </div>
        </div>

        {/* Getting Started Section */}
        <div className="mt-16 bg-white rounded-lg shadow-lg p-8">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            Getting Started
          </h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                1
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">Upload Your Notes</h4>
                <p className="text-gray-600">
                  Start by uploading your course notes, code files, or study materials in Markdown or text format.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                2
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">Ask Questions</h4>
                <p className="text-gray-600">
                  Use the AI chat to ask questions about your notes and get intelligent, context-aware answers.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-semibold">
                3
              </div>
              <div className="ml-4">
                <h4 className="text-lg font-semibold text-gray-900">Stay Organized</h4>
                <p className="text-gray-600">
                  Add your assignment deadlines and exam dates to the calendar and get reminders.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* System Status */}
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            System Status: <span className="text-green-600 font-semibold">All systems operational</span>
          </p>
        </div>
      </main>
    </div>
  )
}

export default HomePage
