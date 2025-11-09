import { useEffect, useState } from 'react'
import { Button, Form, Input, Modal, Space, Table, Tag, Switch, App as AntApp } from 'antd'
import { api } from '../api/client'
import { useTableState } from '../hooks/useTableState'

export default function LocationsPage() {
	const [list, setList] = useState([])
	const [loading, setLoading] = useState(false)
	const [open, setOpen] = useState(false)
	const [editing, setEditing] = useState(null)
	const [form] = Form.useForm()
	const [hardDelete, setHardDelete] = useState(false)
	const { modal, message } = AntApp.useApp()
    const { tableProps } = useTableState()

	async function fetchList() {
		setLoading(true)
		try {
			const { data } = await api.get('/api/locations/')
			const items = (data.results || data)
			setList(items.filter(it => it.is_active))
		} catch (_) {
			message.error('Не вдалося завантажити локації')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => { fetchList() }, [])

	function openCreate() {
		setEditing(null)
		form.resetFields()
		form.setFieldsValue({ is_active: true })
		setOpen(true)
	}

	function openEdit(record) {
		setEditing(record)
		form.setFieldsValue(record)
		setOpen(true)
	}

	async function handleSubmit() {
		const values = await form.validateFields()
		try {
			if (editing) {
				await api.put(`/api/locations/${editing.id}/`, values)
					message.success('Оновлено')
			} else {
				await api.post('/api/locations/', values)
					message.success('Створено')
			}
			setOpen(false)
			await fetchList()
		} catch (_) {
			message.error('Помилка збереження')
		}
	}

	async function handleDelete(record) {
		modal.confirm({
			title: 'Удалить локацию?',
			content: (
				<div style={{ marginTop: 8 }}>
					<Switch checked={hardDelete} onChange={setHardDelete} /> <span style={{ marginLeft: 8 }}>Удалить навсегда</span>
				</div>
			),
			onOk: async () => {
				try {
					const query = hardDelete ? '?hard=1' : ''
					await api.delete(`/api/locations/${record.id}/${query}`)
					message.success('Видалено')
					await fetchList()
				} catch (e) {
					const detail = e?.response?.data ? JSON.stringify(e.response.data) : ''
					message.error('Не вдалося видалити ' + detail)
				}
			},
		})
	}

	const columns = [
		{ title: 'Назва', dataIndex: 'name' },
		{ title: 'Код', dataIndex: 'code', width: 160 },
		{ title: 'Статус', dataIndex: 'is_active', width: 120, render: v => v ? <Tag color="green">Активна</Tag> : <Tag>Вимкнена</Tag> },
		{ title: 'Дії', key: 'actions', width: 220, render: (_, record) => (
			<Space>
				<Button onClick={() => openEdit(record)}>Редагувати</Button>
				<Button danger onClick={() => handleDelete(record)}>Видалити</Button>
			</Space>
		)},
	]

	return (
		<div>
			<Space style={{ marginBottom: 16 }}>
				<Button type='primary' onClick={openCreate}>Добавить локацию</Button>
			</Space>
			<Table rowKey='id' loading={loading} columns={columns} dataSource={list} {...tableProps} />

			<Modal open={open} title={editing ? 'Редактирование локации' : 'Новая локация'} onCancel={() => setOpen(false)} onOk={handleSubmit} okText='Сохранить'>
				<Form layout='vertical' form={form}>
					<Form.Item label='Название' name='name' rules={[{ required: true, message: 'Укажите название' }]}>
						<Input />
					</Form.Item>
					<Form.Item label='Код (необязательно)' name='code'>
						<Input />
					</Form.Item>
					<Form.Item label='Описание' name='description'>
						<Input.TextArea rows={3} />
					</Form.Item>
				</Form>
			</Modal>
		</div>
	)
}
