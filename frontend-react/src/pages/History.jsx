import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { Clock, CheckSquare, ChevronRight } from 'lucide-react'
import './History.css'

export default function HistoryPage() {
    const { token } = useAuth()
    const [conversations, setConversations] = useState([])
    const [loading, setLoading] = useState(true)
    const [selected, setSelected] = useState(null)

    useEffect(() => {
        fetchConversations()
    }, [])

    const fetchConversations = async () => {
        try {
            const res = await fetch('/api/meetings/conversations', {
                headers: { Authorization: `Bearer ${token}` }
            })
            const data = await res.json()
            setConversations(data)
        } catch (err) {
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    const viewConversation = async (id) => {
        try {
            const res = await fetch(`/api/meetings/conversations/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            const data = await res.json()
            setSelected(data)
        } catch (err) {
            console.error(err)
        }
    }

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        })
    }

    return (
        <div className="history-page">
            <div className="page-header">
                <h1 className="gradient-text">History</h1>
                <p>View your past conversations and extracted tasks</p>
            </div>

            <div className="history-layout">
                {/* Sidebar */}
                <div className="history-list glass">
                    {loading ? (
                        <div className="loading-state">Loading...</div>
                    ) : conversations.length === 0 ? (
                        <div className="empty-state">
                            <p>No conversations yet</p>
                            <span>Process a meeting to get started</span>
                        </div>
                    ) : (
                        conversations.map((conv, i) => (
                            <motion.div
                                key={conv.id}
                                className={`history-item ${selected?.id === conv.id ? 'active' : ''}`}
                                onClick={() => viewConversation(conv.id)}
                                initial={{ opacity: 0, x: -20 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.05 }}
                            >
                                <div className="history-item-content">
                                    <h4>{conv.title || 'Meeting'}</h4>
                                    <div className="history-item-meta">
                                        <span><Clock size={12} /> {formatDate(conv.created_at)}</span>
                                        <span><CheckSquare size={12} /> {conv.task_count} tasks</span>
                                    </div>
                                </div>
                                <ChevronRight size={18} className="chevron" />
                            </motion.div>
                        ))
                    )}
                </div>

                {/* Detail */}
                <div className="history-detail glass">
                    {selected ? (
                        <>
                            <div className="detail-header">
                                <h2>{selected.title || 'Meeting'}</h2>
                                <span className="detail-date">{formatDate(selected.created_at)}</span>
                            </div>

                            {selected.summary && (
                                <div className="detail-section">
                                    <h3>Summary</h3>
                                    <p>{selected.summary}</p>
                                </div>
                            )}

                            <div className="detail-section">
                                <h3>Tasks ({selected.tasks?.length || 0})</h3>
                                <div className="detail-tasks">
                                    {selected.tasks?.map(task => (
                                        <div key={task.id} className="detail-task">
                                            <CheckSquare size={16} />
                                            <div>
                                                <strong>{task.title}</strong>
                                                <span>{task.assigned_to} · {task.deadline}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {selected.transcript && (
                                <div className="detail-section">
                                    <h3>Transcript</h3>
                                    <pre>{selected.transcript}</pre>
                                </div>
                            )}
                        </>
                    ) : (
                        <div className="detail-empty">
                            <p>Select a conversation to view details</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}
