import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { motion } from 'framer-motion'
import { MessageSquare, History, Settings, LogOut, Sparkles, Brain } from 'lucide-react'
import './Layout.css'

export default function Layout({ children }) {
    const { user, logout } = useAuth()
    const location = useLocation()

    const navItems = [
        { path: '/', icon: MessageSquare, label: 'Process' },
        { path: '/ask', icon: Brain, label: 'Ask AI' },
        { path: '/history', icon: History, label: 'History' },
        { path: '/settings', icon: Settings, label: 'Settings' }
    ]

    return (
        <div className="layout">
            {/* Sidebar */}
            <aside className="sidebar glass">
                <div className="sidebar-header">
                    <Sparkles className="logo-icon" />
                    <span className="logo-text">MeetingAI</span>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map(item => (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
                        >
                            <item.icon size={20} />
                            <span>{item.label}</span>
                        </Link>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <div className="user-info">
                        <div className="user-avatar">
                            {user?.email?.charAt(0).toUpperCase()}
                        </div>
                        <span className="user-email">{user?.email}</span>
                    </div>
                    <button className="logout-btn" onClick={logout}>
                        <LogOut size={18} />
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="main-content">
                <motion.div
                    key={location.pathname}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3 }}
                >
                    {children}
                </motion.div>
            </main>
        </div>
    )
}
