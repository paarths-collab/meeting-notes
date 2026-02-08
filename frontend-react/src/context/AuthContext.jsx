import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null)
    const [token, setToken] = useState(localStorage.getItem('token'))
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (token) {
            fetchUser()
        } else {
            setLoading(false)
        }
    }, [token])

    const fetchUser = async () => {
        try {
            const res = await fetch('/api/auth/me', {
                headers: { Authorization: `Bearer ${token}` }
            })
            if (res.ok) {
                const data = await res.json()
                setUser(data)
            } else {
                logout()
            }
        } catch (err) {
            logout()
        } finally {
            setLoading(false)
        }
    }

    const login = async (email, password) => {
        const formData = new FormData()
        formData.append('username', email)
        formData.append('password', password)

        const res = await fetch('/api/auth/login', {
            method: 'POST',
            body: formData
        })

        if (!res.ok) {
            const err = await res.json()
            throw new Error(err.detail || 'Login failed')
        }

        const data = await res.json()
        localStorage.setItem('token', data.access_token)
        setToken(data.access_token)
        return data
    }

    const register = async (email, password) => {
        const res = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        })

        if (!res.ok) {
            const err = await res.json()
            throw new Error(err.detail || 'Registration failed')
        }

        return await res.json()
    }

    const logout = () => {
        localStorage.removeItem('token')
        setToken(null)
        setUser(null)
    }

    return (
        <AuthContext.Provider value={{ user, token, loading, login, register, logout }}>
            {children}
        </AuthContext.Provider>
    )
}

export const useAuth = () => useContext(AuthContext)
