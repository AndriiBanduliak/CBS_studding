import './App.css'
import { Layout, Menu, Typography, theme, Button, Space, Dropdown, Card, Row, Col, Statistic, Divider, App as AntApp, Spin, Badge, Tag, Progress } from 'antd'
import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from 'react-router-dom'
import { CalendarOutlined, HomeOutlined, ApartmentOutlined, TeamOutlined, CheckCircleOutlined, SettingOutlined, EnvironmentOutlined, PlusOutlined, ThunderboltOutlined, RocketOutlined, ArrowUpOutlined, TrophyOutlined } from '@ant-design/icons'
import PropertiesPage from './pages/Properties'
import LocationsPage from './pages/Locations'
import CustomersPage from './pages/Customers'
import BookingsPage from './pages/Bookings'
import TasksPage from './pages/Tasks'
import AuthPage from './pages/Auth'
import Dashboard from './Dashboard'
import IntegrationsPage from './pages/Integrations'
import PrivateRoute from './components/PrivateRoute'
import { ErrorBoundary } from './components/ErrorBoundary'
import { useAuth } from './store/useAuth'
import { useEffect, useMemo, useRef, useState } from 'react'
import { api, ensureCsrfCookie } from './api/client'

const { Header, Sider, Content } = Layout
const { Title } = Typography

function CalendarPage() {
  return <Title level={4}><CalendarOutlined /> Календарь бронирований (скоро)</Title>
}

// pages are imported above

function GlobalAxiosHandler() {
  const { message } = AntApp.useApp()
  const { clear } = useAuth()
  const loadingRef = useRef(0)
  const [, force] = useState(0)
  useEffect(() => {
    const inc = () => { loadingRef.current += 1; force(x=>x+1) }
    const dec = () => { loadingRef.current = Math.max(0, loadingRef.current - 1); force(x=>x+1) }

    const reqId = api.interceptors.request.use((config) => { inc(); return config })
    const resId = api.interceptors.response.use(
      (response) => { dec(); return response },
      (error) => {
        dec()
        const status = error?.response?.status
        const url = error?.config?.url || ''
        const detail = error?.response?.data?.detail || error?.message || 'Сталася помилка запиту'
        const isAuthProbe = url.endsWith('/api/auth/me/') || url.endsWith('/api/auth/stats/')
        if (status && status >= 500) {
          message.error('Серверна помилка: ' + detail)
        } else if (status && status >= 400) {
          if (!isAuthProbe) message.warning('Помилка: ' + detail)
        } else {
          message.error(detail)
        }
        if (status === 401) clear()
        return Promise.reject(error)
      }
    )
    return () => {
      api.interceptors.request.eject(reqId)
      api.interceptors.response.eject(resId)
    }
  }, [message])

  const show = loadingRef.current > 0
  return show ? (
    <div style={{ position:'fixed', inset:0, display:'flex', alignItems:'center', justifyContent:'center', pointerEvents:'none', zIndex: 2000 }}>
      <Spin size="large" />
    </div>
  ) : null
}

function Shell() {
  useEffect(() => { ensureCsrfCookie() }, [])
  const { setUser } = useAuth()
  useEffect(() => { api.get('/api/auth/me/', { withCredentials: true }).then(r=>setUser(r.data?.username ? { username: r.data.username } : null)).catch(()=>setUser(null)) }, [])
  const items = [
    { key: 'dashboard', icon: <HomeOutlined />, label: <Link to="/">Головна</Link> },
    { key: 'calendar', icon: <CalendarOutlined />, label: <Link to="/calendar">Календар</Link> },
    { key: 'locations', icon: <EnvironmentOutlined />, label: <Link to="/locations">Локації</Link> },
    { key: 'properties', icon: <ApartmentOutlined />, label: <Link to="/properties">Обʼєкти</Link> },
    { key: 'bookings', icon: <HomeOutlined />, label: <Link to="/bookings">Бронювання</Link> },
    { key: 'tasks', icon: <CheckCircleOutlined />, label: <Link to="/tasks">Завдання</Link> },
    { key: 'customers', icon: <TeamOutlined />, label: <Link to="/customers">Клієнти</Link> },
    { key: 'settings', icon: <SettingOutlined />, label: <a href="http://127.0.0.1:8000/api/docs/" target="_blank" rel="noreferrer">API Docs</a> },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider breakpoint="lg" collapsedWidth="0">
        <div style={{ height: 48, margin: 16, color: '#fff', fontWeight: 600 }}>RentMaster</div>
        <Menu theme="dark" mode="inline" items={items} />
      </Sider>
      <Layout>
        <Header style={{ background: 'transparent', paddingInline: 24, display: 'flex', justifyContent: 'end' }}>
          <UserMenu />
        </Header>
        <Content style={{ margin: 24 }}>
          <Routes>
            <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
            <Route path="/auth" element={<AuthPage />} />
            <Route path="/calendar" element={<PrivateRoute><CalendarPage /></PrivateRoute>} />
            <Route path="/locations" element={<PrivateRoute><LocationsPage /></PrivateRoute>} />
            <Route path="/properties" element={<PrivateRoute><PropertiesPage /></PrivateRoute>} />
            <Route path="/integrations" element={<PrivateRoute><IntegrationsPage /></PrivateRoute>} />
            <Route path="/bookings" element={<PrivateRoute><BookingsPage /></PrivateRoute>} />
            <Route path="/tasks" element={<PrivateRoute><TasksPage /></PrivateRoute>} />
            <Route path="/customers" element={<PrivateRoute><CustomersPage /></PrivateRoute>} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  )
}

function AppRoot() {
  return (
    <AntApp>
      <BrowserRouter>
        <GlobalAxiosHandler />
        <ErrorBoundary>
          <Shell />
        </ErrorBoundary>
      </BrowserRouter>
    </AntApp>
  )
}

function UserMenu() {
  const [user, setUser] = useState(null)
  const navigate = useNavigate()
  useEffect(() => {
    api.get('/api/auth/me/', { withCredentials: true }).then(r=>setUser(r.data)).catch(()=>setUser(null))
  }, [])

  async function doLogout() {
    try { await api.post('/api/auth/logout/', {}, { withCredentials: true }); } catch {}
    setUser(null)
    navigate('/auth')
  }

  if (!user) {
    return <Link to="/auth"><Button>Увійти / Реєстрація</Button></Link>
  }

  const menuItems = [{ key: 'logout', label: <span onClick={doLogout}>Выйти</span> }]
  return (
    <Space>
      <Dropdown menu={{ items: menuItems }}>
        <Button type="text">{user.username}</Button>
      </Dropdown>
    </Space>
  )
}

export default AppRoot
