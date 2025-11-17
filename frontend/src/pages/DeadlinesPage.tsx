import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Calendar as CalendarIcon, Plus, List, AlertCircle, CheckCircle2, Clock } from 'lucide-react'
import deadlineService from '../services/deadlineService'
import { DeadlineCreate } from '../types'
import DeadlineForm from '../components/Deadlines/DeadlineForm'
import DeadlineList from '../components/Deadlines/DeadlineList'

type ViewMode = 'list' | 'upcoming' | 'overdue' | 'completed'

function DeadlinesPage() {
  const queryClient = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [viewMode, setViewMode] = useState<ViewMode>('list')

  // Fetch deadlines based on view mode
  const { data: allDeadlines, isLoading } = useQuery({
    queryKey: ['deadlines', 'all'],
    queryFn: () => deadlineService.getDeadlines({ limit: 100 }),
  })

  const { data: upcomingDeadlines } = useQuery({
    queryKey: ['deadlines', 'upcoming'],
    queryFn: () => deadlineService.getUpcomingDeadlines(7),
  })

  const { data: overdueDeadlines } = useQuery({
    queryKey: ['deadlines', 'overdue'],
    queryFn: () => deadlineService.getOverdueDeadlines(),
  })

  const { data: statistics } = useQuery({
    queryKey: ['deadlines', 'statistics'],
    queryFn: () => deadlineService.getStatistics(),
  })

  // Create deadline mutation
  const createMutation = useMutation({
    mutationFn: (deadline: DeadlineCreate) => deadlineService.createDeadline(deadline),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deadlines'] })
      setShowForm(false)
    },
  })

  // Complete deadline mutation
  const completeMutation = useMutation({
    mutationFn: (id: string) => deadlineService.completeDeadline(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deadlines'] })
    },
  })

  // Delete deadline mutation
  const deleteMutation = useMutation({
    mutationFn: (id: string) => deadlineService.deleteDeadline(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deadlines'] })
    },
  })

  const handleCreateDeadline = (deadline: DeadlineCreate) => {
    createMutation.mutate(deadline)
  }

  const handleCompleteDeadline = (id: string) => {
    completeMutation.mutate(id)
  }

  const handleDeleteDeadline = (id: string) => {
    deleteMutation.mutate(id)
  }

  // Get deadlines to display based on view mode
  const getDisplayDeadlines = () => {
    switch (viewMode) {
      case 'upcoming':
        return upcomingDeadlines || []
      case 'overdue':
        return overdueDeadlines || []
      case 'completed':
        return allDeadlines?.deadlines.filter((d) => d.status === 'completed') || []
      case 'list':
      default:
        return allDeadlines?.deadlines.filter((d) => d.status === 'pending') || []
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
                <CalendarIcon className="w-6 h-6 text-purple-600" />
                DDL 管理
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                管理你的作业、考试和项目截止日期
              </p>
            </div>
            <button
              onClick={() => setShowForm(true)}
              className="flex items-center gap-2 px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
            >
              <Plus className="w-4 h-4" />
              添加 DDL
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-blue-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">全部</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.total}</p>
                </div>
                <List className="w-8 h-8 text-blue-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-yellow-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">待完成</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.pending}</p>
                </div>
                <Clock className="w-8 h-8 text-yellow-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-green-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">已完成</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.completed}</p>
                </div>
                <CheckCircle2 className="w-8 h-8 text-green-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-red-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">已逾期</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.overdue}</p>
                </div>
                <AlertCircle className="w-8 h-8 text-red-500" />
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-4 border-l-4 border-orange-500">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">7天内</p>
                  <p className="text-2xl font-bold text-gray-900">{statistics.upcoming_7days}</p>
                </div>
                <CalendarIcon className="w-8 h-8 text-orange-500" />
              </div>
            </div>
          </div>
        )}

        {/* View Mode Tabs */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setViewMode('list')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  viewMode === 'list'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                全部待办
              </button>
              <button
                onClick={() => setViewMode('upcoming')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  viewMode === 'upcoming'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                即将到期
              </button>
              <button
                onClick={() => setViewMode('overdue')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  viewMode === 'overdue'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                已逾期
              </button>
              <button
                onClick={() => setViewMode('completed')}
                className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                  viewMode === 'completed'
                    ? 'border-purple-500 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                已完成
              </button>
            </nav>
          </div>

          {/* Deadlines List */}
          <div className="p-6">
            {isLoading ? (
              <div className="text-center py-12">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
                <p className="text-gray-500 mt-2">加载中...</p>
              </div>
            ) : (
              <DeadlineList
                deadlines={getDisplayDeadlines()}
                onComplete={handleCompleteDeadline}
                onDelete={handleDeleteDeadline}
              />
            )}
          </div>
        </div>
      </div>

      {/* Create Form Modal */}
      {showForm && (
        <DeadlineForm
          onSubmit={handleCreateDeadline}
          onCancel={() => setShowForm(false)}
          isSubmitting={createMutation.isPending}
        />
      )}
    </div>
  )
}

export default DeadlinesPage
