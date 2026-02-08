import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { Save, Loader2, CheckCircle, XCircle, Eye, EyeOff } from 'lucide-react'
import './Settings.css'

export default function SettingsPage() {
    const { token } = useAuth()
    const [settings, setSettings] = useState({})
    const [status, setStatus] = useState({})
    const [loading, setLoading] = useState(false)
    const [message, setMessage] = useState('')
    const [showSecrets, setShowSecrets] = useState({})

    useEffect(() => {
        fetchStatus()
    }, [])

    const fetchStatus = async () => {
        try {
            const res = await fetch('/api/settings/', {
                headers: { Authorization: `Bearer ${token}` }
            })
            const data = await res.json()
            setStatus(data)
        } catch (err) {
            console.error(err)
        }
    }

    const handleChange = (field, value) => {
        setSettings(prev => ({ ...prev, [field]: value }))
    }

    const handleSave = async () => {
        setLoading(true)
        setMessage('')

        try {
            const res = await fetch('/api/settings/', {
                method: 'PUT',
                headers: {
                    Authorization: `Bearer ${token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(settings)
            })

            if (res.ok) {
                setMessage('Settings saved successfully!')
                fetchStatus()
                setSettings({})
            }
        } catch (err) {
            setMessage('Failed to save settings')
        } finally {
            setLoading(false)
        }
    }

    const toggleShow = (field) => {
        setShowSecrets(prev => ({ ...prev, [field]: !prev[field] }))
    }

    const StatusBadge = ({ configured }) => (
        <span className={`status-badge ${configured ? 'configured' : 'not-configured'}`}>
            {configured ? (
                <><CheckCircle size={14} /> Connected</>
            ) : (
                <><XCircle size={14} /> Not configured</>
            )}
        </span>
    )

    return (
        <div className="settings-page">
            <div className="page-header">
                <h1 className="gradient-text">Settings</h1>
                <p>Configure your integrations for Notion, Slack, and Gemini</p>
            </div>

            <div className="settings-grid">
                {/* Notion */}
                <motion.div
                    className="settings-card glass"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <div className="card-header">
                        <div className="card-icon notion">
                            <svg width="20" height="20" viewBox="0 0 100 100" fill="currentColor">
                                <path d="M6.017 4.313l55.333 -4.087c6.797 -0.583 8.543 -0.19 12.817 2.917l17.663 12.443c2.913 2.14 3.883 2.723 3.883 5.053v68.243c0 4.277 -1.553 6.807 -6.99 7.193L24.467 99.967c-4.08 0.193 -6.023 -0.39 -8.16 -3.113L3.3 79.94c-2.333 -3.113 -3.3 -5.443 -3.3 -8.167V11.113c0 -3.497 1.553 -6.413 6.017 -6.8z" />
                            </svg>
                        </div>
                        <div>
                            <h3>Notion</h3>
                            <StatusBadge configured={status.notion_configured} />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>API Token</label>
                        <div className="input-with-toggle">
                            <input
                                type={showSecrets.notion ? 'text' : 'password'}
                                placeholder="ntn_..."
                                value={settings.notion_token || ''}
                                onChange={(e) => handleChange('notion_token', e.target.value)}
                            />
                            <button type="button" onClick={() => toggleShow('notion')}>
                                {showSecrets.notion ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Task Database ID</label>
                        <input
                            type="text"
                            placeholder="abc123..."
                            value={settings.notion_task_db_id || ''}
                            onChange={(e) => handleChange('notion_task_db_id', e.target.value)}
                        />
                    </div>
                </motion.div>

                {/* Slack */}
                <motion.div
                    className="settings-card glass"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="card-header">
                        <div className="card-icon slack">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" />
                            </svg>
                        </div>
                        <div>
                            <h3>Slack</h3>
                            <StatusBadge configured={status.slack_configured} />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Bot Token</label>
                        <div className="input-with-toggle">
                            <input
                                type={showSecrets.slack ? 'text' : 'password'}
                                placeholder="xoxb-..."
                                value={settings.slack_bot_token || ''}
                                onChange={(e) => handleChange('slack_bot_token', e.target.value)}
                            />
                            <button type="button" onClick={() => toggleShow('slack')}>
                                {showSecrets.slack ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                    </div>

                    <div className="form-group">
                        <label>Channel ID</label>
                        <input
                            type="text"
                            placeholder="C0123456789"
                            value={settings.slack_channel_id || ''}
                            onChange={(e) => handleChange('slack_channel_id', e.target.value)}
                        />
                    </div>
                </motion.div>

                {/* Gemini */}
                <motion.div
                    className="settings-card glass"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="card-header">
                        <div className="card-icon gemini">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                                <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm0 2c5.523 0 10 4.477 10 10s-4.477 10-10 10S2 17.523 2 12 6.477 2 12 2z" />
                            </svg>
                        </div>
                        <div>
                            <h3>Gemini AI</h3>
                            <StatusBadge configured={status.gemini_configured} />
                        </div>
                    </div>

                    <div className="form-group">
                        <label>API Key <span className="optional">(optional)</span></label>
                        <div className="input-with-toggle">
                            <input
                                type={showSecrets.gemini ? 'text' : 'password'}
                                placeholder="AIza..."
                                value={settings.gemini_api_key || ''}
                                onChange={(e) => handleChange('gemini_api_key', e.target.value)}
                            />
                            <button type="button" onClick={() => toggleShow('gemini')}>
                                {showSecrets.gemini ? <EyeOff size={18} /> : <Eye size={18} />}
                            </button>
                        </div>
                        <span className="form-hint">Leave empty to use shared API key</span>
                    </div>
                </motion.div>
            </div>

            {/* Save Button */}
            <div className="save-section">
                {message && (
                    <motion.div
                        className="save-message"
                        initial={{ opacity: 0, y: -10 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        {message}
                    </motion.div>
                )}

                <button className="save-btn" onClick={handleSave} disabled={loading}>
                    {loading ? (
                        <><Loader2 className="spinner" size={20} /> Saving...</>
                    ) : (
                        <><Save size={20} /> Save Settings</>
                    )}
                </button>
            </div>
        </div>
    )
}
