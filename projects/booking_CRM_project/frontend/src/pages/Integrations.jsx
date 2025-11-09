import { useEffect, useState } from 'react'
import { Card, Table, Select, Button, Space, Typography, message } from 'antd'
import { api } from '../api/client'

export default function IntegrationsPage() {
  const [propsList, setPropsList] = useState([])
  const [cals, setCals] = useState([])
  const [loading, setLoading] = useState(false)

  async function load() {
    setLoading(true)
    try {
      const [p, c] = await Promise.all([
        api.get('/api/properties/'),
        api.get('/api/integrations/google/calendars/').catch(()=>({ data: { items: [] }})),
      ])
      setPropsList(p.data?.results || p.data || [])
      setCals(c.data?.items || [])
    } finally { setLoading(false) }
  }

  useEffect(() => { load() }, [])

  async function bindCalendar(propertyId, calendarId) {
    try {
      await api.patch(`/api/properties/${propertyId}/`, { calendar_id: calendarId })
      message.success('Календар привʼязано')
      setPropsList(list => list.map(it => it.id === propertyId ? { ...it, calendar_id: calendarId } : it))
    } catch (e) { message.error('Помилка збереження') }
  }

  const columns = [
    { title: 'Обʼєкт', dataIndex: 'title' },
    { title: 'Адреса', dataIndex: 'address' },
    {
      title: 'Google Calendar',
      render: (_, record) => (
        <Select
          showSearch
          style={{ minWidth: 240 }}
          placeholder="Виберіть календар"
          value={record.calendar_id || undefined}
          onChange={(val) => bindCalendar(record.id, val)}
          options={cals.map(c => ({ label: c.summary, value: c.id }))}
        />
      )
    }
  ]

  return (
    <Card title="Інтеграції → Google Calendar" extra={
      <Space>
        <Button onClick={load}>Оновити</Button>
        <Button type="primary" onClick={async()=>{
          try { const r = await api.get('/api/integrations/google/start/'); window.location.href = r.data.auth_url } catch {}
        }}>Підключити Google</Button>
      </Space>
    }>
      <Typography.Paragraph>
        Привʼяжіть календари до обʼєктів, щоб синхронізувати бронювання.
      </Typography.Paragraph>
      <Table rowKey="id" columns={columns} dataSource={propsList} loading={loading} pagination={false} />
    </Card>
  )
}


