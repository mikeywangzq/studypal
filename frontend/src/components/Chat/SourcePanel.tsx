import { FileText, ExternalLink } from 'lucide-react'
import { SourceReference } from '../../types'

interface SourcePanelProps {
  sources: SourceReference[]
}

function SourcePanel({ sources }: SourcePanelProps) {
  if (sources.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 h-full">
        <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5 text-gray-600" />
          引用来源
        </h2>
        <div className="text-center text-gray-500 text-sm py-8">
          <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
          <p>问题的答案来源会显示在这里</p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 h-full overflow-y-auto">
      <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5 text-gray-600" />
        引用来源 ({sources.length})
      </h2>

      <div className="space-y-4">
        {sources.map((source, index) => (
          <div
            key={source.note_id}
            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer"
          >
            <div className="flex items-start justify-between gap-2 mb-2">
              <h3 className="font-medium text-gray-900 text-sm flex items-center gap-2">
                <span className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-xs font-semibold">
                  {index + 1}
                </span>
                <span className="line-clamp-1">{source.title}</span>
              </h3>
              <button
                onClick={() => {
                  // TODO: Navigate to note detail page
                  console.log('View note:', source.note_id)
                }}
                className="text-gray-400 hover:text-blue-600 transition-colors flex-shrink-0"
                title="查看完整笔记"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>

            <p className="text-xs text-gray-600 mb-3 line-clamp-3">
              {source.content_snippet}
            </p>

            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-200 rounded-full h-1.5">
                <div
                  className="bg-blue-600 h-1.5 rounded-full transition-all"
                  style={{ width: `${(1 - source.relevance_score) * 100}%` }}
                />
              </div>
              <span className="text-xs text-gray-500 font-medium">
                {((1 - source.relevance_score) * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 p-3 bg-blue-50 rounded-lg">
        <p className="text-xs text-blue-800">
          💡 提示：相关度越高，说明该笔记与您的问题越相关
        </p>
      </div>
    </div>
  )
}

export default SourcePanel
