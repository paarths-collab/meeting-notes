import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { Sparkles, ArrowRight, Loader2 } from 'lucide-react'
import './Auth.css'

export default function AuthPage() {
    const navigate = useNavigate()
    const { login, register } = useAuth()
    const [isLogin, setIsLogin] = useState(true)
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showSuccess, setShowSuccess] = useState(false)

    const handleSubmit = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            if (isLogin) {
                await login(email, password)
                navigate('/') // Redirect after successful login
            } else {
                await register(email, password)
                setIsLogin(true)
                setShowSuccess(true)
                // Clear password but keep email
                setPassword('')
            }
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="auth-page">


            {/* Success Popup */}
            {showSuccess && (
                <motion.div
                    className="success-overlay"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                >
                    <motion.div
                        className="success-modal glass"
                        initial={{ scale: 0.9, y: 20 }}
                        animate={{ scale: 1, y: 0 }}
                    >
                        <div className="success-icon">
                            <Sparkles size={32} />
                        </div>
                        <h3>Account Created!</h3>
                        <p>Your account {email} has been successfully created.</p>
                        <button
                            className="auth-btn"
                            onClick={() => setShowSuccess(false)}
                        >
                            Continue to Sign In <ArrowRight size={18} />
                        </button>
                    </motion.div>
                </motion.div>
            )}

            <motion.div
                className="auth-container glass"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5 }}
            >
                <div className="auth-header">
                    <Sparkles className="auth-logo" size={40} />
                    <h1>MeetingAI</h1>
                    <p>Transform meetings into actionable tasks</p>
                </div>

                <form onSubmit={handleSubmit} className="auth-form">
                    <div className="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            placeholder="you@example.com"
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="••••••••"
                            required
                        />
                    </div>

                    {error && (
                        <motion.div
                            className="error-message"
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                        >
                            {error}
                        </motion.div>
                    )}

                    <button type="submit" className="auth-btn" disabled={loading}>
                        {loading ? (
                            <Loader2 className="spinner" size={20} />
                        ) : (
                            <>
                                {isLogin ? 'Sign In' : 'Create Account'}
                                <ArrowRight size={18} />
                            </>
                        )}
                    </button>
                </form>

                <div className="auth-switch">
                    <span>{isLogin ? "Don't have an account?" : "Already have an account?"}</span>
                    <button onClick={() => {
                        setIsLogin(!isLogin)
                        setError('')
                    }}>
                        {isLogin ? 'Sign Up' : 'Sign In'}
                    </button>
                </div>
            </motion.div>
        </div>
    )
}
