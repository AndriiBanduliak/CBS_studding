import { useEffect, useState } from 'react'
import { Button, Form, Input, Modal, Space, Table, Tag, Switch, App as AntApp } from 'antd'
import { api } from '../api/client'
import { useTableState } from '../hooks/useTableState'

export default function CustomersPage() {
  const { message } = AntApp.useApp()
  const [list, setList] = useState([])
  const [loading, setLoading] = useState(false)
  const [open, setOpen] = useState(false)
  const [editing, setEditing] = useState(null)
  const [form] = Form.useForm()
  const { tableProps } = useTableState()

  async function fetchList() {
    setLoading(true)
    try {
      const { data } = await api.get('/api/customers/')
      setList(data.results || data)
    } catch (_) { message.error('Не удалось загрузить клиентов') }
    finally { setLoading(false) }
  }
  useEffect(() => { fetchList() }, [])

  function openCreate() { setEditing(null); form.resetFields(); setOpen(true) }
  function openEdit(rec) { setEditing(rec); form.setFieldsValue(rec); setOpen(true) }

  async function handleSubmit() {
    const values = await form.validateFields()
    try {
      if (editing) await api.put(`/api/customers/${editing.id}/`, values)
      else await api.post('/api/customers/', values)
      message.success('Сохранено')
      setOpen(false); fetchList()
    } catch (_) { message.error('Ошибка сохранения') }
  }

  const columns = [
    { title: 'Имя', render: (_, r) => `${r.first_name || ''} ${r.last_name || ''}`.trim() || '—' },
    { title: 'Email', dataIndex: 'email' },
    { title: 'Телефон', dataIndex: 'phone' },
    { title: 'VIP', dataIndex: 'is_vip', width: 100, render: v => v ? <Tag color="gold">VIP</Tag> : '—' },
    { title: 'Действия', width: 180, render: (_, r) => (
      <Space>
        <Button onClick={() => openEdit(r)}>Редактировать</Button>
      </Space>
    )}
  ]

  return (
    <div>
      <Space style={{ marginBottom: 16 }}>
        <Button type='primary' onClick={openCreate}>Добавить клиента</Button>
      </Space>
      <Table rowKey='id' loading={loading} columns={columns} dataSource={list} {...tableProps} />

      <Modal open={open} title={editing ? 'Редактирование клиента' : 'Новый клиент'} onOk={handleSubmit} onCancel={()=>setOpen(false)} okText='Сохранить'>
        <Form layout='vertical' form={form}>
          <Form.Item label='Имя' name='first_name'><Input /></Form.Item>
          <Form.Item label='Фамилия' name='last_name'><Input /></Form.Item>
          <Form.Item label='Email' name='email'><Input /></Form.Item>
          <Form.Item label='Телефон' name='phone'><Input /></Form.Item>
          <Form.Item label='Заметки' name='notes'><Input.TextArea rows={3} /></Form.Item>
          <Form.Item label='VIP' name='is_vip' valuePropName='checked'>
            <Switch />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}


