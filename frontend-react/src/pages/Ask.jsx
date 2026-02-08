import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, MessageSquare, Brain, Sparkles } from 'lucide-react'
import './Ask.css'

export default function AskPage() {
    const { token } = useAuth()
    const [question, setQuestion] = useState('')
    const [loading, setLoading] = useState(false)
    const [conversation, setConversation] = useState([])
    const [error, setError] = useState('')

    const handleAsk = async () => {
        if (!question.trim() || loading) return

        const userQuestion = question.trim()
        setQuestion('')
        setError('')
        setLoading(true)

        // Add user message to conversation
        setConversation(prev => [...prev, { role: 'user', content: userQuestion }])

        try {
            const res = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: userQuestion })
            })

            if (!res.ok) {
                const err = await res.json()
                throw new Error(err.detail || 'Failed to get answer')
            }

            const data = await res.json()

            // Add AI response to conversation
            setConversation(prev => [...prev, {
                role: 'assistant',
                content: data.answer,
                sources: data.sources
            }])
        } catch (err) {
            setError(err.message)
            // Remove the user's question if there was an error
            setConversation(prev => prev.slice(0, -1))
        } finally {
            setLoading(false)
        }
    }

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault()
            handleAsk()
        }
    }

    return (
        <div className="ask-page">
            <div className="page-header">
                <h1 className="gradient-text">
                    <Brain size={32} /> Ask AI
                </h1>
                <p>Ask questions about your past meetings using AI-powered search</p>
            </div>

            <div className="chat-container glass">
                {/* Chat Messages */}
                <div className="chat-messages">
                    {conversation.length === 0 ? (
                        <div className="empty-chat">
                            <Sparkles size={48} />
                            <h3>Ask me anything about your meetings!</h3>
                            <p>I'll search through your past meetings and provide relevant answers.</p>
                            <div className="example-questions">
                                <span onClick={() => setQuestion("What were the key decisions made recently?")}>
                                    "What were the key decisions made recently?"
                                </span>
                                <span onClick={() => setQuestion("Who is responsible for the frontend tasks?")}>
                                    "Who is responsible for the frontend tasks?"
                                </span>
                                <span onClick={() => setQuestion("What deadlines are coming up?")}>
                                    "What deadlines are coming up?"
                                </span>
                            </div>
                        </div>
                    ) : (
                        <AnimatePresence>
                            {conversation.map((msg, i) => (
                                <motion.div
                                    key={i}
                                    className={`chat-message ${msg.role}`}
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.05 }}
                                >
                                    <div className="message-avatar">
                                        {msg.role === 'user' ? '👤' : '🤖'}
                                    </div>
                                    <div className="message-content">
                                        <div className="message-text">{msg.content}</div>
                                        {msg.sources && msg.sources.length > 0 && (
                                            <div className="message-sources">
                                                <span className="sources-label">Sources:</span>
                                                {msg.sources.map((s, j) => (
                                                    <span key={j} className="source-tag">{s}</span>
                                                ))}
                                            </div>
                                        )}
                                    </div>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    )}

                    {loading && (
                        <motion.div
                            className="chat-message assistant loading"
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                        >
                            <div className="message-avatar">🤖</div>
                            <div className="message-content">
                                <Loader2 className="spinner" size={20} />
                                <span>Searching meetings...</span>
                            </div>
                        </motion.div>
                    )}
                </div>

                {/* Error Message */}
                {error && (
                    <div className="chat-error">
                        ⚠️ {error}
                    </div>
                )}

                {/* Input Area */}
                <div className="chat-input-area">
                    <div className="chat-input-wrapper">
                        <MessageSquare size={20} className="input-icon" />
                        <input
                            type="text"
                            value={question}
                            onChange={(e) => setQuestion(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about your meetings..."
                            disabled={loading}
                        />
                        <button
                            onClick={handleAsk}
                            disabled={loading || !question.trim()}
                            className="send-btn"
                        >
                            {loading ? <Loader2 className="spinner" size={18} /> : <Send size={18} />}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    )
}
