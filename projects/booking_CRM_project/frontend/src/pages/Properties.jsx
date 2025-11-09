import { useEffect, useMemo, useState } from 'react'
import { Button, Form, Input, InputNumber, Select, Table, Space, Tag, Switch, Modal, App as AntApp } from 'antd'
import { api } from '../api/client'
import { useTableState } from '../hooks/useTableState'

const statusOptions = [
	{ value: 'available', label: 'Доступний' },
	{ value: 'booked', label: 'Заброньований' },
	{ value: 'cleaning', label: 'Прибирається' },
	{ value: 'unavailable', label: 'Недоступний' },
]

export default function PropertiesPage() {
    const { message, modal } = AntApp.useApp()
	const [list, setList] = useState([])
	const [loading, setLoading] = useState(false)
    const { tableProps } = useTableState()
	const [locations, setLocations] = useState([])
	const [modalOpen, setModalOpen] = useState(false)
	const [editing, setEditing] = useState(null)
	const [form] = Form.useForm()
	const [hardDelete, setHardDelete] = useState(false)

	async function fetchList() {
		setLoading(true)
		try {
			const { data } = await api.get('/api/properties/')
			const items = (data.results || data)
			setList(items.filter(it => it.status !== 'unavailable'))
		} catch (e) {
			message.error('Не вдалося завантажити список обʼєктів')
		} finally {
			setLoading(false)
		}
	}

	useEffect(() => { fetchList() }, [])

	useEffect(() => {
		(async () => {
			try {
				const { data } = await api.get('/api/locations/')
				const items = (data.results || data).map(l => ({ value: l.id, label: l.name }))
				setLocations(items)
			} catch (_) { /* ignore */ }
		})()
	}, [])

	function openCreate() {
		setEditing(null)
		form.resetFields()
        form.setFieldsValue({ capacity: 1, status: 'available' })
		setModalOpen(true)
	}

	function openEdit(record) {
		setEditing(record)
		form.setFieldsValue({ ...record, location_id: record.location?.id })
		setModalOpen(true)
	}

	async function handleSubmit() {
		const values = await form.validateFields()
        // авто-колір: за статусом, інакше — за локацією
        values.color_hex = pickAutoColor(values.status, values.location_id?.value || values.location_id)
		try {
			if (editing) {
				await api.put(`/api/properties/${editing.id}/`, values)
					message.success('Оновлено')
			} else {
				await api.post(`/api/properties/`, values)
					message.success('Створено')
			}
			setModalOpen(false)
			await fetchList()
		} catch (e) {
			const detail = e?.response?.data ? JSON.stringify(e.response.data) : ''
			message.error('Помилка збереження ' + detail)
		}
	}

	const statusColorMap = {
        available: '#16a34a',
        booked: '#2563eb',
        cleaning: '#f59e0b',
        unavailable: '#9ca3af',
    }

	function hashToPalette(id) {
        const palette = ['#0ea5e9', '#10b981', '#8b5cf6', '#ec4899', '#f97316', '#22c55e', '#14b8a6']
        if (!id && id !== 0) return '#64748b'
        const n = typeof id === 'number' ? id : parseInt(String(id).replace(/\D/g,'')) || 0
        return palette[n % palette.length]
	}

	function pickAutoColor(status, locationId) {
        return statusColorMap[status] || hashToPalette(locationId)
	}

	async function handleDelete(record) {
    modal.confirm({
			title: 'Видалити обʼєкт?',
			content: (
				<div style={{ marginTop: 8 }}>
					<Switch checked={hardDelete} onChange={setHardDelete} /> <span style={{ marginLeft: 8 }}>Удалить навсегда</span>
				</div>
			),
			onOk: async () => {
				try {
					const query = hardDelete ? '?hard=1' : ''
					await api.delete(`/api/properties/${record.id}/${query}`)
					message.success('Видалено')
					await fetchList()
				} catch (e) {
					const detail = e?.response?.data ? JSON.stringify(e.response.data) : ''
					message.error('Не вдалося видалити ' + detail)
				}
			},
    })
	}

	const columns = useMemo(() => [
		{ title: 'Назва', dataIndex: 'title' },
		{ title: 'Адреса', dataIndex: 'address' },
		{ title: 'Місткість', dataIndex: 'capacity', width: 120 },
		{ title: 'Статус', dataIndex: 'status', width: 160, render: (value) => {
			const map = { available: 'green', booked: 'blue', cleaning: 'orange', unavailable: 'default' }
			const label = statusOptions.find(s => s.value === value)?.label || value
			return <Tag color={map[value] || 'default'}>{label}</Tag>
		}},
		{ title: 'Локація', width: 180, render: (_, record) => record.location?.is_active ? record.location.name : '—' },
        { title: 'Колір', dataIndex: 'color_hex', width: 120, render: (_, record) => (
            <span style={{
                display:'inline-block', width:16, height:16, borderRadius:4,
                border:'1px solid #e5e7eb', backgroundColor: pickAutoColor(record.status, record.location?.id)
            }} />
        ) },
		{ title: 'Дії', key: 'actions', width: 220, render: (_, record) => (
			<Space>
				<Button onClick={() => openEdit(record)}>Редагувати</Button>
				<Button danger onClick={() => handleDelete(record)}>Видалити</Button>
			</Space>
		)},
	], [])

	return (
		<div>
			<Space style={{ marginBottom: 16 }}>
				<Button type="primary" onClick={openCreate}>Добавить объект</Button>
			</Space>
			<Table rowKey="id" loading={loading} columns={columns} dataSource={list} {...tableProps} />

			<Modal open={modalOpen} title={editing ? 'Редактирование объекта' : 'Новый объект'} onCancel={() => setModalOpen(false)} onOk={handleSubmit} okText="Сохранить">
				<Form layout="vertical" form={form}>
					<Form.Item label="Название" name="title" rules={[{ required: true, message: 'Укажите название' }]}>
						<Input />
					</Form.Item>
					<Form.Item label="Адрес" name="address" rules={[{ required: true, message: 'Укажите адрес' }]}>
						<Input />
					</Form.Item>
					<Form.Item label="Описание" name="description">
						<Input.TextArea rows={3} />
					</Form.Item>
					<Form.Item label="Вместимость" name="capacity" rules={[{ required: true }]}>
						<InputNumber min={1} style={{ width: '100%' }} />
					</Form.Item>
					<Form.Item label="Статус" name="status" rules={[{ required: true }]}>
						<Select options={statusOptions} />
					</Form.Item>
					<Form.Item label="Локация" name="location_id">
						<Select allowClear placeholder="Не выбрано" options={locations} />
					</Form.Item>
					<Form.Item label="Цвет" name="color_hex" rules={[{ required: true }]}>
						<Input placeholder="#RRGGBB" />
					</Form.Item>
				</Form>
			</Modal>
		</div>
	)
}
