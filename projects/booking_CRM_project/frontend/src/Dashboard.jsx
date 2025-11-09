import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, Row, Col, Statistic, Button, Space, Divider, Typography, theme } from 'antd'
import { ApartmentOutlined, HomeOutlined, TeamOutlined, EnvironmentOutlined, PlusOutlined, ThunderboltOutlined, RocketOutlined, ArrowUpOutlined, TrophyOutlined } from '@ant-design/icons'
import { api } from './api/client'

const { Title } = Typography

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [now, setNow] = useState(new Date())
  const navigate = useNavigate()
  const { token } = theme.useToken()
  
  useEffect(() => { 
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])
  
  useEffect(() => { 
    api.get('/api/auth/stats/', { withCredentials: true })
      .then(r => setStats(r.data))
      .catch(() => {})
  }, [])
  
  const statCards = [
    {
      key: 'properties',
      title: 'Обʼєкти',
      value: stats?.properties ?? 0,
      icon: <ApartmentOutlined />,
      color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      iconBg: '#667eea',
      route: '/properties',
    },
    {
      key: 'bookings',
      title: 'Бронювання',
      value: stats?.bookings ?? 0,
      icon: <HomeOutlined />,
      color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
      iconBg: '#f5576c',
      route: '/bookings',
    },
    {
      key: 'customers',
      title: 'Клієнти',
      value: stats?.customers ?? 0,
      icon: <TeamOutlined />,
      color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
      iconBg: '#4facfe',
      route: '/customers',
    },
    {
      key: 'locations',
      title: 'Локації',
      value: stats?.locations ?? 0,
      icon: <EnvironmentOutlined />,
      color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)',
      iconBg: '#43e97b',
      route: '/locations',
    },
  ]
  
  return (
    <div style={{ width: '100%' }}>
      {/* Welcome Header */}
      <Card 
        style={{ 
          marginBottom: 24, 
          background: `linear-gradient(135deg, ${token.colorPrimary} 0%, ${token.colorPrimaryHover} 100%)`,
          border: 'none',
          borderRadius: 12
        }}
        styles={{ body: { padding: '32px 24px' } }}
      >
        <Row align="middle" justify="space-between">
          <Col>
            <Title level={2} style={{ margin: 0, color: '#fff', fontWeight: 600 }}>
              Ласкаво просимо до RentMaster CRM
            </Title>
            <Typography.Text style={{ color: 'rgba(255,255,255,0.9)', fontSize: 16, display: 'block', marginTop: 8 }}>
              Ваша панель управління посуточною орендою
            </Typography.Text>
          </Col>
          <Col>
            <Card 
              style={{ 
                background: 'rgba(255,255,255,0.15)', 
                border: 'none',
                backdropFilter: 'blur(10px)',
                textAlign: 'center',
                minWidth: 180
              }}
            >
              <Typography.Text style={{ color: '#fff', fontSize: 12, display: 'block' }}>Поточний час</Typography.Text>
              <Typography.Text style={{ color: '#fff', fontSize: 20, fontWeight: 600, display: 'block', marginTop: 4 }}>
                {now.toLocaleTimeString('uk-UA', { hour: '2-digit', minute: '2-digit' })}
              </Typography.Text>
              <Typography.Text style={{ color: 'rgba(255,255,255,0.8)', fontSize: 12, display: 'block', marginTop: 4 }}>
                {now.toLocaleDateString('uk-UA', { weekday: 'long', day: 'numeric', month: 'long' })}
              </Typography.Text>
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Statistics Cards */}
      <Row gutter={[20, 20]} style={{ marginBottom: 24 }}>
        {statCards.map((card) => (
          <Col xs={24} sm={12} lg={6} key={card.key}>
            <Card
              hoverable
              onClick={() => navigate(card.route)}
              className="stat-card"
              style={{
                borderRadius: 12,
                border: 'none',
                boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                height: '100%',
              }}
              styles={{ body: { padding: 24 } }}
            >
              <div style={{ 
                width: 56, 
                height: 56, 
                borderRadius: 12,
                background: card.color,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                marginBottom: 16,
                fontSize: 24,
                color: '#fff',
                boxShadow: `0 4px 12px ${card.iconBg}40`
              }}>
                {card.icon}
              </div>
              <Statistic
                title={<span style={{ color: token.colorTextSecondary, fontSize: 14 }}>{card.title}</span>}
                value={card.value}
                valueStyle={{ fontSize: 32, fontWeight: 700, color: token.colorText }}
                prefix={null}
              />
              <div style={{ marginTop: 12 }}>
                <Button type="link" size="small" style={{ padding: 0 }} onClick={(e) => { e.stopPropagation(); navigate(card.route) }}>
                  Детальніше <ArrowUpOutlined style={{ transform: 'rotate(45deg)' }} />
                </Button>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Quick Actions */}
      <Row gutter={[20, 20]}>
        <Col xs={24} lg={16}>
          <Card 
            title={<><RocketOutlined style={{ marginRight: 8 }} />Швидкі дії</>}
            style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.08)' }}
          >
            <Space wrap size="middle">
              <Button 
                type="primary" 
                size="large"
                icon={<PlusOutlined />} 
                onClick={() => navigate('/properties')}
                style={{ height: 48, borderRadius: 8 }}
              >
                Додати обʼєкт
              </Button>
              <Button 
                size="large"
                icon={<HomeOutlined />} 
                onClick={() => navigate('/bookings')}
                style={{ height: 48, borderRadius: 8 }}
              >
                Нове бронювання
              </Button>
              <Button 
                size="large"
                icon={<EnvironmentOutlined />} 
                onClick={() => navigate('/locations')}
                style={{ height: 48, borderRadius: 8 }}
              >
                Додати локацію
              </Button>
              <Button 
                size="large"
                icon={<TeamOutlined />} 
                onClick={() => navigate('/customers')}
                style={{ height: 48, borderRadius: 8 }}
              >
                Новий клієнт
              </Button>
              <Button
                size="large"
                icon={<ThunderboltOutlined />} 
                onClick={async () => {
                  try { 
                    const r = await api.get('/api/integrations/google/start/', { withCredentials: true })
                    window.location.href = r.data.auth_url 
                  } catch {}
                }}
                style={{ height: 48, borderRadius: 8 }}
              >
                Google Calendar
              </Button>
            </Space>
            <Divider style={{ margin: '20px 0' }} />
            <Space direction="vertical" size="small" style={{ width: '100%' }}>
              <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                💡 <strong>Порада:</strong> Перейдіть до Календаря, щоб швидко створювати бронювання перетягуванням
              </Typography.Text>
              <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                📊 <strong>Статистика:</strong> Всі дані оновлюються автоматично при змінах
              </Typography.Text>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card 
            title={<><TrophyOutlined style={{ marginRight: 8 }} />Підказки</>}
            style={{ borderRadius: 12, boxShadow: '0 2px 8px rgba(0,0,0,0.08)', height: '100%' }}
          >
            <Space direction="vertical" size="middle" style={{ width: '100%' }}>
              <div style={{ 
                padding: 16, 
                background: token.colorBgContainer, 
                borderRadius: 8,
                border: `1px solid ${token.colorBorderSecondary}`
              }}>
                <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                  Перший крок
                </Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  Створіть локацію та додайте перший обʼєкт для початку роботи
                </Typography.Text>
              </div>
              <div style={{ 
                padding: 16, 
                background: token.colorBgContainer, 
                borderRadius: 8,
                border: `1px solid ${token.colorBorderSecondary}`
              }}>
                <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                  Інтеграції
                </Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  Підключіть Google Calendar для автоматичної синхронізації
                </Typography.Text>
              </div>
              <div style={{ 
                padding: 16, 
                background: token.colorBgContainer, 
                borderRadius: 8,
                border: `1px solid ${token.colorBorderSecondary}`
              }}>
                <Typography.Text strong style={{ display: 'block', marginBottom: 8 }}>
                  Календар
                </Typography.Text>
                <Typography.Text type="secondary" style={{ fontSize: 13 }}>
                  Використовуйте календар для перегляду всіх бронювань
                </Typography.Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

