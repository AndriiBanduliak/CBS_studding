import { useEffect, useState } from 'react'
import { Button, DatePicker, Form, InputNumber, Modal, Select, Space, Table, Tag, App as AntApp } from 'antd'
import { api } from '../api/client'
import dayjs from 'dayjs'

const statusOptions = [
  { value: 'draft', label: 'Черновик' },
  { value: 'confirmed', label: 'Подтверждено' },
  { value: 'cancelled', label: 'Отменено' },
]

export default function BookingsPage() {
  const { message, modal } = AntApp.useApp()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()
  const [properties, setProperties] = useState([])
  const [customers, setCustomers] = useState([])
  const [propMap, setPropMap] = useState({})
  const [custMap, setCustMap] = useState({})

  const toPropOptions = (items) => {
    const map = new Map()
    for (const x of items) {
      const label = x.title || x.address || `#${x.id}`
      map.set(x.id, { value: x.id, label })
    }
    return { options: Array.from(map.values()), map: Object.fromEntries(Array.from(map.entries()).map(([id, opt])=>[id, opt.label])) }
  }

  async function loadAll() {
    setLoading(true)
    try {
      const [b, p, c] = await Promise.all([
        api.get('/api/bookings/'),
        api.get('/api/properties/'),
        api.get('/api/customers/'),
      ])
      setList(b.data.results || b.data)
      const pItems = (p.data.results || p.data)
      const cItems = (c.data.results || c.data)
      const prop = toPropOptions(pItems.filter(x => x.status !== 'unavailable'))
      setProperties(prop.options)
      setCustomers(cItems.map(x => ({ value: x.id, label: `${x.first_name || ''} ${x.last_name || ''}`.trim() || x.email || `#${x.id}` })))
      setPropMap(prop.map)
      setCustMap(Object.fromEntries(cItems.map(x => [x.id, (`${x.first_name || ''} ${x.last_name || ''}`.trim() || x.email || `#${x.id}`)])))
    } catch (_) { message.error('Не удалось загрузить данные') }
    finally { setLoading(false) }
  }
  useEffect(() => { loadAll() }, [])

  async function refreshRefs() {
    // Загружаем только справочники (без бронирований) для скорости
    try {
      const [p, c] = await Promise.all([api.get('/api/properties/'), api.get('/api/customers/')])
      const pItems = (p.data.results || p.data)
      const cItems = (c.data.results || c.data)
      const prop = toPropOptions(pItems.filter(x => x.status !== 'unavailable'))
      setProperties(prop.options)
      setCustomers(cItems.map(x => ({ value: x.id, label: `${x.first_name || ''} ${x.last_name || ''}`.trim() || x.email || `#${x.id}` })))
      setPropMap(prop.map)
      setCustMap(Object.fromEntries(cItems.map(x => [x.id, (`${x.first_name || ''} ${x.last_name || ''}`.trim() || x.email || `#${x.id}`)])))
    } catch { /* ignore */ }
  }

  async function openCreate() {
    setProperties([]); setCustomers([])
    await refreshRefs() // ensure fresh names
    setEditing(null); form.resetFields(); setOpen(true)
  }
  function openEdit(rec) {
    setEditing(rec)
    refreshRefs().then(()=>{
      form.setFieldsValue({
      property: rec.property,
      customer: rec.customer,
      guests: rec.guests,
      status: rec.status,
      range: [dayjs(rec.check_in), dayjs(rec.check_out)],
      })
    })
    setOpen(true)
  }

  async function handleSubmit() {
    const v = await form.validateFields()
    const payload = {
      property: v.property,
      customer: v.customer,
      guests: v.guests || 1,
      status: v.status || 'confirmed',
      check_in: v.range?.[0]?.format('YYYY-MM-DD'),
      check_out: v.range?.[1]?.format('YYYY-MM-DD'),
      source: 'crm',
    }
    try {
      if (editing) await api.put(`/api/bookings/${editing.id}/`, payload)
      else await api.post('/api/bookings/', payload)
      message.success('Сохранено')
      setOpen(false); loadAll()
    } catch (e) {
      const detail = e?.response?.data?.detail || e?.response?.data || e?.message || ''
      // Показать красивое предупреждение при конфликте дат
      if (String(detail).toLowerCase().includes('занят')) {
        const dates = `${payload.check_in} → ${payload.check_out}`
        const propName = propMap[payload.property] || payload.property
        // Попробуем подтянуть занятые интервалы для контекста
        try {
          const av = await api.get(`/api/properties/${payload.property}/availability/`, { params: { start: payload.check_in, end: payload.check_out } })
          const booked = (av.data?.booked || []).map(b=>`${b.check_in} → ${b.check_out}`).join(', ')
          modal.warning({
            title: 'Даты заняты',
            content: (
              <div>
                <div><b>{propName}</b></div>
                <div>Запрошенные даты: {dates}</div>
                {booked && <div style={{ marginTop: 8 }}>Занято в периоде: {booked}</div>}
              </div>
            )
          })
        } catch {
          modal.warning({ title: 'Даты заняты', content: `${propName}: ${dates}` })
        }
      } else {
        message.error('Ошибка сохранения ' + (typeof detail === 'string' ? detail : JSON.stringify(detail)))
      }
    }
  }

  const columns = [
    { title: 'Объект', render: (_, r) => propMap[r.property] || r.property },
    { title: 'Клиент', render: (_, r) => custMap[r.customer] || r.customer },
    { title: 'Заезд', dataIndex: 'check_in' },
    { title: 'Выезд', dataIndex: 'check_out' },
    { title: 'Гости', dataIndex: 'guests', width: 90 },
    { title: 'Статус', dataIndex: 'status', width: 140, render: v => <Tag color={v==='cancelled'?'default': v==='draft'?'orange':'green'}>{statusOptions.find(s=>s.value===v)?.label||v}</Tag> },
    { title: 'Действия', width: 320, render: (_, r) => (
      <Space>
        <Button onClick={() => openEdit(r)}>Редактировать</Button>
        <Button danger onClick={async()=>{ try { await api.delete(`/api/bookings/${r.id}/`); message.success('Удалено'); loadAll() } catch(e){ message.error('Не удалось удалить') }}}>Удалить</Button>
        {r.status !== 'cancelled' && (
          <Button onClick={async()=>{ try { await api.patch(`/api/bookings/${r.id}/`, { status: 'cancelled' }); message.success('Отменено'); loadAll() } catch(e){ message.error('Не удалось отменить') }}}>Отменить</Button>
        )}
      </Space>
    )},
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type='primary' onClick={openCreate}>Новое бронирование</Button>
      </Space>
      <Table rowKey='id' loading={loading} columns={columns} dataSource={list} />

      <Modal open={open} title={editing ? 'Редактирование бронирования' : 'Новое бронирование'} onOk={handleSubmit} onCancel={()=>setOpen(false)} okText='Сохранить'>
        <Form layout='vertical' form={form}>
          <Form.Item label='Объект' name='property' rules={[{ required: true }]}>
            <Select
              options={properties}
              showSearch
              optionFilterProp='label'
              filterOption={(input, option)=> (option?.label || '').toLowerCase().includes(input.toLowerCase())}
            />
          </Form.Item>
          <Form.Item label='Клиент' name='customer' rules={[{ required: true }]}>
            <Select options={customers} showSearch filterOption={(i,o)=>o?.label?.toLowerCase().includes(i.toLowerCase())} />
          </Form.Item>
          <Form.Item label='Даты' name='range' rules={[{ required: true }]}>
            <DatePicker.RangePicker format='YYYY-MM-DD' />
          </Form.Item>
          <Form.Item label='Гостей' name='guests'>
            <InputNumber min={1} style={{ width:'100%' }} />
          </Form.Item>
          <Form.Item label='Статус' name='status'>
            <Select options={statusOptions} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}


