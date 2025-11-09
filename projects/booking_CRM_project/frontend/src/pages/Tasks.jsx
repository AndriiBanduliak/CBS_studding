import { useEffect, useState } from 'react'
import { Button, DatePicker, Form, Input, Modal, Select, Space, Table, Tag, App as AntApp } from 'antd'
import dayjs from 'dayjs'
import { api } from '../api/client'

const statusOptions = [
  { value: 'todo', label: 'To Do' },
  { value: 'in_progress', label: 'In Progress' },
  { value: 'done', label: 'Done' },
]

export default function TasksPage() {
  const { message } = AntApp.useApp()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()
  const [properties, setProperties] = useState([])
  const [propMap, setPropMap] = useState({})

  const toPropOptions = (items) => {
    const map = new Map()
    for (const x of items) {
      const label = x.title || x.address || `#${x.id}`
      map.set(x.id, { value: x.id, label })
    }
    return { options: Array.from(map.values()), map: Object.fromEntries(Array.from(map.entries()).map(([id, opt])=>[id, opt.label])) }
  }

  async function load() {
    setLoading(true)
    try {
      const [t, p] = await Promise.all([
        api.get('/api/tasks/'),
        api.get('/api/properties/'),
      ])
      setList(t.data.results || t.data)
      const pItems = (p.data.results || p.data)
      const prop = toPropOptions(pItems.filter(x => x.status !== 'unavailable'))
      setProperties(prop.options)
      setPropMap(prop.map)
    } catch (_) { message.error('Не удалось загрузить данные') }
    finally { setLoading(false) }
  }
  useEffect(() => { load() }, [])

  async function refreshProps() {
    try {
      const p = await api.get('/api/properties/')
      const pItems = (p.data.results || p.data)
      const prop = toPropOptions(pItems.filter(x => x.status !== 'unavailable'))
      setProperties(prop.options)
      setPropMap(prop.map)
    } catch {}
  }
  async function openCreate() { setEditing(null); form.resetFields(); setProperties([]); await refreshProps(); setOpen(true) }
  async function openEdit(rec) { setEditing(rec); await refreshProps(); form.setFieldsValue({ ...rec, due_date: rec.due_date ? dayjs(rec.due_date) : null }); setOpen(true) }

  async function handleSubmit() {
    const v = await form.validateFields()
    const payload = {
      title: v.title,
      notes: v.notes,
      property: v.property || null,
      status: v.status || 'todo',
      due_date: v.due_date ? v.due_date.format('YYYY-MM-DD') : null,
    }
    try {
      if (editing) await api.put(`/api/tasks/${editing.id}/`, payload)
      else await api.post('/api/tasks/', payload)
      message.success('Сохранено'); setOpen(false); load()
    } catch (_) { message.error('Ошибка сохранения') }
  }

  const columns = [
    { title: 'Название', dataIndex: 'title' },
    { title: 'Объект', render: (_, r) => propMap[r.property] || r.property },
    { title: 'Дедлайн', dataIndex: 'due_date' },
    { title: 'Статус', dataIndex: 'status', render: v => <Tag color={v==='done'?'green': v==='in_progress'?'blue':'default'}>{statusOptions.find(s=>s.value===v)?.label||v}</Tag> },
    { title: 'Действия', width: 180, render: (_, r) => (<Space><Button onClick={()=>openEdit(r)}>Редактировать</Button></Space>) },
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type='primary' onClick={openCreate}>Новое задание</Button>
      </Space>
      <Table rowKey='id' loading={loading} columns={columns} dataSource={list} />

      <Modal open={open} title={editing ? 'Редактирование задания' : 'Новое задание'} onOk={handleSubmit} onCancel={()=>setOpen(false)} okText='Сохранить'>
        <Form layout='vertical' form={form}>
          <Form.Item label='Название' name='title' rules={[{ required: true }]}><Input /></Form.Item>
          <Form.Item label='Привязать к объекту' name='property'><Select allowClear options={properties} /></Form.Item>
          <Form.Item label='Дедлайн' name='due_date'><DatePicker format='YYYY-MM-DD' /></Form.Item>
          <Form.Item label='Статус' name='status'><Select options={statusOptions} /></Form.Item>
          <Form.Item label='Описание' name='notes'><Input.TextArea rows={3} /></Form.Item>
        </Form>
      </Modal>
    </div>
  )
}


