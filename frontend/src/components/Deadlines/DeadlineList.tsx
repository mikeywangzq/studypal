import { Calendar, Clock, AlertCircle, CheckCircle2, Trash2, Edit } from 'lucide-react'
import { Deadline } from '../../types'
import { formatDistanceToNow, isPast, formatDate } from 'date-fns'
import { zhCN } from 'date-fns/locale'

interface DeadlineListProps {
  deadlines: Deadline[]
  onComplete: (id: string) => void
  onDelete: (id: string) => void
  onEdit?: (deadline: Deadline) => void
}

function DeadlineList({ deadlines, onComplete, onDelete, onEdit }: DeadlineListProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      case 'low':
        return 'bg-green-100 text-green-800 border-green-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityLabel = (priority: string) => {
    switch (priority) {
      case 'high':
        return '高'
      case 'medium':
        return '中'
      case 'low':
        return '低'
      default:
        return priority
    }
  }

  const getTimeColor = (dueDate: string, status: string) => {
    if (status === 'completed') return 'text-green-600'
    const due = new Date(dueDate)
    const now = new Date()
    const hoursUntilDue = (due.getTime() - now.getTime()) / (1000 * 60 * 60)

    if (isPast(due)) return 'text-red-600'
    if (hoursUntilDue <= 24) return 'text-orange-600'
    if (hoursUntilDue <= 72) return 'text-yellow-600'
    return 'text-gray-600'
  }

  const getTimeText = (dueDate: string, status: string) => {
    if (status === 'completed') return '已完成'
    const due = new Date(dueDate)
    if (isPast(due)) {
      return `逾期 ${formatDistanceToNow(due, { locale: zhCN })}`
    }
    return `还剩 ${formatDistanceToNow(due, { locale: zhCN })}`
  }

  if (deadlines.length === 0) {
    return (
      <div className="text-center py-12">
        <Calendar className="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <p className="text-gray-500">暂无 DDL</p>
        <p className="text-sm text-gray-400 mt-2">点击上方"添加 DDL"按钮创建</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {deadlines.map((deadline) => {
        const isOverdue = isPast(new Date(deadline.due_date)) && deadline.status === 'pending'
        const isCompleted = deadline.status === 'completed'

        return (
          <div
            key={deadline.id}
            className={`border rounded-lg p-4 transition-all hover:shadow-md ${
              isCompleted
                ? 'bg-gray-50 border-gray-200 opacity-75'
                : isOverdue
                ? 'bg-red-50 border-red-200'
                : 'bg-white border-gray-200'
            }`}
          >
            <div className="flex items-start justify-between gap-4">
              {/* Left: Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  {/* Checkbox */}
                  <button
                    onClick={() => onComplete(deadline.id)}
                    disabled={isCompleted}
                    className={`flex-shrink-0 w-5 h-5 rounded border-2 flex items-center justify-center transition-colors ${
                      isCompleted
                        ? 'bg-green-500 border-green-500'
                        : 'border-gray-300 hover:border-blue-500'
                    }`}
                  >
                    {isCompleted && <CheckCircle2 className="w-4 h-4 text-white" />}
                  </button>

                  {/* Title */}
                  <h3
                    className={`text-lg font-semibold ${
                      isCompleted ? 'line-through text-gray-500' : 'text-gray-900'
                    }`}
                  >
                    {deadline.title}
                  </h3>

                  {/* Priority Badge */}
                  <span
                    className={`px-2 py-0.5 text-xs font-medium rounded-full border ${getPriorityColor(
                      deadline.priority
                    )}`}
                  >
                    {getPriorityLabel(deadline.priority)}
                  </span>
                </div>

                {/* Course */}
                {deadline.course && (
                  <p className="text-sm text-gray-600 mb-1">
                    📚 {deadline.course}
                  </p>
                )}

                {/* Description */}
                {deadline.description && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2">
                    {deadline.description}
                  </p>
                )}

                {/* Time Info */}
                <div className="flex items-center gap-4 text-sm">
                  <div className="flex items-center gap-1 text-gray-600">
                    <Clock className="w-4 h-4" />
                    <span>
                      {new Date(deadline.due_date).toLocaleString('zh-CN', {
                        month: 'short',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>

                  <div className={`flex items-center gap-1 font-medium ${getTimeColor(deadline.due_date, deadline.status)}`}>
                    {isOverdue && <AlertCircle className="w-4 h-4" />}
                    <span>{getTimeText(deadline.due_date, deadline.status)}</span>
                  </div>
                </div>
              </div>

              {/* Right: Actions */}
              <div className="flex gap-2">
                {onEdit && !isCompleted && (
                  <button
                    onClick={() => onEdit(deadline)}
                    className="p-2 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                    title="编辑"
                  >
                    <Edit className="w-4 h-4" />
                  </button>
                )}
                <button
                  onClick={() => {
                    if (window.confirm('确定要删除这个 DDL 吗？')) {
                      onDelete(deadline.id)
                    }
                  }}
                  className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                  title="删除"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}

export default DeadlineList
