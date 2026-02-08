import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import { motion, AnimatePresence } from 'framer-motion'
import { Send, Loader2, CheckCircle2, User, Calendar, FileText } from 'lucide-react'
import './Process.css'

export default function ProcessPage() {
    const { token } = useAuth()
    const [inputType, setInputType] = useState('text') // text, link, file
    const [transcript, setTranscript] = useState('')
    const [fileUrl, setFileUrl] = useState('')
    const [filePath, setFilePath] = useState('')
    const [manualTitle, setManualTitle] = useState('')
    const [manualDate, setManualDate] = useState('')
    const [loading, setLoading] = useState(false)
    const [result, setResult] = useState(null)
    const [error, setError] = useState('')

    const handleProcess = async () => {
        setLoading(true)
        setError('')
        setResult(null)

        try {
            let body = {}
            if (inputType === 'text') {
                if (!transcript.trim()) return;
                if (!manualTitle.trim() || !manualDate) {
                    setError("Title and Date are required for text transcripts.");
                    setLoading(false);
                    return;
                }
                body = {
                    transcript,
                    title: manualTitle,
                    meeting_date: manualDate
                }
            } else if (inputType === 'link') {
                if (!fileUrl.trim()) return
                body = {
                    file_url: fileUrl,
                    title: manualTitle || undefined,
                    meeting_date: manualDate || undefined
                }
            } else if (inputType === 'file') {
                if (!filePath.trim()) return
                body = {
                    file_path: filePath,
                    title: manualTitle || undefined,
                    meeting_date: manualDate || undefined
                }
            }

            const res = await fetch('/api/meetings/process', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(body)
            })

            if (!res.ok) {
                const contentType = res.headers.get("content-type");
                if (contentType && contentType.indexOf("application/json") !== -1) {
                    const err = await res.json();
                    throw new Error(err.detail || 'Processing failed');
                } else {
                    const text = await res.text();
                    throw new Error(`Server Error (${res.status}): ${text.substring(0, 100)}...`);
                }
            }

            const data = await res.json()
            setResult(data)
            setTranscript('')
            setFileUrl('')
            setFilePath('')
            setManualTitle('')
            setManualDate('')
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="process-page">
            <div className="page-header">
                <h1 className="gradient-text">Process Meeting</h1>
                <p>Extract tasks from transcripts, links, or files</p>
            </div>

            <div className="process-card glass">
                {/* Input Type Tabs */}
                <div className="input-tabs">
                    <button
                        className={`tab-btn ${inputType === 'text' ? 'active' : ''}`}
                        onClick={() => setInputType('text')}
                    >
                        <FileText size={18} /> Text
                    </button>
                    <button
                        className={`tab-btn ${inputType === 'link' ? 'active' : ''}`}
                        onClick={() => setInputType('link')}
                    >
                        <Send size={18} /> Link
                    </button>
                    <button
                        className={`tab-btn ${inputType === 'file' ? 'active' : ''}`}
                        onClick={() => setInputType('file')}
                    >
                        <Calendar size={18} /> File Path
                    </button>
                </div>

                {inputType === 'text' && (
                    <div className="input-group">
                        <textarea
                            value={transcript}
                            onChange={(e) => setTranscript(e.target.value)}
                            placeholder="Paste your meeting notes or transcript here..."
                            rows={8}
                            className="text-area-input"
                        />
                        <div className="meta-inputs">
                            <div className="meta-field">
                                <label>Meeting Title</label>
                                <input
                                    type="text"
                                    value={manualTitle}
                                    onChange={(e) => setManualTitle(e.target.value)}
                                    placeholder="e.g. Brainstorming Session"
                                    className="text-input"
                                />
                            </div>
                            <div className="meta-field">
                                <label>Meeting Date</label>
                                <input
                                    type="date"
                                    value={manualDate}
                                    onChange={(e) => setManualDate(e.target.value)}
                                    className="text-input"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {inputType === 'link' && (
                    <div className="input-group">
                        <input
                            type="text"
                            value={fileUrl}
                            onChange={(e) => setFileUrl(e.target.value)}
                            placeholder="Enter URL (e.g. https://example.com/transcript.txt)"
                            className="text-input"
                        />
                        <div className="meta-inputs">
                            <div className="meta-field">
                                <label>Meeting Title (optional)</label>
                                <input
                                    type="text"
                                    value={manualTitle}
                                    onChange={(e) => setManualTitle(e.target.value)}
                                    placeholder="e.g. Sprint Planning"
                                    className="text-input"
                                />
                            </div>
                            <div className="meta-field">
                                <label>Meeting Date (optional)</label>
                                <input
                                    type="date"
                                    value={manualDate}
                                    onChange={(e) => setManualDate(e.target.value)}
                                    className="text-input"
                                />
                            </div>
                        </div>
                    </div>
                )}

                {inputType === 'file' && (
                    <div className="input-group">
                        <input
                            type="text"
                            value={filePath}
                            onChange={(e) => setFilePath(e.target.value)}
                            placeholder="Enter local server file path (e.g. /home/user/meeting.mp3)"
                            className="text-input"
                        />
                        <div className="meta-inputs">
                            <div className="meta-field">
                                <label>Meeting Title (optional)</label>
                                <input
                                    type="text"
                                    value={manualTitle}
                                    onChange={(e) => setManualTitle(e.target.value)}
                                    placeholder="e.g. Weekly Standup"
                                    className="text-input"
                                />
                            </div>
                            <div className="meta-field">
                                <label>Meeting Date (optional)</label>
                                <input
                                    type="date"
                                    value={manualDate}
                                    onChange={(e) => setManualDate(e.target.value)}
                                    className="text-input"
                                />
                            </div>
                        </div>
                        <p className="text-sm text-muted">File must be accessible by the backend server.</p>
                    </div>
                )}

                {error && (
                    <motion.div
                        className="error-banner"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        {error}
                    </motion.div>
                )}

                <button
                    className="process-btn"
                    onClick={handleProcess}
                    disabled={
                        loading ||
                        (inputType === 'text' && !transcript.trim()) ||
                        (inputType === 'link' && !fileUrl.trim()) ||
                        (inputType === 'file' && !filePath.trim())
                    }
                >
                    {loading ? (
                        <>
                            <Loader2 className="spinner" size={20} />
                            Processing...
                        </>
                    ) : (
                        <>
                            <Send size={20} />
                            Extract Tasks
                        </>
                    )}
                </button>
            </div>

            {/* Results */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        className="results-section"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                    >
                        {/* Summary */}
                        {result.summary && (
                            <div className="result-card glass">
                                <h3>📝 Summary</h3>
                                <p>{result.summary}</p>
                            </div>
                        )}

                        {/* Key Points */}
                        {result.key_points && result.key_points.length > 0 && (
                            <div className="result-card glass">
                                <h3>💡 Key Points Discussed</h3>
                                <ul className="points-list">
                                    {result.key_points.map((point, i) => (
                                        <li key={i}>{point}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Decisions */}
                        {result.decisions && result.decisions.length > 0 && (
                            <div className="result-card glass">
                                <h3>🎯 Decisions Made</h3>
                                <ul className="points-list">
                                    {result.decisions.map((decision, i) => (
                                        <li key={i}>{decision}</li>
                                    ))}
                                </ul>
                            </div>
                        )}

                        {/* Tasks */}
                        <div className="result-card glass">
                            <div className="card-header">
                                <h3>✅ Extracted Tasks</h3>
                                <span className="task-count">{result.tasks?.length || 0} tasks</span>
                            </div>

                            <div className="tasks-list">
                                {result.tasks?.map((task, i) => (
                                    <motion.div
                                        key={task.id}
                                        className="task-item"
                                        initial={{ opacity: 0, x: -20 }}
                                        animate={{ opacity: 1, x: 0 }}
                                        transition={{ delay: i * 0.1 }}
                                    >
                                        <div className="task-icon">
                                            <CheckCircle2 size={20} />
                                        </div>
                                        <div className="task-content">
                                            <h4>{task.title}</h4>
                                            {task.description && (
                                                <p className="task-desc">{task.description}</p>
                                            )}
                                            <div className="task-meta">
                                                <span><User size={14} /> {task.assigned_to}</span>
                                                <span><Calendar size={14} /> {task.deadline}</span>
                                            </div>
                                        </div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
